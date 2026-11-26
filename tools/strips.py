"""Render a 2bpp blob as a stack of W x H tile strips (row-major tiles per strip)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import lz, tileview

def strips_to_image(data, w, h, bpp=2, gap=2):
    tsz = 8 * bpp; per = w * h * tsz
    n = len(data) // per
    img = np.full((n * (h * 8 + gap), w * 8), 1, np.uint8)
    for s in range(n):
        for t in range(w * h):
            tile = tileview.decode_tile(data[s * per + t * tsz:s * per + (t + 1) * tsz], bpp)
            r, c = divmod(t, w)
            img[s * (h * 8 + gap) + r * 8:s * (h * 8 + gap) + r * 8 + 8, c * 8:c * 8 + 8] = tile
    return img

if __name__ == '__main__':
    rom, src, w, h, out = sys.argv[1:6]
    d = open(rom, 'rb').read()
    data, _ = lz.decompress(d, int(src, 16))
    img = strips_to_image(data, int(w), int(h))
    pal = np.array([0, 255, 128, 200], np.uint8)
    im = Image.fromarray(pal[img])
    im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(out)
