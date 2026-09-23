#!/usr/bin/env bash
# One-command demo control: build, start, self-test, print the cheat sheet
# participants need. Safe to re-run any time to reset to a clean state.
set -euo pipefail
cd "$(dirname "$0")"

CMD="${1:-up}"

start_podman_socket_if_needed() {
    if command -v systemctl >/dev/null 2>&1; then
        if systemctl --user list-unit-files podman.socket >/dev/null 2>&1; then
            systemctl --user start podman.socket 2>/dev/null || true
        fi
    fi
}

lan_ip() {
    # Source IP the OS would use to reach the outside world - works even
    # with no internet, since it's just a routing table lookup.
    ip route get 1.1.1.1 2>/dev/null | awk '{for (i=1;i<=NF;i++) if ($i=="src") print $(i+1)}' \
        || hostname -I | awk '{print $1}'
}

print_cheatsheet() {
    local ip
    ip="$(lan_ip)"
    echo ""
    echo "=================================================================="
    echo " DEMO READY - give participants this:"
    echo "=================================================================="
    echo " Web + stego download:  http://${ip}:5000"
    echo " Recon target:          ${ip}   (nmap it, then connect to what you find)"
    echo ""
    echo " Recon ports exposed:   2121, 9200, 7331 (one of these leaks a flag)"
    echo "=================================================================="
    echo ""
}

up() {
    start_podman_socket_if_needed
    echo "==> Building and starting containers..."
    docker compose up -d --build
    echo "==> Running self-test..."
    if python3 selftest.py; then
        print_cheatsheet
    else
        echo ""
        echo "Self-test FAILED - do not demo yet. See failures above."
        echo "Try: docker compose logs, then './demo.sh down && ./demo.sh up'"
        exit 1
    fi
}

down() {
    echo "==> Stopping containers..."
    docker compose down
}

reset() {
    down
    up
}

status() {
    docker compose ps
    echo ""
    print_cheatsheet
}

case "$CMD" in
    up) up ;;
    down) down ;;
    reset) reset ;;
    status) status ;;
    test) python3 selftest.py ;;
    *)
        echo "Usage: $0 {up|down|reset|status|test}"
        exit 1
        ;;
esac
