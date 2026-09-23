"""
TinkerHub CTF - Steganography round (5 files).

Regenerates all challenge files deterministically. Organizer-only script -
not shown to participants. Requires (once, at build time on a connected
machine): Pillow, piexif, qrcode. Nothing needed at event runtime - these are
just static files.
"""
import os

from PIL import Image
import piexif
import qrcode

OUT_DIR = os.path.join(os.path.dirname(__file__), "output")

FLAG_STRINGS = "flag{str1ngs_f1nds_1t}"
FLAG_EXIF = "flag{ex1f_d4t4_l34ks}"
FLAG_EXT_MISMATCH = "flag{n0t_4_txt_f1l3}"
FLAG_LSB = "flag{ls8_ls_my_f4v0r1t3}"
FLAG_QR = "flag{qr_c0d3_sc4n_m3}"

LSB_TERMINATOR = "@@END@@"


def ensure_out_dir():
    os.makedirs(OUT_DIR, exist_ok=True)


# --- 1. strings - flag appended as plaintext after PNG's real end ----------

def make_strings_challenge():
    img = Image.new("RGB", (300, 200), color=(40, 90, 140))
    path = os.path.join(OUT_DIR, "01_strings.png")
    img.save(path)
    with open(path, "ab") as f:
        f.write(b"\n[internal-note] " + FLAG_STRINGS.encode() + b"\n")
    print(f"wrote {path}")


# --- 2. EXIF metadata --------------------------------------------------------

def make_exif_challenge():
    img = Image.new("RGB", (300, 200), color=(140, 90, 40))
    path = os.path.join(OUT_DIR, "02_exif.jpg")
    img.save(path, "jpeg")

    exif_dict = {"0th": {}, "Exif": {}, "1st": {}, "thumbnail": None, "GPS": {}}
    exif_dict["0th"][piexif.ImageIFD.Artist] = FLAG_EXIF.encode()
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = (
        b"ASCII\x00\x00\x00" + FLAG_EXIF.encode()
    )
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, path)
    print(f"wrote {path}")


# --- 3. extension mismatch - real PNG saved with a wrong extension ---------

def make_extension_mismatch_challenge():
    img = Image.new("RGB", (300, 200), color=(90, 140, 40))
    path = os.path.join(OUT_DIR, "03_vacation_photo.txt")
    img.save(path, "png")
    with open(path, "ab") as f:
        f.write(b"\n" + FLAG_EXT_MISMATCH.encode() + b"\n")
    print(f"wrote {path}")


# --- 4. LSB steganography ----------------------------------------------------

def _text_to_bits(text):
    return "".join(f"{byte:08b}" for byte in text.encode("utf-8"))


def make_lsb_challenge():
    width, height = 300, 300
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            pixels[x, y] = (
                (x * 255) // width,
                (y * 255) // height,
                ((x + y) * 255) // (width + height),
            )

    bits = _text_to_bits(FLAG_LSB + LSB_TERMINATOR)
    bit_i = 0
    for y in range(height):
        for x in range(width):
            if bit_i >= len(bits):
                break
            r, g, b = pixels[x, y]
            channels = [r, g, b]
            for c in range(3):
                if bit_i < len(bits):
                    channels[c] = (channels[c] & ~1) | int(bits[bit_i])
                    bit_i += 1
            pixels[x, y] = tuple(channels)
        if bit_i >= len(bits):
            break

    path = os.path.join(OUT_DIR, "04_lsb.png")
    img.save(path)
    print(f"wrote {path}")


# --- 5. QR code hidden in a larger image ------------------------------------

def make_qr_challenge():
    qr_img = qrcode.make(FLAG_QR).convert("RGB")
    qr_img = qr_img.resize((150, 150))

    background = Image.new("RGB", (800, 500), color=(230, 230, 235))
    px = background.load()
    for y in range(500):
        for x in range(800):
            px[x, y] = (
                200 + (x % 30),
                200 + (y % 20),
                210 + ((x + y) % 25),
            )

    background.paste(qr_img, (600, 320))
    path = os.path.join(OUT_DIR, "05_team_offsite.png")
    background.save(path)
    print(f"wrote {path}")


if __name__ == "__main__":
    ensure_out_dir()
    make_strings_challenge()
    make_exif_challenge()
    make_extension_mismatch_challenge()
    make_lsb_challenge()
    make_qr_challenge()
    print("All 5 stego files generated.")
