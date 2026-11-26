"""Render a tilemap blob + char blob with a palette from a dump, with a tile grid.
usage: layerview.py map_src chr_src bpp dump_prefix out.png [pal_override]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import labels, screen, gfx

class _Rom:
    def __init__(self, d): self.orig = d

def render(rom_bytes, map_src, chr_src, bpp, cgram, scale=3):
    c = labels.BlobCache(_Rom(rom_bytes))
    L = labels.TileLayer(c, map_src, chr_src, bpp)
    pal = screen.palette(cgram)
    img = np.zeros((224, 256, 3), np.uint8); img[:] = (30, 30, 60)
    for ty in range(28):
        for tx in range(32):
            e = L.entry(tx, ty); t = e & 0x3FF; p = e >> 10 & 7
            try:
                tile = L.get_tile(t)
            except AssertionError:
                continue
            if e & 0x4000: tile = tile[:, ::-1]
            if e & 0x8000: tile = tile[::-1, :]
            for y in range(8):
                for x in range(8):
                    if tile[y, x]:
                        img[ty * 8 + y, tx * 8 + x] = pal[p * (1 << bpp) + tile[y, x]]
    im = Image.fromarray(img).resize((256 * scale, 224 * scale), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for k in range(32): d.text((k * 8 * scale + 2, 0), str(k % 10), fill=(255, 255, 0))
    for k in range(28): d.text((0, k * 8 * scale + 6), str(k), fill=(0, 255, 255))
    return im

if __name__ == '__main__':
    rom = open(sys.argv[1], 'rb').read()
    im = render(rom, int(sys.argv[2], 16), int(sys.argv[3], 16), int(sys.argv[4]), open(sys.argv[5] + '.cgram', 'rb').read())
    im.save(sys.argv[6])
