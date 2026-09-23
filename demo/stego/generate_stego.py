"""
TinkerHub CTF - Steganography demo (1 file).

Encodes a flag into the least-significant bit of each pixel's RGB channels
in a generated cover image. Decodable with the paired decode_stego.py.

Only dependency: Pillow (offline after this script runs once).
"""
from PIL import Image
import sys

FLAG = "flag{ls8_hunt3r_1}"
WIDTH, HEIGHT = 300, 300
OUT_PATH = "output/flag.png"

# A terminator so the decoder knows where the payload ends.
TERMINATOR = "@@END@@"


def text_to_bits(text):
    return "".join(f"{byte:08b}" for byte in text.encode("utf-8"))


def make_cover_image():
    img = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = img.load()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            pixels[x, y] = (
                (x * 255) // WIDTH,
                (y * 255) // HEIGHT,
                ((x + y) * 255) // (WIDTH + HEIGHT),
            )
    return img


def encode(img, payload):
    bits = text_to_bits(payload + TERMINATOR)
    pixels = img.load()
    bit_i = 0
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if bit_i >= len(bits):
                return img
            r, g, b = pixels[x, y]
            channels = [r, g, b]
            for c in range(3):
                if bit_i < len(bits):
                    channels[c] = (channels[c] & ~1) | int(bits[bit_i])
                    bit_i += 1
            pixels[x, y] = tuple(channels)
    if bit_i < len(bits):
        raise ValueError("Image too small to hold payload")
    return img


if __name__ == "__main__":
    import os

    os.makedirs("output", exist_ok=True)
    img = make_cover_image()
    img = encode(img, FLAG)
    img.save(OUT_PATH)
    print(f"Wrote {OUT_PATH} with embedded flag (for organizer testing only).")
