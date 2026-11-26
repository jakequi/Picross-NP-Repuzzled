# -*- coding: utf-8 -*-
"""Sprite text for Picross NP Vol. 1 (data consumed by build.py: sprite_text()).

In-game sprite sheet: blob C3:585E (tiles 0x000-0x1FF at OBJ VRAM C000).
Window frames are metasprites (see tools/metasprite.py); window parts are kept, text replaced.
"""

GAME_SHEET = 0x03585E
# Blank tiles in the in-game sheet that are never overwritten during play (checked against VRAM in a live
# puzzle). Rows 0x180-0x1FF are streamed over during puzzles, so only the tutorial menu may use 0x1A0+.
GAME_FREE = list(range(0x0B0, 0x0E0))
TUTORIAL_FREE = list(range(0x1A0, 0x200))
TUTORIAL_FRAMES = (137, 156)

# Pause panel: 8px rows of 10 tiles baked into 16x16 sprites (white panel, text left at px 8).
# (first tile, pixel x0, x1, English)
PAUSE_ROWS = [
    (0x100, 1, 70, 'GIVE UP'),   # ギブアップ
    (0x110, 1, 70, 'SAVE'),      # セーブ
    (0x130, 1, 70, 'STEREO'),    # ステレオ
    (0x140, 1, 52, 'HINT'),      # ヒント (keeps the blue -5)
]

# Window tiles (PICROSS header, frame, pen, shadow, '?' icon) are never removed.
WINDOW_TILES = {0x0F9, 0x0F8, 0x0E8, 0x075, 0x055, 0x13E, 0x13F, 0x14A,
                0x16C, 0x16D, 0x16E, 0x16F}   # 1 2 3 4 digits in the BGM window

PROMPT, OPTION = 2, 3   # palettes: orange prompt / blue options
CX = 8                  # window centre x

# frame -> (lines to remove (y values, or None = all small non-window entries), new lines)
FRAMES = {
    301: (None, [dict(y=-1, text='USE A HINT?', pal=PROMPT, cx=CX), dict(y=15, text='YES', pal=OPTION, cx=CX), dict(y=31, text='NO', pal=OPTION, cx=CX)]),
    303: (None, [dict(y=-1, text='GIVE UP?', pal=PROMPT, cx=CX), dict(y=15, text='YES', pal=OPTION, cx=CX), dict(y=31, text='NO', pal=OPTION, cx=CX)]),
    304: (None, [dict(y=-1, text='SAVE?', pal=PROMPT, cx=CX), dict(y=15, text='YES', pal=OPTION, cx=CX), dict(y=31, text='NO', pal=OPTION, cx=CX)]),
    305: ([31], [dict(y=31, text='OFF', pal=OPTION, cx=CX)]),
    306: (None, [dict(y=-1, text='STEREO?', pal=PROMPT, cx=CX), dict(y=15, text='ON', pal=OPTION, cx=CX), dict(y=31, text='OFF', pal=OPTION, cx=CX)]),
    307: ([31], [dict(y=31, text='START', pal=OPTION, x=-16)]),
    308: ([23], [dict(y=23, text='END', pal=OPTION, x=-16)]),
    309: (None, [dict(y=-1, text='CONFIRM?', pal=PROMPT, cx=CX), dict(y=11, text='YES', pal=OPTION, x=-8),
                dict(y=21, text='NO', pal=OPTION, x=-8), dict(y=31, text='CANCEL', pal=OPTION, x=-8)]),
    314: (None, [dict(y=12, text='SAVED!', pal=OPTION, cx=CX)]),
    317: (None, [dict(y=-1, text='? START?', pal=PROMPT, cx=CX), dict(y=15, text='YES', pal=OPTION, cx=CX), dict(y=31, text='NO', pal=OPTION, cx=CX)]),
}

# How-to-play chapter menu (built from single kana tiles; transparent background).
_T = dict(bg=0)
_TUT = [dict(y=3, text='BASIC RULES', pal=3, x=-24, style=_T),
        dict(y=15, text='HANDY FEATURES', pal=3, x=-24, style=_T),
        dict(y=27, text='? START', pal=2, x=-24, style=_T),
        dict(y=39, text='2-PLAYER', pal=3, x=-24, style=_T),
        dict(y=51, text='VERSUS', pal=3, x=-24, style=_T)]
FRAMES[137] = (None, _TUT)
FRAMES[156] = (None, _TUT)

# Mode badges under the clock: blob C3:7028, 8 labels of 64x16 (8 tiles over 8 tiles).
BADGE_BLOB = 0x037028
BADGES = ['HOW TO PLAY', 'VERSUS', 'BEGINNER', 'CHARACTER', 'REGULAR', 'SPECIAL', 'PROFESSIONAL', 'EXTRA']

# --- menu sprite sheet (blob C2:6612, data select + puzzle select) ---
MENU_SHEET = 0x026612
MENU_FRAMES = range(88, 113)           # frames drawn with this sheet (scope for tile sharing)
MENU_FREE = list(range(0x0EC, 0x100))  # blank tiles
# Data panels: interior cleared, lines centred. (frames, [(centre_y, text)])
PANELS = [
    ((92, 96), [(26, 'NEW GAME')]),
    ((93, 97), [(14, 'CONTINUE'), (26, 'COPY'), (38, 'ERASE')]),
    ((95, 99), [(14, 'IS THIS OK?'), (26, 'YES'), (38, 'NO')]),
]
PANEL_BOX = (1, 9, 46, 45)             # x0, y0, x1, y1 (frame coords) cleared to background
PANEL_STYLE = dict(fill=0xB, outline=0x4, bg=0xE)
# Puzzle-select mode labels (frames 102-107): replaced by one-row labels drawn in reclaimed tiles.
MODE_LABELS = {102: 'BEGINNER', 103: 'CHARACTER', 104: 'REGULAR', 105: 'SPECIAL', 106: 'PROFESSIONAL', 107: 'EXTRA'}
MODE_LABEL_TILES = list(range(0x0A0, 0x0D0))   # old label art, used only by frames 102-107

# --- puzzle-select sheet (blob C2:C7A4, OBJ base 0x8000): mode label frames 174-181 ---
PSEL_SHEET = 0x02C7A4
PSEL_FREE = [0x9D, 0x9E, 0x9F] + list(range(0xDC, 0x100))
PSEL_LABELS = {174: 'HOW TO PLAY', 175: 'VERSUS', 176: 'BEGINNER', 177: 'CHARACTER', 178: 'REGULAR',
               179: 'SPECIAL', 180: 'PROFESSIONAL', 181: 'EXTRA'}
PSEL_LABEL_STYLE = dict(text_col=3, aa_col=4, fill=2, border=1)

# --- bonus certificate sheet (blob C4:6276, OBJ base 0xC000) ---
BONUS_SHEET = 0x046276
BONUS_FREE = list(range(0x0C0, 0x100))
SEAL_TEMPLATE = list(range(0x68, 0x74))        # 3x4 tiles of the よくできました seal (border reused)
SEALS = {583: 'GREAT\n!!', 584: 'VERY\nWELL\nDONE', 585: 'WELL\nDONE'}   # すばらしい!! / たいへんよくできました / よくできました
CERT_BADGES = {586: 'BEGINNER', 587: 'CHARACTER', 588: 'REGULAR', 589: 'SPECIAL', 590: 'PROFESSIONAL'}

# "それいじょうおぼえられません!" banner (frame 313): strip tiles 0x90-0x9F over 0xA0-0xAF in the game sheet.
# Tile 0x90/0xA0 (left cap, reused as right cap) is kept; pixels 8..127 of rows 3..12 are repainted.
BANNER = dict(t0=0x90, x0=8, x1=127, y0=3, y1=13, text="Can't remember any more!", fill=0xA, bg=0xD)
