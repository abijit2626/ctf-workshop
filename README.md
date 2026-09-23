# TinkerHub CTF — Security Study Jam

A beginner-friendly capture-the-flag event, built and run for a college
security study jam aimed at students with **no prior security experience**.

It is deliberately *not* competitive — no leaderboard pressure. The design
goal is that participants work challenges out for themselves through a tiered
hint system rather than asking an organiser for the answer. Every challenge
ships with two to three progressive hints: a conceptual nudge, then a pointer
to the right tool or technique, then a near-solution.

## Layout

| Path | What it is |
|---|---|
| [`demo/`](demo) | A 4-challenge working slice, built to pitch the concept to the club |
| [`event/`](event) | The full 18-challenge one-day event |
| `message.txt` | The original design brief the full build was scoped from |

### `demo/` — the pitch

One recon, two web exploitation, and one steganography challenge — built
first, end-to-end and genuinely working, to show the club the concept and the
hint-driven philosophy before committing to building the whole event. Ships
with a live demo script for presenting it.

```bash
cd demo && ./demo.sh up
```

### `event/` — the full event

Three rounds: network recon (4), web exploitation (9), steganography (5).
Participant-facing descriptions, point values, flags and tiered hints live in
`event/ctfd-import/challenges.yml`; organiser solve-steps are in
`event/ANSWERS.md`.

```bash
cd event && ./event.sh up
```

Per-round setup, firewall rules for the lab network, and the pre-event
testing checklist are in [`event/README.md`](event/README.md).

## Design constraints

These shaped almost every technical decision in the repo:

- **Fully offline at runtime.** The event runs on an isolated lab network
  with no internet access, so nothing may depend on a CDN or an external API.
- **One command to stand up.** `./event.sh up` builds, starts, tests, and
  prints the LAN IP and ports to hand to participants — auto-detected from
  the host's network route, not `localhost`.
- **Self-testing.** 38 automated checks validate all 18 flags at startup:
  recon banners and protocols, every web bug, every stego file. If any check
  fails it says so and refuses to print "ready" — nobody wants to find a
  broken challenge with a room full of people waiting.
- **Resettable.** Everything is stateless, so `./event.sh reset` returns to a
  clean state instantly — between practice runs, or after a participant
  breaks a stateful challenge.
- **Scoped vulnerabilities.** The web app is vulnerable only in the ways the
  challenges require: no unintended extra bugs, and no hardening that would
  block an intended solution.

## Delivery

Challenges are served through self-hosted [CTFd](https://docs.ctfd.io/) on
the isolated lab network. `event/ctfd-import/challenges.yml` is a structured
source of truth for entering them (title, category, description, points,
flag, hints and hint costs) rather than a native CTFd export — that format is
version-specific and can fail silently on import, which is a bad thing to
discover on event day.

## Spoiler warning

`ANSWERS.md` and `HINTS.md` in each directory are organiser references and
contain full solutions. If you came here to play rather than to run this,
stop reading now.
