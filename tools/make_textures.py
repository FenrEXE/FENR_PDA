"""Generates the Fenrir PDA UI textures (icons + brand) as PNG sources and
uncompressed EDDS files using the same header layout as pdaframe.edds."""
import os as _os
TOOLS = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(TOOLS)
MOD = _os.path.join(REPO, "PDA")
BUILD = _os.path.join(TOOLS, "build")          # generated files (not part of the mod)
_os.makedirs(BUILD, exist_ok=True)

import os, struct, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FRAME = _os.path.join(MOD, "gui", "pdaframe.edds")
WOLF = _os.path.join(TOOLS, "art", "wolf_source.png")   # wolf emblem from the original mock-up
OUT_EDDS = _os.path.join(MOD, "gui", "os", "textures")
OUT_PNG = _os.path.join(BUILD, "source_art")
os.makedirs(OUT_EDDS, exist_ok=True)
os.makedirs(OUT_PNG, exist_ok=True)

HEADER = bytearray(open(_os.path.join(TOOLS, "frame", "pdaframe_original.edds"), "rb").read()[:128])


def save_edds(img, name):
    img = img.convert("RGBA")
    w, h = img.size
    hdr = bytearray(HEADER)
    struct.pack_into("<I", hdr, 12, h)
    struct.pack_into("<I", hdr, 16, w)
    struct.pack_into("<I", hdr, 20, w * 4)
    data = img.tobytes("raw", "BGRA")
    with open(os.path.join(OUT_EDDS, name + ".edds"), "wb") as f:
        f.write(hdr)
        f.write(data)
    img.save(os.path.join(OUT_PNG, name + ".png"))


S = 4          # supersample
N = 64         # final icon size
W = N * S
WHITE = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)


def canvas():
    im = Image.new("RGBA", (W, W), CLEAR)
    return im, ImageDraw.Draw(im)


def p(v):
    return v * S


def finish(im, name):
    save_edds(im.resize((N, N), Image.LANCZOS), name)


# ---------------------------------------------------------------- icons
def ic_messages():
    im, d = canvas()
    d.rounded_rectangle([p(6), p(10), p(58), p(46)], radius=p(7), fill=WHITE)
    d.polygon([(p(14), p(44)), (p(14), p(56)), (p(28), p(44))], fill=WHITE)
    for cx in (20, 32, 44):
        d.ellipse([p(cx - 4), p(24), p(cx + 4), p(32)], fill=CLEAR)
    finish(im, "ic_messages")


def ic_announcements():
    im, d = canvas()
    d.polygon([(p(22), p(22)), (p(48), p(8)), (p(48), p(52)), (p(22), p(38))], fill=WHITE)
    d.rectangle([p(8), p(21), p(24), p(39)], fill=WHITE)
    d.polygon([(p(14), p(39)), (p(24), p(39)), (p(28), p(56)), (p(19), p(56))], fill=WHITE)
    d.rounded_rectangle([p(51), p(24), p(57), p(36)], radius=p(3), fill=WHITE)
    finish(im, "ic_announcements")


def ic_groups():
    im, d = canvas()
    def person(cx, cy, r, bw):
        d.ellipse([p(cx - r), p(cy - r), p(cx + r), p(cy + r)], fill=WHITE)
        d.rounded_pieslice = None
        d.chord([p(cx - bw), p(cy + r + 2), p(cx + bw), p(cy + r + 2 + bw * 2)], 180, 360, fill=WHITE)
    person(14, 22, 6, 10)
    person(50, 22, 6, 10)
    # center person drawn with a clear outline to separate
    cx, cy, r, bw = 32, 18, 8, 14
    d.ellipse([p(cx - r - 2), p(cy - r - 2), p(cx + r + 2), p(cy + r + 2)], fill=CLEAR)
    d.chord([p(cx - bw - 2), p(cy + r), p(cx + bw + 2), p(cy + r + bw * 2 + 4)], 180, 360, fill=CLEAR)
    d.ellipse([p(cx - r), p(cy - r), p(cx + r), p(cy + r)], fill=WHITE)
    d.chord([p(cx - bw), p(cy + r + 2), p(cx + bw), p(cy + r + 2 + bw * 2)], 180, 360, fill=WHITE)
    finish(im, "ic_groups")


def ic_trade():
    im, d = canvas()
    d.line([(p(4), p(10)), (p(13), p(10)), (p(20), p(40)), (p(52), p(40))], fill=WHITE, width=p(5), joint="curve")
    d.polygon([(p(14), p(16)), (p(58), p(16)), (p(53), p(34)), (p(18), p(34))], fill=WHITE)
    d.ellipse([p(18), p(45), p(28), p(55)], fill=WHITE)
    d.ellipse([p(43), p(45), p(53), p(55)], fill=WHITE)
    finish(im, "ic_trade")


def ic_map():
    im, d = canvas()
    d.ellipse([p(14), p(4), p(50), p(40)], fill=WHITE)
    d.polygon([(p(16), p(30)), (p(48), p(30)), (p(32), p(60))], fill=WHITE)
    d.ellipse([p(24), p(14), p(40), p(30)], fill=CLEAR)
    finish(im, "ic_map")


def ic_contacts():
    im, d = canvas()
    d.rounded_rectangle([p(8), p(6), p(56), p(58)], radius=p(4), fill=WHITE)
    d.rounded_rectangle([p(13), p(11), p(51), p(53)], radius=p(2), fill=CLEAR)
    d.ellipse([p(18), p(17), p(30), p(29)], fill=WHITE)
    d.chord([p(15), p(31), p(33), p(49)], 180, 360, fill=WHITE)
    d.rectangle([p(15), p(40), p(33), p(44)], fill=WHITE)
    for y in (20, 30, 40):
        d.rectangle([p(37), p(y), p(47), p(y + 4)], fill=WHITE)
    finish(im, "ic_contacts")



def ic_system():
    im, d = canvas()
    cx = cy = 32
    teeth = 8
    pts = []
    for i in range(teeth * 4):
        ang = (i / (teeth * 4)) * 2 * math.pi
        r = 28 if (i % 4) in (1, 2) else 20
        pts.append((p(cx + r * math.cos(ang)), p(cy + r * math.sin(ang))))
    d.polygon(pts, fill=WHITE)
    d.ellipse([p(cx - 22), p(cy - 22), p(cx + 22), p(cy + 22)], fill=WHITE)
    d.ellipse([p(cx - 9), p(cy - 9), p(cx + 9), p(cy + 9)], fill=CLEAR)
    finish(im, "ic_system")


def chevron(name, pts):
    im, d = canvas()
    d.line([(p(x), p(y)) for x, y in pts], fill=WHITE, width=p(6), joint="curve")
    finish(im, name)


def ic_power():
    im, d = canvas()
    d.arc([p(10), p(10), p(54), p(54)], start=-60, end=240, fill=WHITE, width=p(7))
    d.rounded_rectangle([p(28), p(4), p(36), p(32)], radius=p(4), fill=WHITE)
    finish(im, "ic_power")


def ic_admin():
    im, d = canvas()
    d.polygon([(p(32), p(4)), (p(56), p(12)), (p(54), p(34)), (p(32), p(60)), (p(10), p(34)), (p(8), p(12))], fill=WHITE)
    d.polygon([(p(32), p(13)), (p(47), p(18)), (p(46), p(33)), (p(32), p(50)), (p(18), p(33)), (p(17), p(18))], fill=CLEAR)
    d.polygon([(p(32), p(20)), (p(41), p(23)), (p(40), p(32)), (p(32), p(42)), (p(24), p(32)), (p(23), p(23))], fill=WHITE)
    finish(im, "ic_admin")




def cat_rifle():
    im, d = canvas()
    d.polygon([(p(0), p(26)), (p(14), p(22)), (p(14), p(34)), (p(4), p(42)), (p(0), p(40))], fill=WHITE)   # stock
    d.rectangle([p(14), p(22), p(46), p(34)], fill=WHITE)                                          # receiver
    d.rectangle([p(46), p(25), p(64), p(30)], fill=WHITE)                                          # barrel
    d.rectangle([p(20), p(14), p(40), p(20)], fill=WHITE)                                          # scope
    d.rectangle([p(24), p(19), p(28), p(22)], fill=WHITE)
    d.rectangle([p(34), p(19), p(38), p(22)], fill=WHITE)
    d.polygon([(p(30), p(34)), (p(38), p(34)), (p(36), p(52)), (p(28), p(52))], fill=WHITE)         # magazine
    d.polygon([(p(17), p(34)), (p(24), p(34)), (p(22), p(46)), (p(15), p(46))], fill=WHITE)         # grip
    finish(im, "cat_rifle")


def cat_pistol():
    im, d = canvas()
    d.rounded_rectangle([p(8), p(16), p(58), p(28)], radius=p(2), fill=WHITE)
    d.polygon([(p(10), p(28)), (p(28), p(28)), (p(24), p(54)), (p(10), p(54))], fill=WHITE)
    d.arc([p(26), p(24), p(40), p(40)], start=0, end=180, fill=WHITE, width=p(3))
    finish(im, "cat_pistol")


def cat_ammo():
    im, d = canvas()
    for x in (8, 26, 44):
        d.rectangle([p(x), p(26), p(x + 12), p(56)], fill=WHITE)
        d.polygon([(p(x), p(26)), (p(x + 12), p(26)), (p(x + 6), p(8))], fill=WHITE)
        d.rectangle([p(x), p(28), p(x + 12), p(30)], fill=CLEAR)
    finish(im, "cat_ammo")


def cat_medical():
    im, d = canvas()
    # bandage roll (left)
    d.ellipse([p(2), p(14), p(36), p(48)], fill=WHITE)
    d.ellipse([p(12), p(24), p(26), p(38)], fill=CLEAR)
    d.polygon([(p(19), p(48)), (p(36), p(48)), (p(36), p(58)), (p(19), p(58))], fill=WHITE)
    # capsule pill (right, diagonal)
    d.line([(p(42), p(46)), (p(56), p(18))], fill=WHITE, width=p(14))
    d.ellipse([p(35), p(39), p(49), p(53)], fill=WHITE)
    d.ellipse([p(49), p(11), p(63), p(25)], fill=WHITE)
    d.line([(p(43), p(30)), (p(55), p(36))], fill=CLEAR, width=p(3))
    finish(im, "cat_medical")


def cat_build():
    im, d = canvas()
    # hand saw: blade from lower-left to upper-right, handle top-right
    blade = [(p(4), p(46)), (p(38), p(14)), (p(46), p(22)), (p(10), p(56))]
    d.polygon(blade, fill=WHITE)
    for i in range(7):
        t = i / 7.0
        x = 7 + t * 32
        y = 54 - t * 30
        d.polygon([(p(x), p(y)), (p(x + 4), p(y + 1)), (p(x + 1), p(y + 5))], fill=WHITE)
    d.rounded_rectangle([p(38), p(4), p(56), p(24)], radius=p(4), fill=WHITE)
    d.rounded_rectangle([p(43), p(9), p(51), p(19)], radius=p(2), fill=CLEAR)
    # hammer crossing the other way
    d.line([(p(18), p(12)), (p(58), p(58))], fill=CLEAR, width=p(10))
    d.line([(p(22), p(16)), (p(58), p(58))], fill=WHITE, width=p(6))
    d.polygon([(p(10), p(18)), (p(22), p(6)), (p(32), p(16)), (p(20), p(28))], fill=CLEAR)
    d.polygon([(p(12), p(18)), (p(22), p(8)), (p(30), p(16)), (p(20), p(26))], fill=WHITE)
    finish(im, "cat_build")


def cat_clothing():
    im, d = canvas()
    d.polygon([(p(22), p(6)), (p(42), p(6)), (p(60), p(16)), (p(56), p(34)), (p(48), p(30)), (p(48), p(58)),
               (p(16), p(58)), (p(16), p(30)), (p(8), p(34)), (p(4), p(16))], fill=WHITE)
    d.polygon([(p(26), p(6)), (p(38), p(6)), (p(32), p(16))], fill=CLEAR)
    d.rectangle([p(31), p(18), p(33), p(56)], fill=CLEAR)
    finish(im, "cat_clothing")


def cat_other():
    im, d = canvas()
    d.polygon([(p(32), p(6)), (p(58), p(18)), (p(32), p(30)), (p(6), p(18))], fill=WHITE)
    d.polygon([(p(6), p(22)), (p(30), p(34)), (p(30), p(60)), (p(6), p(48))], fill=WHITE)
    d.polygon([(p(58), p(22)), (p(34), p(34)), (p(34), p(60)), (p(58), p(48))], fill=WHITE)
    finish(im, "cat_other")


def ic_bounty():
    im, d = canvas()
    d.ellipse([p(6), p(6), p(58), p(58)], fill=WHITE)
    d.ellipse([p(13), p(13), p(51), p(51)], fill=CLEAR)
    d.ellipse([p(26), p(26), p(38), p(38)], fill=WHITE)
    for a, b in (((29, 0), (35, 22)), ((29, 42), (35, 64)), ((0, 29), (22, 35)), ((42, 29), (64, 35))):
        d.rectangle([p(a[0]), p(a[1]), p(b[0]), p(b[1])], fill=WHITE)
    finish(im, "ic_bounty")


def ic_drive():
    im, d = canvas()
    d.rounded_rectangle([p(10), p(22), p(48), p(52)], radius=p(5), fill=WHITE)
    d.rectangle([p(48), p(28), p(60), p(46)], fill=WHITE)
    d.rectangle([p(51), p(32), p(54), p(36)], fill=CLEAR)
    d.rectangle([p(51), p(38), p(54), p(42)], fill=CLEAR)
    d.rectangle([p(16), p(28), p(40), p(32)], fill=CLEAR)
    d.rectangle([p(16), p(36), p(32), p(40)], fill=CLEAR)
    finish(im, "ic_drive")


def ic_lock():
    im, d = canvas()
    d.rounded_rectangle([p(10), p(28), p(54), p(60)], radius=p(5), fill=WHITE)
    d.arc([p(18), p(6), p(46), p(44)], start=180, end=360, fill=WHITE, width=p(6))
    d.rectangle([p(18), p(24), p(24), p(30)], fill=WHITE)
    d.rectangle([p(40), p(24), p(46), p(30)], fill=WHITE)
    d.ellipse([p(27), p(36), p(37), p(46)], fill=CLEAR)
    d.rectangle([p(30), p(44), p(34), p(52)], fill=CLEAR)
    finish(im, "ic_lock")


def cat_cross():
    im, d = canvas()
    d.rounded_rectangle([p(22), p(6), p(42), p(58)], radius=p(3), fill=WHITE)
    d.rounded_rectangle([p(6), p(22), p(58), p(42)], radius=p(3), fill=WHITE)
    finish(im, "cat_cross")


def cat_hammer():
    im, d = canvas()
    # drawn upright, then rotated
    d.rounded_rectangle([p(28), p(22), p(36), p(62)], radius=p(2), fill=WHITE)          # handle
    d.rectangle([p(30), p(16), p(48), p(26)], fill=WHITE)                                 # face side of head
    d.rectangle([p(48), p(14), p(54), p(28)], fill=WHITE)                                 # striking face
    d.polygon([(p(30), p(16)), (p(30), p(26)), (p(10), p(30)), (p(14), p(24)), (p(22), p(20))], fill=WHITE)  # claw
    d.polygon([(p(16), p(20)), (p(10), p(16)), (p(12), p(12)), (p(22), p(17))], fill=WHITE)
    im = im.rotate(-35, resample=Image.BICUBIC, center=(W / 2, W / 2))
    finish(im, "cat_hammer")


def ic_dot():
    im, d = canvas()
    d.ellipse([p(6), p(6), p(58), p(58)], fill=WHITE)
    finish(im, "ic_dot")


# ---------------------------------------------------------------- brand
def brand():
    BW, BH = 1024, 160
    im = Image.new("RGBA", (BW, BH), CLEAR)

    # Wolf emblem lifted from the user's mockup and converted to a clean
    # green-on-transparent mask.
    src = Image.open(WOLF).convert("RGB")
    src = src.resize((src.width * 2, src.height * 2), Image.LANCZOS)
    r, g, b = src.split()
    alpha = g.point(lambda v: max(0, min(255, int((v - 45) * 2.2))))
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.6))
    fox_h = 150
    fox_w = int(src.width * fox_h / src.height)
    fox = Image.new("RGBA", src.size, (255, 255, 255, 255))   # white: tinted by the theme
    fox.putalpha(alpha)
    fox = fox.resize((fox_w, fox_h), Image.LANCZOS)
    # v8.3: the wolf is its own texture (brand_logo) so servers can swap it;
    # `brand` keeps only the text, at the same place in the same canvas.
    logo = Image.new("RGBA", (172, BH), CLEAR)
    logo.alpha_composite(fox, (0, 5))
    save_edds(logo, "brand_logo")

    d = ImageDraw.Draw(im)
    bold = ImageFont.truetype(_os.path.join(TOOLS, "fonts", "Inter-ExtraBold.otf"), 78)
    reg = ImageFont.truetype(_os.path.join(TOOLS, "fonts", "Inter-Medium.otf"), 70)
    mono = ImageFont.truetype(_os.path.join(TOOLS, "fonts", "DejaVuSansMono.ttf"), 36)

    def tracked(x, y, text, font, fill, track):
        for ch in text:
            d.text((x, y), ch, font=font, fill=fill)
            x += d.textlength(ch, font=font) + track
        return x

    x0 = 196
    x = tracked(x0, 6, "FENRIR", bold, (255, 255, 255, 255), 3)
    tracked(x + 26, 12, "INDUSTRIES", reg, (238, 238, 238, 255), 3)
    tracked(x0 + 2, 104, "SECURE FIELD NETWORK", mono, (205, 205, 205, 255), 13)
    save_edds(im, "brand")


def ic_folder():
    im, d = canvas()
    d.rounded_rectangle([p(4), p(12), p(28), p(24)], radius=p(3), fill=WHITE)      # tab
    d.rounded_rectangle([p(4), p(18), p(60), p(56)], radius=p(4), fill=WHITE)      # body
    d.rectangle([p(8), p(24), p(56), p(26)], fill=CLEAR)                           # lip line
    finish(im, "ic_folder")



def ic_warning():
    im, d = canvas()
    d.polygon([(p(32), p(4)), (p(62), p(58)), (p(2), p(58))], fill=WHITE)
    d.rectangle([p(29), p(20), p(35), p(42)], fill=CLEAR)
    d.rectangle([p(29), p(47), p(35), p(53)], fill=CLEAR)
    finish(im, "ic_warning")



def ic_caret():
    im, d = canvas()
    d.polygon([(p(8), p(8)), (p(56), p(8)), (p(32), p(48))], fill=WHITE)
    finish(im, "ic_caret")


def outlined(shape, name, grow=7):
    """White shape with a dark outline baked in (stays dark when tinted)."""
    mask = Image.new("L", (W, W), 0)
    shape(ImageDraw.Draw(mask))
    edge = mask.filter(ImageFilter.MaxFilter(grow * 2 + 1))
    im = Image.new("RGBA", (W, W), CLEAR)
    dark = Image.new("RGBA", (W, W), (8, 12, 10, 230))
    im.paste(dark, (0, 0), edge)
    white = Image.new("RGBA", (W, W), WHITE)
    im.paste(white, (0, 0), mask)
    finish(im, name)


def ic_cmp_pin():
    # Map pin: round head, pointed tail, hollow centre.
    def shape(d):
        d.ellipse([p(14), p(4), p(50), p(40)], fill=255)
        d.polygon([(p(17), p(30)), (p(47), p(30)), (p(32), p(60))], fill=255)
        d.ellipse([p(25), p(15), p(39), p(29)], fill=0)
    outlined(shape, "ic_cmp_pin")


def map_self():
    # Player arrow for the PDA map, 16 headings (00 = north, 22.5 degree
    # steps clockwise).  Script picks the frame nearest the view heading.
    pts = [(0, -25), (18, 21), (0, 11), (-18, 21)]
    for i in range(16):
        a = math.radians(i * 22.5)
        ca, sa = math.cos(a), math.sin(a)
        rot = [(32 + x * ca - y * sa, 32 + x * sa + y * ca) for x, y in pts]
        def shape(d, rot=rot):
            d.polygon([(p(x), p(y)) for x, y in rot], fill=255)
        outlined(shape, "map_self_%02d" % i, 6)


def ic_cmp_beacon():
    # S.O.S beacon: ring + filled core with an exclamation mark.
    def shape(d):
        d.ellipse([p(4), p(4), p(60), p(60)], outline=255, width=p(5))
        d.ellipse([p(15), p(15), p(49), p(49)], fill=255)
        d.rectangle([p(29), p(21), p(35), p(37)], fill=0)
        d.rectangle([p(29), p(41), p(35), p(46)], fill=0)
    outlined(shape, "ic_cmp_beacon", 5)


def cmp_disc():
    im, d = canvas()
    d.ellipse([p(1), p(1), p(63), p(63)], fill=WHITE)
    finish(im, "cmp_disc")


def cmp_ring():
    im, d = canvas()
    d.ellipse([p(2), p(2), p(62), p(62)], outline=WHITE, width=p(2))
    finish(im, "cmp_ring")


def cmp_arrow():
    # Player arrow (points up), outlined.
    def shape(dr):
        dr.polygon([(p(32), p(4)), (p(56), p(58)), (p(32), p(44)), (p(8), p(58))], fill=255)
    outlined(shape, "cmp_arrow", 5)


def cmp_caret_up():
    im, d = canvas()
    d.polygon([(p(8), p(56)), (p(56), p(56)), (p(32), p(16))], fill=WHITE)
    finish(im, "cmp_caret_up")


def cmp_dot():
    # Compass marker dot (v8.5.1), outlined so it reads on sky and on the strip.
    def shape(dr):
        dr.ellipse([p(14), p(14), p(50), p(50)], fill=255)
    outlined(shape, "cmp_dot", 9)



# Screen opening: one clean rounded rectangle, in 1600x900 frame px.
# The frame art is reworked so its opening is exactly this shape, and the
# UI bezel is the same shape, so the two always line up.
OPEN_X, OPEN_Y, OPEN_W, OPEN_H, OPEN_R = 234, 144, 1116, 586, 40
FRAME_ORIG = _os.path.join(TOOLS, "frame", "pdaframe_original.edds")


def rounded_mask(size, rect, radius, ss=4):
    """Anti-aliased rounded-rect coverage (L image) at `size`."""
    w, h = size
    x, y, rw, rh = rect
    big = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(big).rounded_rectangle(
        [x * ss, y * ss, (x + rw) * ss - 1, (y + rh) * ss - 1], radius * ss, fill=255)
    return big.resize((w, h), Image.LANCZOS)


def pdaframe():
    """Rework pdaframe.edds (from the untouched original in frame_src/): the
    green glass rim and uneven bevel are cut away and replaced by one clean
    rounded opening with a machined lip.  Inside the opening is opaque dark
    (the UI covers it); outside, the metal art is unchanged except for the
    lip shading along the cut."""
    import numpy as np
    raw = open(FRAME_ORIG, "rb").read()
    hdr = raw[:128]
    fr = Image.frombytes("RGBA", (1600, 900), raw[128:], "raw", "BGRA")
    rect = (OPEN_X, OPEN_Y, OPEN_W, OPEN_H)
    inside = np.asarray(rounded_mask((1600, 900), rect, OPEN_R), dtype=np.float32) / 255.0

    def ring(grow):
        g = (OPEN_X - grow, OPEN_Y - grow, OPEN_W + 2 * grow, OPEN_H + 2 * grow)
        return np.asarray(rounded_mask((1600, 900), g, OPEN_R + grow), dtype=np.float32) / 255.0

    art = np.asarray(fr, dtype=np.float32)
    rgb = art[:, :, :3]
    alpha = art[:, :, 3:4]
    # Lip, from the cut outwards: 2 px black gasket, a 1 px light edge
    # where the metal turns into the opening, then a soft shadow that fades
    # into the metal over ~8 px.
    gasket = np.clip(ring(2) - inside, 0, 1)[:, :, None]
    edge = np.clip(ring(3) - ring(2), 0, 1)[:, :, None]
    shade = np.zeros_like(inside)
    for k in range(3, 12):
        shade += np.clip(ring(k + 1) - ring(k), 0, 1) * (1.0 - (k - 3) / 9.0)
    shade = shade[:, :, None]
    rgb = rgb * (1 - 0.45 * shade)
    rgb = rgb * (1 - edge) + np.clip(rgb * 1.35 + 38, 0, 255) * edge
    rgb = rgb * (1 - gasket) + np.array([8, 8, 7], np.float32) * gasket
    alpha = np.maximum(alpha, 255 * gasket)
    # Opening: opaque near-black (no glass tint, no green rim).
    ins = inside[:, :, None]
    rgb = rgb * (1 - ins) + np.array([5, 7, 6], np.float32) * ins
    alpha = alpha * (1 - ins) + 255 * ins
    out = np.concatenate([rgb, alpha], axis=2).clip(0, 255).astype(np.uint8)
    img = Image.fromarray(out, "RGBA")
    with open(FRAME, "wb") as f:
        f.write(hdr)
        f.write(img.tobytes("raw", "BGRA"))
    img.save(_os.path.join(BUILD, "pdaframe_reworked.png"))


def ui_bezel():
    """Theme-coloured screen backing (ui_bezel) and rim line (ui_bezel_line):
    the same rounded rectangle as the reworked frame opening, at full size.
    Writes the placement to bezel_rect.json for gen_layout.py."""
    import json
    size = (OPEN_W, OPEN_H)
    fill = Image.new("RGBA", size, WHITE)
    fill.putalpha(rounded_mask(size, (0, 0, OPEN_W, OPEN_H), OPEN_R))
    save_edds(fill, "ui_bezel")
    outer = rounded_mask(size, (4, 4, OPEN_W - 8, OPEN_H - 8), OPEN_R - 4)
    inner = rounded_mask(size, (6, 6, OPEN_W - 12, OPEN_H - 12), OPEN_R - 6)
    import numpy as np
    a = (np.asarray(outer, np.int16) - np.asarray(inner, np.int16)).clip(0, 255).astype(np.uint8)
    line = Image.new("RGBA", size, WHITE)
    line.putalpha(Image.fromarray(a, "L"))
    save_edds(line, "ui_bezel_line")
    json.dump({"x": OPEN_X, "y": OPEN_Y, "w": OPEN_W, "h": OPEN_H, "r": OPEN_R},
              open(_os.path.join(TOOLS, "bezel_rect.json"), "w"))


def cmp_fade():
    # Horizontal band that fades out at both ends (tinted by script).
    im = Image.new("RGBA", (256, 8), CLEAR)
    for x in range(256):
        t = x / 255.0
        a = min(1.0, t / 0.2, (1 - t) / 0.2)
        for y in range(8):
            im.putpixel((x, y), (255, 255, 255, int(255 * a)))
    save_edds(im, "cmp_fade")


def cmp_disc():
    im, d = canvas()
    d.ellipse([p(1), p(1), p(63), p(63)], fill=WHITE)
    finish(im, "cmp_disc")


def cmp_ring():
    im, d = canvas()
    d.ellipse([p(2), p(2), p(62), p(62)], outline=WHITE, width=p(2))
    finish(im, "cmp_ring")


def cmp_arrow():
    # Player arrow (points up), outlined.
    def shape(dr):
        dr.polygon([(p(32), p(4)), (p(56), p(58)), (p(32), p(44)), (p(8), p(58))], fill=255)
    outlined(shape, "cmp_arrow", 5)


def cmp_caret_up():
    im, d = canvas()
    d.polygon([(p(8), p(56)), (p(56), p(56)), (p(32), p(16))], fill=WHITE)
    finish(im, "cmp_caret_up")


# ---------------------------------------------------------------- PAA
# DayZ map marks (MapWidget.AddUserMark) need .paa textures; .edds marks
# draw as plain squares.  Writes DXT5 PAA with a full mip chain, raw
# (no LZO) blocks, CGVA / CXAM / GALF / SFFO tags.
OUT_PAA = OUT_EDDS


def _dxt5_blocks(img):
    import io
    b = io.BytesIO()
    img.save(b, "DDS", pixel_format="DXT5")
    raw = b.getvalue()
    return raw[128:]          # DDS header is 128 bytes (no DX10 header for DXT5)


def save_paa(img, name):
    img = img.convert("RGBA")
    w, h = img.size
    mips = []
    cw, ch = w, h
    while cw >= 4 and ch >= 4:
        m = img if (cw, ch) == (w, h) else img.resize((cw, ch), Image.LANCZOS)
        mips.append((cw, ch, _dxt5_blocks(m)))
        cw //= 2
        ch //= 2
    px = list(img.get_flattened_data()) if hasattr(img, "get_flattened_data") else list(img.getdata())
    n = len(px)
    avg = [sum(p[i] for p in px) // n for i in range(4)]
    out = bytearray()
    out += struct.pack("<H", 0xFF05)
    def tagg(nm, data):
        return b"GGAT" + nm + struct.pack("<I", len(data)) + data
    out += tagg(b"CGVA", bytes([avg[2], avg[1], avg[0], avg[3]]))
    out += tagg(b"CXAM", bytes([255, 255, 255, 255]))
    out += tagg(b"GALF", struct.pack("<I", 1))
    offs_pos = len(out) + 12
    out += tagg(b"SFFO", bytes(64))
    out += struct.pack("<H", 0)                    # no palette
    offsets = []
    for mw, mh, data in mips:
        offsets.append(len(out))
        out += struct.pack("<HH", mw, mh)
        out += struct.pack("<I", len(data))[:3]
        out += data
    out += bytes(6)                                # end of mipmaps
    for i, o in enumerate(offsets[:16]):
        struct.pack_into("<I", out, offs_pos + i * 4, o)
    with open(os.path.join(OUT_PAA, name + ".paa"), "wb") as f:
        f.write(out)


def read_paa(path):
    """Decodes the first mip of a DXT5 PAA written above (self-check)."""
    import io
    b = open(path, "rb").read()
    assert struct.unpack_from("<H", b, 0)[0] == 0xFF05
    pos = 2
    while b[pos:pos + 4] == b"GGAT":
        ln = struct.unpack_from("<I", b, pos + 8)[0]
        pos += 12 + ln
    npal = struct.unpack_from("<H", b, pos)[0]
    pos += 2 + npal * 3
    w, h = struct.unpack_from("<HH", b, pos)
    ln = int.from_bytes(b[pos + 4:pos + 7], "little")
    data = b[pos + 7:pos + 7 + ln]
    hdr = io.BytesIO()
    tmp = Image.new("RGBA", (w, h))
    tmp.save(hdr, "DDS", pixel_format="DXT5")
    dds = hdr.getvalue()[:128] + data
    return Image.open(io.BytesIO(dds)).convert("RGBA")


def map_icons():
    """PAA icons for the PDA map: pin, S.O.S beacon, 16 player arrows."""
    for src, dst in (("ic_cmp_pin", "map_pin"), ("ic_cmp_beacon", "map_sos")):
        save_paa(Image.open(os.path.join(OUT_PNG, src + ".png")), dst)
    for i in range(16):
        save_paa(Image.open(os.path.join(OUT_PNG, "map_self_%02d.png" % i)), "map_self_%02d" % i)
        edds = os.path.join(OUT_EDDS, "map_self_%02d.edds" % i)
        if os.path.exists(edds):
            os.remove(edds)      # only the .paa is used


for f in (pdaframe, ui_bezel, map_self, cmp_fade, cmp_disc, cmp_ring, cmp_arrow, cmp_caret_up, cmp_dot, ic_cmp_pin, ic_cmp_beacon, ic_messages, ic_announcements, ic_groups, ic_trade, ic_map, ic_contacts, ic_system, ic_dot, ic_power, ic_admin, ic_bounty, ic_drive, ic_lock, cat_pistol, cat_ammo, cat_clothing, cat_other, cat_cross, cat_hammer, ic_folder, ic_warning, ic_caret, brand):
    f()
chevron("ic_up", [(14, 40), (32, 22), (50, 40)])
chevron("ic_down", [(14, 24), (32, 42), (50, 24)])
chevron("ic_prompt", [(22, 12), (42, 32), (22, 52)])
map_icons()
print(sorted(os.listdir(OUT_EDDS)))
