# Picross NP Vol. 1 — technical notes

ROM: `Picross NP Vol. 1 (Japan) (Rev 1) (NP).sfc`, HiROM, 1 MiB, CRC32 `E6F29429`, SHA-1 `75b2b639e73775f1709059a8b1b63f61983de0e8`.
ROM offset = `(bank & 0x3F) << 16 | addr` (e.g. `C2:74D2` → `0x0274D2`).

Free space used by the build (0xFF in the original): `0x016000-0x01FFFF` (bank C1, tutorial + C1 strings),
`0x04A000-0x04FFFF` (bank C4, credit pages), `0x080000-0x09FFFF`, `0x0C4000-0x0DFFFF`.

## Text systems

| System | Where | How it's translated |
|---|---|---|
| **LZ-compressed graphics** (tiles + tilemaps) | decompressor `C0:1992` | `tools/lz.py` codec; build re-renders, recompresses, repoints PEA call sites |
| **Shift-JIS variable-width text** | renderer `C0:261C`, lookup `C0:2646`, font table `C5:0000` (+0x954) | English glyphs drawn into the full-width Latin/punctuation slots; text encoded as full-width SJIS (`tools/vwf_en.py`) |
| **Metasprites** (sprite text) | table `CA:5830`, drawer `C0:110E` | frames rewritten / tiles repainted (`tools/metasprite.py`, `tools/spritetext.py`) |
| **Tilemap-row records** (credits) | table `C4:8421`, copier `C1:53B6` | rebuilt with an 8x16 glyph font (`tools/credits.py`, `tools/glyphfont.py`) |

### LZ codec (`C0:1992`)
Args: PEA dst bank, PEA dst addr, PEA src bank, PEA src addr; `A` = length (0 → u16 header). Header is always skipped.
Flag byte LSB-first: 1 = literal, 0 = u16 `w`: copy `(w & 0xF) + 3` bytes from ring position `w >> 4`.
4 KB ring at `7F:0000`, write position starts at 0. Destinations: `7F:1000` tiles, `7E:4000-6800` tilemaps, `00:0785` palettes.
**Gotcha:** only trust 4-byte long-pointer matches inside banks C0–C1; elsewhere `xx xx C4 00` patterns are coincidental data
(a false match for blob `C4:0000` corrupted a VWF glyph pointer and crashed the Special clear screen).

### Variable-width font
Glyph = width, height, then per row `ceil(w/8)` × (plane0, plane1). The text layer is **hi-res** (512 px): glyphs are drawn
at 2× horizontal resolution; the engine advances `width + 2`. Kanji are looked up linearly in `C0:2A5B` (index + 0x10C + 0x9C).

### Script / string locations
| Data | Location | Notes |
|---|---|---|
| Tutorial bytecode | `C1:1682` (6 section offsets) → moved to `C1:6000` | `tools/tutorial.py` has every command's argument size; 34 refs to the base patched |
| Puzzle DB | `CB:0000` (3-byte offsets, 122 records) → rebuilt at `CC:4000` | record: type, count, solution bitmap, blocks, **name (SJIS)**, trailer; `tools/puzzles.py` |
| 特集 landmark notes | 16-bit ptrs `C1:3B43` (12) | |
| Prize text | `C1:4514` (x, y, long ptr) ×6 | |
| Save warnings | PEA strings at `0x3FEA`, `0x4049` | |
| Menu help lines | blob `C2:74D2`, 22×2 tiles, stride 0x300 | pre-rendered 2bpp |
| Credit pages | `C4:8421` (12 pages) | records `[map offset][words][0000]`, page ends with offset 0 |
| Rank titles | blob `C4:8044`, offsets `C1:5084` (5) | chosen by `C1:5014` from play stats |

### Screens and their blobs (Vol. 1)
| Screen | BG text | Sprites |
|---|---|---|
| Title | BG1 map `C2:3AD3`, chr `C2:0C6B` | `C2:35F6` |
| Main menu | BG2 map `C2:8A51`, chr `C2:5702` (labels, CLEAR stamp, tabs) | `C2:6612` (data panels, frames 92–99) |
| Puzzle select | — | `C2:C7A4` (mode labels, frames 174–181) |
| In game | — | `C3:585E` (windows, frames 301–317, pause panel rows 0x100–0x140), `C3:7028` (mode badges, 8×0x200) |
| Tutorial menu | — | frames 137 / 156 |
| Bonus certificate | BG1 maps `C4:7084` (full) / `C4:7C02` (template), chr `C4:210B` | `C4:6276` (seals 583–585, badges 586–590) |
| Credits | BG3 records, chr `C4:4A0A` | — |
| Credits footer | BG2 map `C4:76F4` (+0x800) | — |
| Prize | BG1 map `C4:17BE`, chr `C4:0000` (also used by Special clear) | — |

Game mode variable `$82`, mode table `C0:3890` (mode 21 = prize screen setup).

## Save RAM (2 KB)
Slot 1 at 0x000, slot 2 at 0x3A0: `NPPicross1`, 0x0A = 0xFF in use, best times `+0x29D + 2*puzzle` (0xFFFF = never cleared),
progress flags `+0x270..0x29C`, checksum u16 at `+0x39D` = sum of LE words over `+0x0B..+0x39C`. `tools/savegen.py` builds an
all-cleared save for testing (unlocks Extra, BONUS, certificate, credits).

## In-game RAM (for the auto-solver)
Field `7E:75F9 + y*0x24 + x`; solution cells 0x27 filled / 0x26 empty (grid origin (9,9)); cursor x `7E:74F7`, y `7E:74F9`.
OAM shadow buffer `7E:0559`.
