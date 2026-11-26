"""Machine-specific settings, overridable with environment variables.

PICROSS_FONT_DIR  folder containing the TrueType fonts used to draw English text
                  (arialbd.ttf, ARIALNB.TTF, verdanab.ttf; default: the Windows font folder)
MESEN             path to Mesen.exe (Mesen 2.x) for the emulator-driven tools (testing only)
"""
import os

FONT_DIR = os.environ.get('PICROSS_FONT_DIR', os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts'))
MESEN = os.environ.get('MESEN', 'Mesen.exe')
