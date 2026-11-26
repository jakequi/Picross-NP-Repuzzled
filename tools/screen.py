"""Analyse a captured SNES screen (from drive.py 'dump NAME').

- render each BG layer and the sprite layer separately (Mode 1 only for now)
- map on-screen tiles back to the compressed blob + offset they came from

usage: screen.py ROM DUMP_PREFIX OUT_PREFIX
"""
import os, sys, json, re
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfx, lz

MODE_BPP = {0: (2, 2, 2, 2), 1: (4, 4, 2, 0), 3: (8, 4, 0, 0), 5: (4, 2, 0, 0)}


def load(prefix):
    st = {}
    for line in open(prefix + '.ppu'):
        k, v = line.rstrip('\n').split('=', 1)
        st[k] = v
    return dict(vram=open(prefix + '.vram', 'rb').read(), cgram=open(prefix + '.cgram', 'rb').read(),
                oam=open(prefix + '.oam', 'rb').read(), wram=open(prefix + '.wram', 'rb').read(), ppu=st)


def palette(cg):
    out = np.zeros((256, 3), np.uint8)
    for k in range(256):
        w = cg[k * 2] | cg[k * 2 + 1] << 8
        out[k] = ((w & 31) << 3, (w >> 5 & 31) << 3, (w >> 10 & 31) << 3)
    return out


def layer_info(s, n):
    p = s['ppu']; L = 'ppu.layers[%d].' % n
    return dict(chr=int(p[L + 'chrAddress']) * 2, map=int(p[L + 'tilemapAddress']) * 2,
                hs=int(p[L + 'hscroll']), vs=int(p[L + 'vscroll']),
                dw=p[L + 'doubleWidth'] == 'true', dh=p[L + 'doubleHeight'] == 'true',
                large=p[L + 'largeTiles'] == 'true')


def map_entry(v, info, tx, ty):
    """tilemap word at tile coords (tx, ty) in the full (possibly 64-wide) map."""
    base = info['map']
    sc = 0
    if info['dw'] and tx >= 32:
        sc += 1
    if info['dh'] and ty >= 32:
        sc += 2 if info['dw'] else 1
    a = base + sc * 0x800 + ((ty & 31) * 32 + (tx & 31)) * 2
    a &= 0xFFFF
    return v[a] | v[a + 1] << 8


def render_layer(s, n, bpp):
    """Returns (rgb image 256x224, list of placed tiles: (sx, sy, vram_addr, entry))."""
    v = s['vram']; pal = palette(s['cgram']); info = layer_info(s, n)
    img = np.zeros((224, 256, 3), np.uint8)
    mask = np.zeros((224, 256), bool)
    placed = []
    tsz = 8 * bpp
    mw = 64 if info['dw'] else 32; mh = 64 if info['dh'] else 32
    for sy in range(0, 224 + 8, 8):
        for sx in range(0, 256 + 8, 8):
            X = (sx + info['hs']) % (mw * 8); Y = (sy + info['vs']) % (mh * 8)
            tx, ty = X // 8, Y // 8
            e = map_entry(v, info, tx, ty)
            t = e & 0x3FF; p = e >> 10 & 7; hf = e >> 14 & 1; vf = e >> 15 & 1
            addr = (info['chr'] + t * tsz) & 0xFFFF
            tile = gfx.decode_tile(v[addr:addr + tsz] + bytes(max(0, addr + tsz - 0x10000)), bpp)
            if hf: tile = tile[:, ::-1]
            if vf: tile = tile[::-1, :]
            ox, oy = sx - X % 8, sy - Y % 8
            placed.append((ox, oy, addr, e))
            base = p * (1 << bpp) if bpp < 8 else 0
            for y in range(8):
                for x in range(8):
                    px, py = ox + x, oy + y
                    if 0 <= px < 256 and 0 <= py < 224 and tile[y, x]:
                        img[py, px] = pal[base + tile[y, x]]; mask[py, px] = True
    return img, mask, placed


OBJ_SIZES = {0: ((8, 8), (16, 16)), 1: ((8, 8), (32, 32)), 2: ((8, 8), (64, 64)), 3: ((16, 16), (32, 32)),
             4: ((16, 16), (64, 64)), 5: ((32, 32), (64, 64)), 6: ((16, 32), (32, 64)), 7: ((16, 32), (32, 32))}


def render_sprites(s):
    v = s['vram']; oam = s['oam']; pal = palette(s['cgram']); p = s['ppu']
    base = int(p['ppu.oamBaseAddress']) * 2
    gap = int(p.get('ppu.oamAddressOffset', '4096')) * 2
    mode = int(p['ppu.oamMode'])
    img = np.zeros((224, 256, 3), np.uint8); placed = []
    for i in range(127, -1, -1):
        x = oam[i * 4] | ((oam[0x200 + i // 4] >> ((i % 4) * 2)) & 1) << 8
        y = oam[i * 4 + 1]; t = oam[i * 4 + 2]; a = oam[i * 4 + 3]
        big = (oam[0x200 + i // 4] >> ((i % 4) * 2 + 1)) & 1
        w, h = OBJ_SIZES[mode][big]
        if x >= 256: x -= 512
        if y >= 224: continue
        name = (a & 1) << 8 | t; palno = a >> 1 & 7; hf = a >> 6 & 1; vf = a >> 7 & 1
        for ty in range(h // 8):
            for tx in range(w // 8):
                c = (name & 0xF0) | ((name + tx) & 0x0F)
                c = c + ty * 16
                c &= 0x1FF
                addr = (base + (c & 0xFF) * 32 + ((c >> 8) & 1) * (256 * 32 + gap - 0x2000 if False else 0) + ((c >> 8) & 1) * (0x2000 + gap)) & 0xFFFF
                addr = (base + (c & 0xFF) * 32 + (((c >> 8) & 1) * (8192 + gap))) & 0xFFFF
                tile = gfx.decode_tile(v[addr:addr + 32], 4)
                if hf: tile = tile[:, ::-1]
                if vf: tile = tile[::-1, :]
                dx = (w // 8 - 1 - tx) if hf else tx
                dy = (h // 8 - 1 - ty) if vf else ty
                ox, oy = x + dx * 8, y + dy * 8
                placed.append((ox, oy, addr, palno))
                for yy in range(8):
                    for xx in range(8):
                        px, py = ox + xx, oy + yy
                        if 0 <= px < 256 and 0 <= py < 224 and tile[yy, xx]:
                            img[py, px] = pal[128 + palno * 16 + tile[yy, xx]]
    return img, placed


def blob_index(rom, srcs):
    """Map 16-byte tile rows (2bpp tile or first half of 4bpp tile) -> [(src, offset)]."""
    idx = {}
    for src, ln in srcs:
        try:
            data, _ = lz.decompress(rom, src, ln or None)
        except Exception:
            continue
        for off in range(0, len(data) - 15, 16):
            chunk = data[off:off + 16]
            if chunk.count(0) == 16:
                continue
            idx.setdefault(chunk, []).append((src, off))
    return idx


def known_blobs(rom):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import subprocess
    out = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'find_blobs.py'),
                          '-'], input=None, capture_output=True, text=True)
    return out


def analyse(rom_path, prefix, outp, blobs):
    rom = open(rom_path, 'rb').read()
    s = load(prefix)
    mode = int(s['ppu']['ppu.bgMode'])
    bpps = MODE_BPP.get(mode, (4, 4, 2, 0))
    os.makedirs(os.path.dirname(outp) or '.', exist_ok=True)
    idx = blob_index(rom, blobs)
    report = {}
    tiles_out = []
    for n in range(4):
        if not bpps[n]:
            continue
        img, mask, placed = render_layer(s, n, bpps[n])
        Image.fromarray(img).save('%s_bg%d.png' % (outp, n + 1))
        hits = {}
        for ox, oy, addr, e in placed:
            chunk = s['vram'][addr:addr + 16]
            for src, off in idx.get(bytes(chunk), [])[:1]:
                hits.setdefault('%06x' % src, 0); hits['%06x' % src] += 1
            tiles_out.append(dict(layer=n + 1, x=ox, y=oy, vram=addr, entry=e,
                                  src=[('%06x' % a, b) for a, b in idx.get(bytes(chunk), [])[:3]]))
        report['bg%d' % (n + 1)] = hits
    simg, splaced = render_sprites(s)
    Image.fromarray(simg).save('%s_obj.png' % outp)
    hits = {}
    for ox, oy, addr, pal in splaced:
        chunk = s['vram'][addr:addr + 16]
        for src, off in idx.get(bytes(chunk), [])[:1]:
            hits.setdefault('%06x' % src, 0); hits['%06x' % src] += 1
        tiles_out.append(dict(layer='obj', x=ox, y=oy, vram=addr, pal=pal,
                              src=[('%06x' % a, b) for a, b in idx.get(bytes(chunk), [])[:3]]))
    report['obj'] = hits
    json.dump(dict(report=report, tiles=tiles_out), open(outp + '_tiles.json', 'w'), indent=0)
    return report
