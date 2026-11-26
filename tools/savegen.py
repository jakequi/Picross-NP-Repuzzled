"""Generate a Picross NP Vol.1 save (SRAM, 2KB) with puzzles marked cleared, for testing.
Slot layout (slot 1 at 0x000, slot 2 at 0x3A0): 'NPPicross1', 0x0A=0xFF (in use),
best times at +0x29D + 2*puzzle (u16 BE seconds?, 0xFFFF = not cleared), checksum u16 LE at +0x39D =
sum of LE words over +0x0B..+0x39C."""
import struct, sys

def checksum(slot):
    return sum(struct.unpack('<%dH' % ((0x39D - 0x0B) // 2), bytes(slot[0x0B:0x39D]))) & 0xFFFF

def make(template, cleared=range(1, 122), time=0x0105, slot=0):
    d = bytearray(template)
    base = slot * 0x3A0
    s = d[base:base + 0x3A0]
    s[0x0A] = 0xFF
    for k in cleared:
        s[0x29D + 2 * k] = time >> 8; s[0x29E + 2 * k] = time & 0xFF
    for a in range(0x270, 0x29D):   # progress / cleared flags (exact meaning partly unknown)
        s[a] = 0xFF
    struct.pack_into('<H', s, 0x39D, checksum(s))
    d[base:base + 0x3A0] = s
    return bytes(d)

if __name__ == '__main__':
    t = open(sys.argv[1], 'rb').read()
    open(sys.argv[2], 'wb').write(make(t))
