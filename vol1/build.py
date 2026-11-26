"""Build the English translation of Picross NP Vol. 1.

usage: python build.py [path/to/Picross NP Vol. 1 (Japan) (Rev 1) (NP).sfc]

Reads the original ROM, regenerates translated text/graphics from script/*,
recompresses them into free ROM space, repoints references, fixes the
checksum and writes out/Picross NP Vol. 1 (English).sfc plus .bps and .ips patches.
"""
import os, re, struct, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
for _t in (os.path.join(HERE, 'tools'), os.path.join(HERE, '..', 'tools')):
    if os.path.isdir(_t):
        sys.path.insert(0, _t)
        break
import lz, gfx, vwf, vwf_en, puzzles, tutorial, labels, spritetext, metasprite, bps

ROM_NAME = 'Picross NP Vol. 1 (Japan) (Rev 1) (NP).sfc'
ROM_CRC32 = 0xE6F29429          # headerless, 1 MiB (No-Intro)
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, ROM_NAME)
OUT_DIR = os.path.join(HERE, 'out')
OUT = os.path.join(OUT_DIR, 'Picross NP Vol. 1 (English).sfc')

HELP_FONT = dict(font='arialbd.ttf', size=11)


def load_tsv_raw(name):
    rows = {}
    for line in open(os.path.join(HERE, 'script', name), encoding='utf-8'):
        if not line.strip() or line.startswith('#'):
            continue
        key, jp, en = line.rstrip('\n').split('\t')
        rows[key] = en.replace('\\n', '\n')
    return rows


def load_tsv(name):
    rows = {}
    for line in open(os.path.join(HERE, 'script', name), encoding='utf-8'):
        if not line.strip() or line.startswith('#'):
            continue
        idx, jp, en = line.rstrip('\n').split('\t')
        rows[int(idx)] = en.replace('\\n', '\n')
    return rows


class Rom:
    def __init__(self, data):
        self.d = bytearray(data)
        self.orig = bytes(data)
        # free regions (ROM offsets) verified to be 0xFF filled in the original
        self.free = [(0x080000, 0x0A0000), (0x0C4000, 0x0E0000), (0x04A000, 0x050000)]

    def alloc(self, n):
        for k, (s, e) in enumerate(self.free):
            if e - s >= n:
                self.free[k] = (s + n, e)
                assert all(b == 0xFF for b in self.orig[s:s + n]), 'free space not empty'
                return s
        raise RuntimeError('out of free space')

    def alloc_high(self, n, minimum):
        """Allocate from a free region starting at or above `minimum` (for forward-relative pointers)."""
        for k, (s, e) in enumerate(self.free):
            if s >= minimum and e - s >= n:
                self.free[k] = (s + n, e)
                assert all(b == 0xFF for b in self.orig[s:s + n]), 'free space not empty'
                return s
        raise RuntimeError('out of high free space')

    def alloc_in(self, n, lo, hi):
        """Allocate n bytes inside [lo, hi) (for pointers with a limited reach)."""
        for k, (s, e) in enumerate(self.free):
            a = max(s, lo)
            if a + n <= min(e, hi):
                assert all(b == 0xFF for b in self.orig[a:a + n]), 'free space not empty'
                if a == s:
                    self.free[k] = (s + n, e)
                else:
                    self.free[k] = (s, a); self.free.insert(k + 1, (a + n, e))
                return a
        raise RuntimeError('no free space in range %06x-%06x' % (lo, hi))

    def write(self, off, data):
        self.d[off:off + len(data)] = data

    # --- references to compressed blobs -------------------------------------------
    def blob_refs(self, src):
        """Find PEA-immediate call sites and 4-byte long-pointer tables pointing at src."""
        bank = 0xC0 | (src >> 16); addr = src & 0xFFFF
        refs = []
        for m in re.finditer(rb'\x22\x92\x19\xc0', self.orig):
            j = m.start(); pre = self.orig[j - 15:j]
            if pre[6] == 0xF4 and pre[9] == 0xF4 and pre[7] == bank and pre[10] | pre[11] << 8 == addr:
                refs.append(('pea', j - 15))
        # 4-byte long pointers in tables: only trusted inside the code banks (C0-C1), where the
        # known blob tables live; elsewhere such byte patterns are coincidental data.
        pat = bytes([addr & 0xFF, addr >> 8, bank, 0])
        for m in re.finditer(re.escape(pat), self.orig[:0x020000]):
            refs.append(('long', m.start()))
        return refs

    def repoint(self, src, new):
        bank = 0xC0 | (new >> 16); addr = new & 0xFFFF
        refs = self.blob_refs(src)
        for kind, p in refs:
            if kind == 'pea':
                self.d[p + 7] = bank
                self.d[p + 10] = addr & 0xFF; self.d[p + 11] = addr >> 8
            else:
                self.d[p] = addr & 0xFF; self.d[p + 1] = addr >> 8; self.d[p + 2] = bank
        return refs

    def replace_blob(self, src, data, header=True):
        comp = lz.compress(data, header=header)
        check, _ = lz.decompress(comp, 0, None if header else len(data))
        assert check == data, 'compressor round-trip failed'
        new = self.alloc(len(comp))
        self.write(new, comp)
        refs = self.repoint(src, new)
        print('  blob %06x -> %06x (%d bytes, %d refs)' % (src, new, len(comp), len(refs)))
        assert refs, 'no references found for blob %06x' % src
        return new

    def fix_checksum(self):
        d = self.d
        d[0xFFDC:0xFFE0] = b'\xff\xff\x00\x00'
        s = sum(d) & 0xFFFF
        d[0xFFDE] = s & 0xFF; d[0xFFDF] = s >> 8
        c = s ^ 0xFFFF
        d[0xFFDC] = c & 0xFF; d[0xFFDD] = c >> 8


def blob(rom, src):
    return lz.decompress(rom.orig, src)[0]


# --- assets ---------------------------------------------------------------------------
def menu_help(rom):
    """Main menu help lines: 22x2-tile 2bpp strips at stride 0x300 in blob C2:74D2."""
    src = 0x0274D2
    data = bytearray(blob(rom, src))
    for idx, en in load_tsv('menu_help.tsv').items():
        img, size = gfx.render_text(en, 176, 16, **HELP_FONT)
        if size < HELP_FONT['size']:
            print('  note: menu_help %d shrunk to %dpx' % (idx, size))
        data[idx * 0x300:idx * 0x300 + 0x2C0] = gfx.image_to_tiles(img, 2)
    rom.replace_blob(src, bytes(data))


def vwf_font(rom):
    """English glyphs for the Shift-JIS text engine (hi-res layer: glyphs drawn 2x wide)."""
    done = vwf_en.install(rom.d, rom.alloc)
    print('  %d glyphs replaced' % len(done))


def puzzle_names(rom):
    """Rebuild the puzzle database (pointer table at CB:0000) with English names in free space."""
    names = load_tsv('puzzle_names.tsv')
    ps = puzzles.all_puzzles(rom.orig)
    offs = [p['off'] for p in ps]
    end = 0x0C3FFF
    while rom.orig[end] == 0xFF:
        end -= 1
    end += 1
    blob = bytearray()
    new_offs = []
    for k, p in enumerate(ps):
        rec_end = offs[k + 1] if k + 1 < len(offs) else end
        rec = rom.orig[p['off']:rec_end]
        enc = vwf_en.encode(names[p['index']])
        a = p['name_off'] - p['off']; b = p['name_end'] - p['off']
        new_offs.append(len(blob))
        blob += rec[:a] + enc + rec[b:]
    base = rom.alloc_high(len(blob), minimum=puzzles.DB)
    rom.write(base, blob)
    for k, o in enumerate(new_offs):
        rel = base + o - puzzles.DB
        rom.d[puzzles.DB + k * 3:puzzles.DB + k * 3 + 3] = bytes([rel & 0xFF, rel >> 8 & 0xFF, rel >> 16])
    print('  %d records, %d bytes at %06x' % (len(ps), len(blob), base))


TUT_NEW_BASE = 0x016000          # C1:6000, free space in the same bank
TUT_LINE_PX = 340                # hi-res pixels available per line
TUT_LINES = 4


def encode_vwf_text(en):
    """English with \n -> engine bytes (01 = newline, full-width SJIS chars)."""
    out = bytearray()
    for k, part in enumerate(en.split('\n')):
        if k:
            out.append(1)
        out += vwf_en.encode(part)
    return bytes(out)


def check_pages(ops, english, label):
    """Simulate the 4-line tutorial box; warn on overflow."""
    x = 0; line = 0; problems = []
    for i, (c, payload) in enumerate(ops):
        if c == 0x04:
            x = 0; line = 0
        if c in (1, 2):
            text = english.get(i)
            for k, part in enumerate(text.split('\n')):
                if k:
                    x = 0; line += 1
                x += vwf_en.text_width(part)
                if x > TUT_LINE_PX:
                    problems.append('%s.%d line too wide (%d px): %r' % (label, i, x, part))
                if line >= TUT_LINES and part:
                    problems.append('%s.%d more than %d lines' % (label, i, TUT_LINES))
    return problems


def tutorial_script(rom):
    tr = load_tsv_raw('tutorial.tsv')
    d = rom.orig
    offs = tutorial.section_offsets(d)
    body = bytearray(); new_offs = []
    head = 2 * tutorial.NSECT
    problems = []
    for k, o in enumerate(offs):
        ops, _ = tutorial.parse_section(d, o)
        english = {}
        new_ops = []
        for i, (c, payload) in enumerate(ops):
            if c in (1, 2):
                key = '%d.%d' % (k, i)
                if key not in tr:
                    raise KeyError('tutorial line %s missing' % key)
                english[i] = tr[key]
                payload = encode_vwf_text(tr[key])
            new_ops.append((c, payload))
        problems += check_pages(ops, english, str(k))
        new_offs.append(head + len(body))
        body += tutorial.serialize(new_ops)
    block = struct.pack('<%dH' % tutorial.NSECT, *new_offs) + body
    base = TUT_NEW_BASE
    assert all(b == 0xFF for b in rom.orig[base:base + len(block)])
    rom.write(base, block)
    # repoint every reference to C1:1682+k (LDA long,X / LDA long) and the ADC #$1682
    old = tutorial.BASE & 0xFFFF; new = base & 0xFFFF
    n = 0
    for m in re.finditer(rb'[\xaf\xbf][\x80-\x8f]\x16\xc1', rom.orig):
        p = m.start() + 1
        a = rom.orig[p] | rom.orig[p + 1] << 8
        a2 = new + (a - old)
        rom.d[p] = a2 & 0xFF; rom.d[p + 1] = a2 >> 8; n += 1
    assert rom.orig[0x10B26:0x10B29] == b'\x69\x82\x16'
    rom.d[0x10B27] = new & 0xFF; rom.d[0x10B28] = new >> 8; n += 1
    print('  %d bytes at %06x, %d refs patched' % (len(block), base, n))
    for pr in problems:
        print('  WARNING', pr)
    return base + len(block)


def jp_line_widths(rom_bytes, raw):
    """Hi-res pixel widths of each line of an original Shift-JIS string (game metrics)."""
    d = rom_bytes
    def glyph(code):
        lead, trail = code & 0xFF, code >> 8
        if lead < 0x84:
            return vwf_en.glyph_index(d, lead << 8 | trail)
        k = 0
        while True:
            w = struct.unpack_from('<H', d, 0x2A5B + k)[0]
            if w == 0:
                return 0x9C
            if w == code:
                return k // 2 + 0x10C + 0x9C
            k += 2
    widths = [0]; p = 0
    while p < len(raw):
        if raw[p] == 1:
            widths.append(0); p += 1; continue
        code = raw[p] | raw[p + 1] << 8
        widths[-1] += d[vwf.glyph_ptr(d, glyph(code))] + 2
        p += 2
    return widths


def sjis_string_at(d, p):
    q = p
    while d[q] != 0:
        q += 1 if d[q] == 1 else 2
    return bytes(d[p:q])


class BankAlloc:
    """Allocator for free space inside one bank (for 16-bit pointers)."""
    def __init__(self, rom, start, end):
        self.rom, self.p, self.end = rom, start, end

    def put(self, data):
        assert self.p + len(data) <= self.end, 'bank full'
        assert all(b == 0xFF for b in self.rom.orig[self.p:self.p + len(data)])
        a = self.p
        self.rom.write(a, data); self.p += len(data)
        return a


def pointer_strings(rom, tsv, entries, alloc, label, slack=8):
    """entries: list of (index, pointer_offset, pointer_size). Writes English strings
    via alloc and repoints. Width limit per set = widest original line + slack."""
    tr = load_tsv(tsv)
    limit = 0
    for idx, po, size in entries:
        ptr = int.from_bytes(rom.orig[po:po + size], 'little')
        raw = sjis_string_at(rom.orig, (po & 0xFF0000) | (ptr & 0xFFFF))
        limit = max(limit, max(jp_line_widths(rom.orig, raw)))
    limit += slack
    for idx, po, size in entries:
        en = tr[idx]
        for line in en.split('\n'):
            w = vwf_en.text_width(line)
            if w > limit:
                print('  WARNING %s %d too wide (%d > %d): %r' % (label, idx, w, limit, line))
        a = alloc.put(encode_vwf_text(en) + b'\x00')
        old = int.from_bytes(rom.orig[po:po + size], 'little')
        new = (old & ~0xFFFF) | (a & 0xFFFF) if size > 2 else a & 0xFFFF
        rom.write(po, new.to_bytes(size, 'little'))
    print('  %s: %d strings (limit %d px)' % (label, len(entries), limit))


def feature_and_prize_text(rom, c1):
    pointer_strings(rom, 'feature_text.tsv', [(k, 0x013B43 + k * 2, 2) for k in range(12)], c1, 'feature')
    pointer_strings(rom, 'prize_text.tsv', [(k, 0x014514 + k * 8 + 4, 3) for k in range(6)], c1, 'prize')


def pea_strings(rom, tsv, refs, alloc, label):
    """Strings passed as PEA bank / PEA addr (refs = ROM offsets of the address operand)."""
    tr = load_tsv(tsv)
    for idx, ref in refs:
        assert rom.orig[ref - 1] == 0xF4 and rom.orig[ref - 4] == 0xF4
        bank = rom.orig[ref - 3]
        old = ((bank & 0x3F) << 16) | rom.orig[ref] | rom.orig[ref + 1] << 8
        limit = max(jp_line_widths(rom.orig, sjis_string_at(rom.orig, old))) + 8
        en = tr[idx]
        for line in en.split('\n'):
            if vwf_en.text_width(line) > limit:
                print('  WARNING %s %d too wide: %r' % (label, idx, line))
        a = alloc.put(encode_vwf_text(en) + b'\x00')
        rom.d[ref - 3] = 0xC0 | (a >> 16)
        rom.d[ref] = a & 0xFF; rom.d[ref + 1] = a >> 8 & 0xFF
    print('  %s: %d strings' % (label, len(refs)))


# --- graphic labels in BG tilemaps ----------------------------------------------------
GFX_LAYERS = {
    # name: (tilemap blob, char blob, bpp[, map byte offset for 64-wide maps])
    'menu_bg2': (0x028A51, 0x025702, 4),
    'title_bg1': (0x023AD3, 0x020C6B, 4),
    'cert_bg1': (0x047084, 0x04210B, 4, 0x000),     # bonus certificate (page 1)
    'cert_bg1b': (0x047084, 0x04210B, 4, 0x800),    # right half (not edited; for tile sharing)
    'bonus_bg2a': (0x0476F4, 0x04210B, 4, 0x000),   # not edited; for tile sharing
    'footer_bg2': (0x0476F4, 0x04210B, 4, 0x800),   # credits footer
    'prize_bg1': (0x0417BE, 0x040000, 4),           # prize screen postcard / deadline
}

LABEL_STYLES = {
    'menu': dict(fill=1, outline=3, font='arialbd.ttf', size=12),
    'header': dict(fill=4, outline=0xB, font='arialbd.ttf', size=13, keep_rows=(13, 16), y_off=1),
    'title_small': dict(fill=0xF, outline=None, font='verdanab.ttf', size=8),
    'title_big': dict(fill=1, outline=None, font='arialbd.ttf', size=14),
    'tab_green': dict(fill=5, outline=None, font='arialbd.ttf', size=8, panel=9, vertical=True),
    'tab_pink': dict(fill=5, outline=None, font='arialbd.ttf', size=8, panel=0xE, vertical=True),
    'cert': dict(fill=4, outline=None, font='arialbd.ttf', size=12, bg=3, blank=0x0BF),
    'footer': dict(fill=3, outline=6, font='arialbd.ttf', size=11),
    'card': dict(fill=3, outline=None, font='ARIALNB.TTF', size=12, bg=7, blank=0x50),
    'deadline': dict(fill=0xB, outline=7, font='arialbd.ttf', size=11, blank=0x20),
}


def load_labels():
    rows = []
    for line in open(os.path.join(HERE, 'script', 'labels.tsv'), encoding='utf-8'):
        if not line.strip() or line.startswith('#'):
            continue
        lid, layer, rect, style, jp, en = line.rstrip('\n').split('\t')
        rows.append(dict(id=lid, layer=layer, rect=tuple(int(v) for v in rect.split(',')), style=style,
                         jp=jp, en=en.replace('\\n', '\n')))
    return rows


def render_label_image(layer, rect, st, en):
    import numpy as np
    tx, ty, w, h = rect
    W, H = w * 8, h * 8
    orig = layer.read_rect(tx, ty, w, h)
    if st.get('vertical'):
        # panel: clear interior to panel colour, stack letters top to bottom
        img = orig.copy()
        img[(img != 0) & (img != st['panel'])] = st['panel']
        # keep the panel's border pixels (non-panel, non-zero colours on the edge columns)
        img[:, -3:] = orig[:, -3:]
        img[-2:, :] = orig[-2:, :]
        letters = list(en)
        cell_h = (H - 2) // len(letters)
        for k, ch in enumerate(letters):
            g, _ = labels.render_outlined(ch, W - 3, cell_h, fill=st['fill'], outline=None,
                                          font=st['font'], size=st['size'])
            sub = img[1 + k * cell_h:1 + (k + 1) * cell_h, 0:W - 3]
            sub[g != 0] = g[g != 0]
        return img
    img, size = labels.render_outlined(en, W, H, fill=st['fill'], outline=st.get('outline'),
                                       font=st['font'], size=st['size'], y_off=st.get('y_off'))
    if size < st['size']:
        print('  note: label %r shrunk to %dpx' % (en, size))
    if 'keep_rows' in st:
        a, b = st['keep_rows']
        img[a:b, :] = np.where(img[a:b, :] != 0, img[a:b, :], orig[a:b, :])
    return img


def graphic_labels(rom, cache):
    layers = {k: labels.TileLayer(cache, v[0], v[1], v[2], map_off=v[3] if len(v) > 3 else 0)
              for k, v in GFX_LAYERS.items()}
    def others(k):
        return [set(L.usage()) for k2, L in layers.items() if k2 != k and L.chr_src == layers[k].chr_src]
    pools = {}
    for k, L in layers.items():   # one shared pool per char blob
        pools.setdefault(L.chr_src, labels.free_tiles(L, others(k)))
    for lab in load_labels():
        L = layers[lab['layer']]
        st = LABEL_STYLES[lab['style']]
        img = render_label_image(L, lab['rect'], st, lab['en'])
        pool = pools[L.chr_src]
        labels.write_label(L, lab['rect'], img, pool, other_maps=others(lab['layer']),
                           bg=st.get('bg'), blank=st.get('blank', 0))
        used = {L.entry(x, y) & 0x3FF for y in range(lab['rect'][1], lab['rect'][1] + lab['rect'][3])
                for x in range(lab['rect'][0], lab['rect'][0] + lab['rect'][2])}
        pool[:] = [t for t in pool if t not in used]
    print('  %d labels' % len(load_labels()))
    # menu "★クリア" stamp (BG2 tiles 0x0C-0x13 over 0x14-0x1B in char blob C2:5702) -> CLEAR
    import numpy as np, tinyfont
    chr_ = cache.get(0x025702)
    img = np.vstack([np.hstack([gfx.decode_tile(chr_[t * 32:t * 32 + 32], 4) for t in range(r0, r0 + 8)])
                     for r0 in (0x0C, 0x14)])
    img[2:11, 31:57] = tinyfont.render('CLEAR', 26, 9, fill=0xE, outline=None, bg=9)
    for k, r0 in enumerate((0x0C, 0x14)):
        for c in range(8):
            chr_[(r0 + c) * 32:(r0 + c) * 32 + 32] = gfx.encode_tile(img[k * 8:k * 8 + 8, c * 8:c * 8 + 8], 4)


def sprite_text(rom, cache):
    """Sprite text: pause panel (in place), window frames (rewritten), mode badges."""
    import importlib.util, numpy as np
    spec = importlib.util.spec_from_file_location('sprites', os.path.join(HERE, 'script', 'sprites.py'))
    S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
    sheet = spritetext.Sheet(cache, S.GAME_SHEET, free=S.GAME_FREE)
    sheet.check_free()
    for t0, x0, x1, text in S.PAUSE_ROWS:
        spritetext.repaint_row(sheet, t0, 10, x0, x1, text, x_text=8 - x0)
    B = S.BANNER
    strip = sheet.read_strip(B['t0'], 16, rows=2)
    strip[B['y0']:B['y1'], B['x0']:B['x1']] = B['bg']
    txt, _ = labels.render_outlined(B['text'], B['x1'] - B['x0'], B['y1'] - B['y0'], fill=B['fill'],
                                    outline=None, font='ARIALNB.TTF', size=11)
    area = strip[B['y0']:B['y1'], B['x0']:B['x1']]
    area[txt != 0] = txt[txt != 0]
    sheet.write_strip(B['t0'] + 1, strip[:, 8:], rows=2)
    for frame, (ys, lines) in sorted(S.FRAMES.items()):
        def remove(e, ys=ys):
            return (not e['big']) and e['tile'] not in S.WINDOW_TILES and (ys is None or e['y'] in ys)
        spritetext.rewrite_frame(rom, frame, sheet, remove, lines, rom.alloc)
    badges = cache.get(S.BADGE_BLOB)
    for k, text in enumerate(S.BADGES):
        img = spritetext.badge(text)
        for t in range(16):
            r, c = divmod(t, 8)
            o = k * 0x200 + t * 32
            badges[o:o + 32] = gfx.encode_tile(img[r * 8:r * 8 + 8, c * 8:c * 8 + 8], 4)
    print('  %d pause rows, %d frames, %d badges, %d sheet tiles left' % (
        len(S.PAUSE_ROWS), len(S.FRAMES), len(S.BADGES), len(sheet.free)))
    menu_sprites(rom, cache, S)


def mode_label_image(text):
    """16px label: red text, white outline, coloured ring (index 2), like the original."""
    import numpy as np, tinyfont
    ink = tinyfont.text_bitmap(text)
    w = ((ink.shape[1] + 6) + 7) // 8 * 8
    m = np.zeros((16, w), bool)
    x0 = (w - ink.shape[1]) // 2
    m[5:10, x0:x0 + ink.shape[1]] = ink
    def grow(a):
        o = np.zeros_like(a)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                o |= np.roll(np.roll(a, dy, 0), dx, 1)
        return o
    o1 = grow(m); o2 = grow(o1)
    img = np.zeros((16, w), np.uint8)
    img[o2] = 2; img[o1] = 0xE; img[m] = 9
    return img


def menu_sprites(rom, cache, S):
    import numpy as np, tinyfont
    sheet = spritetext.Sheet(cache, S.MENU_SHEET, free=S.MENU_FREE)
    sheet.check_free()
    users = {}
    for f in S.MENU_FRAMES:
        for i, t, *_ in spritetext.frame_cells(metasprite.parse_frame(rom.orig, f)):
            users.setdefault(t, set()).add(f)
    x0, y0, x1, y1 = S.PANEL_BOX
    for frames, lines in S.PANELS:
        for f in frames:
            def painter(cv, ox, oy, lines=lines):
                cv[y0 + oy:y1 + oy, x0 + ox:x1 + ox] = S.PANEL_STYLE['bg']
                for cy, text in lines:
                    w = x1 - x0
                    img = tinyfont.render(text, w, 7, fill=S.PANEL_STYLE['fill'], outline=S.PANEL_STYLE['outline'],
                                          bg=S.PANEL_STYLE['bg'], y_top=1)
                    cv[cy - 3 + oy:cy + 4 + oy, x0 + ox:x1 + ox] = img
            spritetext.paint_frames(rom, sheet, [f], painter, rom.alloc, users, group=set(frames))
    # mode labels: reclaim old label tiles, draw one label per frame as 8x8 entries
    reclaim = [t for t in S.MODE_LABEL_TILES if users.get(t, set()) <= set(S.MODE_LABELS)]
    for t in reclaim:
        sheet.put(t, np.zeros((8, 8), np.uint8))
    sheet.free = reclaim + sheet.free
    for f, text in sorted(S.MODE_LABELS.items()):
        pal = metasprite.parse_frame(rom.orig, f)[0]['pal']
        img = spritetext.text_strip(text, fill=9, outline=0xE, bg=0)
        row = sheet.alloc_strip(img)
        w = img.shape[1]
        ents = [dict(x=-w // 2 + k * 8, y=3, tile=t, pal=pal, big=False, hf=False, vf=False) for k, t in enumerate(row)]
        data = metasprite.encode_frame(ents)
        off = rom.alloc(len(data)); rom.write(off, data)
        p = metasprite.TABLE + f * 4; a = 0xC00000 | off
        rom.d[p] = a & 0xFF; rom.d[p + 1] = a >> 8 & 0xFF; rom.d[p + 2] = a >> 16
    print('  menu sheet: %d panels, %d labels, %d tiles left' % (len(S.PANELS), len(S.MODE_LABELS), len(sheet.free)))
    psel = spritetext.Sheet(cache, S.PSEL_SHEET, free=S.PSEL_FREE)
    psel.check_free()
    def make(text):
        import tinyfont
        from PIL import ImageFont
        f = ImageFont.truetype(os.path.join(spritetext.FONT_DIR, 'verdanab.ttf'), 8)
        bb = f.getbbox(text); w = ((bb[2] - bb[0]) + 8 + 7) // 8 * 8
        return spritetext.badge(text, w=w, **S.PSEL_LABEL_STYLE)
    spritetext.relabel_frames(rom, psel, S.PSEL_LABELS, make, rom.alloc)
    print('  puzzle-select labels: %d, %d tiles left' % (len(S.PSEL_LABELS), len(psel.free)))
    bonus_sprites(rom, cache, S)


def bonus_sprites(rom, cache, S):
    import numpy as np, tinyfont
    sh = spritetext.Sheet(cache, S.BONUS_SHEET, free=S.BONUS_FREE)
    sh.check_free()
    tmpl = np.vstack([np.hstack([sh.get(S.SEAL_TEMPLATE[r * 3 + c]) for c in range(3)]) for r in range(4)])
    def seal(text):
        img = tmpl.copy()
        img[2:26, 2:22] = 0
        lines = text.split('\n')
        top = 2 + (24 - 7 * len(lines)) // 2
        for k, ln in enumerate(lines):
            img[top + 7 * k:top + 7 * k + 7, 2:22] = tinyfont.render(ln, 20, 7, fill=0xB, outline=None, bg=0, y_top=1)
        return img
    spritetext.relabel_frames(rom, sh, S.SEALS, seal, rom.alloc)
    # badges: ring colour taken from each original badge (first non-zero pixel of its middle row)
    def badge_for(frame):
        old = metasprite.parse_frame(rom.orig, frame)
        cells = list(spritetext.frame_cells(old))
        xs = [c[2] for c in cells]; ys = [c[3] for c in cells]
        cv = np.zeros((max(ys) - min(ys) + 8, max(xs) - min(xs) + 8), np.uint8)
        for _, t, x, y, hf, vf in cells:
            cv[y - min(ys):y - min(ys) + 8, x - min(xs):x - min(xs) + 8] |= sh.get(t)
        mid = cv[cv.shape[0] // 2 - 1]
        ring = int(mid[np.nonzero(mid)[0][0]])
        def make(text):
            from PIL import ImageFont
            f = ImageFont.truetype(os.path.join(spritetext.FONT_DIR, 'verdanab.ttf'), 8)
            bb = f.getbbox(text); w = ((bb[2] - bb[0]) + 8 + 7) // 8 * 8
            return spritetext.badge(text, w=w, text_col=0xB, fill=0, border=ring)
        return make
    for f, text in sorted(S.CERT_BADGES.items()):
        spritetext.relabel_frames(rom, sh, {f: text}, badge_for(f), rom.alloc)
    print('  bonus sheet: %d seals, %d badges, %d tiles left' % (len(S.SEALS), len(S.CERT_BADGES), len(sh.free)))


CERT_CHR = 0x04210B
CERT_MAPS = {'full': 0x047084, 'template': 0x047C02}
CERT_OTHER = [(0x047084, 0x800), (0x0476F4, 0x000), (0x0476F4, 0x800)]   # same char blob, not edited here
CERT_BLANK = 0x0BF


def certificates(rom, cache):
    """Bonus certificates: clear Japanese text cells, write English with an 8x16 glyph font."""
    import glyphfont
    layers = {k: labels.TileLayer(cache, m, CERT_CHR, 4) for k, m in CERT_MAPS.items()}
    other = set()
    for m, off in CERT_OTHER:
        other |= set(labels.TileLayer(cache, m, CERT_CHR, 4, map_off=off).usage())
    rows = range(9, 21)
    text_tiles = set(); spans = {}
    for k, L in layers.items():
        u = L.usage()
        cells = []
        for ty in rows:
            for tx in range(32):
                t = L.entry(tx, ty) & 0x3FF
                if t == CERT_BLANK or t in other:
                    continue
                if all(py in rows for px, py in u[t]):
                    cells.append((tx, ty)); text_tiles.add(t)
        spans[k] = (min(c[0] for c in cells), max(c[0] for c in cells))
        blank_word = next(L.entry(tx, 9) for tx in range(32) if L.entry(tx, 9) & 0x3FF == CERT_BLANK)
        for tx, ty in cells:
            L.set_entry(tx, ty, blank_word)
        layers[k].blank_word = blank_word
    # tiles freed from both certificates (and blank, unreferenced tiles) become the glyph pool
    data = cache.get(CERT_CHR)
    pool = sorted(text_tiles)
    font = glyphfont.GlyphFont(cache, CERT_CHR, 4, pool, dict(fill=4, shadow=6, bg=3))
    n = 0
    for line in open(os.path.join(HERE, 'script', 'certificate.tsv'), encoding='utf-8'):
        if not line.strip() or line.startswith('#'):
            continue
        mp, row, col, jp, en = line.rstrip('\n').split('\t')
        L = layers[mp]; row = int(row)
        lo, hi = spans[mp]
        start = (lo + hi + 1 - len(en)) // 2 if col == 'c' else int(col)
        attr = L.blank_word & 0xFC00
        for k, c in enumerate(font.cells(en)):
            if c is None:
                continue
            L.set_entry(start + k, row, attr | c[0]); L.set_entry(start + k, row + 1, attr | c[1])
        n += 1
    print('  %d lines, %d glyphs, %d spare tiles' % (n, len(font.glyphs), len(font.pool)))


CREDIT_FONT_BLOB = 0x044A0A       # BG3 2bpp char blob (credits / certificate titles)
CREDIT_ATTR = {'T': 1, 'N': 5}    # palettes used by original titles / names
CREDIT_CENTRE = 41                # 2 x centre column of the original lines (20.5)


def credit_pages(rom, cache):
    """Rebuild the bonus credit pages (C4:8421) in English using an 8x16 glyph font in C4:4A0A."""
    import credits as C, glyphfont, lz as _lz
    data = cache.get(CREDIT_FONT_BLOB)
    pool = [t for t in range(0x255, len(data) // 16) if not any(data[t * 16:t * 16 + 16])]
    blank = pool.pop(0)
    font = glyphfont.GlyphFont(cache, CREDIT_FONT_BLOB, 2, pool, dict(fill=1, shadow=2))
    rows = {}
    for line in open(os.path.join(HERE, 'script', 'credits.tsv'), encoding='utf-8'):
        if not line.strip() or line.startswith('#'):
            continue
        page, row, kind, jp, en = line.rstrip('\n').split('\t')
        rows.setdefault(int(page), []).append((int(row), kind, en))
    pages = C.pages(rom.orig)
    for p, lines in rows.items():
        if p == 0:   # keep decoration (palette 4) records, drop the old title
            recs = [r for r in pages[0] if (r[1][0] >> 10) & 7 == 4]
        else:
            recs = []
        for row, kind, en in lines:
            cells = font.cells(en)
            col = (CREDIT_CENTRE - len(en)) // 2
            pal = CREDIT_ATTR[kind]
            for half in (0, 1):
                words = []
                for c in cells:
                    if c is None:
                        words.append(0x2000 | pal << 10 | blank)
                    else:
                        t = c[half]; words.append(0x2000 | pal << 10 | t)
                recs.append(((row + half) * 64 + col * 2, words))
        pages[p] = recs
    offs, blob = C.encode(pages)
    base = C.TABLE + 2 * C.NPAGES
    old_end = C.TABLE + max(struct.unpack_from('<H', rom.orig, C.TABLE + 2 * k)[0] for k in range(C.NPAGES))
    # new data goes to free space in the same bank (C4), table entries are relative to C4:8421
    new = rom.alloc_in(len(blob), C.TABLE, C.TABLE + 0xFFFF - len(blob))
    rel_base = new - C.TABLE
    rom.write(new, blob)
    for k, o in enumerate(offs):
        struct.pack_into('<H', rom.d, C.TABLE + 2 * k, rel_base + o)
    print('  %d pages, %d glyphs, %d bytes at %06x' % (len(pages), len(font.glyphs), len(blob), new))
    # certificate rank titles: 16x2 map cells copied from blob C4:8044 at offsets in table C1:5084
    titles = {}
    for line in open(os.path.join(HERE, 'script', 'ranks.tsv'), encoding='utf-8'):
        if line.strip() and not line.startswith('#'):
            k, jp, en = line.rstrip('\n').split('\t'); titles[int(k)] = en
    m = cache.get(0x048044)
    for k, en in titles.items():
        o = struct.unpack_from('<H', rom.orig, 0x015084 + 2 * k)[0]
        assert len(en) <= 16
        start = (16 - len(en)) // 2
        cells = font.cells(en)
        for half in (0, 1):
            for c in range(16):
                i = c - start
                w = 0
                if 0 <= i < len(cells) and cells[i] is not None:
                    w = 0x2000 | cells[i][half]
                elif 0 <= i < len(cells):
                    w = 0x2000 | blank
                struct.pack_into('<H', m, o + half * 0x40 + c * 2, w)
    print('  %d rank titles, %d glyphs total' % (len(titles), len(font.glyphs)))


def ips(orig, new):
    out = bytearray(b'PATCH')
    i = 0; n = len(new)
    while i < n:
        if i < len(orig) and orig[i] == new[i]:
            i += 1; continue
        j = i
        while j < n and j - i < 0xFFFF and (j >= len(orig) or orig[j] != new[j] or
                                             (j + 1 < n and j + 1 < len(orig) and orig[j + 1] != new[j + 1])):
            j += 1
        if i == 0x454F46:  # 'EOF' offset can't be encoded; back up one byte
            i -= 1
        out += bytes([i >> 16, (i >> 8) & 0xFF, i & 0xFF, (j - i) >> 8, (j - i) & 0xFF]) + new[i:j]
        i = j
    out += b'EOF'
    return bytes(out)


def main():
    if not os.path.exists(SRC):
        sys.exit('ROM not found: %s (pass the path to %s)' % (SRC, ROM_NAME))
    data = open(SRC, 'rb').read()
    if len(data) % 0x8000 == 512:
        data = data[512:]   # strip copier header
    if zlib.crc32(data) != ROM_CRC32:
        sys.exit('Unexpected ROM (CRC32 %08X, expected %08X): use %s' % (zlib.crc32(data), ROM_CRC32, ROM_NAME))
    rom = Rom(data)
    print('menu help text'); menu_help(rom)
    print('VWF font'); vwf_font(rom)
    print('puzzle names'); puzzle_names(rom)
    print('tutorial'); end = tutorial_script(rom)
    c1 = BankAlloc(rom, (end + 0xFF) & ~0xFF, 0x020000)
    print('feature/prize text'); feature_and_prize_text(rom, c1)
    print('system text'); pea_strings(rom, 'system_text.tsv', [(0, 0x3FEA), (1, 0x4049)], c1, 'save warnings')
    print('graphic labels'); cache = labels.BlobCache(rom); graphic_labels(rom, cache)
    print('sprite text'); sprite_text(rom, cache)
    print('credits'); credit_pages(rom, cache)
    print('certificates'); certificates(rom, cache)
    cache.commit()
    rom.fix_checksum()
    os.makedirs(OUT_DIR, exist_ok=True)
    open(OUT, 'wb').write(rom.d)
    open(os.path.splitext(OUT)[0] + '.ips', 'wb').write(ips(rom.orig, bytes(rom.d)))
    patch = bps.create(rom.orig, bytes(rom.d))
    assert bps.apply(rom.orig, patch) == bytes(rom.d), 'BPS self-test failed'
    open(os.path.splitext(OUT)[0] + '.bps', 'wb').write(patch)
    print('BPS patch: %d bytes (verified)' % len(patch))
    print('wrote', OUT)


if __name__ == '__main__':
    main()
