# -*- coding: utf-8 -*-
"""Sprite text for Picross NP Vol. 8: Vol. 6's spec (identical frames and sheet contents),
sheet blobs relocated."""
import importlib.util, os

_spec = importlib.util.spec_from_file_location(
    'vol6_sprites', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'vol6', 'script', 'sprites.py'))
_v6 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v6)
globals().update({k: v for k, v in vars(_v6).items() if not k.startswith('_')})

MENU_SHEET = 0x0269C7
PSEL_SHEET = 0x02B59D
BONUS_SHEET = 0x04A082
