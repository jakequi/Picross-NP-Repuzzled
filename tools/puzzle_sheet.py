"""Render every puzzle's solution bitmap with its Japanese name (and English if given) for sense-checking."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import puzzles
from config import FONT_DIR
from PIL import Image, ImageDraw, ImageFont

def sheet(d, out, english=None, cols=6, cell=(190, 150)):
    ps = puzzles.all_puzzles(d)
    jf = ImageFont.truetype(os.path.join(FONT_DIR, 'msgothic.ttc'), 13)
    ef = ImageFont.truetype(os.path.join(FONT_DIR, 'arial.ttf'), 12)
    rows = (len(ps) + cols - 1) // cols
    im = Image.new('RGB', (cols * cell[0], rows * cell[1]), (250, 250, 245))
    dr = ImageDraw.Draw(im)
    for p in ps:
        r, c = divmod(p['index'], cols)
        x0, y0 = c * cell[0] + 6, r * cell[1] + 4
        s = 4
        for y in range(p['h']):
            for x in range(p['w']):
                if p['solution'][y, x]:
                    dr.rectangle([x0 + x * s, y0 + y * s, x0 + x * s + s - 1, y0 + y * s + s - 1], fill=(20, 20, 60))
        dr.rectangle([x0 - 1, y0 - 1, x0 + p['w'] * s, y0 + p['h'] * s], outline=(180, 180, 180))
        dr.text((x0, y0 + 102), '%d  %s' % (p['index'], puzzles.sjis_text(p['name_raw'])), font=jf, fill=(0, 0, 0))
        if english:
            dr.text((x0, y0 + 120), english.get(p['index'], ''), font=ef, fill=(160, 0, 0))
    im.save(out)

if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    sheet(d, sys.argv[2])
