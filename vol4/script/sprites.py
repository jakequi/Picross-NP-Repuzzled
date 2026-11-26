# -*- coding: utf-8 -*-
"""Sprite text for Picross NP Vol. 4: Vol. 3's spec with one inserted frame (320, a 'Confirm? / Yes / No' window),
so Vol. 3 frames >= 320 move up by one. Sheets relocated (contents identical)."""
import importlib.util, os

_spec = importlib.util.spec_from_file_location(
    'vol3_sprites', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'vol3', 'script', 'sprites.py'))
_v3 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v3)
globals().update({k: v for k, v in vars(_v3).items() if not k.startswith('_')})


def remap4(f):
    return f + 1 if f >= 320 else f


MENU_SHEET = 0x02692F
PSEL_SHEET = 0x02CD26
BONUS_SHEET = 0x048F3B

FRAMES = {remap4(f): v for f, v in _v3.FRAMES.items()}
TUTORIAL_FRAMES = tuple(remap4(f) for f in _v3.TUTORIAL_FRAMES)
PSEL_LABELS = {remap4(f): t for f, t in _v3.PSEL_LABELS.items()}
SEALS = {remap4(f): t for f, t in _v3.SEALS.items()}
CERT_BADGES = {remap4(f): t for f, t in _v3.CERT_BADGES.items()}
MODE_LABELS = {remap4(f): t for f, t in _v3.MODE_LABELS.items()}
PANELS = [(tuple(remap4(f) for f in fs), lines) for fs, lines in _v3.PANELS]
MENU_FRAMES = [remap4(f) for f in _v3.MENU_FRAMES]
CUSTOM_PANELS = [dict(p, frames=tuple(remap4(f) for f in p['frames'])) for p in _v3.CUSTOM_PANELS]
NOT_GAME_FRAMES = tuple(remap4(f) for f in _v3.NOT_GAME_FRAMES)

# new in Vol. 4: 決定しますか? / はい / いいえ
FRAMES[320] = (None, [dict(y=-1, text='CONFIRM?', pal=PROMPT, cx=CX),
                      dict(y=11, text='YES', pal=OPTION, x=-8),
                      dict(y=23, text='NO', pal=OPTION, x=-8)])
