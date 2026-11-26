"""Render chosen metasprite frames large. usage: show_frames.py rom dump_prefix out.png i,j,k-l [cols] [scale]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metasprite as ms, gfx, screen
from PIL import Image, ImageDraw
rom, prefix, out, sel = sys.argv[1:5]
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 4
sc = int(sys.argv[6]) if len(sys.argv) > 6 else 2
ids = []
for part in sel.split(','):
    if '-' in part:
        a, b = part.split('-'); ids += list(range(int(a), int(b) + 1))
    else:
        ids.append(int(part))
BASE = int(os.environ.get("OBJBASE", "0xC000"), 16); BASE2 = BASE + 0x2000
d = open(rom, 'rb').read(); s = screen.load(prefix); v = s['vram']
def tile(t):
    a = ((BASE2 if t & 0x100 else BASE) + (t & 0xFF) * 32) & 0xFFFF
    return gfx.decode_tile(v[a:a + 32], 4)
pal = screen.palette(s['cgram']); prgb = [pal[128 + p * 16:128 + p * 16 + 16] for p in range(8)]
W, H = 192, 112
sheet = Image.new('RGB', (cols * W * sc, ((len(ids) + cols - 1) // cols) * (H * sc + 14)), (20, 20, 20)); dr = ImageDraw.Draw(sheet)
for k, i in enumerate(ids):
    img = Image.fromarray(ms.render_frame(ms.parse_frame(d, i), tile, prgb, (W, H), (96, 56))).resize((W * sc, H * sc), Image.NEAREST)
    r, c = divmod(k, cols); sheet.paste(img, (c * W * sc, r * (H * sc + 14) + 14)); dr.text((c * W * sc + 2, r * (H * sc + 14)), 'frame %d @%06x' % (i, ms.frame_ptr(d, i)), fill=(255, 255, 0))
sheet.save(out)
