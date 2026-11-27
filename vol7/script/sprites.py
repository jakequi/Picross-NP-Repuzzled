# -*- coding: utf-8 -*-
"""Sprite text for Picross NP Vol. 7: Vol. 6's spec (identical frames and sheet contents),
sheet blobs relocated."""
import importlib.util, os

_spec = importlib.util.spec_from_file_location(
    'vol6_sprites', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'vol6', 'script', 'sprites.py'))
_v6 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v6)
globals().update({k: v for k, v in vars(_v6).items() if not k.startswith('_')})

MENU_SHEET = 0x026C77
PSEL_SHEET = 0x02BA61
BONUS_SHEET = 0x04A068
