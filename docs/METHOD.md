# How to translate another Picross NP volume

All eight Picross NP volumes (Nintendo Power, 1999–2000) run on the same engine as Vol. 1, so the tools in
`tools/` work across them. What changes per volume: addresses (blob pointers, table locations), the puzzles,
the tutorial / feature text, and any screens unique to that volume. This guide is the order that worked for Vol. 1.

Requirements: Python 3.10+, `pip install pillow numpy`, the fonts listed in `tools/config.py`
(Arial Bold, Arial Narrow Bold, Verdana Bold; on Windows they are already installed), and
[Mesen 2](https://github.com/SourMesen/Mesen2) for testing (`set MESEN=C:\path\to\Mesen.exe`).

## 0. Set up
```
cp -r vol1 volN                       # start from the Vol. 1 build and translation tables
# put the volN ROM in volN/ (never commit it), update ROM_NAME / ROM_CRC32 in volN/build.py
```
Every address in `volN/build.py` and `volN/script/sprites.py` must be re-checked. Start with the survey, which finds
the engine structures by code signature (validated on Vol. 1, where it reproduces every address in `vol1/NOTES.md`):
```
python tools/survey.py volN/ROM.sfc
#   lz_decompressor / lz_call_sites, vwf_glyph_table, sjis_row_table, kanji_list, metasprite_table,
#   tutorial_base, puzzle_db, puzzle_size_table, mode_table, credit_pages, free_space
```
Update the constants in `tools/puzzles.py`, `tools/tutorial.py`, `tools/metasprite.py`, `tools/credits.py`, `tools/vwf.py`
and `volN/build.py` from its output; anything the survey cannot find is a signal that routine changed in that volume.

## 1. Find the compressed blobs and their call sites
```
python tools/find_blobs.py ROM          # every PEA call to the LZ decompressor (C0:1992 in Vol. 1)
python tools/catalog.py ROM out/cat     # renders every blob as 2bpp/4bpp tile sheets
```
If the decompressor moved, search for `22 xx xx C0` calls preceded by four `F4` (PEA) instructions.

## 2. Text-engine text (Shift-JIS)
* `python tools/find_sjis.py ROM` lists Shift-JIS runs — tutorial script, puzzle names, feature notes, prize text.
* `tools/tutorial.py`: confirm `BASE`, the 6 section offsets and that every section round-trips
  (`serialize(parse_section()) == original`). If a new command byte appears, read its handler in the jump table
  (`dis65816.py`) and add its argument size.
* `tools/puzzles.py`: confirm `DB`, `SIZE_TBL`, `BLOCK_TBL`; then render the solution sheet
  (`python tools/puzzle_sheet.py ROM sheet.png`) and translate each name **while looking at its picture**.
* VWF font (`tools/vwf.py`, `vwf_en.py`): check the glyph table base and the `+2` advance at the width routine.

## 3. Screens with graphic text
For each screen:
1. Reach it with `tools/explore.py` (input plans, `MENU` macro). For locked content generate a save with
   `tools/savegen.py`; for post-puzzle screens use `tools/autosolve.lua` (`lua AUTOSOLVE()` in a plan);
   for hidden modes write the mode variable (`$82`) from a `lua` step.
2. `dump NAME` in the plan, then `screen.analyse(...)` → which layer holds the text and which blobs feed it.
3. BG text: match the VRAM tilemap to a tilemap blob, render it with `tools/layerview.py` (tile grid), add rows to
   `script/labels.tsv` (rect in tile coords + style). Check the style's colour indices against the original pixels.
4. Sprite text: list frames using the text tiles (`tools/show_frames.py` with the right `OBJBASE`), then either repaint
   tiles in place (pause panel), rewrite the frame (`spritetext.rewrite_frame`), or relabel whole frames
   (`spritetext.relabel_frames`). Always check which tiles are blank/free **in VRAM on that screen**.
5. Glyph-composed text (credits, certificates, rank titles): use `tools/glyphfont.py` and keep lines ≤ ~20 characters.

## 4. Build, verify, test
```
python volN/build.py path/to/ROM        # writes volN/out/*.sfc, .bps (self-verified), .ips
```
The build warns about any line too wide for its box. Then replay every screen with `tools/explore.py` and look at the
contact sheets. Regression-test the screens that share blobs with ones you edited (e.g. the prize card and the Special
clear screen share `C4:0000` in Vol. 1).

## Lessons from Vol. 1
* Text layer of the VWF engine is hi-res: render English glyphs at 2× width.
* Never trust long-pointer pattern matches outside the code banks.
* Many tiles are shared between screens (certificate templates, labels, animation frames): check tile users before
  painting in place, and prefer drawing into blank tiles / rebuilding frames.
* Keep Mesen's save folder clean between runs (`drive.run(fresh=True)`) so input plans stay reproducible.
