"""Render VRAM dump as tiles using a CGRAM palette. usage: vramview.py vram cgram start len bpp pal out [cols] [scale]"""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, __import__('os').path.dirname(__file__))
from tileview import decode_tile
vram, cgram, start, length, bpp, pal, out = sys.argv[1:8]
cols = int(sys.argv[8]) if len(sys.argv) > 8 else 16
scale = int(sys.argv[9]) if len(sys.argv) > 9 else 3
v = open(vram, 'rb').read(); cg = open(cgram, 'rb').read()
bpp = int(bpp); pal = int(pal); s = int(start, 16); l = int(length, 16)
cols_rgb = []
for k in range(256):
    w = cg[k*2] | cg[k*2+1] << 8
    cols_rgb.append(((w & 31) * 8, ((w >> 5) & 31) * 8, ((w >> 10) & 31) * 8))
tsz = 8 * bpp; n = l // tsz; rows = (n + cols - 1) // cols
img = np.zeros((rows * 8, cols * 8, 3), np.uint8)
for t in range(n):
    tile = decode_tile(v[s + t*tsz:s + (t+1)*tsz], bpp)
    r, c = divmod(t, cols)
    for y in range(8):
        for x in range(8):
            px = tile[y, x]
            img[r*8+y, c*8+x] = cols_rgb[pal * (1 << bpp) + px] if px else (255, 0, 255) if False else cols_rgb[pal * (1 << bpp) + px]
im = Image.fromarray(img)
im.resize((im.width * scale, im.height * scale), Image.NEAREST).save(out)
