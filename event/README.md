# TinkerHub CTF - Full One-Day Event

18 challenges across 3 rounds: Network Recon, Web Exploitation, and
Steganography. Fully offline at runtime, Dockerized, self-testing.

| Round | # | Notes |
|---|---|---|
| Network Recon | 4 | 1 marked stretch |
| Web Exploitation | 9 | |
| Steganography | 5 | 1 marked stretch |

Full challenge list, descriptions, point values, flags, and tiered hints are
in `ctfd-import/challenges.yml`. Organizer solve-steps are in `ANSWERS.md`.

## Quick start (one command)

```bash
cd event
./event.sh up
```

This builds both containers, starts them, runs an automated test of **all
18 flags** (recon banners/protocols, every web bug, every stego file), and
prints the exact IP/ports to give participants - auto-detected from the
host's network route. If anything fails, it says so and refuses to print
"ready", so you never run the event on something broken.

Other commands:
```bash
./event.sh status   # reprint the cheat sheet / show container state
./event.sh test       # rerun just the self-test
./event.sh reset      # down + up, back to a clean state
./event.sh down        # stop everything
```

## Putting it on the lab network

1. Get the host laptop and all participant devices on the same network
   (existing lab router/switch, or turn the host laptop into a WiFi hotspot).
2. Open the firewall for ports `5000, 2121, 9200, 7331, 2100, 4444, 8080`:
   - Linux (ufw): `sudo ufw allow 5000/tcp 2121/tcp 9200/tcp 7331/tcp 2100/tcp 4444/tcp 8080/tcp`
   - Windows: Defender Firewall -> Advanced Settings -> Inbound Rules -> New
     Rule -> Port -> enter the port list -> Allow
   - macOS: System Settings -> Network -> Firewall -> Options -> allow
     incoming, or disable for the exercise (isolated network, low risk)
3. Run `./event.sh up` - the cheat sheet it prints already has the correct
   LAN IP, not `localhost`.

**Design note on Round 1:** all recon challenges live on one target host
(many ports), not multiple container IPs simulating a ping-sweep across
several machines. Arbitrary container IPs on a custom docker network are
not reliably reachable from outside the docker host across every
Docker/Podman/Docker-Desktop setup, and giving containers real per-host LAN
IPs would need a macvlan network, which is fragile on WiFi adapters. A
single host with several ports is portable everywhere and teaches the same
skills (port scanning, banner grabbing, protocol interaction).

## Setting up CTFd

`ctfd-import/challenges.yml` is a structured reference (title, category,
description, point value, flag, and 2-3 tiered hints with costs) for every
challenge - not a native CTFd export/import zip. That internal export
format is version-specific, and shipping a wrong one can silently fail to
import, so the safer path with only 18 challenges is:

1. Stand up CTFd (`docker run` or their own docker-compose - see
   [CTFd's install docs](https://docs.ctfd.io/) offline-cached if needed).
2. In CTFd admin: Challenges -> create one per entry in `challenges.yml`,
   using it as your source of truth (category, description, points, flag,
   hints + hint costs). Budget 60-90 minutes for all 18.
3. In each description, replace `<SERVER_IP>` with the actual LAN IP
   `./event.sh up` prints on event day (it may differ from any IP used
   during testing).

If you'd rather script the import against CTFd's REST API instead of
clicking through the UI, ask and I'll write that script.

## Pre-event testing checklist

- [ ] `./event.sh up` completes and prints "All 38 checks passed."
- [ ] From a **second device** on the same network (not the host laptop),
      confirm you can: `nmap` the host IP, `nc` into port 7331, and load
      `http://<ip>:5000` in a browser.
- [ ] Firewall rules applied on the host laptop for all 7 ports.
- [ ] CTFd is reachable from participant devices and challenges are
      imported with `<SERVER_IP>` replaced in each description.
- [ ] Do one full read-through of `ctfd-import/challenges.yml` hints for
      typos/clarity - these are what participants see, unlike `ANSWERS.md`.
- [ ] After the event (or between test runs), `./event.sh reset` to return
      to a clean state - everything here is stateless, so this is instant
      and safe.

## Folder structure

```
event/
├── event.sh                 # one-command build/start/test/reset/down
├── selftest.py               # automated check of all 18 flags
├── docker-compose.yml
├── recon/                    # Round 1 target (6 TCP ports, stdlib only)
├── webapp/                   # Round 2 Flask app (9 routes) + stego downloads
├── stego/                    # Round 3 file generator + organizer decode tools
├── ctfd-import/challenges.yml # participant-facing text: descriptions + hints
├── ANSWERS.md                 # organizer-only: solve steps + flags
└── README.md                  # this file
```
