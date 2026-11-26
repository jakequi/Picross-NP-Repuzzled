"""Run an input plan (semicolon separated) and build a contact sheet of every 'shot'.
usage: explore.py rom outdir "plan; steps; ..." sheet.png [cols]
Prefix 'MENU' expands to boot -> main menu."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drive
from PIL import Image, ImageDraw
MENU = 'w 600; p start; w 120; p a; w 150; p a; w 150'
def run(rom, outdir, plan, sheet, cols=4, extra='', sram=None):
    plan = plan.replace('MENU', MENU)
    steps = [s.strip() for s in plan.split(';') if s.strip()]
    print(drive.run(rom, steps, outdir, extra, sram=sram))
    shots = [s.split()[1] for s in steps if s.startswith('shot ')]
    ims = [Image.open(os.path.join(outdir, n + '.png')).convert('RGB') for n in shots if os.path.exists(os.path.join(outdir, n + '.png'))]
    if not ims: return
    w, h = 256, 236
    rows = (len(ims) + cols - 1) // cols
    sh = Image.new('RGB', (w * cols, h * rows), (40, 40, 40))
    dr = ImageDraw.Draw(sh)
    for k, (n, im) in enumerate(zip(shots, ims)):
        r, c = divmod(k, cols)
        sh.paste(im.resize((256, 224)), (c * w, r * h + 12)); dr.text((c * w + 2, r * h), n, fill=(255, 255, 0))
    sh.save(sheet)
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]) if len(sys.argv) > 5 else 4)
