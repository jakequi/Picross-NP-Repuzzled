# Handoff — current state of the project

Read this first when resuming on a new machine or in a new session.

## Setup on a new PC
1. Python 3.10+, `pip install pillow numpy`; fonts Arial Bold, Arial Narrow Bold, Verdana Bold (Windows has them;
   elsewhere set `PICROSS_FONT_DIR`).
2. Clone this repo. Put each ROM in its volume folder (ROMs are git-ignored):
   `vol1/Picross NP Vol. 1 (Japan) (Rev 1) (NP).sfc`, `vol2/Picross NP Vol. 2 (Japan) (Rev 1) (NP).sfc`, …
3. For testing: download Mesen 2 (https://github.com/SourMesen/Mesen2/releases) and `set MESEN=C:\path\Mesen.exe`.
   The emulator tools (`tools/drive.py`, `explore.py`, `autosolve.lua`, `savegen.py`) run it headless.
4. Build a volume: `python volN/build.py` → `volN/out/*.sfc/.bps` (BPS is self-verified).

## Architecture
* `tools/npbuild.py` — the shared build (all stages). It reads `volN/volume.py` (addresses) and `volN/script/*`
  (translations + sprite specs). `volN/build.py` is a 3-line wrapper.
* `tools/survey.py ROM` finds engine addresses by code signature — start every new volume with it.
* `docs/METHOD.md` — step-by-step method; `vol1/NOTES.md` — engine formats and Vol. 1 addresses.

## Status
| Volume | State |
|---|---|
| Vol. 1 | Complete (latest release v1.3: all 30 certificate titles translated, Poké Doll). |
| Vol. 2 | Complete (first in v1.2; v1.3 adds the 30 certificate titles, Rotary Phone, Baby Bowser). `vol2/script/sprites.py` loads Vol. 1's spec and renumbers frames (<125 same, 125–317 +1, ≥318 +2); new frames 319 (Ready? window) and 125 (Versus round picker, `CUSTOM_PANELS`). All screens checked in Mesen. |
| Vol. 3 | Complete (release v1.4). Same engine/frames as Vol. 2; addresses mapped with `tools/match_volume.py`. Tutorial identical to Vol. 2; Kirby characters 26–37; Special 86–94 hide the keyword 雲 (cloud), names follow the pictures (X button shows a big illustration, no extra text). Certificate and credits page 6 (4 names) checked OK in Mesen. |
| Vol. 4 | Complete (release v1.5). C0 code shifted -4 vs Vol. 3 (LZ_JSL C0:198E, SJIS_ROWS 0x2691, SAVE_WARN_PEA 0x4050/0x40AF); frames >=320 +1 with new frame 320 (Confirm?/Yes/No); Star Fox 64 cast 26-37; Special 86-97 = Tale of Genji theme; prize deadline label needed `EXTRA_FREE` (unreferenced old digit tiles). Checked in Mesen: title, menu, tutorial menu, puzzle select, Ready? window, pause, prize, save-corrupt warning. Certificate, credits and all pause windows also checked OK. Vol. 4 save slot is shifted +2: best times at +0x29F+2*puzzle, checksum at +0x39F (sum over 0x0B..0x39E) — `tools/savegen.py` still uses the Vol. 1–3 offsets, so patch it (or build the save by hand) when testing Vol. 4+. Frame 320 not located on screen. |
| Vol. 5 | Complete (not yet released). Same engine/frames as Vol. 4 (`vol5/script/sprites.py` loads Vol. 4's spec, only sheet addresses change); C0/C1 code identical to Vol. 4 except tables found by data search (puzzle block table 0x7159, rank table 0x14F94, prize table 0x1442E with 5 entries, save-warning PEAs 0x4058/0x40B7); C4 blobs +0x62 vs Vol. 4, verified identical by content. Zelda: Ocarina of Time cast 26-37; Special 86-97 = constellation theme. Prize card sits one tile further left than Vol. 4's and the deadline is 3 lines (平成12年); labels may now reuse tiles freed by earlier labels (`npbuild.graphic_labels`), with the deadline processed first. Credits identical to Vol. 4. Save layout = Vol. 4's (slot size 0x3A2, times +0x29F, checksum +0x39F). Checked in Mesen: title, menu + all help lines, Versus picker, tutorial, puzzle select, Ready?/pause/Give Up/Save/BGM/Stereo windows, Regular/Character/Special clears, prize, certificate, credits + footer. |
| Vol. 6–8 | Not started. 1.5 MB ROMs, 242 puzzles each; survey output differs more (metasprite table ~0x0A549x, tutorial base 0x0116E2, VWF base add 0x960). |

## Testing notes
* Rebuilding Vols. 1–4 from this repo reproduces the released patches byte for byte (checked 2026-11-26).
* `tools/autosolve.lua` uses Vol. 1 RAM addresses and does not work on Vol. 3+. A pad-driven solver that finds the
  grid in RAM (cells 0x26/0x27 from 7E:7600, stride 0x24) and presses d-pad/A (3 frames on, 9 off) works on Vols. 3–5.

## Rules learned the hard way
* Small text: always `tools/tinyfont.py` (users flagged mixed fonts as inconsistent).
* In-game sprite tiles 0x180–0x1FF are streamed during puzzles; verify any "free" tile against live VRAM on every
  screen its frame appears on.
* Issue #4 (fixed in v1.6.1): Professional/Extra (clock, "Go!!"/"Ready") overwrite game-sheet tiles 0xB0-0xBF, and Versus
  overwrites them too. Window text now comes from reclaimed old text tiles + 0xC0-0xDF; only windows those modes never
  show (`NON_PRO_FRAMES`: hint prompt, Ready? window) may use 0xB0-0xBF, and the build asserts this. Test new window
  text in Beginner, Professional, Extra and Versus, not just Regular.
* Long-pointer pattern matches are only trusted inside banks C0–C1.
* Never commit ROMs or ROM-derived binaries; screenshots for the README live on the `screenshots` branch.
* Releases: one project-wide version number (v1.1, v1.2, …). Every release contains the current `.bps` of every
  finished volume, and nothing else. Patch file names carry no version: `Picross_NP_VolN_English.bps` (underscores, RHDN-style).
* Frames from different sprite sheets share tile numbers: exclude other-sheet frames (`NOT_GAME_FRAMES`) when
  counting tile users, and only reclaim tiles of entries actually removed from a frame.
