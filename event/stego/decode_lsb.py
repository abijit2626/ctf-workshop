"""
LSB decoder for challenge 04 - this is the kind of small tool participants
get hinted toward writing/using themselves.
Usage: python3 decode_lsb.py output/04_lsb.png
"""
from PIL import Image
import sys

TERMINATOR = "@@END@@"


def decode(path):
    img = Image.open(path).convert("RGB")
    pixels = img.load()
    bits = []
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            for c in (r, g, b):
                bits.append(str(c & 1))

    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte = "".join(bits[i:i + 8])
        chars.append(chr(int(byte, 2)))
        text = "".join(chars)
        if TERMINATOR in text:
            return text[: text.index(TERMINATOR)]
    return "".join(chars)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "output/04_lsb.png"
    print(decode(path))
