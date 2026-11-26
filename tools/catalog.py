"""Collect all known LZ blobs and render each as 2bpp + 4bpp tile sheets."""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lz, tileview
from PIL import Image, ImageDraw
ROM, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
d = open(ROM, 'rb').read()
blobs = {}
for l in subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'find_blobs.py'), ROM], capture_output=True, text=True).stdout.splitlines():
    s = json.loads(l)
    if s.get('src') is not None and s['dst'] != 0x000785:
        blobs.setdefault(s['src'], (s['dst'], s['len']))
def tab(addr, n, stride=4):
    return [((d[addr + k*stride + 2] & 0x3F) << 16) | d[addr + k*stride] | d[addr + k*stride + 1] << 8 for k in range(n)]
for p in tab(0x7d19, 7) + tab(0x7cfd, 7): blobs.setdefault(p, ('tbl', 0))
for p in (0x29070, 0x2aa06, 0x2d564, 0x2de86): blobs.setdefault(p, ('dyn', 0))
json.dump({hex(k): v for k, v in sorted(blobs.items())}, open(os.path.join(OUT, 'blobs.json'), 'w'), indent=1)
for src, (dst, ln) in sorted(blobs.items()):
    try:
        out, used = lz.decompress(d, src, ln or None)
    except Exception as e:
        print('fail', hex(src), e); continue
    if dst in (0x7e4000, 0x7e4800, 0x7e5000, 0x7e5800, 0x7e6000, 0x7e6800, 0x7e3000):
        continue  # tilemaps
    a = tileview.render(out, 2, 32, 1); b = tileview.render(out, 4, 32, 1)
    im = Image.new('L', (a.width + b.width + 8, max(a.height, b.height) + 10), 60)
    im.paste(a, (0, 10)); im.paste(b, (a.width + 8, 10))
    ImageDraw.Draw(im).text((0, 0), '%06x dst %s' % (src, dst if isinstance(dst, str) else hex(dst)), fill=255)
    im.save(os.path.join(OUT, '%06x.png' % src))
    print(hex(src), hex(len(out)))
