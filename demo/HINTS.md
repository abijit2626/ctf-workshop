# Hints (organizer reference)

Three tiers per challenge: a conceptual nudge, a tool/technique pointer, then a
near-solution. Point costs are suggestions - tune to your CTFd scoring.

---

## Round 1 - Network Recon: "The Diagnostics Port"
**Prompt:** TinkerCorp accidentally left some internal services reachable.
Find them and see what they're leaking. Target: `<recon-host-ip>`

- Flag: `flag{n3tw0rk_r3c0n_1s_ez}`
- Hint 1 (5 pts): "Computers talk to each other over numbered doors called
  ports. Most services only listen on a handful of them. You need a way to
  ask 'which doors are open?' before you can knock."
- Hint 2 (10 pts): "The standard tool for this is `nmap`. Try scanning a
  range of ports on the target, e.g. `nmap -p 2000-9300 <ip>`."
- Hint 3 (15 pts): "Once you find the open ports, connect to each one
  directly with `nc <ip> <port>` and read what comes back. One of them isn't
  a decoy."

---

## Round 2a - Web: "Company Announcements" (view-source)
**Prompt:** The announcements page looks empty, but is it really?

- Flag: `flag{v13w_s0urc3_ftw}`
- Hint 1 (5 pts): "What you see rendered in the browser isn't always
  everything that got sent to you."
- Hint 2 (10 pts): "Right-click the page and look for a 'View Page Source'
  option (or press Ctrl+U)."
- Hint 3 (15 pts): "Search (Ctrl+F) the source for `flag{` - some text on
  this page is styled to be invisible, not actually removed."

---

## Round 2b - Web: "Staff Login" (SQL injection)
**Prompt:** Log in as `admin` without knowing the password.

- Flag: `flag{sql1_1s_n3v3r_s4f3}`
- Hint 1 (5 pts): "This login form builds a database query directly out of
  what you type. What if your input changed the *meaning* of the query,
  not just the value?"
- Hint 2 (10 pts): "Look up 'SQL injection' and the classic trick of using a
  quote character (`'`) to break out of a string, then adding your own
  always-true condition."
- Hint 3 (15 pts): "Try username: `admin' OR '1'='1' -- ` and any password."

---

## Round 3 - Steganography: "Hidden in Plain Sight" (LSB)
**Prompt:** `flag.png` looks like an ordinary gradient image. Is it?

- Flag: `flag{ls8_hunt3r_1}`
- Hint 1 (5 pts): "Some steganography techniques hide data in parts of a file
  that don't change how it *looks* - like the very last bit of each color
  value in every pixel."
- Hint 2 (10 pts): "This is called 'LSB steganography' (Least Significant
  Bit). Search for how the lowest bit of each pixel's red/green/blue value
  can encode hidden text."
- Hint 3 (15 pts): "Write (or use) a script that reads each pixel's R, G, B
  values, takes the last bit of each, and reassembles those bits 8 at a time
  into ASCII characters."
