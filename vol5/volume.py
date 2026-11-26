"""Picross NP Vol. 5 — addresses and settings for tools/npbuild.py (ROM offsets, HiROM: bank C0 = 0x000000).
Derived with tools/survey.py; the blobs are Vol. 4's, relocated (bank C4 data shifted by +0x62), and were
identified by matching decompressed blobs against VRAM dumps taken in Mesen."""

ROM_NAME = 'Picross NP Vol. 5 (Japan) (Rev 1) (NP).sfc'
ROM_CRC32 = 0x5AC117C9
OUT_NAME = 'Picross NP Vol. 5 (English).sfc'

# free space (0xFF in the original)
FREE = [(0x0C2800, 0x0E0000), (0x0A8260, 0x0B0000), (0x03CA20, 0x040000), (0x05E040, 0x060000), (0x04BA00, 0x050000)]

# engine (same code as Vol. 4)
LZ_JSL = bytes([0x22, 0x8E, 0x19, 0xC0])                # JSL C0:198E
VWF_TABLE, VWF_BASE_ADD = 0x050000, 0x954
KANJI_LIST = 0x002A57
SJIS_ROWS = 0x002691
METASPRITE_TABLE = 0x0A5A74
PUZZLE_DB, PUZZLE_SIZE_TBL, PUZZLE_BLOCK_TBL = 0x0B0000, 0x0A6BDC, 0x007159
PUZZLE_DB_END = 0x0C271E

TUT_BASE = 0x011682
TUT_NEW_BASE = 0x016000
TUT_ADC_SITE = 0x010B26
C1_BANK_END = 0x020000
FEATURE_PTRS = None                                # no Special-mode landmark notes
PRIZE_PTRS = (0x01442E, 5)
SAVE_WARN_PEA = [(0, 0x4058), (1, 0x40B7)]

HELP_BLOB = 0x027C2D
CLEAR_STAMP_CHR = 0x02594A
GFX_LAYERS = {
    'menu_bg2': (0x029104, 0x02594A, 4),
    'title_bg1': (0x023D3B, 0x020C6B, 4),
    'cert_bg1': (0x049DAB, 0x044D6C, 4, 0x000),
    'cert_bg1b': (0x049DAB, 0x044D6C, 4, 0x800),
    'bonus_bg2a': (0x04A41B, 0x044D6C, 4, 0x000),
    'footer_bg2': (0x04A41B, 0x044D6C, 4, 0x800),
    'prize_bg1': (0x0443FC, 0x042C13, 4),
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
}

CERT_CHR = 0x044D6C
CERT_MAPS = {'full': 0x049DAB, 'template': 0x04A929}
CERT_OTHER = [(0x049DAB, 0x800), (0x04A41B, 0x000), (0x04A41B, 0x800)]
CERT_BLANK = 0x0BF
CREDIT_FONT_BLOB = 0x047674
CREDIT_TABLE = 0x04B148
CREDIT_ATTR = {'T': 1, 'N': 5}
CREDIT_CENTRE = 41
RANK_MAP_BLOB = 0x04AD6B
RANK_TABLE = 0x014F94
