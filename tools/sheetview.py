"""Render a decompressed blob as a tile sheet (VRAM-style rows) with a CGRAM palette and grid labels.
usage: sheetview.py rom src_hex bpp cgram pal_index out.png [cols] [scale]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import lz, gfx, screen

def render(data, bpp, pal_rgb, cols=16, scale=3, grid=True):
    tsz = 8 * bpp; n = len(data) // tsz; rows = (n + cols - 1) // cols
    img = np.zeros((rows * 8, cols * 8, 3), np.uint8)
    for t in range(n):
        r, c = divmod(t, cols)
        tile = gfx.decode_tile(data[t * tsz:(t + 1) * tsz], bpp)
        img[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = pal_rgb[tile]
    im = Image.fromarray(img).resize((cols * 8 * scale, rows * 8 * scale), Image.NEAREST)
    if grid:
        d = ImageDraw.Draw(im)
        for r in range(rows):
            d.text((0, r * 8 * scale), '%03x' % (r * cols), fill=(255, 255, 0))
    return im

if __name__ == '__main__':
    rom, src, bpp, cg, pal, out = sys.argv[1:7]
    cols = int(sys.argv[7]) if len(sys.argv) > 7 else 16
    scale = int(sys.argv[8]) if len(sys.argv) > 8 else 3
    d = open(rom, 'rb').read()
    data, _ = lz.decompress(d, int(src, 16))
    bpp = int(bpp)
    full = screen.palette(open(cg, 'rb').read())
    p = int(pal)
    pr = full[p * (1 << bpp):(p + 1) * (1 << bpp)].copy()
    pr[0] = (40, 0, 40)
    render(data, bpp, pr, cols, scale).save(out)
