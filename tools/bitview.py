"""Render ROM bytes as 1bpp: each byte = one 8px row; strips of H rows laid side by side.
usage: bitview.py rom start length H out.png [scale] [bytes_per_row]"""
import sys
from PIL import Image
import numpy as np
rom, start, length, H, out = sys.argv[1:6]
scale = int(sys.argv[6]) if len(sys.argv) > 6 else 2
bpr = int(sys.argv[7]) if len(sys.argv) > 7 else 1
d = open(rom, 'rb').read()
s, l, H = int(start, 16), int(length, 16), int(H)
data = d[s:s + l]
rows = len(data) // bpr
strips = (rows + H - 1) // H
img = np.zeros((H, strips * (8 * bpr + 2)), np.uint8)
for r in range(rows):
    st, y = divmod(r, H)
    for b in range(bpr):
        v = data[r * bpr + b]
        for x in range(8):
            if v & (0x80 >> x):
                img[y, st * (8 * bpr + 2) + b * 8 + x] = 255
    img[:, st * (8 * bpr + 2) + 8 * bpr:st * (8 * bpr + 2) + 8 * bpr + 2] = 80
im = Image.fromarray(img)
im.resize((im.width * scale, im.height * scale), Image.NEAREST).save(out)
