"""Picross NP Vol. 1 — addresses and settings for tools/npbuild.py (ROM offsets, HiROM: bank C0 = 0x000000).
Engine addresses can be re-derived with `python tools/survey.py ROM`; see vol1/NOTES.md for what each one is."""

ROM_NAME = 'Picross NP Vol. 1 (Japan) (Rev 1) (NP).sfc'
ROM_CRC32 = 0xE6F29429
OUT_NAME = 'Picross NP Vol. 1 (English).sfc'

# free space (0xFF in the original) used for relocated data, in allocation order
FREE = [(0x080000, 0x0A0000), (0x0C4000, 0x0E0000), (0x04A000, 0x050000)]

# engine
LZ_JSL = bytes([0x22, 0x92, 0x19, 0xC0])          # JSL C0:1992 (LZ decompressor)
VWF_TABLE, VWF_BASE_ADD = 0x050000, 0x954          # glyph pointer table C5:0000 (+0x954)
KANJI_LIST = 0x002A5B
METASPRITE_TABLE = 0x0A5830
PUZZLE_DB, PUZZLE_SIZE_TBL, PUZZLE_BLOCK_TBL = 0x0B0000, 0x0A698C, 0x006F2A
PUZZLE_DB_END = 0x0C39C8                           # end of the last puzzle record

# text engine scripts
TUT_BASE = 0x011682                                # tutorial bytecode (C1:1682)
TUT_NEW_BASE = 0x016000                            # relocated to C1:6000 (free space in bank C1)
TUT_ADC_SITE = 0x010B26                            # ADC #$1682 that also needs repointing
C1_BANK_END = 0x020000
FEATURE_PTRS = (0x013B43, 12)                      # 16-bit pointers to the Special landmark notes
PRIZE_PTRS = (0x014514, 6)                         # (x, y, long ptr) entries for the prize text
SAVE_WARN_PEA = [(0, 0x3FEA), (1, 0x4049)]         # PEA-passed save warning strings

# pre-rendered graphics
HELP_BLOB = 0x0274D2                               # main-menu help lines
CLEAR_STAMP_CHR = 0x025702                         # menu BG2 chr holding the ★クリア stamp
GFX_LAYERS = {
    # name: (tilemap blob, char blob, bpp[, map byte offset for 64-wide maps])
    'menu_bg2': (0x028A51, 0x025702, 4),
    'title_bg1': (0x023AD3, 0x020C6B, 4),
    'cert_bg1': (0x047084, 0x04210B, 4, 0x000),     # bonus certificate (page 1)
    'cert_bg1b': (0x047084, 0x04210B, 4, 0x800),    # right half (not edited; for tile sharing)
    'bonus_bg2a': (0x0476F4, 0x04210B, 4, 0x000),   # not edited; for tile sharing
    'footer_bg2': (0x0476F4, 0x04210B, 4, 0x800),   # credits footer
    'prize_bg1': (0x0417BE, 0x040000, 4),           # prize screen postcard / deadline
    'cert_tmpl': (0x047C02, 0x04210B, 4),   # not edited: its tiles must not be taken by the footer labels
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

# bonus certificate / credits / rank titles
CERT_CHR = 0x04210B
CERT_MAPS = {'full': 0x047084, 'template': 0x047C02}
CERT_OTHER = [(0x047084, 0x800), (0x0476F4, 0x000), (0x0476F4, 0x800)]
CERT_BLANK = 0x0BF
CREDIT_FONT_BLOB = 0x044A0A
CREDIT_TABLE = 0x048421
CREDIT_ATTR = {'T': 1, 'N': 5}
CREDIT_CENTRE = 41
RANK_MAP_BLOB = 0x048044
RANK_TABLE = 0x015084
