# Picross NP Repuzzled

English translations of the eight **Picross NP** (Nintendo Power) Super Famicom games, built with an
open-source, AI-assisted toolchain. Each volume is a patch for the original Japanese ROM; no ROM data is
included in this repository.

| Volume | Status | Patch |
|---|---|---|
| Picross NP Vol. 1 | ✅ Complete | [`patches/Picross NP Vol. 1 (English).bps`](patches/) |
| Picross NP Vol. 2 | Planned | — |
| Picross NP Vol. 3 | Planned | — |
| Picross NP Vol. 4 | Planned | — |
| Picross NP Vol. 5 | Planned | — |
| Picross NP Vol. 6 | Planned | — |
| Picross NP Vol. 7 | Planned | — |
| Picross NP Vol. 8 | Planned | — |

## Screenshots (Vol. 1)

<table>
<tr>
<td><img src="https://github.com/jakequi/Picross-NP-Repuzzled/releases/download/v1.1/screenshot-0-title.png" width="384" alt="Title screen"></td>
<td><img src="https://github.com/jakequi/Picross-NP-Repuzzled/releases/download/v1.1/screenshot-1-main-menu.png" width="384" alt="Main menu"></td>
</tr>
<tr>
<td><img src="https://github.com/jakequi/Picross-NP-Repuzzled/releases/download/v1.1/screenshot-2-tutorial.png" width="384" alt="How to Play tutorial"></td>
<td><img src="https://github.com/jakequi/Picross-NP-Repuzzled/releases/download/v1.1/screenshot-3-in-game.png" width="384" alt="In-game hint window"></td>
</tr>
<tr>
<td><img src="https://github.com/jakequi/Picross-NP-Repuzzled/releases/download/v1.1/screenshot-5-puzzle-clear.png" width="384" alt="Puzzle clear"></td>
<td><img src="https://github.com/jakequi/Picross-NP-Repuzzled/releases/download/v1.1/screenshot-4-special-landmark.png" width="384" alt="Special mode landmark description"></td>
</tr>
</table>

## Applying a patch

Use any BPS patcher (e.g. [Floating IPS](https://www.smwcentral.net/?p=section&a=details&id=11474),
[Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/), or `python tools/bps.py apply ROM PATCH OUT`).

**Vol. 1** — source ROM (No-Intro): `Picross NP Vol. 1 (Japan) (Rev 1) (NP).sfc`
* size 1,048,576 bytes, no copier header
* CRC32 `E6F29429`, SHA-1 `75b2b639e73775f1709059a8b1b63f61983de0e8`
* patched result: CRC32 `D611A49A`, SHA-1 `7192728bbd1aa7bdc3757feddf85d268ee4daafe`

## What's translated (Vol. 1)

Everything Japanese in the game, verified screen by screen in an emulator:

* Title tagline, save-file panels (New Game / Continue / Copy / Erase), main menu, help lines, CLEAR stamps, menu tabs
* All 122 puzzle names (checked against each puzzle's solution picture), puzzle-select and in-game mode labels
* In-game windows: hint prompt, pause menu, Give Up / Save / BGM / Stereo / ? Start / Confirm, "Saved!"
* The complete How to Play tutorial (Basic Rules, Handy Features, ? Start, 2-Player, Versus)
* Special (特集) landmark descriptions, the prize-contest screen (address card, deadline, rules)
* Bonus certificate (text, rank titles, seals), staff credits, "more volumes coming" footer
* Save-data warning messages

The stylised ピクロス logo artwork is left as is.

## Building from source

Requirements: Python 3.10+, `pip install pillow numpy`, and the fonts Arial Bold, Arial Narrow Bold and
Verdana Bold (standard on Windows; elsewhere set `PICROSS_FONT_DIR`).

```
python vol1/build.py "path/to/Picross NP Vol. 1 (Japan) (Rev 1) (NP).sfc"
```

Output goes to `vol1/out/` (`.sfc`, `.bps`, `.ips`). Translations live in plain-text tables in `vol1/script/`
(`*.tsv`: id, Japanese, English) — edit them and rebuild. The build warns if a line is too wide for its box.

## Repository layout

| Path | Contents |
|---|---|
| `tools/` | Shared engine tools: LZ codec, variable-width font, metasprites, tile/label renderers, BPS, emulator driver, auto-solver, save generator, disassembler |
| `vol1/` | Vol. 1 build script, translation tables, technical notes (`NOTES.md`) |
| `docs/METHOD.md` | Step-by-step method for translating the other volumes with these tools |
| `patches/` | Released patches |

## Credits

* Translation and hacking: jakequi, AI-assisted (Claude)
* Original game: Nintendo / Jupiter, 1995–1999; Pokémon puzzles © Nintendo / Creatures / GAME FREAK

This is an unofficial fan translation, not affiliated with or endorsed by Nintendo.

## License

The tools, build scripts and translation tables are released under the MIT License (see `LICENSE`).
