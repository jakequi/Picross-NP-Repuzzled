"""Find graphics the build left untouched that contain art not present in Vol. 1 (where untranslated text could hide).
usage: sweep.py VOL1_ROM ORIG_ROM PATCHED_ROM OUT.png
For every LZ blob of ORIG_ROM that is still referenced unchanged in PATCHED_ROM, every 32-byte tile (4bpp) that does
not occur anywhere in Vol. 1's blobs is collected and rendered (as 4bpp and 2bpp) for visual inspection."""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lz, gfx, numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))


def blobs(path):
    out = subprocess.run([sys.executable, os.path.join(HERE, 'find_blobs.py'), path], capture_output=True, text=True).stdout
    d = open(path, 'rb').read(); res = {}
    for line in out.splitlines():
        s = json.loads(line)
        if s.get('src') is not None and 'err' not in s and s['src'] not in res:
            try:
                res[s['src']] = bytes(lz.decompress(d, s['src'], s['len'] or None)[0])
            except Exception:
                pass
    return res


v1_path, orig_path, new_path, out_png = sys.argv[1:5]
v1, orig, new = blobs(v1_path), blobs(orig_path), blobs(new_path)
known = set()
for data in v1.values():
    for o in range(0, len(data) - 31, 16):      # 2bpp and 4bpp tile alignment
        known.add(data[o:o + 32])
cands = []
for src, data in sorted(orig.items()):
    if new.get(src) != data:
        continue                                  # replaced/relocated by the build -> translated stage
    tiles = [o for o in range(0, len(data) - 31, 32) if any(data[o:o + 32]) and data[o:o + 32] not in known]
    if tiles:
        cands.append((src, data, tiles))
        print('blob %06x len %5x: %d new tiles' % (src, len(data), len(tiles)))
# render: per blob, its new tiles as 4bpp and 2bpp strips
rows = []
for src, data, tiles in cands:
    t4 = [gfx.decode_tile(data[o:o + 32], 4) for o in tiles[:256]]
    t2 = [gfx.decode_tile(data[o:o + 16], 2) for o in tiles[:256]]
    for kind, ts in (('4bpp', t4), ('2bpp', t2)):
        for k in range(0, len(ts), 32):
            row = np.zeros((8, 256), np.uint8)
            for j, t in enumerate(ts[k:k + 32]):
                row[:, j * 8:j * 8 + 8] = t
            rows.append(('%06x %s' % (src, kind), row))
S = 3
img = Image.new('RGB', (256 * S + 110, max(1, len(rows)) * (8 * S + 2)), (0, 0, 0)); dr = ImageDraw.Draw(img)
for k, (label, row) in enumerate(rows):
    g = (255 - row.astype(int) * 16).clip(0, 255).astype(np.uint8)
    g[row == 0] = 40
    img.paste(Image.fromarray(g).resize((256 * S, 8 * S), Image.NEAREST), (110, k * (8 * S + 2)))
    dr.text((2, k * (8 * S + 2) + 4), label, fill=(255, 255, 0))
img.save(out_png)
print('%d candidate blobs, image %s' % (len(cands), out_png))
