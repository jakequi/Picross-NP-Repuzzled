"""Tile encode/decode and English text rendering for Picross NP graphics."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config import FONT_DIR


def decode_tile(b, bpp):
    px = np.zeros((8, 8), np.uint8)
    for y in range(8):
        for p in range(bpp):
            off = (p // 2) * 16 + y * 2 + (p % 2)
            v = b[off]
            for x in range(8):
                if v & (0x80 >> x):
                    px[y, x] |= 1 << p
    return px


def encode_tile(px, bpp):
    out = bytearray(8 * bpp)
    for y in range(8):
        for p in range(bpp):
            v = 0
            for x in range(8):
                if px[y, x] >> p & 1:
                    v |= 0x80 >> x
            out[(p // 2) * 16 + y * 2 + (p % 2)] = v
    return bytes(out)


def tiles_to_image(data, w, h, bpp):
    """Decode w*h tiles (row-major) to a pixel-index array."""
    tsz = 8 * bpp
    img = np.zeros((h * 8, w * 8), np.uint8)
    for t in range(w * h):
        r, c = divmod(t, w)
        img[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = decode_tile(data[t * tsz:(t + 1) * tsz], bpp)
    return img


def image_to_tiles(img, bpp):
    h, w = img.shape
    out = bytearray()
    for r in range(h // 8):
        for c in range(w // 8):
            out += encode_tile(img[r * 8:r * 8 + 8, c * 8:c * 8 + 8], bpp)
    return bytes(out)


def _font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def render_text(text, width, height, font='tahomabd.ttf', size=11, levels=(0, 1, 2, 3),
                align='center', y_off=None, min_size=8, spacing=0):
    """Render text anti-aliased and quantise coverage to 4 colour indices.
    levels maps coverage buckets (none, low, mid, full) to palette indices.
    Shrinks the font until the text fits; returns (index array, size used)."""
    lines = text.split('\n')
    while True:
        f = _font(font, size)
        widths = [f.getlength(l) + spacing * max(len(l) - 1, 0) for l in lines]
        if max(widths) <= width - 2 or size <= min_size:
            break
        size -= 1
    scale = 4
    big = Image.new('L', (width * scale, height * scale), 0)
    d = ImageDraw.Draw(big)
    fb = _font(font, size * scale)
    asc, desc = fb.getmetrics()
    line_h = (asc + desc)
    total_h = line_h * len(lines)
    y = (height * scale - total_h) // 2 if y_off is None else y_off * scale
    for l, wpx in zip(lines, widths):
        if align == 'center':
            x = (width - wpx) / 2 * scale
        elif align == 'left':
            x = scale
        else:
            x = (width - wpx - 1) * scale
        if spacing:
            for ch in l:
                d.text((x, y), ch, font=fb, fill=255)
                x += fb.getlength(ch) + spacing * scale
        else:
            d.text((x, y), l, font=fb, fill=255)
        y += line_h
    cov = np.asarray(big.resize((width, height), Image.BOX), np.float32) / 255.0
    out = np.zeros((height, width), np.uint8)
    out[cov > 0.18] = levels[1]
    out[cov > 0.42] = levels[2]
    out[cov > 0.66] = levels[3]
    return out, size


def preview(img, path, pal=((0, 0, 0), (80, 80, 80), (170, 170, 170), (255, 255, 255)), scale=3):
    pal = np.array(list(pal) + [(255, 0, 255)] * (256 - len(pal)), np.uint8)
    im = Image.fromarray(pal[img])
    im.resize((im.width * scale, im.height * scale), Image.NEAREST).save(path)
