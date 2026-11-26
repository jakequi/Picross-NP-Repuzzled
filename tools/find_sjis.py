"""List Shift-JIS text runs in a ROM (kana-heavy runs of >= MIN chars; 00/01 bytes allowed as separators).
usage: python find_sjis.py ROM [MIN]"""
import sys

def runs(d, minimum=4):
    def sj(i):
        a, b = d[i], d[i + 1]
        return (0x81 <= a <= 0x84 or 0x88 <= a <= 0x9F or 0xE0 <= a <= 0xEA) and 0x40 <= b <= 0xFC and b != 0x7F
    i = 0
    while i < len(d) - 1:
        if not sj(i):
            i += 1; continue
        j = i; n = kana = 0
        while j < len(d) - 1:
            if sj(j):
                kana += d[j] in (0x82, 0x83); j += 2; n += 1
            elif d[j] in (0, 1):
                j += 1
            else:
                break
        if n >= minimum and kana / n > 0.5:
            yield i, j, n
        i = j if n >= minimum else i + 1

if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    for s, e, n in runs(d, int(sys.argv[2]) if len(sys.argv) > 2 else 4):
        t = d[s:e].replace(b'\x00', b'|').replace(b'\x01', b'/')
        try:
            t = t.decode('cp932')
        except UnicodeDecodeError:
            t = '?'
        print('%06x %4d %s' % (s, n, t))
