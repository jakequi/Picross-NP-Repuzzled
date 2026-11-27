# -*- coding: utf-8 -*-
"""Sprite text for Picross NP Vol. 6 (the "2000 renewal" look; Vols. 7-8 share it).

Frames are Vol. 5's, renumbered by aligning the two metasprite tables by content: the menu block (26-125) was
redrawn and shrank, 8 frames were added after 302 and 28 after 408. The Versus picker became two panels
(117: how many rounds, 118: battle type). Sheets relocated; free tiles re-measured (the menu sheet has far fewer).
"""
import importlib.util, os

_spec = importlib.util.spec_from_file_location(
    'vol5_sprites', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'vol5', 'script', 'sprites.py'))
_v5 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v5)
globals().update({k: v for k, v in vars(_v5).items() if not k.startswith('_')})

# Vol. 5 frame -> Vol. 6 frame, for the frames the spec uses
_MAP = {138: 131, 157: 150,                                       # tutorial chapter menu
        302: 303, 304: 305, 305: 306, 306: 307, 307: 308, 308: 309, 309: 310, 310: 311, 315: 316,
        318: 319, 319: 320, 320: 321,                             # in-game windows
        175: 168, 176: 169, 177: 170, 178: 171, 179: 172, 180: 173, 181: 174, 182: 175,   # puzzle-select labels
        586: 615, 587: 616, 588: 617, 589: 618, 590: 619, 591: 620, 592: 621, 593: 622,   # seals, badges
        102: 90, 103: 91, 104: 92, 105: 93, 106: 94, 107: 95,     # menu mode labels
        92: 80, 93: 81, 95: 83, 96: 84, 97: 85, 99: 87}           # data-select panels


def remap6(f):
    return _MAP[f]


GAME_SHEET = 0x033DFB
BADGE_BLOB = 0x035671
MENU_SHEET = 0x02686F
PSEL_SHEET = 0x02B72A
BONUS_SHEET = 0x04A11A

FRAMES = {remap6(f): v for f, v in _v5.FRAMES.items()}
TUTORIAL_FRAMES = tuple(remap6(f) for f in _v5.TUTORIAL_FRAMES)
PSEL_LABELS = {remap6(f): t for f, t in _v5.PSEL_LABELS.items()}
SEALS = {remap6(f): t for f, t in _v5.SEALS.items()}
CERT_BADGES = {remap6(f): t for f, t in _v5.CERT_BADGES.items()}
MODE_LABELS = {remap6(f): t for f, t in _v5.MODE_LABELS.items()}
PANELS = [(tuple(remap6(f) for f in fs), lines) for fs, lines in _v5.PANELS]
MENU_FRAMES = list(range(26, 126))          # every menu-sheet frame (conservative tile-sharing checks)
NOT_GAME_FRAMES = (117, 118)                 # menu-sheet frames whose tile numbers overlap the game sheet's
NON_PRO_FRAMES = tuple(remap6(f) for f in _v5.NON_PRO_FRAMES)   # hint prompt + Ready? window (issue #4)
RECLAIM_MODE_LABELS_FIRST = True

# blank tiles measured in the Vol. 6 sheets
MENU_FREE = list(range(0x0F4, 0x0FC)) + list(range(0x16A, 0x170)) + list(range(0x17A, 0x180))
PSEL_FREE = list(range(0x0DC, 0x100))
MODE_LABEL_TILES = list(range(0x0A0, 0x0CD)) + list(range(0x0D0, 0x0DC)) + [0x0EA, 0x0EB]

_V = _v5.CUSTOM_PANELS[0]
_BOXES = _V['boxes']
CUSTOM_PANELS = [
    dict(frames=(117,), group=(117, 118), boxes=_BOXES, lines=_V['lines']),   # 118 then copies only differing tiles
    # 対戦 / どんなたいせん? / ろんりてき / ちょっとカン / かなりカン / キャンセル
    dict(frames=(118,), boxes=_BOXES,
         lines=[(-1, 'VERSUS', 0xE, 0xA, 9, 1, 63, 'center'),
                (10, 'WHICH TYPE?', 1, 0xF, 0xE, 1, 63, 'center'),
                (23, 'LOGIC', 1, 7, 0xE, 12, 62, 'left'),
                (33, 'HUNCH', 1, 7, 0xE, 12, 62, 'left'),
                (43, 'BIG HUNCH', 1, 7, 0xE, 12, 62, 'left'),
                (53, 'CANCEL', 1, 7, 0xE, 12, 62, 'left')]),
]
