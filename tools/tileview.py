"""Render ROM bytes as SNES tiles to a PNG for inspection.
usage: tileview.py rom start length bpp out.png [cols] [scale]"""
import sys
from PIL import Image
import numpy as np

def decode_tile(b, bpp):
    px = np.zeros((8, 8), np.uint8)
    for y in range(8):
        for p in range(bpp):
            off = (p // 2) * 16 + y * 2 + (p % 2)
            v = b[off] if off < len(b) else 0
            for x in range(8):
                if v & (0x80 >> x):
                    px[y, x] |= 1 << p
    return px

def render(data, bpp, cols=32, scale=2):
    tsz = 8 * bpp
    n = len(data) // tsz
    rows = (n + cols - 1) // cols
    img = np.zeros((rows * 8, cols * 8), np.uint8)
    for t in range(n):
        tile = decode_tile(data[t * tsz:(t + 1) * tsz], bpp)
        r, c = divmod(t, cols)
        img[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = tile
    maxv = (1 << bpp) - 1
    im = Image.fromarray((img.astype(np.uint16) * 255 // maxv).astype(np.uint8), 'L')
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST)

if __name__ == '__main__':
    rom, start, length, bpp, out = sys.argv[1:6]
    cols = int(sys.argv[6]) if len(sys.argv) > 6 else 32
    scale = int(sys.argv[7]) if len(sys.argv) > 7 else 2
    d = open(rom, 'rb').read()
    s = int(start, 16); l = int(length, 16)
    render(d[s:s + l], int(bpp), cols, scale).save(out)
