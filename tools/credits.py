"""Credit / bonus pages (Picross NP Vol.1): table of u16 offsets at TABLE (relative to TABLE),
each page = records [u16 map offset][u16 tilemap words...][0000], ended by offset 0000.
Copied by C1:53B6 into the WRAM BG3 map buffer (7E:67F0 + offset)."""
import struct

TABLE = 0x048421
NPAGES = 12


def pages(d):
    out = []
    for k in range(NPAGES):
        p = TABLE + struct.unpack_from('<H', d, TABLE + 2 * k)[0]
        recs = []
        while True:
            off = struct.unpack_from('<H', d, p)[0]; p += 2
            if off == 0:
                break
            words = []
            while True:
                w = struct.unpack_from('<H', d, p)[0]; p += 2
                if w == 0:
                    break
                words.append(w)
            recs.append((off, words))
        out.append(recs)
    return out


def encode(pages_):
    blob = bytearray(); offs = []
    for recs in pages_:
        offs.append(len(blob))
        for off, words in recs:
            blob += struct.pack('<H', off) + b''.join(struct.pack('<H', w) for w in words) + b'\0\0'
        blob += b'\0\0'
    return offs, bytes(blob)
