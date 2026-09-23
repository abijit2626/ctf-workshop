# Answer Key (organizer reference - not for participants)

Full solve steps + flags for all 18 challenges. Replace `<ip>` with the LAN
IP printed by `./event.sh up`. Tiered hints (for participants) live in
`ctfd-import/challenges.yml`, not here.

---

## Round 1: Network Recon

### 1. Diagnostics Port - `flag{n3tw0rk_r3c0n_1s_ez}`
```
nmap -p 2000-9300 -T4 <ip>
nc <ip> 7331
```
Flag is directly in the banner. Ports 2121/9200 are decoys (plausible
banners, no flag).

### 2. Anonymous Drop - `flag{an0n_ftp_no_p4ssw0rd}`
```
nc <ip> 2100
USER anonymous
PASS anything
LIST
RETR flag.txt
```
Simplified text-protocol FTP simulation (not full RFC 959 - a real `ftp`
client's passive-mode data channel needs NAT config that's fragile across
Docker/Podman setups; `nc` gets the same lesson without the fragility).

### 3. The Secret Phrase - `flag{s3nd_th3_r1ght_str1ng}`
```
nc <ip> 4444
```
then type `OPEN SESAME` (exact case) and press enter.

### 4. Wrong Address (stretch) - `flag{h0st_h34d3r_l34k}`
```
curl -H "Host: internal.tinkercorp.lab" http://<ip>:8080/
```
Any other Host header gets a generic "nothing to see here" response.

---

## Round 2: Web Exploitation

All at `http://<ip>:5000`.

### 5. Company Announcements (`/ch1`) - `flag{v13w_s0urc3_ftw}`
View Page Source (Ctrl+U), search for `flag{`. Text is styled
white-on-white so it's invisible when rendered.

### 6. Robots Don't Keep Secrets (`/robots.txt`) - `flag{r0b0ts_txt_g1v3s_1t_away}`
Visit `/robots.txt`, see `Disallow: /internal-9f3a2c`, visit that path
directly.

### 7. About Us (`/ch3`) - `flag{c0mm3nts_ar3nt_s3cr3ts}`
View Page Source, flag is inside an HTML comment (`<!-- -->`).

### 8. System Status (`/ch4`) - `flag{1nsp3ct_th3_dom}`
View Page Source shows nothing - the page fetches `/ch4/api/status` via JS
after load and inserts a `display:none` div with the flag into the live
DOM. Must use DevTools "Elements" tab (or just watch the Network tab for the
fetch response).

### 9. Session Info (`/ch5`) - `flag{c00k13_j4r_s3cr3ts}`
DevTools -> Application/Storage -> Cookies, or `document.cookie` in console.
Cookie name: `debug_flag`.

### 10. Admin Panel (`/ch6`) - `flag{r0l3_fl1p_pr1v_3sc}`
Edit the `role` cookie from `user` to `admin` in DevTools, reload the page.

### 11. My Profile (`/ch7/profile?user_id=104`) - `flag{1d0r_us3r_103_pwn3d}`
Change `user_id=104` to `user_id=103` in the URL. No ownership check
server-side (classic IDOR).

### 12. Staff Login (`/login`) - `flag{sql1_1s_n3v3r_s4f3}`
Username: `admin' OR '1'='1' -- ` (trailing space matters), any password.
Query is built via raw string concatenation.

### 13. Search TinkerCorp Docs (`/ch9/search`) - `flag{xss_st34ls_c00k13s}`
The `q` parameter is reflected unescaped. Payload:
`<script>alert(document.cookie)</script>` in the search box - the flag is
in a cookie (`search_flag`) that nothing on the page displays normally.

---

## Round 3: Steganography

Files downloadable from the web portal homepage, or in `stego/output/`.

### 14. Hidden in Binary (`01_strings.png`) - `flag{str1ngs_f1nds_1t}`
```
strings 01_strings.png | grep flag
```

### 15. Camera Metadata (`02_exif.jpg`) - `flag{ex1f_d4t4_l34ks}`
```
exiftool 02_exif.jpg
```
Look at "Artist" / "User Comment" fields.

### 16. Vacation Photo? (`03_vacation_photo.txt`) - `flag{n0t_4_txt_f1l3}`
```
file 03_vacation_photo.txt      # reveals it's actually a PNG
strings 03_vacation_photo.txt | grep flag
```

### 17. Pixel Whispers (`04_lsb.png`) - `flag{ls8_ls_my_f4v0r1t3}`
```
python3 stego/decode_lsb.py stego/output/04_lsb.png
```
Flag is encoded in the least-significant bit of each pixel's R/G/B values.

### 18. Team Offsite Photo (stretch) (`05_team_offsite.png`) - `flag{qr_c0d3_sc4n_m3}`
A QR code is pasted into the bottom-right area of the image. Crop and scan
it with any phone QR scanner, or decode programmatically:
```
python3 -c "from pyzbar import pyzbar; from PIL import Image; print(pyzbar.decode(Image.open('stego/output/05_team_offsite.png')))"
```

---

## Full verification in one command

`./event.sh test` (or `./event.sh up`, which runs this automatically) checks
all 18 flags end-to-end and refuses to print "ready" if anything's broken.
