"""Minimal raP (binarized config / rvmat) decoder -> text config."""
import struct, sys


class R:
    def __init__(self, b):
        self.b = b

    def asciiz(self, p):
        e = self.b.index(b"\0", p)
        return self.b[p:e].decode("latin-1"), e + 1

    def cint(self, p):
        v = 0; shift = 0
        while True:
            c = self.b[p]; p += 1
            v |= (c & 0x7F) << shift
            if not c & 0x80:
                return v, p
            shift += 7


def fmt_float(f):
    # float32 -> shortest text that round-trips at float32 precision
    for digits in range(1, 10):
        t = "%.*g" % (digits, f)
        if struct.unpack("<f", struct.pack("<f", float(t)))[0] == struct.unpack("<f", struct.pack("<f", f))[0]:
            return t
    return "%.9g" % f


def value(r, p, kind):
    if kind == 0:
        s, p = r.asciiz(p); return '"' + s.replace('"', '""') + '"', p
    if kind == 1:
        return fmt_float(struct.unpack_from("<f", r.b, p)[0]), p + 4
    if kind == 2:
        return str(struct.unpack_from("<i", r.b, p)[0]), p + 4
    raise ValueError("value kind %d" % kind)


def array(r, p):
    n, p = r.cint(p)
    items = []
    for _ in range(n):
        t = r.b[p]; p += 1
        if t == 3:
            v, p = array(r, p)
        elif t == 4:
            v, p = r.asciiz(p)
        else:
            v, p = value(r, p, t)
        items.append(v)
    return "{" + ",".join(items) + "}", p


def body(r, p, ind):
    out = []
    inherit, p = r.asciiz(p)
    n, p = r.cint(p)
    pad = "\t" * ind
    for _ in range(n):
        t = r.b[p]; p += 1
        if t == 0:
            name, p = r.asciiz(p)
            off = struct.unpack_from("<I", r.b, p)[0]; p += 4
            sub_inherit, _ = r.asciiz(off)
            head = "class " + name + (": " + sub_inherit if sub_inherit else "")
            out.append(pad + head)
            out.append(pad + "{")
            out.extend(body(r, off, ind + 1))
            out.append(pad + "};")
        elif t == 1:
            sub = r.b[p]; p += 1
            name, p = r.asciiz(p)
            v, p = value(r, p, sub)
            out.append(pad + name + "=" + v + ";")
        elif t == 2:
            name, p = r.asciiz(p)
            v, p = array(r, p)
            out.append(pad + name + "[]=" + v + ";")
        elif t == 3:
            name, p = r.asciiz(p)
            out.append(pad + "class " + name + ";")
        elif t == 4:
            name, p = r.asciiz(p)
            out.append(pad + "delete " + name + ";")
        else:
            raise ValueError("entry type %d at %d" % (t, p))
    return out


def decode(b):
    assert b[:4] == b"\0raP", "not raP"
    r = R(b)
    return "\n".join(body(r, 16, 0)) + "\n"


if __name__ == "__main__":
    sys.stdout.write(decode(open(sys.argv[1], "rb").read()))
