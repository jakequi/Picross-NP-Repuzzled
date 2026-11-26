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
| Vol. 2 | In progress (WIP pushed). ROM CRC32 `1DF8A75C`. Done: `vol2/volume.py` (all addresses), `script/tutorial.tsv` (94/97 lines reused from Vol. 1, 3 new translated), `script/puzzle_names.tsv` (all 122, checked against pictures). To do: copy/adapt the remaining `vol1/script` files (help lines differ: blob 027A73; prize text deadline is 7/10; labels/title tagline line 2 is new 第二弾登場!; credits may differ), `script/sprites.py` with frames remapped (+1 from ~110, +2 from 583; sheets: game 035C4A, badges 0374BB, menu 026688, psel 02CACC, bonus 048EE9) and two NEW frames: 319 = in-game 'Ready? / Start / Use a hint / Cancel', 125 = Versus round picker (Versus / How many rounds? / 1-3 rounds / Cancel). Then build, screenshot-check every screen, release v1.0. |
| Vol. 3–8 | Not started. |

## Rules learned the hard way
* Small text: always `tools/tinyfont.py` (users flagged mixed fonts as inconsistent).
* In-game sprite tiles 0x180–0x1FF are streamed during puzzles; verify any "free" tile against live VRAM on every
  screen its frame appears on.
* Long-pointer pattern matches are only trusted inside banks C0–C1.
* Never commit ROMs or ROM-derived binaries; screenshots for the README live on the `screenshots` branch.
* Releases: GitHub release per volume version with the `.bps` only.
