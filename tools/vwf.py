"""Picross NP variable-width font (glyph table at C5:0000, 3-byte offsets + 0x954).
Glyph record: width, height, then per row ceil(w/8) byte-columns, each as (plane0, plane1)."""
import numpy as np

TABLE = 0x50000
BASE_ADD = 0x954

def glyph_ptr(d, i):
    v = d[TABLE + i * 3] | d[TABLE + i * 3 + 1] << 8 | d[TABLE + i * 3 + 2] << 16
    return TABLE + v + BASE_ADD

def glyph_count(d):
    return BASE_ADD // 3

def decode_glyph(d, p):
    w, h = d[p], d[p + 1]
    bc = (w + 7) // 8
    img = np.zeros((h, bc * 8), np.uint8)
    q = p + 2
    for y in range(h):
        for c in range(bc):
            p0, p1 = d[q], d[q + 1]; q += 2
            for x in range(8):
                img[y, c * 8 + x] = (p0 >> (7 - x) & 1) | (p1 >> (7 - x) & 1) << 1
    return w, h, img[:, :max(w, 1)], q - p

def encode_glyph(img):
    h, w = img.shape
    bc = (w + 7) // 8
    out = bytearray([w, h])
    pad = np.zeros((h, bc * 8), np.uint8); pad[:, :w] = img
    for y in range(h):
        for c in range(bc):
            p0 = p1 = 0
            for x in range(8):
                v = pad[y, c * 8 + x]
                p0 |= (v & 1) << (7 - x); p1 |= (v >> 1 & 1) << (7 - x)
            out += bytes([p0, p1])
    return bytes(out)
