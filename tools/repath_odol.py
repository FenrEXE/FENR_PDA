"""Re-paths texture / material strings inside binarized (ODOL) p3d models.

ODOL keeps every LOD at an absolute file offset listed in two tables
(LOD start / LOD end, uint32 each, right after the model header).  Texture
and material paths are plain zero-terminated strings inside each LOD with
no size fields around them, so a LOD can grow if the tables are rewritten.
"""
import struct, sys, re


def find_tables(b, n):
    L = len(b)
    for off in range(8, 2048):
        starts = struct.unpack_from("<%dI" % n, b, off)
        ends = struct.unpack_from("<%dI" % n, b, off + 4 * n)
        if max(ends) != L:
            continue
        pairs = sorted(zip(starts, ends))
        if all(pairs[i][1] == pairs[i + 1][0] for i in range(n - 1)) and all(s < e for s, e in pairs):
            return off, list(starts), list(ends)
    raise ValueError("LOD tables not found")


def repath(b, old, new):
    assert b[:4] == b"ODOL"
    n = struct.unpack_from("<I", b, 8)[0]
    toff, starts, ends = find_tables(b, n)
    first = min(starts)
    head = bytearray(b[:first])
    assert re.search(re.escape(old), bytes(head), re.I) is None, "path in header"
    order = sorted(range(n), key=lambda i: starts[i])
    out = bytearray(head)
    new_starts = [0] * n
    new_ends = [0] * n
    count = 0
    for i in order:
        seg = b[starts[i]:ends[i]]
        seg2, k = re.subn(re.escape(old), lambda m: new, seg, flags=re.I)
        count += k
        new_starts[i] = len(out)
        out += seg2
        new_ends[i] = len(out)
    struct.pack_into("<%dI" % n, out, toff, *new_starts)
    struct.pack_into("<%dI" % n, out, toff + 4 * n, *new_ends)
    return bytes(out), count, (starts, ends, new_starts, new_ends)


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    data = open(src, "rb").read()
    out, count, info = repath(data, b"pda\\data\\", b"fenr_pda\\pda\\data\\")
    open(dst, "wb").write(out)
    print(src, "->", dst, "strings", count, "size", len(data), "->", len(out))
    print("  old", info[0], info[1])
    print("  new", info[2], info[3])
