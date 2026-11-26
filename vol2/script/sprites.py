# -*- coding: utf-8 -*-
"""Sprite text for Picross NP Vol. 2.

Vol. 2 reuses Vol. 1's sprite graphics and metasprite frames unchanged except for two inserted frames
(125: Versus round picker, 319: in-game 'Ready?' window). So this file loads Vol. 1's spec, renumbers its frames,
points it at Vol. 2's sheet blobs, and adds the two new frames.
"""
import importlib.util, os

_spec = importlib.util.spec_from_file_location(
    'vol1_sprites', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'vol1', 'script', 'sprites.py'))
_v1 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v1)
globals().update({k: v for k, v in vars(_v1).items() if not k.startswith('_')})


def remap(f):
    """Vol. 1 frame number -> Vol. 2 (frames 125 and 319 are new in Vol. 2)."""
    return f if f < 125 else f + 1 if f < 318 else f + 2


# sheet blobs in Vol. 2 (same contents as Vol. 1's, relocated; the menu sheet gained tiles 0x100-0x17F)
GAME_SHEET = 0x035C4A
BADGE_BLOB = 0x0374BB
MENU_SHEET = 0x026688
PSEL_SHEET = 0x02CACC
BONUS_SHEET = 0x048EE9

FRAMES = {remap(f): v for f, v in _v1.FRAMES.items()}
TUTORIAL_FRAMES = tuple(remap(f) for f in _v1.TUTORIAL_FRAMES)
PSEL_LABELS = {remap(f): t for f, t in _v1.PSEL_LABELS.items()}
SEALS = {remap(f): t for f, t in _v1.SEALS.items()}
CERT_BADGES = {remap(f): t for f, t in _v1.CERT_BADGES.items()}
MODE_LABELS = {remap(f): t for f, t in _v1.MODE_LABELS.items()}
PANELS = [(tuple(remap(f) for f in fs), lines) for fs, lines in _v1.PANELS]
MENU_FRAMES = [remap(f) for f in _v1.MENU_FRAMES] + [125]
MENU_FREE = list(range(0x0F0, 0x0FC)) + list(range(0x160, 0x180)) + list(range(0x154, 0x160)) + list(range(0x144, 0x150))
NOT_GAME_FRAMES = (125,)   # menu-sheet frame whose tile numbers overlap the game sheet's window text

# new in Vol. 2: in-game "Ready?" window (Ready? / スタート / ヒントをつかう / キャンセル); "Ready?" is kept
FRAMES[319] = ([11, 21, 31], [dict(y=11, text='START', pal=3, x=-21),
                              dict(y=21, text='USE A HINT', pal=3, x=-21),
                              dict(y=31, text='CANCEL', pal=3, x=-21)])

# new in Vol. 2: Versus round picker, text baked into 16x16 panel tiles (painted like the data panels).
# boxes: ((x0, y0, x1, y1), colour) cleared first (frame coords, x1/y1 exclusive).
# lines: (top y of a 7px row, text, fill, outline, bg, x0, x1, align) - caps occupy rows top+1..top+5.
# 'HOW MANY ROUNDS?' does not fit the 62px interior, and the options answer 'HOW MANY?'.
CUSTOM_PANELS = [
    dict(frames=(125,), boxes=[((1, -2, 63, 7), 9), ((1, 9, 63, 62), 0xE)],
         lines=[(-1, 'VERSUS', 0xE, 0xA, 9, 1, 63, 'center'),
                (10, 'HOW MANY?', 1, 0xF, 0xE, 1, 63, 'center'),
                (23, '1 ROUND', 1, 7, 0xE, 12, 62, 'left'),
                (33, '2 ROUNDS', 1, 7, 0xE, 12, 62, 'left'),
                (43, '3 ROUNDS', 1, 7, 0xE, 12, 62, 'left'),
                (53, 'CANCEL', 1, 7, 0xE, 12, 62, 'left')]),
]
