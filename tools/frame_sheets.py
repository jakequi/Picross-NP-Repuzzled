"""Render every metasprite frame using a screen dump's sprite VRAM + palette.
usage: frame_sheets.py rom dump_prefix out_prefix [obj_base_byte] [obj_second_byte]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metasprite as ms, gfx, screen
from PIL import Image, ImageDraw

def run(rom, prefix, outp, base=0xC000, second=0xE000, cols=12, per=17, W=128, H=80):
    d = open(rom, 'rb').read(); n = ms.count(d)
    s = screen.load(prefix); v = s['vram']
    def tile(t):
        a = ((second if t & 0x100 else base) + (t & 0xFF) * 32) & 0xFFFF
        return gfx.decode_tile(v[a:a + 32], 4)
    pal = screen.palette(s['cgram']); prgb = [pal[128 + p * 16:128 + p * 16 + 16] for p in range(8)]
    rows = (n + cols - 1) // cols; outs = []
    for part in range(0, rows, per):
        sheet = Image.new('RGB', (cols * W, per * (H + 10)), (20, 20, 20)); dr = ImageDraw.Draw(sheet)
        for i in range(part * cols, min(n, (part + per) * cols)):
            img = ms.render_frame(ms.parse_frame(d, i), tile, prgb, (W, H), (W // 2, H // 2))
            r, c = divmod(i - part * cols, cols)
            sheet.paste(Image.fromarray(img), (c * W, r * (H + 10) + 10)); dr.text((c * W + 2, r * (H + 10)), str(i), fill=(255, 255, 0))
        f = '%s_%d.png' % (outp, part // per); sheet.save(f); outs.append(f)
    return n, outs

if __name__ == '__main__':
    print(run(sys.argv[1], sys.argv[2], sys.argv[3]))
