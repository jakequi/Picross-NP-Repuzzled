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
| Vol. 1 | Released v1.1 (issues #1, #2 fixed). Build is byte-identical through `npbuild.py`. |
| Vol. 2 | In progress. ROM: CRC32 `1DF8A75C`. Survey: same engine; moved: metasprite table `0A59B0`, size table `0A6B14`, credit pages `04B094`. 42 of Vol. 1's 54 blobs are identical (relocated); changed: title, help lines, menu sheet, credits/cert fonts, prize screen. |
| Vol. 3–8 | Not started. |

## Rules learned the hard way
* Small text: always `tools/tinyfont.py` (users flagged mixed fonts as inconsistent).
* In-game sprite tiles 0x180–0x1FF are streamed during puzzles; verify any "free" tile against live VRAM on every
  screen its frame appears on.
* Long-pointer pattern matches are only trusted inside banks C0–C1.
* Never commit ROMs or ROM-derived binaries; screenshots for the README live on the `screenshots` branch.
* Releases: GitHub release per volume version with the `.bps` only.
