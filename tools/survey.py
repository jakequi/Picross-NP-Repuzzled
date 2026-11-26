"""Locate the Picross NP engine structures in a ROM by code signature (no hard-coded addresses).

Run this first on a new volume: it reports the addresses that build.py / tools need, so they can be
updated quickly. usage: python survey.py ROM
"""
import re, struct, sys


def rom_off(bank, addr):
    return ((bank & 0x3F) << 16) | addr


def find(d, pat, limit=0x40000):
    return [m for m in re.finditer(pat, d[:limit], re.S)]


def survey(d):
    r = {}
    # LZ decompressor: PHB PHD PHX PHY PHA PHA PHA TSC TCD PEA $7F00 PLB PLB
    m = find(d, rb'\x8b\x0b\xda\x5a\x48\x48\x48\x3b\x5b\xf4\x00\x7f\xab\xab')
    r['lz_decompressor'] = ['%02X:%04X' % (0xC0 | x.start() >> 16, x.start() & 0xFFFF) for x in m]
    calls = []
    for x in m:
        a = x.start()
        jsl = bytes([0x22, a & 0xFF, a >> 8 & 0xFF, 0xC0 | a >> 16])
        calls.append('%02X:%04X x%d' % (0xC0 | a >> 16, a & 0xFFFF, len(re.findall(re.escape(jsl), d))))
    r['lz_call_sites'] = calls
    # VWF glyph table: LDA $bbaaaa,X ; CLC ; ADC #$base ; STA $01
    m = find(d, rb'\xbf(..)(.)\x18\x69(..)\x85\x01')
    r['vwf_glyph_table'] = ['%06X (+%04X)' % (rom_off(x.group(2)[0], struct.unpack('<H', x.group(1))[0]),
                                             struct.unpack('<H', x.group(3))[0]) for x in m]
    # SJIS lead-byte row table + kanji list (C0:2646 in Vol. 1)
    m = find(d, rb'\xc9\x84\x00\xb0.\x38\xe9\x81\x00\x90.\x0a\xaa\xa3\x02\x29\xff\x00\x38\xe9\x40\x00\x0a\x18'
                 rb'\x7f(..)(.)\xaa\xbf(..)(.)')
    r['sjis_row_table'] = ['%06X -> %06X' % (rom_off(x.group(2)[0], struct.unpack('<H', x.group(1))[0]),
                                            rom_off(x.group(4)[0], struct.unpack('<H', x.group(3))[0])) for x in m]
    m = find(d, rb'\xa2\x00\x00\xbf(..)(.)\xf0.\xc3\x01')
    r['kanji_list'] = ['%06X' % rom_off(x.group(2)[0], struct.unpack('<H', x.group(1))[0]) for x in m]
    # Metasprite pointer table: LDA $table,X ; STA $01 ; INC ; INC ; STA $05
    m = find(d, rb'\xbf(..)(.)\x85\x01\x1a\x1a\x85\x05')
    r['metasprite_table'] = sorted({'%06X' % rom_off(x.group(2)[0], struct.unpack('<H', x.group(1))[0]) for x in m})
    # Tutorial script base: LDA $base,X ; AND #$00FF ; ASL ; TAX ; JSR ($tbl,X)
    m = find(d, rb'\xbf(..)(.)\x29\xff\x00\x0a\xaa\xfc(..)')
    r['tutorial_base'] = ['%06X (cmd table %02X:%04X)' % (rom_off(x.group(2)[0], struct.unpack('<H', x.group(1))[0]),
                                                         0xC0 | x.start() >> 16, struct.unpack('<H', x.group(3))[0])
                          for x in m]
    # Puzzle database: LDA $bb0000,X ; CLC ; ADC #$0000 ; STA $05
    m = find(d, rb'\xbf\x00\x00(.)\x18\x69\x00\x00\x85\x05')
    r['puzzle_db'] = ['%06X' % rom_off(x.group(1)[0], 0) for x in m]
    # Puzzle size table (w, h per type): LDA $tbl,X / $tbl+1,X / $tbl+2,X / $tbl+3,X after ASL x3
    m = find(d, rb'\x0a\x0a\x0a\xaa\xbf(..)(.)\x29\xff\x00\x99\x1e\x00')
    r['puzzle_size_table'] = ['%06X' % rom_off(x.group(2)[0], struct.unpack('<H', x.group(1))[0]) for x in m]
    # Game mode table: LDA $tbl,X ; STA $000108
    m = find(d, rb'\xbf(..)(.)\x8f\x08\x01\x00')
    r['mode_table'] = ['%06X' % rom_off(x.group(2)[0], struct.unpack('<H', x.group(1))[0]) for x in m]
    # Credit/bonus page table: ASL ; TAX ; LDA $tbl,X ; TAX ; LDA $tbl,X
    m = find(d, rb'\x0a\xaa\xbf(..)(.)\xaa\xbf\1\2')
    r['credit_pages'] = ['%06X' % rom_off(x.group(2)[0], struct.unpack('<H', x.group(1))[0]) for x in m]
    # Free space (0xFF runs >= 8 KB)
    free = []
    for m in re.finditer(rb'\xff{8192,}', d):
        free.append('%06X-%06X' % (m.start(), m.end()))
    r['free_space'] = free
    return r


if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    if len(d) % 0x8000 == 512:
        d = d[512:]
    print('internal name:', d[0xFFC0:0xFFD5].decode('ascii', 'replace'))
    for k, v in survey(d).items():
        print('%-20s %s' % (k, v))
