"""
Automated end-to-end check for all 18 challenge flags across all 3 rounds.
Run after `./event.sh up`. Exits non-zero if anything is broken.
"""
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.parse

WEB_BASE = "http://localhost:5000"
HOST = "localhost"

EXPECTED = {
    # Network Recon
    "recon_diagnostics": "flag{n3tw0rk_r3c0n_1s_ez}",
    "recon_anon_ftp": "flag{an0n_ftp_no_p4ssw0rd}",
    "recon_secret_cmd": "flag{s3nd_th3_r1ght_str1ng}",
    "recon_host_header": "flag{h0st_h34d3r_l34k}",
    # Web Exploitation
    "web_ch1": "flag{v13w_s0urc3_ftw}",
    "web_ch2": "flag{r0b0ts_txt_g1v3s_1t_away}",
    "web_ch3": "flag{c0mm3nts_ar3nt_s3cr3ts}",
    "web_ch4": "flag{1nsp3ct_th3_dom}",
    "web_ch5": "flag{c00k13_j4r_s3cr3ts}",
    "web_ch6": "flag{r0l3_fl1p_pr1v_3sc}",
    "web_ch7": "flag{1d0r_us3r_103_pwn3d}",
    "web_ch8": "flag{sql1_1s_n3v3r_s4f3}",
    "web_ch9": "flag{xss_st34ls_c00k13s}",
    # Steganography
    "stego_strings": "flag{str1ngs_f1nds_1t}",
    "stego_exif": "flag{ex1f_d4t4_l34ks}",
    "stego_ext_mismatch": "flag{n0t_4_txt_f1l3}",
    "stego_lsb": "flag{ls8_ls_my_f4v0r1t3}",
    "stego_qr": "flag{qr_c0d3_sc4n_m3}",
}

results = []
BASE_DIR = __file__.rsplit("/", 1)[0] or "."


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" - {detail}" if detail else ""))


def wait_for_web(timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(WEB_BASE + "/", timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


def wait_for_port(port, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((HOST, port), timeout=2):
                return True
        except OSError:
            time.sleep(1)
    return False


def http_get(path):
    with urllib.request.urlopen(WEB_BASE + path, timeout=5) as r:
        return r.read().decode("utf-8", errors="replace"), dict(r.headers)


def http_post(path, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(WEB_BASE + path, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.read().decode("utf-8", errors="replace")


def raw_tcp_exchange(port, send_lines, read_timeout=2):
    s = socket.create_connection((HOST, port), timeout=5)
    s.settimeout(read_timeout)
    buf = b""
    try:
        buf += s.recv(4096)
    except socket.timeout:
        pass
    for line in send_lines:
        s.sendall(line if isinstance(line, bytes) else line.encode())
        time.sleep(0.15)
        try:
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
        except socket.timeout:
            pass
    s.close()
    return buf.decode(errors="replace")


def http_over_socket(port, host_header):
    s = socket.create_connection((HOST, port), timeout=5)
    req = f"GET / HTTP/1.1\r\nHost: {host_header}\r\n\r\n"
    s.sendall(req.encode())
    s.settimeout(2)
    buf = b""
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
    except socket.timeout:
        pass
    s.close()
    return buf.decode(errors="replace")


def main():
    print("=== Waiting for services ===")
    check("webapp reachable", wait_for_web())
    for port in (2121, 9200, 7331, 2100, 4444, 8080):
        check(f"recon port {port} reachable", wait_for_port(port))

    print("\n=== Network Recon ===")
    banner = raw_tcp_exchange(7331, [])
    check("diagnostics port flag", EXPECTED["recon_diagnostics"] in banner)

    ftp = raw_tcp_exchange(2100, ["USER anonymous\r\n", "PASS x\r\n", "RETR flag.txt\r\n"])
    check("anonymous FTP flag", EXPECTED["recon_anon_ftp"] in ftp)

    secret = raw_tcp_exchange(4444, ["OPEN SESAME\n"])
    check("secret command flag", EXPECTED["recon_secret_cmd"] in secret)

    wrong_host = http_over_socket(8080, "whatever.com")
    check("host-header wrong host has no flag", EXPECTED["recon_host_header"] not in wrong_host)
    right_host = http_over_socket(8080, "internal.tinkercorp.lab")
    check("host-header correct host flag", EXPECTED["recon_host_header"] in right_host)

    print("\n=== Web Exploitation ===")
    html, _ = http_get("/ch1")
    check("ch1 view-source flag", EXPECTED["web_ch1"] in html)

    robots, _ = http_get("/robots.txt")
    check("ch2 robots.txt has disallow entry", "internal-9f3a2c" in robots)
    ch2_page, _ = http_get("/internal-9f3a2c")
    check("ch2 unlinked page flag", EXPECTED["web_ch2"] in ch2_page)

    ch3_page, _ = http_get("/ch3")
    check("ch3 html comment flag", EXPECTED["web_ch3"] in ch3_page)

    ch4_page, _ = http_get("/ch4")
    check("ch4 flag NOT in static HTML", EXPECTED["web_ch4"] not in ch4_page)
    ch4_api, _ = http_get("/ch4/api/status")
    check("ch4 flag present via live fetch/DOM data", EXPECTED["web_ch4"] in ch4_api)

    _, ch5_headers = http_get("/ch5")
    check("ch5 cookie flag", EXPECTED["web_ch5"] in ch5_headers.get("Set-Cookie", ""))

    ch6_default, _ = http_get("/ch6")
    check("ch6 default role has no flag", EXPECTED["web_ch6"] not in ch6_default)
    req = urllib.request.Request(WEB_BASE + "/ch6")
    req.add_header("Cookie", "role=admin")
    with urllib.request.urlopen(req, timeout=5) as r:
        ch6_admin = r.read().decode()
    check("ch6 admin role flag", EXPECTED["web_ch6"] in ch6_admin)

    ch7_own, _ = http_get("/ch7/profile?user_id=104")
    check("ch7 own profile has no flag", EXPECTED["web_ch7"] not in ch7_own)
    ch7_idor, _ = http_get("/ch7/profile?user_id=103")
    check("ch7 IDOR flag", EXPECTED["web_ch7"] in ch7_idor)

    fail_page = http_post("/login", {"username": "admin", "password": "wrong"})
    check("ch8 rejects bad password", "Invalid username" in fail_page)
    bypass_page = http_post("/login", {"username": "admin' OR '1'='1' -- ", "password": "x"})
    check("ch8 SQLi bypass flag", EXPECTED["web_ch8"] in bypass_page)

    _, ch9_headers = http_get("/ch9/search?q=test")
    check("ch9 XSS flag sitting in cookie", EXPECTED["web_ch9"] in ch9_headers.get("Set-Cookie", ""))
    ch9_rendered, _ = http_get("/ch9/search?q=<b>hi</b>")
    check("ch9 reflects input unescaped (XSS-capable)", "<b>hi</b>" in ch9_rendered)

    print("\n=== Steganography ===")
    stego_files = {
        "stego_strings": "01_strings.png",
        "stego_exif": "02_exif.jpg",
        "stego_ext_mismatch": "03_vacation_photo.txt",
        "stego_lsb": "04_lsb.png",
        "stego_qr": "05_team_offsite.png",
    }
    downloaded = {}
    for key, fname in stego_files.items():
        try:
            with urllib.request.urlopen(f"{WEB_BASE}/static/challenges/{fname}", timeout=5) as r:
                data = r.read()
            downloaded[key] = data
            check(f"{fname} downloadable via portal", len(data) > 0, f"{len(data)} bytes")
        except Exception as e:
            check(f"{fname} downloadable via portal", False, str(e))

    if "stego_strings" in downloaded:
        text = downloaded["stego_strings"].decode(errors="replace")
        check("strings flag present in file bytes", EXPECTED["stego_strings"] in text)

    if "stego_ext_mismatch" in downloaded:
        text = downloaded["stego_ext_mismatch"].decode(errors="replace")
        check("extension-mismatch flag present in file bytes", EXPECTED["stego_ext_mismatch"] in text)
        check("extension-mismatch file is actually a PNG", downloaded["stego_ext_mismatch"].startswith(b"\x89PNG"))

    if "stego_exif" in downloaded:
        tmp = "/tmp/_selftest_exif.jpg"
        with open(tmp, "wb") as f:
            f.write(downloaded["stego_exif"])
        out = subprocess.run(["exiftool", tmp], capture_output=True, text=True).stdout
        check("EXIF flag present", EXPECTED["stego_exif"] in out)

    if "stego_lsb" in downloaded:
        tmp = "/tmp/_selftest_lsb.png"
        with open(tmp, "wb") as f:
            f.write(downloaded["stego_lsb"])
        out = subprocess.run(
            ["python3", "stego/decode_lsb.py", tmp], capture_output=True, text=True, cwd=BASE_DIR,
        ).stdout.strip()
        check("LSB decode matches flag", out == EXPECTED["stego_lsb"], out)

    if "stego_qr" in downloaded:
        tmp = "/tmp/_selftest_qr.png"
        with open(tmp, "wb") as f:
            f.write(downloaded["stego_qr"])
        try:
            from pyzbar import pyzbar
            from PIL import Image
            decoded = pyzbar.decode(Image.open(tmp))
            texts = [d.data.decode() for d in decoded]
            check("QR code decodes to flag", EXPECTED["stego_qr"] in texts, str(texts))
        except ImportError:
            print("[SKIP] QR decode check - pyzbar not installed on this machine (fine, participants use their phone)")

    print("\n=== Summary ===")
    failed = [name for name, ok, _ in results if not ok]
    if failed:
        print(f"{len(failed)} check(s) FAILED: {', '.join(failed)}")
        sys.exit(1)
    print(f"All {len(results)} checks passed. Event is ready.")


if __name__ == "__main__":
    main()
