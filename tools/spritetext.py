"""Sprite (OBJ) text tools: repaint tile strips in a sprite sheet blob, draw badges,
and rewrite metasprite frames to use freshly drawn English text tiles."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import gfx, metasprite as ms, tinyfont

from config import FONT_DIR


class Sheet:
    """4bpp sprite sheet held in a BlobCache; tile t lives at offset (t - base) * 32."""
    def __init__(self, cache, src, base=0, free=()):
        self.cache, self.src, self.base = cache, src, base
        self.free = list(free)
        self.strips = {}

    @property
    def data(self):
        return self.cache.get(self.src)

    def get(self, t):
        o = (t - self.base) * 32
        return gfx.decode_tile(self.data[o:o + 32], 4)

    def put(self, t, px):
        o = (t - self.base) * 32
        assert 0 <= o < len(self.data)
        self.data[o:o + 32] = gfx.encode_tile(px, 4)

    def read_strip(self, t0, n, rows=1):
        img = np.zeros((8 * rows, 8 * n), np.uint8)
        for r in range(rows):
            for k in range(n):
                img[r * 8:r * 8 + 8, k * 8:k * 8 + 8] = self.get(t0 + r * 16 + k)
        return img

    def write_strip(self, t0, img, rows=1):
        n = img.shape[1] // 8
        for r in range(rows):
            for k in range(n):
                self.put(t0 + r * 16 + k, img[r * 8:r * 8 + 8, k * 8:k * 8 + 8])

    def check_free(self):
        for t in self.free:
            assert not self.get(t).any(), 'tile %x not blank' % t

    def alloc_strip(self, img, key=None):
        """Store an 8-row image as consecutive new tiles; returns list of tile numbers."""
        if key is not None and key in self.strips:
            return self.strips[key]
        n = img.shape[1] // 8
        tiles = []
        for k in range(n):
            if not self.free:
                raise RuntimeError('sprite sheet %06x out of free tiles' % self.src)
            t = self.free.pop(0)
            self.put(t, img[:, k * 8:k * 8 + 8])
            tiles.append(t)
        if key is not None:
            self.strips[key] = tiles
        return tiles


def text_strip(text, fill=0xF, outline=0xE, bg=0xD, min_w=0, pad=1):
    """8px tall tiny-font strip, width rounded up to whole tiles."""
    w = max(tinyfont.width(text) + 2 * pad, min_w)
    w = (w + 7) // 8 * 8
    return tinyfont.render(text, w, 8, fill=fill, outline=outline, bg=bg)


def repaint_row(sheet, t0, n, x0, x1, text, fill=0xF, outline=0xE, bg=0xD, align='left', x_text=None):
    """Repaint pixel columns [x0, x1) of an 8px tile row with tiny-font text."""
    img = sheet.read_strip(t0, n)
    area = tinyfont.render(text, x1 - x0, 8, fill=fill, outline=outline, bg=bg, align=align,
                           x_off=x_text)
    img[:, x0:x1] = area
    sheet.write_strip(t0, img)


def badge(text, w=None, h=16, text_col=7, aa_col=8, fill=0xD, border=0xF, **_):
    """Rounded badge (border + fill) with text in the pixel font used by all small text.
    w=None sizes the badge to the text (rounded up to whole tiles)."""
    ink = tinyfont.text_bitmap(text)
    tw = ink.shape[1]
    bw = tw + 8
    if w is None:
        w = (bw + 7) // 8 * 8
    if bw > w:
        raise ValueError('badge text %r too wide (%d > %d)' % (text, bw, w))
    x0 = (w - bw) // 2
    img = np.zeros((h, w), np.uint8)
    top, bot = 0, 12                       # rounded rectangle rows 0..12, like the original badges
    for y in range(top, bot + 1):
        inset = 2 if y in (top, bot) else (1 if y in (top + 1, bot - 1) else 0)
        img[y, x0 + inset:x0 + bw - inset] = border
        if top < y < bot:
            img[y, x0 + inset + 1:x0 + bw - inset - 1] = fill
    tx = x0 + (bw - tw) // 2
    img[4:9, tx:tx + tw][ink] = text_col
    return img


def frame_cells(entries):
    """Yield (entry_index, sub_tile, frame_x, frame_y, hf, vf) for every 8x8 cell of a frame."""
    for i, e in enumerate(entries):
        n = 2 if e['big'] else 1
        for ty in range(n):
            for tx in range(n):
                t = e['tile'] + tx + ty * 16
                dx = (n - 1 - tx) if e['hf'] else tx
                dy = (n - 1 - ty) if e['vf'] else ty
                yield i, t, e['x'] + dx * 8, e['y'] + dy * 8, e['hf'], e['vf']


DEDUPE_PAINTED = False   # set by the build for volumes that opt in (Vol. 6+)


def paint_frames(rom, sheet, frames, painter, alloc, all_frames_tiles, group=None):
    """Paint onto the rendered image of `frames` (which must share identical layout).
    painter(canvas, ox, oy) edits the index canvas in place (frame coords + (ox, oy)).
    Tiles changed are written in place when only these frames use them, else copied to new tiles.
    all_frames_tiles: dict tile -> set(frames using it), for sharing checks."""
    base = ms.parse_frame(rom.orig, frames[0])
    cells = list(frame_cells(base))
    xs = [c[2] for c in cells]; ys = [c[3] for c in cells]
    ox, oy = -min(xs) + 8, -min(ys) + 8
    W, H = max(xs) + ox + 16, max(ys) + oy + 16
    canvas = np.zeros((H, W), np.uint8)
    for i, t, x, y, hf, vf in reversed(cells):
        tile = sheet.get(t)
        if hf: tile = tile[:, ::-1]
        if vf: tile = tile[::-1, :]
        m = tile != 0
        canvas[y + oy:y + oy + 8, x + ox:x + ox + 8][m] = tile[m]
    before = canvas.copy()
    painter(canvas, ox, oy)
    # write back: topmost entry (lowest index) owns each cell
    remap = {}
    new_entries = [dict(e) for e in base]
    for i, t, x, y, hf, vf in cells:
        new = canvas[y + oy:y + oy + 8, x + ox:x + ox + 8].copy()
        old = before[y + oy:y + oy + 8, x + ox:x + ox + 8]
        if (new == old).all():
            continue
        if hf: new = new[:, ::-1]
        if vf: new = new[::-1, :]
        users = all_frames_tiles.get(t, set())
        if users <= set(group or frames):
            sheet.put(t, new)
        else:
            remap[(i, t)] = new
    if remap:
        # split affected big entries into 8x8 entries and point changed cells at new tiles
        out = []
        for i, e in enumerate(new_entries):
            subs = [c for c in cells if c[0] == i]
            if any((i, c[1]) in remap for c in subs):
                for _, t, x, y, hf, vf in subs:
                    nt = t
                    if (i, t) in remap:
                        img = remap[(i, t)]
                        key = ('painted', img.tobytes()) if DEDUPE_PAINTED else None   # identical tiles shared
                        nt = sheet.alloc_strip(img, key=key)[0]
                    out.append(dict(e, x=x, y=y, tile=nt, big=False))
            else:
                out.append(e)
        data = ms.encode_frame(out)
        for f in frames:
            off = alloc(len(data)); rom.write(off, data)
            p = ms.TABLE + f * 4; a = 0xC00000 | off
            rom.d[p] = a & 0xFF; rom.d[p + 1] = a >> 8 & 0xFF; rom.d[p + 2] = a >> 16
    return canvas


def relabel_frames(rom, sheet, labels, make_image, alloc):
    """Replace whole label frames with new images.
    labels: {frame: text}. Each frame's own tiles are repainted first (in place), extra cells take
    sheet.free tiles. New frame = 8x8 entries centred on the old bounding box."""
    claimed = set()
    for f, text in sorted(labels.items()):
        old = ms.parse_frame(rom.orig, f)
        cells = sorted(frame_cells(old), key=lambda c: (c[3], c[2]))
        own = [c[1] for c in cells if c[1] not in claimed]
        own = list(dict.fromkeys(own))
        xs = [c[2] for c in cells]; ys = [c[3] for c in cells]
        cx = (min(xs) + max(xs) + 8) // 2
        img = make_image(text)
        h, w = img.shape
        ents = []
        for r in range(h // 8):
            for k in range(w // 8):
                cell = img[r * 8:r * 8 + 8, k * 8:k * 8 + 8]
                if not cell.any():
                    continue
                if own:
                    t = own.pop(0); sheet.put(t, cell)
                else:
                    t = sheet.alloc_strip(cell)[0]
                claimed.add(t)
                ents.append(dict(x=cx - w // 2 + k * 8, y=min(ys) + r * 8, tile=t, pal=old[0]['pal'],
                                 big=False, hf=False, vf=False))
        for t in own:          # leftover old tiles of this label: blank them
            sheet.put(t, np.zeros((8, 8), np.uint8)); claimed.add(t)
        data = ms.encode_frame(ents)
        off = alloc(len(data)); rom.write(off, data)
        p = ms.TABLE + f * 4; a = 0xC00000 | off
        rom.d[p] = a & 0xFF; rom.d[p + 1] = a >> 8 & 0xFF; rom.d[p + 2] = a >> 16


def tile_users(d, nframes):
    users = {}
    for f in range(nframes):
        for i, t, *_ in frame_cells(ms.parse_frame(d, f)):
            users.setdefault(t, set()).add(f)
    return users


def rewrite_frame(rom, frame, sheet, remove, lines, alloc, keep=None):
    """Replace a metasprite frame's text.
    remove(entry) -> True for entries to drop; lines: list of dict(y, text, pal, x (left) or cx (centre),
    plus optional strip style). New frame data goes to alloc(n) (ROM offset); pointer is updated."""
    ents = ms.parse_frame(rom.orig, frame)
    kept = [e for e in ents if not remove(e)]
    new = []
    for ln in lines:
        img = text_strip(ln['text'], **ln.get('style', {}))
        tiles = sheet.alloc_strip(img, key=(ln['text'], img.shape[1], tuple(sorted(ln.get('style', {}).items()))))
        w = img.shape[1]
        x = ln['x'] if 'x' in ln else ln['cx'] - w // 2
        for k, t in enumerate(tiles):
            new.append(dict(x=x + k * 8, y=ln['y'], tile=t, pal=ln['pal'], big=False, hf=False, vf=False))
    data = ms.encode_frame(new + kept)
    off = alloc(len(data))
    rom.write(off, data)
    p = ms.TABLE + frame * 4
    a = 0xC00000 | off
    rom.d[p] = a & 0xFF; rom.d[p + 1] = a >> 8 & 0xFF; rom.d[p + 2] = a >> 16
    return off
