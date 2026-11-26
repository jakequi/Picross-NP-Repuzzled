"""Metasprite frames (Picross NP engine).

Pointer table: CA:5830, 4 bytes per frame (long pointer; bank byte = high word low byte).
Null (zero) slots exist. Frame: entries of 4 bytes (x s8, y s8, tile u8, attr u8).
attr: bit0 tile+0x100, bits1-3 palette, bit4 16x16 sprite, bit5 last entry, bits6-7 h/v flip.
Drawn by C0:110E / C0:1134.
"""
import numpy as np
import gfx

TABLE = 0x0A5830


def rom_off(addr24):
    return ((addr24 >> 16) & 0x3F) << 16 | (addr24 & 0xFFFF)


def frame_ptr(d, i):
    p = TABLE + i * 4
    return d[p] | d[p + 1] << 8 | d[p + 2] << 16


def count(d):
    """Number of table slots: run until an entry that is neither null nor a long pointer."""
    n = 0
    while True:
        p = TABLE + n * 4
        if d[p + 3] != 0:
            break
        if not (d[p + 2] >= 0xC0 or (d[p] | d[p + 1] | d[p + 2]) == 0):
            break
        n += 1
    return n


def parse_frame(d, i):
    if frame_ptr(d, i) == 0:
        return []
    p = rom_off(frame_ptr(d, i))
    out = []
    for _ in range(128):
        x, y, t, a = d[p], d[p + 1], d[p + 2], d[p + 3]
        out.append(dict(x=x - 256 if x > 127 else x, y=y - 256 if y > 127 else y,
                        tile=t | (a & 1) << 8, pal=a >> 1 & 7, big=bool(a & 0x10),
                        hf=bool(a & 0x40), vf=bool(a & 0x80), attr=a))
        p += 4
        if a & 0x20:
            break
    return out


def encode_frame(entries):
    out = bytearray()
    for k, e in enumerate(entries):
        a = (e['tile'] >> 8 & 1) | (e['pal'] & 7) << 1 | (0x10 if e['big'] else 0) | \
            (0x40 if e['hf'] else 0) | (0x80 if e['vf'] else 0)
        if k == len(entries) - 1:
            a |= 0x20
        out += bytes([e['x'] & 0xFF, e['y'] & 0xFF, e['tile'] & 0xFF, a])
    return bytes(out)


def render_frame(entries, sheet_tiles, pal_rgb, size=(128, 96), origin=(64, 48)):
    """sheet_tiles(t) -> 8x8 index array; pal_rgb[pal] -> 16x3 colours."""
    img = np.zeros((size[1], size[0], 3), np.uint8); img[:] = (40, 0, 40)
    for e in reversed(entries):
        n = 2 if e['big'] else 1
        for ty in range(n):
            for tx in range(n):
                t = e['tile'] + tx + ty * 16
                tile = sheet_tiles(t)
                if tile is None:
                    continue
                if e['hf']: tile = tile[:, ::-1]
                if e['vf']: tile = tile[::-1, :]
                dx = (n - 1 - tx) if e['hf'] else tx
                dy = (n - 1 - ty) if e['vf'] else ty
                ox = origin[0] + e['x'] + dx * 8; oy = origin[1] + e['y'] + dy * 8
                for yy in range(8):
                    for xx in range(8):
                        px, py = ox + xx, oy + yy
                        if 0 <= px < size[0] and 0 <= py < size[1] and tile[yy, xx]:
                            img[py, px] = pal_rgb[e['pal']][tile[yy, xx]]
    return img
