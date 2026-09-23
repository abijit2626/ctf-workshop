"""
TinkerHub CTF - Network Recon round target.

Single host, multiple TCP services on different ports. Participants port-scan
this container, then interact with each open port to figure out which ones
matter. Two are decoys with no flag; the rest are the real challenges.

Design note: everything lives on one target host/IP rather than multiple
container IPs on a custom docker network. Arbitrary container IPs are not
reliably reachable from outside the docker host across every Docker/Podman/
Docker-Desktop setup (rootless Podman and Docker Desktop in particular only
forward explicitly published ports, not whole subnets), and per-container
"real" LAN IPs would need macvlan, which is fragile on WiFi adapters. A single
published-port host works identically everywhere.

Stdlib only, no external deps, fully offline at runtime.
"""
import socketserver
import threading

FLAG_DIAGNOSTICS = "flag{n3tw0rk_r3c0n_1s_ez}"
FLAG_ANON_FTP = "flag{an0n_ftp_no_p4ssw0rd}"
FLAG_SECRET_CMD = "flag{s3nd_th3_r1ght_str1ng}"
FLAG_HOST_HEADER = "flag{h0st_h34d3r_l34k}"

SECRET_PHRASE = "OPEN SESAME"
TRUSTED_HOSTNAME = "internal.tinkercorp.lab"

# --- Simple decoy banners (connect, get text, connection closes) ---------

DECOY_BANNERS = {
    2121: b"220 TinkerCorp FTP Server (ProFTPD 1.3.5) ready.\r\n",
    9200: b'{"name":"tinkercorp-node-1","cluster_name":"tinkercorp","version":{"number":"7.9.3"}}\n',
    7331: (
        b"=== TinkerCorp Internal Diagnostics Port ===\n"
        b"status: ok\n"
        b"build: v0.9.1-legacy\n"
        b"note: this port should NOT be internet-facing (ticket #4521)\n"
        + FLAG_DIAGNOSTICS.encode() + b"\n"
    ),
}


class DecoyBannerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        banner = DECOY_BANNERS.get(self.server.server_address[1], b"")
        try:
            self.request.sendall(banner)
        except OSError:
            pass


# --- Challenge: simplified anonymous "FTP" (text protocol, port 2100) ----
# Not full RFC 959 - a real `ftp` client's passive-mode data channel would
# need masquerade IP config that changes per-deployment. This is deliberately
# a single-connection text protocol solvable with `nc`, teaching the same
# "anonymous login exposes files" concept without NAT fragility.

class AnonFTPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b"220 TinkerCorp FTP Server (chal-ftp) ready.\r\n")
        logged_in = False
        try:
            while True:
                line = self.rfile.readline()
                if not line:
                    return
                cmd = line.decode(errors="replace").strip()
                upper = cmd.upper()
                if upper.startswith("USER"):
                    parts = cmd.split(maxsplit=1)
                    if len(parts) == 2 and parts[1].strip().lower() == "anonymous":
                        self.wfile.write(b"331 Please specify the password.\r\n")
                    else:
                        self.wfile.write(b"530 Login incorrect.\r\n")
                elif upper.startswith("PASS"):
                    logged_in = True
                    self.wfile.write(b"230 Login successful.\r\n")
                elif upper.startswith("LIST"):
                    if not logged_in:
                        self.wfile.write(b"530 Please login with USER and PASS.\r\n")
                        continue
                    self.wfile.write(b"150 Here comes the directory listing.\r\n")
                    self.wfile.write(b"-rw-r--r-- 1 ftp ftp 40 Jan 01 00:00 flag.txt\r\n")
                    self.wfile.write(b"226 Directory send OK.\r\n")
                elif upper.startswith("RETR"):
                    if not logged_in:
                        self.wfile.write(b"530 Please login with USER and PASS.\r\n")
                        continue
                    parts = cmd.split(maxsplit=1)
                    filename = parts[1].strip() if len(parts) == 2 else ""
                    if filename.lower() == "flag.txt":
                        self.wfile.write(b"150 Opening data connection for flag.txt.\r\n")
                        self.wfile.write((FLAG_ANON_FTP + "\r\n").encode())
                        self.wfile.write(b"226 Transfer complete.\r\n")
                    else:
                        self.wfile.write(b"550 Failed to open file.\r\n")
                elif upper.startswith("QUIT"):
                    self.wfile.write(b"221 Goodbye.\r\n")
                    return
                else:
                    self.wfile.write(b"500 Unknown command.\r\n")
        except OSError:
            return


# --- Challenge: secret command over raw TCP (port 4444) ------------------

class SecretCommandHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b"Enter the access phrase: ")
        try:
            line = self.rfile.readline()
        except OSError:
            return
        phrase = line.decode(errors="replace").strip()
        if phrase == SECRET_PHRASE:
            self.wfile.write((FLAG_SECRET_CMD + "\n").encode())
        else:
            self.wfile.write(b"Access denied.\n")


# --- Challenge (stretch): HTTP Host-header leak (port 8080) ---------------

class HostHeaderHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            request_line = self.rfile.readline().decode(errors="replace")
            headers = {}
            while True:
                header_line = self.rfile.readline().decode(errors="replace")
                if header_line in ("\r\n", "\n", ""):
                    break
                if ":" in header_line:
                    k, v = header_line.split(":", 1)
                    headers[k.strip().lower()] = v.strip()
        except OSError:
            return

        host = headers.get("host", "")
        if host.lower() == TRUSTED_HOSTNAME:
            body = f"Internal dashboard\n{FLAG_HOST_HEADER}\n"
        else:
            body = "TinkerCorp public site. Nothing to see here.\n"

        response = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Content-Type: text/plain\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{body}"
        )
        try:
            self.wfile.write(response.encode())
        except OSError:
            pass


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


PORT_HANDLERS = {
    2121: DecoyBannerHandler,
    9200: DecoyBannerHandler,
    7331: DecoyBannerHandler,
    2100: AnonFTPHandler,
    4444: SecretCommandHandler,
    8080: HostHeaderHandler,
}


def serve_port(port, handler_cls):
    with ThreadingTCPServer(("0.0.0.0", port), handler_cls) as server:
        server.serve_forever()


if __name__ == "__main__":
    threads = []
    for port, handler_cls in PORT_HANDLERS.items():
        t = threading.Thread(target=serve_port, args=(port, handler_cls), daemon=True)
        t.start()
        threads.append(t)
    print(f"Serving on ports: {list(PORT_HANDLERS)}", flush=True)
    for t in threads:
        t.join()
