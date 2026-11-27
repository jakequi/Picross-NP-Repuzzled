"""Puzzle database for Picross NP (Vol. 1 layout; addresses are per-game config).

Pointer table at DB (ROM 0xB0000): N x 3-byte offsets relative to CB:0000.
Record: [size type][count] [solution bitmap (a bytes)] [block (b-a)] [count*c bytes] [name SJIS..] 00 00 [trailer]
Size table (w, h, ...) at ROM 0xA698C (8 bytes each); block size table (a, b, c words) at ROM 0x6F2A.
"""
import struct
import numpy as np

DB = 0x0B0000
SIZE_TBL = 0x0A698C
BLOCK_TBL = 0x006F2A


def count(d):
    return struct.unpack_from('<H', d, DB)[0] // 3


def record_offsets(d):
    n = count(d)
    return [DB + (d[DB + k * 3] | d[DB + k * 3 + 1] << 8 | d[DB + k * 3 + 2] << 16) for k in range(n)]


def parse(d, off):
    t, cnt = d[off], d[off + 1]
    w, h = d[SIZE_TBL + t * 8], d[SIZE_TBL + t * 8 + 1]
    a, b, c = struct.unpack_from('<3H', d, BLOCK_TBL + t * 8)
    bmp = off + 2
    name = bmp + b + c * cnt
    p = name
    while d[p] | d[p + 1] << 8:
        p += 2 if d[p] >= 0x81 else 1    # Shift-JIS pairs; Vol. 6+ names also use single bytes (0x2F '/')
    bits = np.unpackbits(np.frombuffer(d[bmp:bmp + a], np.uint8))[:w * h].reshape(h, w)
    return dict(off=off, type=t, w=w, h=h, count=cnt, name_off=name, name_end=p,
                name_raw=bytes(d[name:p]), solution=bits)


def sjis_text(raw):
    try:
        return raw.decode('cp932')
    except UnicodeDecodeError:
        return raw.hex()


def all_puzzles(d):
    return [dict(parse(d, o), index=k) for k, o in enumerate(record_offsets(d))]
