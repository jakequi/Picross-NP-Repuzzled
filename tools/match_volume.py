"""Map a known volume's blob addresses to a new volume by content.
usage: match_volume.py OLD_ROM NEW_ROM hexaddr [hexaddr ...]
Prints, for each old blob, the new blob with the most similar decompressed contents."""
import sys, os, json, subprocess, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lz

def blobs(path):
    out = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'find_blobs.py'), path],
                         capture_output=True, text=True).stdout
    d = open(path, 'rb').read()
    res = {}
    for line in out.splitlines():
        s = json.loads(line)
        if s.get('src') is not None and 'err' not in s and s['src'] not in res:
            res[s['src']] = bytes(lz.decompress(d, s['src'], s['len'] or None)[0])
    return res

old_path, new_path = sys.argv[1:3]
old, new = blobs(old_path), blobs(new_path)
for a in sys.argv[3:]:
    a = int(a, 16)
    if a not in old:
        print('%06x not a blob in old ROM' % a); continue
    src = old[a]
    best = max(new.items(), key=lambda kv: (kv[1] == src, difflib.SequenceMatcher(None, src[:4096], kv[1][:4096], autojunk=False).quick_ratio() if abs(len(kv[1]) - len(src)) < len(src) else 0))
    r = 1.0 if best[1] == src else difflib.SequenceMatcher(None, src[:4096], best[1][:4096], autojunk=False).ratio()
    print('%06x -> %06x  %.3f  (len %d -> %d)' % (a, best[0], r, len(src), len(best[1])))
