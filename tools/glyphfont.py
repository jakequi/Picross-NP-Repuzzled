"""8x16 monospace Latin glyphs stored once in a character blob and referenced per map cell.

Used where text is composed from glyph tiles (credits, certificates): each character occupies
one map column, two rows (top tile, bottom tile). Glyphs are allocated lazily from a pool.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import gfx

from config import FONT_DIR


def render_glyph(ch, font='ARIALNB.TTF', size=13, fill=1, shadow=2, outline=None, w=8, h=16, baseline=12, bg=0):
    img = np.full((h, w), bg, np.uint8)
    if ch == ' ':
        return img
    f = ImageFont.truetype(os.path.join(FONT_DIR, font), size)
    im = Image.new('L', (w * 3, h), 0)
    asc, _ = f.getmetrics()
    ImageDraw.Draw(im).text((w, baseline - asc), ch, font=f, fill=255)
    ink = np.asarray(im) > 110
    cols = np.where(ink.any(axis=0))[0]
    if len(cols):
        gw = cols[-1] - cols[0] + 1
        x0 = cols[0] - max(0, (w - 1 - gw) // 2)
        ink = ink[:, x0:x0 + w]
        if ink.shape[1] < w:
            ink = np.pad(ink, ((0, 0), (0, w - ink.shape[1])))
    else:
        ink = ink[:, :w]
    if outline is not None:
        o = np.zeros_like(ink)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                o |= np.roll(np.roll(ink, dy, 0), dx, 1)
        img[o] = outline
    if shadow is not None:
        sh = np.roll(np.roll(ink, 1, 0), 1, 1) & ~ink
        img[sh & (img == bg)] = shadow
    img[ink] = fill
    return img


class GlyphFont:
    """Glyphs in a char blob (BlobCache) of given bpp; tile t at offset (t - base) * 8 * bpp."""
    def __init__(self, cache, chr_src, bpp, pool, style, base=0):
        self.cache, self.chr_src, self.bpp, self.base = cache, chr_src, bpp, base
        self.pool = list(pool)
        self.style = style
        self.glyphs = {}

    def _put(self, t, px):
        o = (t - self.base) * 8 * self.bpp
        data = self.cache.get(self.chr_src)
        assert 0 <= o and o + 8 * self.bpp <= len(data)
        data[o:o + 8 * self.bpp] = gfx.encode_tile(px, self.bpp)

    def glyph(self, ch):
        if ch == ' ':
            return None
        if ch not in self.glyphs:
            img = render_glyph(ch, **self.style)
            if len(self.pool) < 2:
                raise RuntimeError('glyph pool exhausted at %r' % ch)
            top, bot = self.pool.pop(0), self.pool.pop(0)
            self._put(top, img[:8]); self._put(bot, img[8:])
            self.glyphs[ch] = (top, bot)
        return self.glyphs[ch]

    def cells(self, text):
        """List of (top_tile, bottom_tile) or None (space) per character."""
        return [self.glyph(c) for c in text]
