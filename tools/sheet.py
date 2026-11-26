"""Combine PNGs into a labelled contact sheet. usage: sheet.py out.png cols img1 img2 ..."""
import sys, os
from PIL import Image, ImageDraw
out, cols, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
ims = [Image.open(f).convert('RGB') for f in files]
w = max(i.width for i in ims); h = max(i.height for i in ims) + 12
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (w * cols, h * rows), (40, 40, 40))
d = ImageDraw.Draw(sheet)
for k, (f, im) in enumerate(zip(files, ims)):
    r, c = divmod(k, cols)
    sheet.paste(im, (c * w, r * h + 12))
    d.text((c * w + 2, r * h), os.path.basename(f), fill=(255, 255, 0))
sheet.save(out)
