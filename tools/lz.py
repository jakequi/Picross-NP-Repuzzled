"""LZSS codec used by Picross NP (decompressor at C0:1992).
Format: optional u16 length header (when caller passes length 0), then groups:
flag byte (bits LSB first): 1 = literal byte, 0 = u16 LE word w: copy (w & 0xF) + 3 bytes
from absolute ring position w >> 4. Ring buffer is 4096 bytes, write position starts at 0."""

def decompress(data, pos=0, length=None, ring_init=0):
    if length is None:
        length = data[pos] | data[pos + 1] << 8
        pos += 2
    ring = bytearray([ring_init]) * 4096
    out = bytearray(); r = 0; flags = 0; start = pos
    while len(out) < length:
        flags >>= 1
        if not flags & 0x100:
            flags = data[pos] | 0xFF00; pos += 1
        if flags & 1:
            b = data[pos]; pos += 1
            out.append(b); ring[r] = b; r = (r + 1) & 0xFFF
        else:
            w = data[pos] | data[pos + 1] << 8; pos += 2
            n = (w & 0xF) + 3; o = w >> 4
            for _ in range(n):
                b = ring[o]; out.append(b); ring[r] = b
                r = (r + 1) & 0xFFF; o = (o + 1) & 0xFFF
    return bytes(out[:length]) if len(out) > length else bytes(out), pos - start

def compress(src, header=True):
    """Greedy LZSS compressor producing data the game's decoder accepts.
    Only references ring positions already written in this stream."""
    out = bytearray()
    if header:
        out += bytes([len(src) & 0xFF, len(src) >> 8])
    i = 0; n = len(src)
    # hash index: 3-byte key -> list of positions
    from collections import defaultdict
    idx = defaultdict(list)
    while i < n:
        flagpos = len(out); out.append(0); flags = 0
        for bit in range(8):
            if i >= n:
                break
            best_len = 0; best_pos = 0
            if i + 3 <= n:
                key = src[i:i + 3]
                cands = idx.get(key, [])
                for p in reversed(cands[-64:]):
                    if i - p > 4096 - 18:  # keep within ring window (avoid overwritten data)
                        break
                    l = 0
                    while l < 18 and i + l < n and src[p + l] == src[i + l]:
                        l += 1
                    if l > best_len:
                        best_len, best_pos = l, p
                        if l == 18:
                            break
            if best_len >= 3:
                w = ((best_pos & 0xFFF) << 4) | (best_len - 3)
                out += bytes([w & 0xFF, w >> 8])
                for k in range(best_len):
                    if i + k + 3 <= n:
                        idx[src[i + k:i + k + 3]].append(i + k)
                i += best_len
            else:
                flags |= 1 << bit
                out.append(src[i])
                if i + 3 <= n:
                    idx[src[i:i + 3]].append(i)
                i += 1
        out[flagpos] = flags
    return bytes(out)
