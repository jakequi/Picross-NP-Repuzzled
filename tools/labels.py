"""Rewrite graphic text labels that live in LZ-compressed tile + tilemap blobs.

A label is a rectangle of a BG tilemap (32x32 words, in a compressed map blob) whose tiles
come from a compressed character blob. English is rendered into the rectangle with an
outlined pixel style; tiles are reused from the label itself first, then from a pool of
verified-free tiles; the tilemap is rewritten to point at them.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import gfx, lz

from config import FONT_DIR


class BlobCache:
    """Decompressed blobs being edited; committed (recompressed + repointed) once at the end."""
    def __init__(self, rom):
        self.rom = rom
        self.data = {}
        self.lengths = {}

    def get(self, src, length=None):
        if src not in self.data:
            out, _ = lz.decompress(self.rom.orig, src, length)
            self.data[src] = bytearray(out)
            self.lengths[src] = length
        return self.data[src]

    def commit(self):
        for src, data in sorted(self.data.items()):
            orig, _ = lz.decompress(self.rom.orig, src, self.lengths[src])
            if bytes(data) != orig:
                self.rom.replace_blob(src, bytes(data), header=self.lengths[src] is None)


def render_outlined(text, w, h, fill=1, outline=3, shadow=None, font='arialbd.ttf', size=11,
                    min_size=7, align='center', y_off=None, thicken=False):
    """Crisp (non anti-aliased) text with a 1px 8-connected outline, auto-shrunk to fit."""
    pad = 1 if outline is not None else 0
    lines = text.split('\n')
    while True:
        f = ImageFont.truetype(os.path.join(FONT_DIR, font), size)
        widths = [f.getbbox(l)[2] - f.getbbox(l)[0] if l else 0 for l in lines]
        asc, desc = f.getmetrics()
        lh = size + 1
        if max(widths) + 2 * pad + (1 if thicken else 0) <= w and lh * len(lines) + 2 * pad <= h + 2 or size <= min_size:
            break
        size -= 1
    im = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(im)
    total = lh * len(lines)
    y = (h - total) // 2 if y_off is None else y_off
    for l, wd in zip(lines, widths):
        bb = f.getbbox(l)
        if align == 'center':
            x = (w - wd) // 2 - bb[0]
        elif align == 'left':
            x = pad - bb[0]
        else:
            x = w - wd - pad - bb[0]
        top = f.getbbox('Ag')[1]
        d.text((x, y - top + pad), l, font=f, fill=255)
        y += lh
    ink = np.asarray(im) > 110
    if thicken:
        ink = ink | np.roll(ink, 1, axis=1)
    out = np.zeros((h, w), np.uint8)
    if outline is not None:
        o = np.zeros_like(ink)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                o |= np.roll(np.roll(ink, dy, 0), dx, 1)
        out[o] = outline
    if shadow is not None:
        sh = np.roll(np.roll(ink, 1, 0), 1, 1) & ~ink
        out[sh & (out == 0)] = shadow
    out[ink] = fill
    return out, size


class TileLayer:
    """One BG layer: tilemap blob + char blob, with tile index -> blob offset mapping."""
    def __init__(self, cache, map_src, chr_src, bpp=4, tile_base=0, map_off=0):
        self.cache, self.map_src, self.chr_src = cache, map_src, chr_src
        self.bpp, self.tile_base, self.map_off = bpp, tile_base, map_off
        self.tsz = 8 * bpp

    @property
    def map(self):
        return self.cache.get(self.map_src)

    @property
    def chr(self):
        return self.cache.get(self.chr_src)

    def entry(self, tx, ty):
        a = self.map_off + (ty * 32 + tx) * 2
        return self.map[a] | self.map[a + 1] << 8

    def set_entry(self, tx, ty, e):
        a = self.map_off + (ty * 32 + tx) * 2
        self.map[a] = e & 0xFF; self.map[a + 1] = e >> 8

    def tile_off(self, t):
        off = (t - self.tile_base) * self.tsz
        assert 0 <= off < len(self.chr), 'tile %x outside char blob' % t
        return off

    def get_tile(self, t):
        o = self.tile_off(t)
        return gfx.decode_tile(self.chr[o:o + self.tsz], self.bpp)

    def put_tile(self, t, px):
        o = self.tile_off(t)
        self.chr[o:o + self.tsz] = gfx.encode_tile(px, self.bpp)

    def usage(self):
        u = {}
        for ty in range(32):
            for tx in range(32):
                t = self.entry(tx, ty) & 0x3FF
                u.setdefault(t, []).append((tx, ty))
        return u

    def read_rect(self, tx, ty, w, h):
        img = np.zeros((h * 8, w * 8), np.uint8)
        for y in range(h):
            for x in range(w):
                e = self.entry(tx + x, ty + y); t = e & 0x3FF
                try:
                    tile = self.get_tile(t)
                except AssertionError:
                    continue
                if e & 0x4000: tile = tile[:, ::-1]
                if e & 0x8000: tile = tile[::-1, :]
                img[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = tile
        return img


def write_label(layer, rect, img, pool, attr=None, blank=0, other_maps=(), bg=None):
    """Write pixel image `img` (h*8 x w*8 palette indices) into tile rect.
    Tiles are taken from the rect's own exclusively-used tiles, then from `pool`.
    Returns list of tiles left unused (can return to pool)."""
    tx0, ty0, w, h = rect
    usage = layer.usage()
    own = []
    first_attr = None
    for y in range(h):
        for x in range(w):
            e = layer.entry(tx0 + x, ty0 + y); t = e & 0x3FF
            if t != blank and first_attr is None:
                first_attr = e & 0xFC00
            inside = all(tx0 <= px < tx0 + w and ty0 <= py < ty0 + h for px, py in usage.get(t, []))
            shared = any(t in m for m in other_maps)
            if t != blank and inside and not shared and t not in own and t not in pool:
                own.append(t)
    if attr is None:
        attr = first_attr if first_attr is not None else 0
    attr &= ~0xC000  # no flips for new text
    avail = own + [t for t in pool if t not in own]
    used = []
    for y in range(h):
        for x in range(w):
            cell = img[y * 8:y * 8 + 8, x * 8:x * 8 + 8]
            if not cell.any():
                layer.set_entry(tx0 + x, ty0 + y, (attr & 0xFC00) | blank)
                continue
            if not avail:
                raise RuntimeError('out of tiles for label at %r' % (rect,))
            t = avail.pop(0); used.append(t)
            if bg is not None:
                cell = cell.copy(); cell[cell == 0] = bg
            layer.put_tile(t, cell)
            layer.set_entry(tx0 + x, ty0 + y, attr | t)
    for t in avail:
        if t in own:
            layer.put_tile(t, np.zeros((8, 8), np.uint8))
    return [t for t in avail]


def free_tiles(layer, other_maps=()):
    """Blank, unreferenced tiles in the char blob (candidates for new label tiles)."""
    used = set(layer.usage().keys())
    for m in other_maps:
        used |= set(m)
    n = len(layer.chr) // layer.tsz
    out = []
    for k in range(n):
        t = layer.tile_base + k
        if t in used:
            continue
        o = k * layer.tsz
        if not any(layer.chr[o:o + layer.tsz]):
            out.append(t)
    return out
