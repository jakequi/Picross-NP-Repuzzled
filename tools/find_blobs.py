"""Statically find LZ blob pointers passed to the decompressor (C0:1992)."""
import re, sys, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
import lz
ROM = sys.argv[1]
d = open(ROM, 'rb').read()
def rom(bank, addr): return ((bank & 0x3F) << 16) | addr
sites = []
for m in re.finditer(rb'\x22\x92\x19\xc0', d):
    j = m.start()
    pre = d[j - 15:j]
    # pattern: PEA dbank / PEA daddr / PEA sbank / PEA saddr / LDA #len
    if pre[0] == 0xF4 and pre[3] == 0xF4 and pre[6] == 0xF4 and pre[9] == 0xF4 and pre[12] == 0xA9:
        dbank = pre[1]; daddr = pre[4] | pre[5] << 8
        sbank = pre[7]; saddr = pre[10] | pre[11] << 8
        ln = pre[13] | pre[14] << 8
        sites.append(dict(site=j, src=rom(sbank, saddr), dst=(dbank << 16) | daddr, len=ln))
    else:
        sites.append(dict(site=j, src=None, note=pre.hex(' ')))
for s in sites:
    if s.get('src') is not None:
        try:
            out, used = lz.decompress(d, s['src'], s['len'] or None)
            s['outlen'] = len(out); s['used'] = used
        except Exception as e:
            s['err'] = str(e)
    print(json.dumps(s))
