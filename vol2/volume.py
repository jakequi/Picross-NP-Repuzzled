"""Picross NP Vol. 2 — addresses and settings for tools/npbuild.py (ROM offsets, HiROM: bank C0 = 0x000000).
Derived with tools/survey.py and by matching Vol. 1's blobs/frames by content (most are identical, relocated)."""

ROM_NAME = 'Picross NP Vol. 2 (Japan) (Rev 1) (NP).sfc'
ROM_CRC32 = 0x1DF8A75C
OUT_NAME = 'Picross NP Vol. 2 (English).sfc'

# free space (0xFF in the original); Vol. 2 uses 0x080000-0x09FFFF itself
FREE = [(0x0C5000, 0x0E0000), (0x0A8200, 0x0B0000), (0x03CA20, 0x040000), (0x05DEC0, 0x060000), (0x04B8E0, 0x050000)]

# engine (same code as Vol. 1 unless noted)
LZ_JSL = bytes([0x22, 0x92, 0x19, 0xC0])
VWF_TABLE, VWF_BASE_ADD = 0x050000, 0x954
KANJI_LIST = 0x002A5B
METASPRITE_TABLE = 0x0A59B0                        # moved
PUZZLE_DB, PUZZLE_SIZE_TBL, PUZZLE_BLOCK_TBL = 0x0B0000, 0x0A6B14, 0x007054
PUZZLE_DB_END = 0x0C4F4C

TUT_BASE = 0x011682
TUT_NEW_BASE = 0x016000
TUT_ADC_SITE = 0x010B26
C1_BANK_END = 0x020000
FEATURE_PTRS = None                                # Vol. 2 has no Special-mode landmark notes
PRIZE_PTRS = (0x014446, 6)
SAVE_WARN_PEA = [(0, 0x3FEA), (1, 0x4049)]

HELP_BLOB = 0x027A73
CLEAR_STAMP_CHR = 0x025719
GFX_LAYERS = {
    'menu_bg2': (0x028F4D, 0x025719, 4),
    'title_bg1': (0x023B04, 0x020C6B, 4),
    'cert_bg1': (0x049CF7, 0x044D3A, 4, 0x000),
    'cert_bg1b': (0x049CF7, 0x044D3A, 4, 0x800),
    'bonus_bg2a': (0x04A367, 0x044D3A, 4, 0x000),
    'footer_bg2': (0x04A367, 0x044D3A, 4, 0x800),
    'prize_bg1': (0x0443EA, 0x042C11, 4),
    'cert_tmpl': (0x04A875, 0x044D3A, 4),   # not edited: its tiles must not be taken by the footer labels
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

CERT_CHR = 0x044D3A
CERT_MAPS = {'full': 0x049CF7, 'template': 0x04A875}
CERT_OTHER = [(0x049CF7, 0x800), (0x04A367, 0x000), (0x04A367, 0x800)]
CERT_BLANK = 0x0BF
CREDIT_FONT_BLOB = 0x047641
CREDIT_TABLE = 0x04B094
CREDIT_ATTR = {'T': 1, 'N': 5}
CREDIT_CENTRE = 41
RANK_MAP_BLOB = 0x04ACB7
RANK_TABLE = 0x014FB6
