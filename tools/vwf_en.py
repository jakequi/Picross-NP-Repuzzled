"""English glyphs for the Picross NP variable-width font.

English text is stored as full-width Shift-JIS (A -> 82 60 ...), so the game's own
lookup (C0:2646) finds the glyph slot; we replace those slots' bitmaps with narrow
anti-aliased Latin glyphs. The engine advances by glyph width + 2.
"""
import os, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import vwf

from config import FONT_DIR
FONT = os.path.join(FONT_DIR, 'arialbd.ttf')
SIZE = 11
HEIGHT = 12
BASELINE = 10        # row of the baseline inside the 12-row cell

# ASCII -> Shift-JIS full-width code
SJIS = {' ': 0x8140, ',': 0x8143, '.': 0x8144, ':': 0x8146, ';': 0x8147, '?': 0x8148, '!': 0x8149,
        "'": 0x8166, '"': 0x8168, '(': 0x8169, ')': 0x816A, '-': 0x817C, '/': 0x815E, '&': 0x8195,
        '*': 0x8196, '#': 0x8194, '%': 0x8193, '+': 0x817B, '=': 0x8181, '~': 0x8160, '$': 0x8190,
        '@': 0x8197, '[': 0x816D, ']': 0x816E, 'x': None}
for k in range(10):
    SJIS[chr(48 + k)] = 0x824F + k
for k in range(26):
    SJIS[chr(65 + k)] = 0x8260 + k
    SJIS[chr(97 + k)] = 0x8281 + k
# accented letters used in names map onto plain glyphs
FOLD = {'é': 'e', 'É': 'E', '’': "'", '“': '"', '”': '"', '…': '...', '–': '-', '—': '-'}


def encode(text):
    """English string -> Shift-JIS full-width bytes the game's VWF engine renders."""
    out = bytearray()
    for ch in text:
        for c in FOLD.get(ch, ch):
            code = SJIS.get(c)
            if code is None:
                raise ValueError('no glyph for %r in %r' % (c, text))
            out += bytes([code >> 8, code & 0xFF])
    return bytes(out)


SJIS_ROWS = 0x2695   # Shift-JIS row table in bank C0 (Vol. 4: 0x2691; set from volume.py)
GLYPH_ADD = 0x9C     # ADC #$009C after the row lookup (C0:268D); Vol. 6+: 0xA0 (4 more glyphs)


def glyph_index(rom, code):
    """Glyph number the game uses for a Shift-JIS code (mirrors C0:2646)."""
    lead, trail = code >> 8, code & 0xFF
    rows = struct.unpack_from('<3H', rom, SJIS_ROWS)
    v = struct.unpack_from('<H', rom, SJIS_ROWS + 6 + rows[lead - 0x81] + (trail - 0x40) * 2)[0]
    return v + GLYPH_ADD


def render_char(ch, font=FONT, size=SIZE, xscale=2):
    """Render one glyph. The text layer is hi-res (512 px wide), so glyphs are drawn
    at `xscale` times horizontal resolution to look normal on screen."""
    if ch == ' ':
        return np.zeros((HEIGHT, 3 * xscale), np.uint8)
    s = 8
    f = ImageFont.truetype(font, size * s)
    asc, _ = f.getmetrics()
    Wn = size * 2
    im = Image.new('L', (Wn * s, HEIGHT * s), 0)
    ImageDraw.Draw(im).text((s * 2, BASELINE * s - asc), ch, font=f, fill=255)
    cov = np.asarray(im.resize((Wn * xscale, HEIGHT), Image.BOX), np.float32) / 255
    out = np.zeros(cov.shape, np.uint8)
    out[cov > 0.18] = 1
    out[cov > 0.42] = 2
    out[cov > 0.66] = 3
    cols = np.where(out.max(axis=0) > 0)[0]
    if len(cols) == 0:
        return np.zeros((HEIGHT, 2), np.uint8)
    return out[:, cols[0]:cols[-1] + 1]


GAP = 2  # engine adds 2 hi-res px after every glyph (C0:2D33)


def text_width(text):
    """Width in hi-res pixels of one line of English as the engine lays it out."""
    return sum(render_char(c).shape[1] + GAP for c in text)


def chars():
    return [c for c in SJIS if SJIS[c] is not None]


def install(rom, alloc):
    """Write English glyph bitmaps to free space and repoint their glyph-table slots.
    rom: bytearray; alloc(n) -> ROM offset of n free bytes (must be > 0x50954)."""
    done = {}
    for ch in chars():
        gi = glyph_index(rom, SJIS[ch])
        if gi in done:
            continue
        g = render_char(ch)
        data = vwf.encode_glyph(g)
        off = alloc(len(data))
        rom[off:off + len(data)] = data
        rel = off - (vwf.TABLE + vwf.BASE_ADD)
        assert rel >= 0
        rom[vwf.TABLE + gi * 3:vwf.TABLE + gi * 3 + 3] = bytes([rel & 0xFF, rel >> 8 & 0xFF, rel >> 16])
        done[gi] = ch
    return done


def preview(text, path, scale=4):
    imgs = []
    for ch in text:
        g = render_char(ch)
        imgs.append(g); imgs.append(np.zeros((HEIGHT, 2), np.uint8))
    img = np.hstack(imgs)
    pal = np.array([20, 110, 180, 255], np.uint8)
    Image.fromarray(pal[img]).resize((img.shape[1] * scale, HEIGHT * scale), Image.NEAREST).save(path)
