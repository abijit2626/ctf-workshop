# TinkerHub CTF - Working Demo (4 challenges)

A small, fully-working slice of the planned study jam: one recon challenge,
two web exploitation challenges, and one steganography challenge. Built to
show the club the concept and the hint-driven, self-discovery philosophy
before committing to building the full ~19-challenge event.

Everything here is real and tested end-to-end (not just a mockup):
recon banners, the SQLi bypass, and the LSB-encoded image all actually work.

## What's inside

| Round | Challenge | Flag |
|---|---|---|
| Recon | Diagnostics port (nmap + banner grab) | `flag{n3tw0rk_r3c0n_1s_ez}` |
| Web | Company Announcements (view page source) | `flag{v13w_s0urc3_ftw}` |
| Web | Staff Login (SQL injection bypass) | `flag{sql1_1s_n3v3r_s4f3}` |
| Stego | flag.png (LSB steganography) | `flag{ls8_hunt3r_1}` |

Hints (3 tiers each) are in `HINTS.md` - use those live during the pitch to
show how a participant would be nudged instead of just told the answer.

## Running it (one command)

Requires Docker (or Podman with the docker-compose shim, which is what this
was tested on). No internet needed at runtime - only the one-time image
build pulls `python:3.12-slim` and Flask.

```bash
cd demo
./demo.sh up
```

This builds both containers, starts them, runs an automated self-test against
all 4 challenges (recon banner, view-source flag, SQLi bypass, stego
decode), and prints the exact IP/URL to give participants - detected
automatically from the host's network route. If any check fails, it tells
you and refuses to print the "ready" banner, so you never walk on stage with
something broken.

Other commands:
```bash
./demo.sh status   # show container state + reprint the cheat sheet
./demo.sh test      # rerun just the self-test (containers already up)
./demo.sh reset     # down + up again, back to a clean state
./demo.sh down       # stop everything
```

The stego file is also served over the web portal at `/static/challenges/flag.png`
so participants can download it from their own device - no shared folder or
USB stick needed. Regenerate it with `python3 stego/generate_stego.py` if you
ever change the flag (requires `pip install Pillow` once, then rerun
`./demo.sh reset` to rebuild the image with the new file).

Containers are stateless, so `./demo.sh reset` always returns to a clean
state - safe to run between practice attempts or after someone messes with
the login form.

## Putting it on a shared network (lab/router or laptop hotspot)

1. Get the host laptop and all participant devices on the same network
   (existing lab router/switch, or turn the host laptop into a WiFi hotspot).
2. Open the firewall for ports `5000, 2121, 7331, 9200` on the host:
   - Linux (ufw): `sudo ufw allow 5000/tcp && sudo ufw allow 2121/tcp && sudo ufw allow 7331/tcp && sudo ufw allow 9200/tcp`
   - Windows: Defender Firewall → Advanced Settings → Inbound Rules → New Rule → Port → `5000,2121,7331,9200` → Allow
   - macOS: System Settings → Network → Firewall → Options → allow incoming, or disable for the exercise (isolated network, low risk)
3. Run `./demo.sh up` - the printed cheat sheet already has the correct LAN IP
   for participants to use, not `localhost`.

## Live demo script (for the club pitch)

**1. Recon (2-3 min)**
```bash
nmap -p 2000-9300 -T4 <ip-from-demo.sh-output>   # or 'localhost' if presenting solo
```
Show the open ports. Ask "which one looks interesting?" Then:
```bash
nc <ip> 7331
```
Flag appears in the banner. Point out the two decoy ports (2121, 9200) that
look like real services but lead nowhere - teaches "not everything you find
is useful, that's part of recon."

**2. Web - view source (1 min)**
Open `http://localhost:5000/ch1` in a browser. Page looks blank. Ctrl+U to
view source, Ctrl+F for `flag{`. Instant "oh, that's clever" moment - good
for showing how low the entry bar is for challenge #1.

**3. Web - SQL injection (2 min)**
Open `http://localhost:5000/login`. Try a wrong password first (fails
normally). Then enter username `admin' OR '1'='1' -- ` with any password.
Flag appears. Good moment to briefly explain *why* it works (the quote
breaks out of the query string) - ties into the hint tiers in `HINTS.md`.

**4. Steganography (1-2 min)**
Show `flag.png` (download it from the portal, or open `stego/output/flag.png`)
- looks like a plain gradient. Run (from inside `demo/`):
```bash
python3 stego/decode_stego.py stego/output/flag.png
```
Flag prints. Mention participants would be hinted toward writing/using this
kind of LSB decoder themselves, not handed the script.

**5. Wrap-up talking point**
Walk through one challenge's 3-tier hints in `HINTS.md` out loud - this is
the core pitch: nobody gets stuck asking an organizer, everybody has a path
forward, and nobody gets the answer handed to them either.

## Notes on how this scales to the full event

This is a deliberately trimmed slice. The full plan (already scoped, not yet
built) adds:
- ~4 more recon challenges (ping sweep across decoy hosts, anonymous FTP,
  HTTP header/vhost leak)
- ~7 more web challenges (robots.txt, HTML comments, hidden DOM elements,
  cookie viewing/tampering, IDOR, reflected XSS)
- ~3-4 more stego challenges (EXIF metadata, extension mismatch via `file`,
  binwalk carving, QR code)
- A CTFd bulk-import file (title/category/description/points/flag/hints) so
  none of this has to be manually re-entered into CTFd
- A top-level README with a pre-event testing checklist

Say the word and I'll build the rest out using this same structure.
