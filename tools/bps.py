"""Minimal BPS patch writer / applier (beat format, linear SourceRead + TargetRead actions)."""
import zlib


def _vlq(n):
    out = bytearray()
    while True:
        x = n & 0x7F
        n >>= 7
        if n == 0:
            out.append(0x80 | x)
            return bytes(out)
        out.append(x)
        n -= 1


def _read_vlq(d, p):
    data, shift = 0, 1
    while True:
        x = d[p]; p += 1
        data += (x & 0x7F) * shift
        if x & 0x80:
            return data, p
        shift <<= 7
        data += shift


def create(source, target, metadata=b''):
    out = bytearray(b'BPS1')
    out += _vlq(len(source)) + _vlq(len(target)) + _vlq(len(metadata)) + metadata
    i, n = 0, len(target)
    while i < n:
        same = i < len(source) and source[i] == target[i]
        j = i
        while j < n and ((j < len(source) and source[j] == target[j]) == same):
            # keep short equal runs inside TargetRead to avoid tiny actions
            j += 1
        length = j - i
        if same:
            out += _vlq((length - 1) << 2 | 0)
        else:
            out += _vlq((length - 1) << 2 | 1) + target[i:j]
        i = j
    out += zlib.crc32(source).to_bytes(4, 'little')
    out += zlib.crc32(target).to_bytes(4, 'little')
    out += zlib.crc32(bytes(out)).to_bytes(4, 'little')
    return bytes(out)


def apply(source, patch):
    assert patch[:4] == b'BPS1'
    p = 4
    ss, p = _read_vlq(patch, p); ts, p = _read_vlq(patch, p); ms_, p = _read_vlq(patch, p)
    p += ms_
    assert len(source) == ss, 'source size mismatch'
    assert zlib.crc32(source) == int.from_bytes(patch[-12:-8], 'little'), 'source CRC mismatch'
    out = bytearray(); src_rel = tgt_rel = 0
    end = len(patch) - 12
    while p < end:
        v, p = _read_vlq(patch, p)
        cmd, length = v & 3, (v >> 2) + 1
        if cmd == 0:
            out += source[len(out):len(out) + length]
        elif cmd == 1:
            out += patch[p:p + length]; p += length
        elif cmd == 2:
            o, p = _read_vlq(patch, p); src_rel += (-1 if o & 1 else 1) * (o >> 1)
            out += source[src_rel:src_rel + length]; src_rel += length
        else:
            o, p = _read_vlq(patch, p); tgt_rel += (-1 if o & 1 else 1) * (o >> 1)
            for _ in range(length):
                out.append(out[tgt_rel]); tgt_rel += 1
    assert len(out) == ts
    assert zlib.crc32(bytes(out)) == int.from_bytes(patch[-8:-4], 'little'), 'target CRC mismatch'
    return bytes(out)


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'apply':
        src, patch, out = sys.argv[2:5]
        open(out, 'wb').write(apply(open(src, 'rb').read(), open(patch, 'rb').read()))
        print('patched ->', out)
