"""Approximate render of the generated layout over the real frame texture."""
import os as _os
TOOLS = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(TOOLS)
MOD = _os.path.join(REPO, "PDA")
BUILD = _os.path.join(TOOLS, "build")          # generated files (not part of the mod)
_os.makedirs(BUILD, exist_ok=True)

import sys
from PIL import Image, ImageDraw, ImageFont
import gen_layout as G

OX, OY = 266, 169
FONT = _os.path.join(TOOLS, "fonts", "DejaVuSans.ttf")
_fc = {}


def font(px):
    px = max(6, int(round(px)))
    if px not in _fc:
        _fc[px] = ImageFont.truetype(FONT, px)
    return _fc[px]


def col(c):
    return tuple(int(round(v * 255)) for v in c)


def render(show=(), hide=(), texts=None, out=_os.path.join(BUILD, "preview.png"), mods=None):
    texts = texts or {}
    mods = mods or {}
    root, _ = G.build()
    base = Image.open(_os.path.join(BUILD, "pdaframe_reworked.png")).convert("RGBA")
    bg = Image.new("RGBA", base.size, (70, 80, 60, 255))
    bg.alpha_composite(base)
    im = bg
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))

    def draw_node(n, prect):
        vis = n.attrs.get("visible", 1)
        if n.name in show:
            vis = 1
        if n.name in hide:
            vis = 0
        if not vis:
            return
        if n.name in ("FI_OS_Root", "FI_Device", "FI_Frame"):
            for c in n.children:
                draw_node(c, (0, 0, G.DW, G.DH))
            return
        r = n.rect if n.rect is not None else prect
        if n.exact == "frac":
            fx, fy, fw, fh = n.frac
            r = (fx * 1600 - OX, fy * 900 - OY, fw * 1600, fh * 900)
        if getattr(n, "rect_glass", False):
            r = (0, 0, G.DW, G.DH)
        if n.name in mods:
            r = mods[n.name]
        if isinstance(n.exact, dict):
            px, py, pw, ph = prect
            if n.rect is None:
                t = n.exact.get("h") or n.exact.get("w")
                if "h" in n.exact:
                    y = py if n.align is None else py + ph - t
                    r = (px, y, pw, t)
                else:
                    x = px if n.align is None else px + pw - t
                    r = (x, py, t, ph)
        x, y, w, h = r
        d = ImageDraw.Draw(layer)
        A = n.attrs
        if n.cls == "PanelWidgetClass":
            c = col(A["color"])
            if c[3] > 0:
                tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
                ImageDraw.Draw(tmp).rectangle([OX + x, OY + y, OX + x + w - 1, OY + y + h - 1], fill=c)
                layer.alpha_composite(tmp)
        elif n.cls in ("TextWidgetClass", "MultilineTextWidgetClass"):
            s = texts.get(n.name, A.get("text", ""))
            c = col(A["color"])
            if n.cls == "TextWidgetClass":
                f = font(h * 0.92)
                tw = d.textlength(s, font=f)
                ha = A.get('"text halign"', "left")
                tx = x if ha == "left" else (x + w - tw if ha == "right" else x + (w - tw) / 2)
                d.text((OX + tx, OY + y + h / 2), s, font=f, fill=c, anchor="lm")
            else:
                f = font(15)
                lines = []
                for para in s.split("\n"):
                    cur = ""
                    for word in para.split(" "):
                        t = (cur + " " + word).strip()
                        if d.textlength(t, font=f) > w and cur:
                            lines.append(cur)
                            cur = word
                        else:
                            cur = t
                    lines.append(cur)
                for i, ln in enumerate(lines):
                    if (i + 1) * 19 > h + 6:
                        break
                    d.text((OX + x, OY + y + i * 19), ln, font=f, fill=c)
        elif n.cls == "ImageWidgetClass":
            tex = A["image0"].split("/")[-1].replace(".edds", ".png")
            src = Image.open(_os.path.join(BUILD, "source_art", tex)).convert("RGBA").resize((max(1, int(w)), max(1, int(h))), Image.LANCZOS)
            c = col(A["color"])
            tint = Image.new("RGBA", src.size, c[:3] + (255,))
            r_, g_, b_, a_ = src.split()
            if tex == "brand.png":
                # brand is a white/grey mask: multiply by the tint
                from PIL import ImageChops
                tint = ImageChops.multiply(src, Image.new("RGBA", src.size, c[:3] + (255,)))
            else:
                tint.putalpha(a_)
            layer.alpha_composite(tint, (int(OX + x), int(OY + y)))
        elif n.cls == "EditBoxWidgetClass":
            pass
        elif n.cls == "MultilineEditBoxWidgetClass":
            d.rectangle([OX + x, OY + y, OX + x + w, OY + y + h], fill=col(A["color"]))
        for c in n.children:
            draw_node(c, r)

    draw_node(root, (0, 0, G.DW, G.DH))
    im.alpha_composite(layer)
    im.convert("RGB").save(out)


if __name__ == "__main__":
    render()
