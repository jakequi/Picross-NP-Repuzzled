# -*- coding: utf-8 -*-
"""Sprite text for Picross NP Vol. 5: same metasprite frames as Vol. 4 (table at the same address),
sheet blobs relocated (contents checked blank where the spec expects free tiles)."""
import importlib.util, os

_spec = importlib.util.spec_from_file_location(
    'vol4_sprites', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'vol4', 'script', 'sprites.py'))
_v4 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v4)
globals().update({k: v for k, v in vars(_v4).items() if not k.startswith('_')})

GAME_SHEET = 0x035C4A
BADGE_BLOB = 0x0374BB
MENU_SHEET = 0x0268C2
PSEL_SHEET = 0x02C961
BONUS_SHEET = 0x048F9D
