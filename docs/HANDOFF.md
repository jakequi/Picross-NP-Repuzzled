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
| Vol. 3 | Complete (release v1.4). Same engine/frames as Vol. 2; addresses mapped with `tools/match_volume.py`. Tutorial identical to Vol. 2; Kirby characters 26–37; Special 86–94 hide the keyword 雲 (cloud), names follow the pictures (X button shows a big illustration, no extra text). Not seen in emulator: credits page 6 (4 names, rows 9/11/14/16).
| Vol. 4–8 | Not started. Recipe: copy `vol3/` → `volN/`, run `tools/survey.py` + `tools/match_volume.py` (old vs new ROM, list of Vol. 3 blob addresses) to fill `volume.py`, diff tutorial/puzzle names with a script, read help/title/credits graphics, build, check, release. |

## Rules learned the hard way
* Small text: always `tools/tinyfont.py` (users flagged mixed fonts as inconsistent).
* In-game sprite tiles 0x180–0x1FF are streamed during puzzles; verify any "free" tile against live VRAM on every
  screen its frame appears on.
* Long-pointer pattern matches are only trusted inside banks C0–C1.
* Never commit ROMs or ROM-derived binaries; screenshots for the README live on the `screenshots` branch.
* Releases: one project-wide version number (v1.1, v1.2, …). Every release contains the current `.bps` of every
  finished volume, and nothing else. Patch file names carry no version: `Picross_NP_VolN_English.bps` (underscores, RHDN-style).
* Frames from different sprite sheets share tile numbers: exclude other-sheet frames (`NOT_GAME_FRAMES`) when
  counting tile users, and only reclaim tiles of entries actually removed from a frame.
