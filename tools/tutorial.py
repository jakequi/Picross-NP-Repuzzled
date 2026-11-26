"""Tutorial ("how to play") script for Picross NP Vol. 1.

Base C1:1682 (ROM 0x11682): u16 section offsets (6), then bytecode interpreted at C1:0A37.
The dispatcher consumes the command byte; argument sizes below were read from each handler.
Text commands 01 (typed) and 02 (instant) take Shift-JIS until 00; byte 01 inside text = newline.
"""
import struct

BASE = 0x011682
NSECT = 6
FIXED = {0x00: 0, 0x03: 0, 0x04: 0, 0x05: 0, 0x06: 0, 0x08: 8, 0x09: 2, 0x0A: 1, 0x0B: 1,
         0x0E: 0, 0x0F: 0, 0x10: 0, 0x11: 0, 0x12: 0, 0x13: 1, 0x14: 0, 0x15: 0, 0x16: 0,
         0x17: 0, 0x18: 0, 0x19: 0, 0x1A: 0, 0x1B: 0, 0x1C: 0, 0x1D: 2, 0x1F: 1, 0x20: 3,
         0x21: 1, 0x22: 1, 0x23: 0, 0x24: 0, 0x25: 0, 0x26: 0}


def section_offsets(d):
    return list(struct.unpack_from('<%dH' % NSECT, d, BASE))


def read_text(d, p):
    start = p
    while True:
        b = d[p]
        if b == 0:
            return bytes(d[start:p]), p + 1
        if b == 1:
            p += 1
        else:
            p += 2


def parse_section(d, off):
    """Return list of (cmd, payload) until command 00 (end of section)."""
    p = BASE + off
    ops = []
    while True:
        c = d[p]; p += 1
        if c in (0x01, 0x02):
            txt, p = read_text(d, p)
            ops.append((c, txt))
        elif c == 0x07:
            n = 2 if struct.unpack_from('<H', d, p)[0] == 0 else 4
            ops.append((c, bytes(d[p:p + n]))); p += n
        elif c in (0x0C, 0x0D):
            q = p
            while struct.unpack_from('<H', d, q)[0] != 0xFFFF:
                q += 2
            q += 2
            ops.append((c, bytes(d[p:q]))); p = q
        elif c == 0x1E:
            q = p
            while d[q] != 0:
                q += 4
            q += 1
            ops.append((c, bytes(d[p:q]))); p = q
        elif c in FIXED:
            n = FIXED[c]
            ops.append((c, bytes(d[p:p + n]))); p += n
        else:
            raise ValueError('unknown tutorial command %02x at %06x' % (c, p - 1))
        if c == 0x00:
            return ops, p


def serialize(ops):
    out = bytearray()
    for c, payload in ops:
        out.append(c)
        out += payload
        if c in (0x01, 0x02):
            out.append(0)
    return bytes(out)


def text_to_display(raw):
    s = ''; p = 0
    while p < len(raw):
        if raw[p] == 1:
            s += '\\n'; p += 1
        else:
            try:
                s += raw[p:p + 2].decode('cp932')
            except UnicodeDecodeError:
                s += '{%s}' % raw[p:p + 2].hex()
            p += 2
    return s
