"""Picross NP Vol. 8 — addresses and settings for tools/npbuild.py (ROM offsets, HiROM: bank C0 = 0x000000).
1.5 MB ROM, 242 puzzles, the "2000 renewal" look. Engine addresses from tools/survey.py; blobs paired with Vol. 5's
by their order in the ROM and checked by content. Built from Vol. 6's config: same C0/C1 tables, same sheets/frames; blobs relocated."""

ROM_NAME = 'Picross NP Vol. 8 (Japan) (Rev 1) (NP).sfc'
ROM_CRC32 = 0x2FBEEA6E
OUT_NAME = 'Picross NP Vol. 8 (English).sfc'

# free space (0xFF in the original). The rebuilt puzzle database (~126 KB) only fits at 0x140000 (banks D4-D7).
FREE = [(0x0D4D10, 0x0E0000), (0x140000, 0x180000), (0x0A8C30, 0x0B0000), (0x03BC20, 0x040000),
        (0x05E1E0, 0x060000), (0x04CA70, 0x050000), (0x02DC20, 0x030000)]

# engine
LZ_JSL = bytes([0x22, 0x8E, 0x19, 0xC0])                # JSL C0:198E
VWF_TABLE, VWF_BASE_ADD = 0x050000, 0x960
KANJI_LIST = 0x002A57
SJIS_ROWS = 0x002691
METASPRITE_TABLE = 0x0A548C
PUZZLE_DB, PUZZLE_SIZE_TBL, PUZZLE_BLOCK_TBL = 0x0B0000, 0x0A6668, 0x00730E
PUZZLE_DB_END = 0x0D4D0E

TUT_BASE = 0x0116E2
TUT_NEW_BASE = 0x016000
TUT_ADC_SITE = 0x010B28
C1_BANK_END = 0x020000
FEATURE_PTRS = None                                # no Special-mode landmark notes
PRIZE_PTRS = (0x01461D, 5)
SAVE_WARN_PEA = [(0, 0x3FF0), (1, 0x404F)]

HELP_BLOB = 0x027CDC
CLEAR_STAMP_CHR = 0x02563E
GFX_LAYERS = {
    'menu_bg2': (0x028D76, 0x02563E, 4),
    'title_bg1': (0x0242E6, 0x020C6B, 4),
    'cert_bg1': (0x04AE90, 0x0461A8, 4, 0x000),
    'cert_bg1b': (0x04AE90, 0x0461A8, 4, 0x800),
    'bonus_bg2a': (0x04B38C, 0x0461A8, 4, 0x000),
    'footer_bg2': (0x04B38C, 0x0461A8, 4, 0x800),
    'prize_bg1': (0x0459C4, 0x0441AE, 4),
    'cert_tmpl': (0x04BA17, 0x0461A8, 4),   # not edited: its tiles must not be taken by the footer labels
    'gift_bg1': (0x03B875, 0x03983F, 4),     # new in Vol. 6: "120 puzzles from Vols. 1-5" gift message
}
LABEL_STYLES = {
    'menu': dict(fill=1, outline=3, font='arialbd.ttf', size=12),
    'header': dict(fill=4, outline=0xB, font='arialbd.ttf', size=13, keep_rows=(13, 16), y_off=1),
    'title_small': dict(fill=0xF, outline=None, pixel=True),
    'title_big': dict(fill=1, outline=None, font='arialbd.ttf', size=14),
    'tab_green': dict(fill=5, outline=None, font='arialbd.ttf', size=8, panel=9, vertical=True),
    'tab_pink': dict(fill=5, outline=None, font='arialbd.ttf', size=8, panel=0xE, vertical=True),
    'cert': dict(fill=4, outline=None, font='arialbd.ttf', size=12, bg=3, blank=0x0BF),
    'footer': dict(fill=3, outline=6, font='arialbd.ttf', size=11),
    'card': dict(fill=3, outline=None, font='ARIALNB.TTF', size=12, bg=7, blank=0x50),
    'deadline': dict(fill=0xB, outline=7, font='arialbd.ttf', size=11, blank=0x20),
    # Vol. 6+ redesign
    'menu6': dict(fill=0xF, outline=1, font='arialbd.ttf', size=12),
    'header6': dict(fill=8, outline=1, font='arialbd.ttf', size=13, keep_rows=(8, 13), y_off=1),
    'tab_red6': dict(fill=0xF, outline=None, font='arialbd.ttf', size=8, panel=6, vertical=True),
    'tab_green6': dict(fill=0xF, outline=None, font='arialbd.ttf', size=8, panel=5, vertical=True),
    'title_band6': dict(fill=1, outline=None, font='arialbd.ttf', size=14, pattern=(8, 1)),
    'gift6': dict(fill=6, outline=None, font='arialbd.ttf', size=12, bg=3, blank=0x14C),
    'gift6_hi': dict(fill=5, outline=None, font='arialbd.ttf', size=12, bg=3, blank=0x14C),
}

CERT_CHR = 0x0461A8
CERT_MAPS = {'full': 0x04AE90, 'template': 0x04BA17}
CERT_OTHER = [(0x04AE90, 0x800), (0x04B38C, 0x000), (0x04B38C, 0x800)]
CERT_BLANK = 0x0BF
CREDIT_FONT_BLOB = 0x048408
CREDIT_TABLE = 0x04C132
CREDIT_ATTR = {'T': 1, 'N': 5}
CREDIT_CENTRE = 33                                 # Vol. 6+: credit box is further left (Vols. 1-5: 41)
RANK_MAP_BLOB = 0x04BD55
RANK_TABLE = 0x015177
CREDIT_PAGES = 13                                  # 12 staff pages + copyright page (Vols. 1-5: 12)
CREDIT_RECLAIM = True                              # font has only 70 blank tiles: reuse replaced kana glyphs
GLYPH_ADD = 0xA0                                   # glyph number = row value + 0xA0 (C0:268D; Vols. 1-5: 0x9C)
RANK_GLYPH_LIMIT = 0x100                           # per-mode certificate uploads only font tiles < 0x100 (Vol. 6)
