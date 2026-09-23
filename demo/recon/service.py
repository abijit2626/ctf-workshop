"""
TinkerHub CTF - Recon Round target.

Exposes a few plain TCP "services" with canned banners. Participants nmap-scan
this container's ports, then connect to each open port (nc/telnet) to read
the banner. Two are decoys with no flag; one leaks the flag in its banner.

No external deps, no internet needed at runtime - stdlib only.
"""
import socketserver
import threading

FLAG = "flag{n3tw0rk_r3c0n_1s_ez}"

BANNERS = {
    2121: b"220 TinkerCorp FTP Server (ProFTPD 1.3.5) ready.\r\n",
    9200: b'{"name":"tinkercorp-node-1","cluster_name":"tinkercorp","version":{"number":"7.9.3"}}\n',
    7331: (
        b"=== TinkerCorp Internal Diagnostics Port ===\n"
        b"status: ok\n"
        b"build: v0.9.1-legacy\n"
        b"note: this port should NOT be internet-facing (ticket #4521)\n"
        + FLAG.encode() + b"\n"
    ),
}


class BannerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        banner = BANNERS.get(self.server.server_address[1], b"")
        try:
            self.request.sendall(banner)
        except OSError:
            pass


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def serve_port(port):
    with ThreadingTCPServer(("0.0.0.0", port), BannerHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    threads = []
    for port in BANNERS:
        t = threading.Thread(target=serve_port, args=(port,), daemon=True)
        t.start()
        threads.append(t)
    print(f"Serving banners on ports: {list(BANNERS)}", flush=True)
    for t in threads:
        t.join()
