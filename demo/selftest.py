"""
Automated end-to-end check for all 4 demo challenges. Run after the stack is
up. Exits non-zero if anything is broken, so it's safe to gate the demo on.
"""
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.parse

WEB_BASE = "http://localhost:5000"
RECON_HOST = "localhost"
RECON_PORTS = {2121: False, 9200: False, 7331: True}  # port -> expects flag
EXPECTED_FLAGS = {
    "recon": "flag{n3tw0rk_r3c0n_1s_ez}",
    "ch1": "flag{v13w_s0urc3_ftw}",
    "sqli": "flag{sql1_1s_n3v3r_s4f3}",
    "stego": "flag{ls8_hunt3r_1}",
}

results = []


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
            with socket.create_connection((RECON_HOST, port), timeout=2):
                return True
        except OSError:
            time.sleep(1)
    return False


def http_get(path):
    with urllib.request.urlopen(WEB_BASE + path, timeout=5) as r:
        return r.read().decode("utf-8", errors="replace")


def http_post(path, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(WEB_BASE + path, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.read().decode("utf-8", errors="replace")


def main():
    print("=== Waiting for services ===")
    web_up = wait_for_web()
    check("webapp reachable", web_up)
    if not web_up:
        print("Aborting - webapp never came up. Is `docker compose up -d` running?")
        sys.exit(1)

    for port in RECON_PORTS:
        up = wait_for_port(port)
        check(f"recon port {port} reachable", up)

    print("\n=== Recon challenge ===")
    try:
        with socket.create_connection((RECON_HOST, 7331), timeout=3) as s:
            banner = s.recv(4096).decode(errors="replace")
        ok = EXPECTED_FLAGS["recon"] in banner
        check("recon flag in banner", ok, "" if ok else banner[:80])
    except Exception as e:
        check("recon flag in banner", False, str(e))

    print("\n=== Web: view-source challenge ===")
    try:
        html = http_get("/ch1")
        ok = EXPECTED_FLAGS["ch1"] in html
        check("ch1 flag in HTML source", ok)
    except Exception as e:
        check("ch1 flag in HTML source", False, str(e))

    print("\n=== Web: SQL injection challenge ===")
    try:
        fail_page = http_post("/login", {"username": "admin", "password": "wrong"})
        check("login rejects bad password", "Invalid username" in fail_page)

        bypass_page = http_post(
            "/login",
            {"username": "admin' OR '1'='1' -- ", "password": "x"},
        )
        ok = EXPECTED_FLAGS["sqli"] in bypass_page
        check("SQLi bypass returns flag", ok)
    except Exception as e:
        check("SQLi bypass returns flag", False, str(e))

    print("\n=== Steganography challenge ===")
    try:
        req = urllib.request.Request(WEB_BASE + "/static/challenges/flag.png")
        with urllib.request.urlopen(req, timeout=5) as r:
            data = r.read()
        check("stego file downloadable via web portal", len(data) > 0, f"{len(data)} bytes")

        tmp_path = "/tmp/_selftest_flag.png"
        with open(tmp_path, "wb") as f:
            f.write(data)
        decoded = subprocess.run(
            ["python3", "stego/decode_stego.py", tmp_path],
            capture_output=True, text=True, cwd=__file__.rsplit("/", 1)[0] or ".",
        ).stdout.strip()
        ok = decoded == EXPECTED_FLAGS["stego"]
        check("stego decode matches expected flag", ok, decoded)
    except Exception as e:
        check("stego decode matches expected flag", False, str(e))

    print("\n=== Summary ===")
    failed = [name for name, ok, _ in results if not ok]
    if failed:
        print(f"{len(failed)} check(s) FAILED: {', '.join(failed)}")
        sys.exit(1)
    print(f"All {len(results)} checks passed. Demo is ready.")


if __name__ == "__main__":
    main()
