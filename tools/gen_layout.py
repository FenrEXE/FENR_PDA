"""
Fenrir PDA - Field OS 7 layout generator.

All geometry is authored in reference pixels of the frame's glass area
(1067 x 554, measured from pdaframe.edds at 1600x900).  The serializer turns
those absolute coordinates into the parent-relative fractions DayZ expects,
so the whole UI scales uniformly with the 16:9 device container.  Border
lines are the only exact-pixel widgets so they stay crisp at any resolution.
"""
import os as _os
TOOLS = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(TOOLS)
MOD = _os.path.join(REPO, "PDA")
BUILD = _os.path.join(TOOLS, "build")          # generated files (not part of the mod)
_os.makedirs(BUILD, exist_ok=True)

import json, sys

DW, DH = 1067.0, 554.0          # glass reference size
# v8.2.3: the reworked frame opening is (234,144,1116,586); the display sits
# 16 px inside it on every side (same height, so text scale is unchanged).
GLASS = (250 / 1600, 160 / 900, 1084 / 1600, 554 / 900)

FONT_S = "gui/fonts/Metron14"
FONT_M = "gui/fonts/metronlight16"
FONT_L = "gui/fonts/metronlight22"


def rgb(r, g, b, a=255):
    return (r / 255, g / 255, b / 255, a / 255)


C = {
    "lcd":        rgb(2, 18, 11),
    "panel":      rgb(0, 22, 13),
    "card":       rgb(0, 27, 16),
    "input":      rgb(0, 12, 7),
    "active":     rgb(4, 65, 40),
    "line":       rgb(34, 138, 88),
    "lineDim":    rgb(18, 84, 54),
    "lineBright": rgb(80, 220, 150),
    "text":       rgb(150, 236, 185),
    "textBright": rgb(205, 255, 225),
    "textDim":    rgb(92, 182, 132),
    "accent":     rgb(60, 215, 95),
    "warn":       rgb(230, 170, 60),
    "clear":      rgb(0, 0, 0, 0),
    "shadow":     rgb(0, 0, 0, 220),
}


class N:
    def __init__(self, cls, name, rect=None, attrs=None, children=None, exact=None, align=None):
        self.cls, self.name, self.rect = cls, name, rect
        self.attrs = attrs or {}
        self.children = children or []
        self.exact = exact            # dict for exact-pixel border lines
        self.align = align            # (halign, valign)

    def add(self, *kids):
        self.children.extend(k for k in kids if k is not None)
        return self


# ------------------------------------------------------------------ helpers
def frame(name, rect, kids=(), **a):
    return N("FrameWidgetClass", name, rect, a, list(kids))


def panel(name, rect, color, **a):
    a.setdefault("ignorepointer", 1)
    return N("PanelWidgetClass", name, rect, dict(color=color, style="rover_sim_colorable", **a))


def text(name, rect, s, color="text", font=FONT_M, halign="left", **a):
    a.setdefault("ignorepointer", 1)
    attrs = dict(text=s, font=font, color=C[color], **a)
    attrs['"text halign"'] = halign
    attrs['"text valign"'] = "center"
    return N("TextWidgetClass", name, rect, attrs)


def mtext(name, rect, s, color="text", font=FONT_S, **a):
    a.setdefault("ignorepointer", 1)
    attrs = dict(text=s, font=font, color=C[color], wrap=1, **a)
    attrs['"exact text"'] = 1
    return N("MultilineTextWidgetClass", name, rect, attrs)


def image(name, rect, tex, color="text", **a):
    a.setdefault("ignorepointer", 1)
    attrs = dict(image0=f"FENR_PDA/PDA/gui/os/textures/{tex}.edds", mode="blend", color=C[color], stretch=1, **a)
    attrs['"src alpha"'] = 1
    attrs['"no wrap"'] = 1
    return N("ImageWidgetClass", name, rect, attrs)



# Header brand block (v8.3, replaceable from the server config):
#   <p>BrandLogo   logo (built-in wolf, or the server's image)
#   <p>Brand       built-in "FENRIR INDUSTRIES / SECURE FIELD NETWORK" text art
#   <p>BrandName   / <p>BrandTag   server-set name and tagline as live text
#   <p>BrandBanner one image replacing all of the above (hidden by default)
BRAND_W, BRAND_H = 435, 68
BRAND_LOGO_W = 435 * 172 / 1024        # 73.07
BRAND_TEXT_X = 435 * 196 / 1024        # 83.27 (text starts here)


def brand_block(parent, p, x, y):
    parent.add(image(p + "BrandLogo", (x, y, BRAND_LOGO_W, BRAND_H), "brand_logo", "lineBright"))
    parent.add(image(p + "Brand", (x, y, BRAND_W, BRAND_H), "brand", "lineBright"))
    tx = x + BRAND_TEXT_X
    parent.add(text(p + "BrandName", (tx, y + 4, BRAND_W - BRAND_TEXT_X, 34), "FENRIR INDUSTRIES", "lineBright", FONT_L, visible=0))
    parent.add(text(p + "BrandTag", (tx + 1, y + 44, BRAND_W - BRAND_TEXT_X, 16), "SECURE FIELD NETWORK", "text", FONT_S, visible=0))
    bn = image(p + "BrandBanner", (x, y, BRAND_W, BRAND_H), "brand", "lineBright", visible=0)
    parent.add(bn)


def px_image(name, tex, color):
    """Hidden image positioned / sized in pixels by script."""
    attrs = dict(visible=0, ignorepointer=1, image0=f"FENR_PDA/PDA/gui/os/textures/{tex}.edds", mode="blend",
                 color=C[color], stretch=1)
    attrs['"src alpha"'] = 1
    attrs['"no wrap"'] = 1
    return N("ImageWidgetClass", name, None, attrs, exact="pxi")


def px_text(name, color):
    attrs = dict(visible=0, ignorepointer=1, text="", font=FONT_S, color=C[color])
    attrs['"text valign"'] = "center"
    return N("TextWidgetClass", name, None, attrs, exact="px")

def border(name, rect, color="line", t=2):
    """Four exact-pixel lines hugging the parent rect."""
    f = frame(name, rect, ignorepointer=1)
    col = C[color]
    f.add(
        N("PanelWidgetClass", name + "_T", None, dict(color=col, style="rover_sim_colorable", ignorepointer=1), exact=dict(h=t)),
        N("PanelWidgetClass", name + "_B", None, dict(color=col, style="rover_sim_colorable", ignorepointer=1), exact=dict(h=t), align=("left", "bottom_ref")),
        N("PanelWidgetClass", name + "_L", None, dict(color=col, style="rover_sim_colorable", ignorepointer=1), exact=dict(w=t)),
        N("PanelWidgetClass", name + "_R", None, dict(color=col, style="rover_sim_colorable", ignorepointer=1), exact=dict(w=t), align=("right_ref", "top")),
    )
    return f


def hline(name, x, y, w, color="line", t=1):
    return N("PanelWidgetClass", name, (x, y, w, t), dict(color=C[color], style="rover_sim_colorable", ignorepointer=1), exact=dict(h=t))


def vline(name, x, y, h, color="line", t=1):
    return N("PanelWidgetClass", name, (x, y, t, h), dict(color=C[color], style="rover_sim_colorable", ignorepointer=1), exact=dict(w=t))


def box_panel(name, rect, bg="panel", bd="lineDim", t=2):
    """Bordered pane (visual only)."""
    return frame(name, rect, [panel(name + "_BG", rect, C[bg]), border(name + "_Bd", rect, bd, t)], ignorepointer=1)


def hit(name, rect):
    attrs = dict(style="Default", color=C["clear"], text="")
    return N("ButtonWidgetClass", name, rect, attrs)


def button(name, rect, label, icon=None, label_h=None, halign="center", kind="action"):
    """Interactive button: visuals in NAME_Box, transparent hit button NAME on top."""
    x, y, w, h = rect
    lh = label_h or min(17, h * 0.42)
    f = frame(name + "_Box", rect)
    bg_col = C["clear"] if kind == "nav" else C["input"]
    bd_col = "clear" if kind == "nav" else "line"
    f.add(panel(name + "_BG", rect, bg_col), border(name + "_Bd", rect, bd_col, 2))
    tx = x + 10
    if icon:
        isz = min(h * 0.68, 26)
        f.add(image(name + "_Icon", (x + 18, y + (h - isz) / 2, isz, isz), icon))
        tx = x + 18 + isz + 22
    if halign == "center" and not icon:
        f.add(text(name + "_Label", (x + 4, y + (h - lh) / 2, w - 8, lh), label, "text", FONT_M, "center"))
    else:
        f.add(text(name + "_Label", (tx, y + (h - lh) / 2, x + w - tx - 8, lh), label, "text", FONT_M, "left"))
    f.add(hit(name, rect))
    return f


def icon_button(name, rect, tex):
    x, y, w, h = rect
    f = frame(name + "_Box", rect)
    f.add(panel(name + "_BG", rect, C["input"]), border(name + "_Bd", rect, "line", 2))
    isz = min(w, h) * 0.72
    f.add(image(name + "_Icon", (x + (w - isz) / 2, y + (h - isz) / 2, isz, isz), tex))
    f.add(hit(name, rect))
    return f


def text_input(name, rect, hint, prompt=False, text_h=16):
    x, y, w, h = rect
    f = frame(name + "_Box", rect)
    f.add(panel(name + "_BG", rect, C["input"]), border(name + "_Bd", rect, "line", 2))
    ex = x + 14
    if prompt:
        f.add(image(name + "_Prompt", (x + 14, y + (h - 16) / 2, 16, 16), "ic_prompt", "text"))
        ex = x + 46
    eh = text_h + 8
    edit_attrs = dict(style="DefaultBorder", text="", font=FONT_M, color=C["input"])
    f.add(N("EditBoxWidgetClass", name, (ex, y + (h - eh) / 2, x + w - ex - 10, eh), edit_attrs))
    f.add(text(name + "Hint", (ex + 4, y + (h - text_h) / 2, x + w - ex - 14, text_h), hint, "textDim", FONT_M))
    return f


def scrollbar(prefix, x, y, h, w=17):
    f = frame(prefix + "_Scroll", (x, y, w, h))
    f.add(button(prefix + "_Up", (x, y, w, w), "", None))
    f.add(image(prefix + "_UpIcon", (x + 2, y + 2, w - 4, w - 4), "ic_up", "text"))
    f.add(button(prefix + "_Down", (x, y + h - w, w, w), "", None))
    f.add(image(prefix + "_DownIcon", (x + 2, y + h - w + 2, w - 4, w - 4), "ic_down", "text"))
    tr = (x + 3, y + w + 4, w - 6, h - 2 * w - 8)
    track = frame(prefix + "_Track", tr, ignorepointer=1)
    track.add(border(prefix + "_TrackBd", tr, "lineDim", 1))
    track.add(panel(prefix + "_Thumb", (tr[0] + 2, tr[1] + tr[3] * 0.55, tr[2] - 4, tr[3] * 0.45), C["accent"]))
    f.add(track)
    # Drag area: the whole bar between the arrows (wider than the thin track).
    f.add(hit(prefix + "_TrackHit", (x, y + w, w, h - 2 * w)))
    return f


def row(prefix, i, rect, meta_w=None):
    name = f"{prefix}_R{i}"
    x, y, w, h = rect
    f = frame(name + "_Box", rect)
    f.add(panel(name + "_BG", rect, C["card"]), border(name + "_Bd", rect, "lineDim", 1))
    lh = min(16, h * 0.5)
    mw = meta_w if meta_w is not None else min(w * 0.38, 150)
    f.add(text(name + "_Label", (x + 12, y + (h - lh) / 2, w - mw - 20, lh), "ROW", "text", FONT_M))
    f.add(text(name + "_Meta", (x + w - mw, y + (h - 13) / 2, mw - 12, 13), "", "textDim", FONT_S, "right"))
    f.add(hit(name, rect))
    return f


def row_list(prefix, x, y, w, h, row_h=34, gap=6, scroll=True, meta_w=None):
    sw = 17 if scroll else 0
    lw = w - (sw + 12 if scroll else 0)
    n = int((h + gap) // (row_h + gap))
    f = frame(prefix + "_List", (x, y, w, h), ignorepointer=1)
    for i in range(n):
        f.add(row(prefix, i, (x, y + i * (row_h + gap), lw, row_h), meta_w))
    if scroll:
        f.add(scrollbar(prefix, x + w - sw, y, h, sw))
    return f, n


def card(prefix, i, rect):
    name = f"{prefix}_Card{i}"
    x, y, w, h = rect
    f = frame(name, rect, ignorepointer=1)
    f.add(panel(name + "_BG", rect, C["card"]), border(name + "_Bd", rect, "line", 1))
    f.add(text(name + "_Name", (x + 14, y + 9, w * 0.7, 16), "SENDER", "textBright", FONT_M))
    f.add(text(name + "_Time", (x + w * 0.7, y + 10, w * 0.3 - 14, 14), "", "text", FONT_S, "right"))
    f.add(mtext(name + "_Body", (x + 14, y + 33, w - 28, 22), "Message", "text", FONT_M))
    return f


def chat_view(prefix, root_name, x0, y0, x1, y1, input_name, send_name, hint, title, sub,
              extra_header=()):
    """Bordered conversation pane + input row, matching the reference art."""
    v = frame(root_name, (x0, y0, x1 - x0, y1 - y0))
    py1 = y1 - 60
    v.add(box_panel(prefix + "_Pane", (x0, y0, x1 - x0, py1 - y0), "panel", "lineDim"))
    v.add(text(prefix + "_ChatTitle", (x0 + 18, y0 + 14, 560, 24), title, "textBright", FONT_L))
    v.add(text(prefix + "_ChatSub", (x0 + 18, y0 + 45, 560, 16), sub, "text", FONT_M))
    for e in extra_header:
        v.add(e)
    v.add(hline(prefix + "_ChatRule", x0 + 18, y0 + 72, x1 - x0 - 60, "line", 1))
    area = (x0 + 18, y0 + 87, x1 - x0 - 68, py1 - y0 - 87 - 10)
    a = frame(prefix + "_Cards", area, clipchildren=1, ignorepointer=1)
    cy = area[1]
    for i in range(12):
        a.add(card(prefix, i, (area[0], cy, area[2], 60)))
        cy += 71
    v.add(a)
    v.add(scrollbar(prefix, x1 - 32, y0 + 83, py1 - y0 - 92))
    iy = y1 - 47
    v.add(text_input(input_name, (x0, iy, (x1 - x0) - 156, 47), hint, prompt=True))
    v.add(button(send_name, (x1 - 139, iy, 139, 47), "SEND"))
    return v


def status_pill(name, x, y, w=124, h=36, label="ONLINE"):
    f = frame(name + "_Box", (x, y, w, h), ignorepointer=1)
    f.add(panel(name + "_BG", (x, y, w, h), C["input"]), border(name + "_Bd", (x, y, w, h), "line", 2))
    f.add(text(name, (x + 10, y + (h - 15) / 2, w - 44, 15), label, "text", FONT_S, "center"))
    f.add(image(name + "_Dot", (x + w - 28, y + (h - 14) / 2, 14, 14), "ic_dot", "accent"))
    return f


def page_header(prefix, x0, y0, w, title, sub):
    return [
        text(prefix + "_Title", (x0 + 18, y0 + 14, w - 220, 24), title, "textBright", FONT_L),
        text(prefix + "_Subtitle", (x0 + 18, y0 + 45, w - 220, 16), sub, "text", FONT_M),
        hline(prefix + "_Rule", x0 + 18, y0 + 72, w - 36, "line", 1),
    ]


# ------------------------------------------------------------------ shell
HX0, HY0, HX1, HY1 = 270, 80, 1028, 530     # page host region (glass px)
NAV_ITEMS = {
    "Announcements": ("ANNOUNCEMENTS", "ic_announcements"), "Messages": ("MESSAGES", "ic_messages"),
    "Groups": ("GROUPS", "ic_groups"), "Contacts": ("CONTACTS", "ic_contacts"),
    "Map": ("MAP", "ic_map"), "Drives": ("DRIVES", "ic_drive"),
    "Trade": ("TRADE", "ic_trade"), "Bounties": ("BOUNTIES", "ic_bounty"),
    "System": ("SYSTEM", "ic_system"), "Admin": ("ADMIN", "ic_admin")}
NAV_GROUPS = [("Comms", "COMMS", ["Announcements", "Messages", "Groups", "Contacts"]),
              ("Field", "FIELD", ["Map", "Drives"]),
              ("Market", "MARKET", ["Trade", "Bounties"]),
              ("Device", "DEVICE", ["System", "Admin"])]
NAV = [(k, NAV_ITEMS[k][0], NAV_ITEMS[k][1]) for _, _, ks in NAV_GROUPS for k in ks]
NAV_HDR_STEP, NAV_ROW, NAV_GAP = 16, 28, 5


def build():
    disp = frame("FI_Display", (0, 0, DW, DH))
    # Transparent: the rounded bezel under the display is the screen colour.
    disp.add(panel("FI_LCD", (0, 0, DW, DH), C["clear"], ignorepointer=0))

    # ---- sidebar
    sb = frame("FI_Sidebar", (14, 8, 236, 538), ignorepointer=1)
    sb.add(box_panel("FI_SidebarPane", (14, 8, 236, 538), "panel", "lineDim"))
    sb.add(text("FI_Unit", (56, 19, 170, 17), "FI-PDA-01", "text", FONT_M))
    sb.add(text("FI_Version", (56, 39, 120, 15), "FIELD OS v8.8", "textDim", FONT_S))
    sb.add(button("FI_SosQuick", (154, 18, 36, 38), "SOS", None, 12))
    cb = (196, 18, 40, 38)
    cl = frame("FI_Close_Box", cb)
    cl.add(panel("FI_Close_BG", cb, C["input"]), border("FI_Close_Bd", cb, "line", 2))
    cl.add(image("FI_Close_Icon", (cb[0] + 10, cb[1] + 9, 20, 20), "ic_power", "text"))
    cl.add(hit("FI_Close", cb))
    sb.add(cl)
    sb.add(hline("FI_SidebarRule", 22, 66, 220, "line", 1))
    # Grouped navigation (v8.4).  Script reflows it (FENR_PDA_Menu.LayoutNav)
    # when boards are disabled or the player is not an admin; a section with
    # nothing left in it hides its heading.
    ny = 70
    for gkey, glabel, items in NAV_GROUPS:
        sb.add(text("FI_NavHdr_" + gkey, (34, ny, 200, 12), glabel, "textDim", FONT_S))
        ny += NAV_HDR_STEP
        for key in items:
            label, icon = NAV_ITEMS[key]
            sb.add(button("FI_Nav_" + key, (20, ny, 224, NAV_ROW - 2), label, icon, 15, "left", "nav"))
            ny += NAV_ROW
        ny += NAV_GAP
    sb.add(hline("FI_SidebarRule2", 22, 436, 220, "line", 1))
    sb.add(text("FI_Local", (36, 444, 200, 16), "LOCAL NETWORK", "text", FONT_M))
    sb.add(text("FI_SignalLabel", (36, 466, 80, 16), "SIGNAL:", "text", FONT_M))
    for i in range(6):
        sh = 6 + i * 2.4
        sb.add(panel(f"FI_Sig{i}", (112 + i * 11, 480 - sh, 8, sh), C["accent"] if i < 4 else C["lineDim"]))
    sb.add(text("FI_Battery", (36, 488, 200, 16), "BATTERY: --", "text", FONT_M))
    sb.add(text("FI_UnitStatus", (36, 510, 200, 16), "UNIT: FI-PDA-01", "text", FONT_M))
    disp.add(sb)
    disp.add(vline("FI_VLine", 256, 14, 526, "lineDim", 1))

    # ---- header
    hd = frame("FI_Header", (270, 8, 758, 70), ignorepointer=1)
    brand_block(hd, "FI_", 270, 9)
    hd.add(text("FI_User", (700, 28, 210, 17), "USER: --", "text", FONT_M, "right"))
    # battery glyph built from panels so it can show real charge
    bx, by = 925, 29
    hd.add(border("FI_BattShell", (bx, by, 30, 16), "text", 2))
    hd.add(panel("FI_BattNub", (bx + 30, by + 5, 3, 6), C["text"]))
    hd.add(panel("FI_BattFill", (bx + 4, by + 4, 22 * 0.82, 8), C["accent"]))
    hd.add(text("FI_BattPct", (962, 27, 62, 19), "--%", "textBright", FONT_M, "right"))
    disp.add(hd)

    # ---- page host
    host = frame("FI_PageHost", (HX0, HY0, HX1 - HX0, HY1 - HY0), clipchildren=1)
    W = HX1 - HX0

    # MESSAGES -------------------------------------------------------
    msg = frame("FI_MSG_Root", (HX0, HY0, W, HY1 - HY0), visible=0)
    inbox = frame("FI_MSG_InboxView", (HX0, HY0, W, HY1 - HY0))
    inbox.add(box_panel("FI_MSG_InboxPane", (HX0, HY0, W, HY1 - HY0)))
    inbox.add(*page_header("FI_MSG", HX0, HY0, W, "MESSAGES / INBOX", "IDENTITY: CONNECTING..."))
    lst, n_inbox = row_list("FI_MSG_Inbox", HX0 + 18, HY0 + 87, W - 36, HY1 - HY0 - 105, 38, 7)
    inbox.add(lst)
    msg.add(inbox)
    chat = chat_view("FI_MSG", "FI_MSG_ChatView", HX0, HY0, HX1, HY1, "FI_MSG_Input", "FI_MSG_Send",
                     "Type message...", "MESSAGES / DIRECT", "CONVERSATION: --",
                     extra_header=[button("FI_MSG_Mute", (HX1 - 395, HY0 + 15, 102, 36), "MUTE"),
                                   button("FI_MSG_Back", (HX1 - 285, HY0 + 15, 140, 36), "< INBOX"),
                                   status_pill("FI_MSG_Status", HX1 - 132, HY0 + 15)])
    chat.attrs["visible"] = 0
    msg.add(chat)
    host.add(msg)

    # ANNOUNCEMENTS --------------------------------------------------
    ann = frame("FI_ANN_Root", (HX0, HY0, W, HY1 - HY0), visible=0)
    lw = 280
    ann.add(box_panel("FI_ANN_ListPane", (HX0, HY0, lw, HY1 - HY0)))
    ann.add(text("FI_ANN_ListTitle", (HX0 + 16, HY0 + 14, lw - 32, 24), "BULLETINS", "textBright", FONT_L))
    ann.add(text("FI_ANN_Count", (HX0 + 16, HY0 + 45, lw - 32, 16), "0 RECEIVED", "text", FONT_M))
    ann.add(hline("FI_ANN_ListRule", HX0 + 16, HY0 + 72, lw - 32, "line", 1))
    lst, n_ann = row_list("FI_ANN_List", HX0 + 14, HY0 + 87, lw - 28, HY1 - HY0 - 101, 38, 7)
    ann.add(lst)
    rx = HX0 + lw + 14
    rw = HX1 - rx
    ann.add(box_panel("FI_ANN_ReaderPane", (rx, HY0, rw, HY1 - HY0)))
    ann.add(text("FI_ANN_Title", (rx + 18, HY0 + 14, rw - 36, 24), "ANNOUNCEMENTS", "textBright", FONT_L))
    ann.add(text("FI_ANN_Source", (rx + 18, HY0 + 45, rw - 36, 16), "SELECT A BULLETIN", "text", FONT_M))
    ann.add(hline("FI_ANN_Rule", rx + 18, HY0 + 72, rw - 36, "line", 1))
    ann.add(text("FI_ANN_Meta", (rx + 18, HY0 + 86, rw - 36, 14), "OFFICIAL SECURE FIELD NETWORK BULLETIN", "textDim", FONT_S))
    rb = box_panel("FI_ANN_BodyPane", (rx + 18, HY0 + 112, rw - 36, HY1 - HY0 - 130), "card", "line")
    ann.add(rb)
    ann.add(mtext("FI_ANN_Body", (rx + 34, HY0 + 126, rw - 68, HY1 - HY0 - 158), "Select a bulletin from the archive.", "text", FONT_M))
    host.add(ann)

    # GROUPS ---------------------------------------------------------
    grp = frame("FI_GRP_Root", (HX0, HY0, W, HY1 - HY0), visible=0)
    gl = frame("FI_GRP_ListView", (HX0, HY0, W, HY1 - HY0))
    py1 = HY1 - 60
    gl.add(box_panel("FI_GRP_ListPane", (HX0, HY0, W, py1 - HY0)))
    gl.add(*page_header("FI_GRP", HX0, HY0, W, "GROUPS / PRIVATE CHANNELS", "MEMBER-ONLY SECURE COMMUNICATION"))
    gl.add(button("FI_GRP_Refresh", (HX1 - 150, HY0 + 15, 132, 36), "REFRESH"))
    lst, n_grp = row_list("FI_GRP_List", HX0 + 18, HY0 + 87, W - 36, py1 - HY0 - 101, 38, 7)
    gl.add(lst)
    gl.add(text_input("FI_GRP_NameInput", (HX0, HY1 - 47, W - 156, 47), "New private channel name...", prompt=True))
    gl.add(button("FI_GRP_Create", (HX1 - 139, HY1 - 47, 139, 47), "CREATE"))
    grp.add(gl)
    gc = chat_view("FI_GRP", "FI_GRP_ChatView", HX0, HY0, HX1, HY1, "FI_GRP_MessageInput", "FI_GRP_Send",
                   "Type group message...", "GROUPS / CHANNEL", "Select a channel to load its secure transcript.",
                   extra_header=[button("FI_GRP_Mute", (HX1 - 400, HY0 + 15, 102, 36), "MUTE"),
                                 button("FI_GRP_Back", (HX1 - 290, HY0 + 15, 150, 36), "< CHANNELS"),
                                 button("FI_GRP_Manage", (HX1 - 132, HY0 + 15, 114, 36), "MANAGE")])
    gc.attrs["visible"] = 0
    grp.add(gc)
    gm = frame("FI_GRP_ManageView", (HX0, HY0, W, HY1 - HY0), visible=0)
    gm.add(box_panel("FI_GRP_ManagePane", (HX0, HY0, W, HY1 - HY0)))
    gm.add(text("FI_GRP_SettingsTitle", (HX0 + 18, HY0 + 14, 500, 24), "GROUPS / SETTINGS", "textBright", FONT_L))
    gm.add(text("FI_GRP_Owner", (HX0 + 18, HY0 + 45, 500, 16), "OWNER: --", "text", FONT_M))
    gm.add(button("FI_GRP_ManageBack", (HX1 - 150, HY0 + 15, 132, 36), "< BACK"))
    gm.add(hline("FI_GRP_SetRule", HX0 + 18, HY0 + 72, W - 36, "line", 1))
    gm.add(text_input("FI_GRP_RenameInput", (HX0 + 18, HY0 + 86, 420, 40), "Channel name"))
    gm.add(button("FI_GRP_Rename", (HX0 + 450, HY0 + 86, 130, 40), "RENAME"))
    gm.add(button("FI_GRP_Leave", (HX1 - 18 - 150, HY0 + 86, 150, 40), "LEAVE"))
    colw = (W - 36 - 20) / 2
    c1, c2 = HX0 + 18, HX0 + 18 + colw + 20
    gm.add(text("FI_GRP_MembersLabel", (c1, HY0 + 140, colw, 15), "CURRENT MEMBERS", "textDim", FONT_S))
    gm.add(text("FI_GRP_ContactsLabel", (c2, HY0 + 140, colw, 15), "DIRECTORY CONTACTS", "textDim", FONT_S))
    lst, n_mem = row_list("FI_GRP_Members", c1, HY0 + 162, colw, 180, 32, 5)
    gm.add(lst)
    lst, n_con = row_list("FI_GRP_Contacts", c2, HY0 + 162, colw, 180, 32, 5)
    gm.add(lst)
    gm.add(button("FI_GRP_RemoveMember", (c1, HY0 + 352, colw, 38), "REMOVE SELECTED MEMBER"))
    gm.add(button("FI_GRP_AddMember", (c2, HY0 + 352, colw, 38), "ADD SELECTED CONTACT"))
    gm.add(button("FI_GRP_Delete", (HX0 + 18, HY0 + 400, W - 36, 36), "DELETE PRIVATE CHANNEL"))
    grp.add(gm)
    host.add(grp)

    # CONTACTS -------------------------------------------------------
    con = frame("FI_CON_Root", (HX0, HY0, W, HY1 - HY0), visible=0)
    lw = 320
    con.add(box_panel("FI_CON_ListPane", (HX0, HY0, lw, HY1 - HY0)))
    con.add(text("FI_CON_ListTitle", (HX0 + 16, HY0 + 14, lw - 32, 24), "CONTACTS", "textBright", FONT_L))
    con.add(text("FI_CON_Count", (HX0 + 16, HY0 + 45, lw - 32, 16), "FIELD DIRECTORY", "text", FONT_M))
    con.add(hline("FI_CON_ListRule", HX0 + 16, HY0 + 72, lw - 32, "line", 1))
    lst, n_cl = row_list("FI_CON_List", HX0 + 14, HY0 + 87, lw - 28, 290, 34, 6)
    con.add(lst)
    con.add(text("FI_CON_AddLabel", (HX0 + 16, HY0 + 385, lw - 32, 14), "ADD TO DIRECTORY", "textDim", FONT_S))
    con.add(text_input("FI_CON_AddInput", (HX0 + 14, HY0 + 404, lw - 112, 36), "Player ID / name"))
    con.add(button("FI_CON_Add", (HX0 + lw - 90, HY0 + 404, 76, 36), "ADD"))
    rx = HX0 + lw + 14
    rw = HX1 - rx
    con.add(box_panel("FI_CON_DetailPane", (rx, HY0, rw, HY1 - HY0)))
    con.add(text("FI_CON_DetailTitle", (rx + 18, HY0 + 14, rw - 36, 24), "CONTACT RECORD", "textBright", FONT_L))
    con.add(text("FI_CON_Relation", (rx + 18, HY0 + 45, rw - 36, 16), "RELATION: DIRECTORY CONTACT", "text", FONT_M))
    con.add(hline("FI_CON_DetailRule", rx + 18, HY0 + 72, rw - 36, "line", 1))
    cd = box_panel("FI_CON_Card", (rx + 18, HY0 + 88, rw - 36, 112), "card", "line")
    con.add(cd)
    con.add(text("FI_CON_Name", (rx + 34, HY0 + 102, rw - 200, 26), "NO CONTACT SELECTED", "textBright", FONT_L))
    con.add(status_pill("FI_CON_Status", rx + rw - 18 - 138, HY0 + 100, 124, 34, "--"))
    con.add(text("FI_CON_ID", (rx + 34, HY0 + 142, rw - 68, 15), "PLAYER ID: --", "text", FONT_S))
    con.add(text("FI_CON_Info", (rx + 34, HY0 + 168, rw - 68, 15), "Select a contact from the directory.", "textDim", FONT_S))
    bw = (rw - 36 - 14) / 2
    con.add(button("FI_CON_Message", (rx + 18, HY0 + 216, bw, 40), "SEND MESSAGE"))
    con.add(button("FI_CON_Block", (rx + 32 + bw, HY0 + 216, bw, 40), "BLOCK"))
    con.add(text_input("FI_CON_RenameInput", (rx + 18, HY0 + 270, rw - 36 - 144, 40), "Contact name"))
    con.add(button("FI_CON_Rename", (rx + rw - 18 - 130, HY0 + 270, 130, 40), "RENAME"))
    con.add(button("FI_CON_Remove", (rx + 18, HY0 + 324, rw - 36, 40), "REMOVE FROM DIRECTORY"))
    con.add(button("FI_CON_RateUp", (rx + 18, HY0 + 378, bw, 38), "+ GOOD TRADE"))
    con.add(button("FI_CON_RateDown", (rx + 32 + bw, HY0 + 378, bw, 38), "- BAD TRADE"))
    host.add(con)


    # ADMIN ----------------------------------------------------------
    adm = frame("FI_ADM_Root", (HX0, HY0, W, HY1 - HY0), visible=0)
    adm.add(box_panel("FI_ADM_Pane", (HX0, HY0, W, HY1 - HY0)))
    atw = 98
    tx = HX1 - 18 - 4 * atw - 3 * 6
    adm.add(text("FI_ADM_Title", (HX0 + 18, HY0 + 14, tx - HX0 - 28, 24), "ADMIN / CONTROL", "textBright", FONT_L))
    adm.add(text("FI_ADM_Subtitle", (HX0 + 18, HY0 + 45, tx - HX0 - 28, 16), "VERIFYING AUTHORIZATION...", "text", FONT_M))
    adm.add(button("FI_ADM_TabArchive", (tx, HY0 + 15, atw, 36), "ARCHIVE"))
    adm.add(button("FI_ADM_TabPlayers", (tx + (atw + 6), HY0 + 15, atw, 36), "PLAYERS"))
    adm.add(button("FI_ADM_TabBroadcast", (tx + 2 * (atw + 6), HY0 + 15, atw, 36), "BROADCAST"))
    adm.add(button("FI_ADM_TabIntel", (tx + 3 * (atw + 6), HY0 + 15, atw, 36), "INTEL"))
    adm.add(hline("FI_ADM_Rule", HX0 + 18, HY0 + 72, W - 36, "line", 1))
    X0 = HX0 + 18
    XW = W - 36

    # Archive view
    av = frame("FI_ADM_ArchiveView", (HX0, HY0 + 80, W, HY1 - HY0 - 80))
    av.add(text_input("FI_ADM_Query", (X0, HY0 + 86, 330, 38), "Search name, Steam64, group or text..."))
    av.add(button("FI_ADM_Type", (X0 + 340, HY0 + 86, 150, 38), "TYPE: ALL"))
    av.add(button("FI_ADM_Search", (X0 + 500, HY0 + 86, 110, 38), "SEARCH"))
    av.add(button("FI_ADM_Clear", (X0 + 618, HY0 + 86, XW - 618, 38), "CLEAR"))
    area = (X0, HY0 + 136, XW - 32, 252)
    a = frame("FI_ADM_Cards", area, clipchildren=1, ignorepointer=1)
    cy = area[1]
    for i in range(12):
        a.add(card("FI_ADM", i, (area[0], cy, area[2], 60)))
        cy += 71
    av.add(a)
    av.add(scrollbar("FI_ADM", HX1 - 18 - 17, HY0 + 132, 260))
    av.add(button("FI_ADM_Prev", (X0, HY0 + 400, 110, 34), "< PREV"))
    av.add(text("FI_ADM_PageInfo", (X0 + 120, HY0 + 409, XW - 240, 16), "NO SEARCH RUN", "text", FONT_M, "center"))
    av.add(button("FI_ADM_Next", (HX1 - 18 - 110, HY0 + 400, 110, 34), "NEXT >"))
    adm.add(av)

    # Players view
    pv = frame("FI_ADM_PlayersView", (HX0, HY0 + 80, W, HY1 - HY0 - 80), visible=0)
    lst, n_adm = row_list("FI_ADM_Players", X0, HY0 + 86, 400, 314, 34, 6)
    pv.add(lst)
    pv.add(text("FI_ADM_PlayerCount", (X0, HY0 + 412, 400, 16), "0 PLAYERS ONLINE", "textDim", FONT_M))
    dx = X0 + 416
    dw = HX1 - 18 - dx
    pv.add(box_panel("FI_ADM_PlayerPane", (dx, HY0 + 86, dw, 346), "card", "line"))
    pv.add(text("FI_ADM_PlayerName", (dx + 16, HY0 + 100, dw - 32, 24), "NO PLAYER SELECTED", "textBright", FONT_L))
    pv.add(text("FI_ADM_PlayerID", (dx + 16, HY0 + 134, dw - 32, 15), "STEAM64: --", "text", FONT_S))
    pv.add(text("FI_ADM_PlayerState", (dx + 16, HY0 + 156, dw - 32, 15), "DEVICE: --", "textDim", FONT_S))
    pv.add(hline("FI_ADM_PlayerRule", dx + 16, HY0 + 182, dw - 32, "lineDim", 1))
    pv.add(button("FI_ADM_PlayerMessage", (dx + 16, HY0 + 196, dw - 32, 38), "SEND MESSAGE"))
    pv.add(button("FI_ADM_PlayerAdd", (dx + 16, HY0 + 242, dw - 32, 38), "ADD TO CONTACTS"))
    pv.add(button("FI_ADM_PlayerLogs", (dx + 16, HY0 + 288, dw - 32, 38), "SEARCH THEIR LOGS"))
    pv.add(button("FI_ADM_PlayersRefresh", (dx + 16, HY0 + 380, dw - 32, 38), "REFRESH LIST"))
    adm.add(pv)

    # Broadcast view: the edit box scrolls, so a large preview shows the
    # whole message wrapped while typing.
    bv = frame("FI_ADM_BroadcastView", (HX0, HY0 + 80, W, HY1 - HY0 - 80), visible=0)
    bv.add(box_panel("FI_ADM_BcPane", (X0, HY0 + 86, XW, 62), "card", "line"))
    bv.add(image("FI_ADM_BcIcon", (X0 + 14, HY0 + 99, 34, 34), "ic_announcements", "text"))
    bv.add(text("FI_ADM_BcTitle", (X0 + 60, HY0 + 94, XW - 76, 22), "NETWORK BROADCAST", "textBright", FONT_L))
    bv.add(text("FI_ADM_BcInfo", (X0 + 60, HY0 + 122, XW - 76, 15), "Sent to every logged-in PDA as a bulletin in Announcements. The audit log records you.", "text", FONT_S))
    bv.add(text("FI_ADM_BcPreviewLabel", (X0, HY0 + 158, XW, 14), "MESSAGE PREVIEW", "textDim", FONT_S))
    bv.add(box_panel("FI_ADM_BcPreviewPane", (X0, HY0 + 176, XW, 156), "panel", "lineDim"))
    bv.add(mtext("FI_ADM_BcPreview", (X0 + 16, HY0 + 186, XW - 32, 138), "Start typing below. The full message appears here.", "text", FONT_M))
    bv.add(text_input("FI_ADM_BcInput", (X0, HY0 + 340, XW - 156, 47), "Broadcast message (max 256 characters)...", prompt=True))
    bv.add(button("FI_ADM_BcSend", (HX1 - 18 - 139, HY0 + 340, 139, 47), "BROADCAST"))
    bv.add(text("FI_ADM_BcStatus", (X0, HY0 + 400, XW - 120, 16), "", "text", FONT_M))
    bv.add(text("FI_ADM_BcCount", (HX1 - 18 - 110, HY0 + 400, 110, 15), "0 / 256", "textDim", FONT_S, "right"))
    adm.add(bv)

    # Intel view: write a custom file to the Intel Drive in the admin's PDA.
    iv = frame("FI_ADM_IntelView", (HX0, HY0 + 80, W, HY1 - HY0 - 80), visible=0)
    iv.add(box_panel("FI_ADM_IntelPane", (X0, HY0 + 86, XW, 62), "card", "line"))
    iv.add(image("FI_ADM_IntelIcon", (X0 + 14, HY0 + 99, 34, 34), "ic_drive", "text"))
    iv.add(text("FI_ADM_IntelTitleText", (X0 + 60, HY0 + 94, XW - 76, 22), "WRITE INTEL DRIVE", "textBright", FONT_L))
    iv.add(text("FI_ADM_IntelInfo", (X0 + 60, HY0 + 122, XW - 76, 15), "Insert an Intel Drive in your PDA. Type | in the text for a new line.", "text", FONT_S))
    iv.add(text_input("FI_ADM_IntelTitle", (X0, HY0 + 156, XW, 38), "Intel title (max 48 characters)"))
    iv.add(text("FI_ADM_IntelPreviewLabel", (X0, HY0 + 202, XW, 14), "FILE PREVIEW", "textDim", FONT_S))
    iv.add(box_panel("FI_ADM_IntelPreviewPane", (X0, HY0 + 220, XW, 112), "panel", "lineDim"))
    iv.add(mtext("FI_ADM_IntelPreview", (X0 + 16, HY0 + 228, XW - 32, 96), "", "text", FONT_M))
    iv.add(text_input("FI_ADM_IntelBody", (X0, HY0 + 340, XW - 156, 47), "Intel text (max 1000 characters)...", prompt=True))
    iv.add(button("FI_ADM_IntelWrite", (HX1 - 18 - 139, HY0 + 340, 139, 47), "WRITE"))
    iv.add(text("FI_ADM_IntelStatus", (X0, HY0 + 400, XW - 120, 16), "", "text", FONT_M))
    iv.add(text("FI_ADM_IntelCount", (HX1 - 18 - 110, HY0 + 400, 110, 15), "0 / 1000", "textDim", FONT_S, "right"))
    adm.add(iv)
    host.add(adm)

    # STATIC PAGES -----------------------------------------------------
    def static_cols(root, prefix, title, sub, cols):
        r = frame(root, (HX0, HY0, W, HY1 - HY0), visible=0)
        r.add(box_panel(prefix + "_Pane", (HX0, HY0, W, HY1 - HY0)))
        r.add(*page_header(prefix, HX0, HY0, W, title, sub))
        n = len(cols)
        gap = 16
        cw = (W - 36 - gap * (n - 1)) / n
        for i, (key, ctitle, body) in enumerate(cols):
            cx = HX0 + 18 + i * (cw + gap)
            r.add(box_panel(f"{prefix}_{key}Pane", (cx, HY0 + 92, cw, 330), "card", "line"))
            r.add(text(f"{prefix}_{key}Title", (cx + 16, HY0 + 108, cw - 32, 22), ctitle, "textBright", FONT_L))
            r.add(hline(f"{prefix}_{key}Rule", cx + 16, HY0 + 140, cw - 32, "lineDim", 1))
            r.add(mtext(f"{prefix}_{key}Text", (cx + 16, HY0 + 154, cw - 32, 250), body, "text", FONT_M))
        return r

    # TRADE ----------------------------------------------------------
    trd = frame("FI_TRD_Root", (HX0, HY0, W, HY1 - HY0), visible=0)
    trd.add(box_panel("FI_TRD_Pane", (HX0, HY0, W, HY1 - HY0)))
    trd.add(text("FI_TRD_Title", (HX0 + 18, HY0 + 14, 330, 24), "TRADE / FIELD EXCHANGE", "textBright", FONT_L))
    trd.add(text("FI_TRD_Subtitle", (HX0 + 18, HY0 + 45, 330, 16), "SURVIVOR BUY AND SELL BULLETINS", "text", FONT_M))
    tw = 124
    tx = HX1 - 18 - 3 * tw - 2 * 6
    trd.add(button("FI_TRD_TabBuy", (tx, HY0 + 15, tw, 36), "BUY BOARD"))
    trd.add(button("FI_TRD_TabSell", (tx + tw + 6, HY0 + 15, tw, 36), "SELL BOARD"))
    trd.add(button("FI_TRD_TabCreate", (tx + 2 * (tw + 6), HY0 + 15, tw, 36), "CREATE LISTING"))
    trd.add(hline("FI_TRD_Rule", HX0 + 18, HY0 + 72, W - 36, "line", 1))
    X0 = HX0 + 18
    XW = W - 36

    # Board view: 4 x 5 tile grid
    bv = frame("FI_TRD_BoardView", (HX0, HY0 + 80, W, HY1 - HY0 - 80))
    gx, gy, gw, gh = X0, HY0 + 84, XW, 318
    cols, rows, cg, rg = 4, 5, 8, 6
    tile_w = (gw - (cols - 1) * cg) / cols
    tile_h = (gh - (rows - 1) * rg) / rows
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            name = f"FI_TRD_T{i}"
            x = gx + c * (tile_w + cg)
            y = gy + r * (tile_h + rg)
            rect = (x, y, tile_w, tile_h)
            t = frame(name + "_Box", rect)
            t.add(panel(name + "_BG", rect, C["card"]), border(name + "_Bd", rect, "lineDim", 1))
            t.add(image(name + "_Icon", (x + 6, y + (tile_h - 38) / 2, 38, 38), "cat_other", "text"))
            tx0 = x + 50
            t.add(text(name + "_Label", (tx0, y + 5, x + tile_w - tx0 - 6, 15), "LISTING TITLE", "textBright", FONT_M))
            iw_ = x + tile_w - tx0 - 6
            t.add(text(name + "_Price", (tx0, y + 23, iw_ * 0.62, 13), "PRICE", "text", FONT_S))
            t.add(text(name + "_Status", (tx0 + iw_ * 0.62, y + 23, iw_ * 0.38, 12), "OPEN", "accent", FONT_S, "right"))
            t.add(text(name + "_Lister", (tx0, y + tile_h - 17, iw_, 12), "LISTER", "textDim", FONT_S))
            t.add(hit(name, rect))
            bv.add(t)
    bv.add(text("FI_TRD_Empty", (gx, gy + gh / 2 - 9, gw, 18), "No listings on this board yet.", "textDim", FONT_M, "center"))
    bv.add(button("FI_TRD_Prev", (X0, HY0 + 410, 110, 34), "< PREV"))
    bv.add(button("FI_TRD_Filter", (X0 + 120, HY0 + 410, 190, 34), "FILTER: ALL"))
    bv.add(text("FI_TRD_PageInfo", (X0 + 320, HY0 + 419, XW - 440, 16), "LOADING...", "text", FONT_M, "center"))
    bv.add(button("FI_TRD_Next", (HX1 - 18 - 110, HY0 + 410, 110, 34), "NEXT >"))
    trd.add(bv)

    # Create view: form + my listings
    cv = frame("FI_TRD_CreateView", (HX0, HY0 + 80, W, HY1 - HY0 - 80), visible=0)
    fw = 420
    cv.add(box_panel("FI_TRD_FormPane", (X0, HY0 + 84, fw, 350), "card", "line"))
    cv.add(text("FI_TRD_FormTitle", (X0 + 16, HY0 + 96, fw - 32, 20), "NEW LISTING", "textBright", FONT_L))
    cv.add(text("FI_TRD_TypeLabel", (X0 + 16, HY0 + 130, 60, 14), "TYPE", "textDim", FONT_S))
    cv.add(button("FI_TRD_TypeSell", (X0 + 80, HY0 + 122, 154, 30), "SELLING"))
    cv.add(button("FI_TRD_TypeBuy", (X0 + 242, HY0 + 122, 162, 30), "BUYING"))
    cats = [("GUNS", "cat_pistol"), ("AMMO", "cat_ammo"), ("MEDICAL", "cat_cross"), ("TOOLS", "cat_hammer"), ("CLOTHING", "cat_clothing"), ("OTHER", "cat_other")]
    cw_ = (fw - 32 - 5 * 4) / 6
    for i, (cat, tex) in enumerate(cats):
        cv.add(icon_button("FI_TRD_Cat" + cat, (X0 + 16 + i * (cw_ + 4), HY0 + 158, cw_, 40), tex))
    cv.add(text_input("FI_TRD_TitleInput", (X0 + 16, HY0 + 206, fw - 32, 36), "Item title (max 32 characters)"))
    cv.add(text_input("FI_TRD_PriceInput", (X0 + 16, HY0 + 248, fw - 32, 36), "Price or trade offer (max 24)"))
    cv.add(text_input("FI_TRD_DescInput", (X0 + 16, HY0 + 290, fw - 32, 36), "Details: condition, quantity, meet point..."))
    cv.add(button("FI_TRD_Post", (X0 + 16, HY0 + 334, fw - 32, 38), "POST LISTING"))
    cv.add(text("FI_TRD_CreateStatus", (X0 + 16, HY0 + 382, fw - 32, 15), "", "text", FONT_M))
    cv.add(text("FI_TRD_CreateHint", (X0 + 16, HY0 + 410, fw - 32, 14), "Listings expire automatically. An active listing limit applies.", "textDim", FONT_S))
    mx = X0 + fw + 16
    mw = HX1 - 18 - mx
    cv.add(text("FI_TRD_MineLabel", (mx, HY0 + 86, mw, 15), "MY LISTINGS", "textDim", FONT_S))
    lst, n_mine = row_list("FI_TRD_Mine", mx, HY0 + 106, mw, 328, 34, 6)
    cv.add(lst)
    trd.add(cv)

    # Floating listing detail popup (drawn last so it sits above the boards)
    pp = frame("FI_TRD_Popup", (HX0, HY0, W, HY1 - HY0), visible=0)
    pp.add(panel("FI_TRD_PopupDim", (HX0, HY0, W, HY1 - HY0), rgb(0, 0, 0, 170)))
    pp.add(hit("FI_TRD_PopupShade", (HX0, HY0, W, HY1 - HY0)))
    dw, dh = 520, 424
    dx = HX0 + (W - dw) / 2
    dy = HY0 + 12
    dlg = frame("FI_TRD_Dialog", (dx, dy, dw, dh))
    dlg.add(panel("FI_TRD_Dialog_BG", (dx, dy, dw, dh), C["panel"]), border("FI_TRD_Dialog_Bd", (dx, dy, dw, dh), "lineBright", 2))
    dlg.add(box_panel("FI_TRD_PopupIconPane", (dx + 18, dy + 14, 56, 56), "card", "lineDim"))
    dlg.add(image("FI_TRD_PopupIcon", (dx + 24, dy + 20, 44, 44), "cat_other", "text"))
    dlg.add(text("FI_TRD_PopupKind", (dx + 86, dy + 14, dw - 160, 14), "FOR SALE", "accent", FONT_S))
    dlg.add(button("FI_TRD_PopupClose", (dx + dw - 18 - 40, dy + 10, 40, 30), "X"))
    dlg.add(text("FI_TRD_PopupTitle", (dx + 86, dy + 32, dw - 104, 24), "LISTING TITLE", "textBright", FONT_L))
    dlg.add(text("FI_TRD_PopupPrice", (dx + 86, dy + 60, dw - 104, 16), "PRICE: --", "text", FONT_M))
    dlg.add(text("FI_TRD_PopupLister", (dx + 18, dy + 86, dw - 36, 15), "SELLER: --", "text", FONT_S))
    dlg.add(text("FI_TRD_PopupStatus", (dx + 18, dy + 106, dw - 36, 15), "STATUS: --", "text", FONT_S))
    dlg.add(text("FI_TRD_PopupPosted", (dx + 18, dy + 126, dw - 36, 15), "POSTED: --", "textDim", FONT_S))
    dlg.add(hline("FI_TRD_PopupRule", dx + 18, dy + 150, dw - 36, "lineDim", 1))
    dlg.add(box_panel("FI_TRD_PopupDescPane", (dx + 18, dy + 160, dw - 36, 104), "card", "lineDim"))
    dlg.add(mtext("FI_TRD_PopupDesc", (dx + 30, dy + 170, dw - 60, 88), "No details provided.", "text", FONT_M))
    vs = frame("FI_TRD_PopupViewer", (dx, dy + 272, dw, 140))
    vs.add(button("FI_TRD_PopupContact", (dx + 18, dy + 276, 300, 38), "CONTACT SELLER"))
    vs.add(button("FI_TRD_PopupBlock", (dx + 328, dy + 276, dw - 346, 38), "BLOCK SELLER"))
    half = (dw - 36 - 10) / 2
    vs.add(button("FI_TRD_PopupRateUp", (dx + 18, dy + 322, half, 36), "+ GOOD TRADE"))
    vs.add(button("FI_TRD_PopupRateDown", (dx + 28 + half, dy + 322, half, 36), "- BAD TRADE"))
    vs.add(button("FI_TRD_PopupAdminRemove", (dx + 18, dy + 366, dw - 36, 36), "REMOVE LISTING (ADMIN)"))
    dlg.add(vs)
    os_ = frame("FI_TRD_PopupOwner", (dx, dy + 272, dw, 140), visible=0)
    os_.add(button("FI_TRD_PopupPending", (dx + 18, dy + 276, 236, 38), "MARK PENDING"))
    os_.add(button("FI_TRD_PopupClosed", (dx + 266, dy + 276, dw - 284, 38), "MARK SOLD"))
    os_.add(button("FI_TRD_PopupRemove", (dx + 18, dy + 322, dw - 36, 36), "REMOVE LISTING"))
    dlg.add(os_)
    pp.add(dlg)
    trd.add(pp)
    host.add(trd)

    # BOUNTIES ---------------------------------------------------------
    bn = frame("FI_BNT_Root", (HX0, HY0, W, HY1 - HY0), visible=0)
    bn.add(box_panel("FI_BNT_Pane", (HX0, HY0, W, HY1 - HY0)))
    bn.add(text("FI_BNT_Title", (HX0 + 18, HY0 + 14, 330, 24), "BOUNTIES / CONTRACTS", "textBright", FONT_L))
    bn.add(text("FI_BNT_Subtitle", (HX0 + 18, HY0 + 45, 330, 16), "ACTIVE BOUNTIES", "text", FONT_M))
    tw = 124
    tx = HX1 - 18 - 3 * tw - 2 * 6
    bn.add(button("FI_BNT_TabBoard", (tx, HY0 + 15, tw, 36), "ACTIVE BOARD"))
    bn.add(button("FI_BNT_TabMine", (tx + tw + 6, HY0 + 15, tw, 36), "MY BOUNTIES"))
    bn.add(button("FI_BNT_TabPost", (tx + 2 * (tw + 6), HY0 + 15, tw, 36), "POST BOUNTY"))
    bn.add(hline("FI_BNT_Rule", HX0 + 18, HY0 + 72, W - 36, "line", 1))
    X0 = HX0 + 18
    XW = W - 36

    bbv = frame("FI_BNT_BoardView", (HX0, HY0 + 80, W, HY1 - HY0 - 80))
    gx, gy, gw, gh = X0, HY0 + 84, XW, 318
    cols, rows, cg, rg = 3, 4, 8, 6
    tile_w = (gw - (cols - 1) * cg) / cols
    tile_h = (gh - (rows - 1) * rg) / rows
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            name = f"FI_BNT_T{i}"
            x = gx + c * (tile_w + cg)
            y = gy + r * (tile_h + rg)
            rect = (x, y, tile_w, tile_h)
            t = frame(name + "_Box", rect)
            t.add(panel(name + "_BG", rect, C["card"]), border(name + "_Bd", rect, "lineDim", 1))
            t.add(image(name + "_Icon", (x + 8, y + (tile_h - 42) / 2, 42, 42), "ic_bounty", "text"))
            tx0 = x + 60
            iw_ = x + tile_w - tx0 - 8
            t.add(text(name + "_Label", (tx0, y + 8, iw_ * 0.7, 17), "TARGET", "textBright", FONT_M))
            t.add(text(name + "_Tag", (tx0 + iw_ * 0.7, y + 10, iw_ * 0.3, 12), "", "warn", FONT_S, "right"))
            t.add(text(name + "_Reward", (tx0, y + 31, iw_, 14), "REWARD", "text", FONT_S))
            t.add(text(name + "_Poster", (tx0, y + tile_h - 20, iw_ * 0.62, 12), "POSTER", "textDim", FONT_S))
            t.add(text(name + "_Status", (tx0 + iw_ * 0.62, y + tile_h - 20, iw_ * 0.38, 12), "OPEN", "accent", FONT_S, "right"))
            t.add(hit(name, rect))
            bbv.add(t)
    bbv.add(text("FI_BNT_Empty", (gx, gy + gh / 2 - 9, gw, 18), "No active bounties. Quiet out there.", "textDim", FONT_M, "center"))
    bbv.add(button("FI_BNT_Prev", (X0, HY0 + 410, 110, 34), "< PREV"))
    bbv.add(text("FI_BNT_PageInfo", (X0 + 120, HY0 + 419, XW - 240, 16), "LOADING...", "text", FONT_M, "center"))
    bbv.add(button("FI_BNT_Next", (HX1 - 18 - 110, HY0 + 410, 110, 34), "NEXT >"))
    bn.add(bbv)

    mv = frame("FI_BNT_MineView", (HX0, HY0 + 80, W, HY1 - HY0 - 80), visible=0)
    mv.add(text("FI_BNT_MineLabel", (X0, HY0 + 86, XW, 14), "BOUNTIES YOU POSTED OR CLAIMED", "textDim", FONT_S))
    lst, n_bmine = row_list("FI_BNT_Mine", X0, HY0 + 106, XW, 330, 34, 6)
    mv.add(lst)
    bn.add(mv)

    pv = frame("FI_BNT_PostView", (HX0, HY0 + 80, W, HY1 - HY0 - 80), visible=0)
    fw = 430
    pv.add(box_panel("FI_BNT_FormPane", (X0, HY0 + 84, fw, 350), "card", "line"))
    pv.add(text("FI_BNT_FormTitle", (X0 + 16, HY0 + 96, fw - 32, 20), "NEW BOUNTY", "textBright", FONT_L))
    pv.add(text_input("FI_BNT_TargetInput", (X0 + 16, HY0 + 128, fw - 32, 36), "Target player name"))
    pv.add(text_input("FI_BNT_RewardInput", (X0 + 16, HY0 + 172, fw - 32, 36), "Reward (max 40 characters)"))
    pv.add(text_input("FI_BNT_ReasonInput", (X0 + 16, HY0 + 216, fw - 32, 36), "Reason, last seen location..."))
    pv.add(button("FI_BNT_ServerToggle", (X0 + 16, HY0 + 260, fw - 32, 32), "SERVER BOUNTY: OFF"))
    pv.add(button("FI_BNT_Post", (X0 + 16, HY0 + 300, fw - 32, 38), "POST BOUNTY"))
    pv.add(text("FI_BNT_PostStatus", (X0 + 16, HY0 + 348, fw - 32, 15), "", "text", FONT_M))
    pv.add(text("FI_BNT_PostHint", (X0 + 16, HY0 + 410, fw - 32, 14), "Bounties expire automatically. An active bounty limit applies.", "textDim", FONT_S))
    ix = X0 + fw + 16
    iw2 = HX1 - 18 - ix
    pv.add(box_panel("FI_BNT_InfoPane", (ix, HY0 + 84, iw2, 350), "card", "lineDim"))
    pv.add(text("FI_BNT_InfoTitle", (ix + 14, HY0 + 96, iw2 - 28, 20), "HOW IT WORKS", "textBright", FONT_L))
    pv.add(mtext("FI_BNT_InfoText", (ix + 14, HY0 + 128, iw2 - 28, 290),
                 "1. Post a bounty with the target, reward and reason.\n\n2. A hunter claims it with a proof note (where, when, how).\n\n3. You confirm or reject the claim from MY BOUNTIES.\n\n4. Rewards are paid in person. Honour system - use reputation.", "text", FONT_M))
    bn.add(pv)

    bp = frame("FI_BNT_Popup", (HX0, HY0, W, HY1 - HY0), visible=0)
    bp.add(panel("FI_BNT_PopupDim", (HX0, HY0, W, HY1 - HY0), rgb(0, 0, 0, 170)))
    bp.add(hit("FI_BNT_PopupShade", (HX0, HY0, W, HY1 - HY0)))
    dw, dh = 520, 424
    dx = HX0 + (W - dw) / 2
    dy = HY0 + 12
    dlg = frame("FI_BNT_Dialog", (dx, dy, dw, dh))
    dlg.add(panel("FI_BNT_Dialog_BG", (dx, dy, dw, dh), C["panel"]), border("FI_BNT_Dialog_Bd", (dx, dy, dw, dh), "lineBright", 2))
    dlg.add(box_panel("FI_BNT_PopupIconPane", (dx + 18, dy + 14, 56, 56), "card", "lineDim"))
    dlg.add(image("FI_BNT_PopupIcon", (dx + 24, dy + 20, 44, 44), "ic_bounty", "text"))
    dlg.add(text("FI_BNT_PopupKind", (dx + 86, dy + 14, dw - 160, 14), "PLAYER BOUNTY", "accent", FONT_S))
    dlg.add(button("FI_BNT_PopupClose", (dx + dw - 18 - 40, dy + 10, 40, 30), "X"))
    dlg.add(text("FI_BNT_PopupTarget", (dx + 86, dy + 32, dw - 104, 24), "TARGET", "textBright", FONT_L))
    dlg.add(text("FI_BNT_PopupReward", (dx + 86, dy + 60, dw - 104, 16), "REWARD: --", "text", FONT_M))
    dlg.add(text("FI_BNT_PopupPoster", (dx + 18, dy + 86, dw - 36, 15), "POSTED BY: --", "text", FONT_S))
    dlg.add(text("FI_BNT_PopupStatus", (dx + 18, dy + 106, dw - 36, 15), "STATUS: --", "text", FONT_S))
    dlg.add(text("FI_BNT_PopupPosted", (dx + 18, dy + 126, dw - 36, 15), "POSTED: --", "textDim", FONT_S))
    dlg.add(hline("FI_BNT_PopupRule", dx + 18, dy + 150, dw - 36, "lineDim", 1))
    dlg.add(box_panel("FI_BNT_PopupReasonPane", (dx + 18, dy + 160, dw - 36, 70), "card", "lineDim"))
    dlg.add(mtext("FI_BNT_PopupReason", (dx + 30, dy + 168, dw - 60, 56), "No reason given.", "text", FONT_M))
    dlg.add(text("FI_BNT_PopupClaim", (dx + 18, dy + 238, dw - 36, 15), "", "warn", FONT_S))
    vs = frame("FI_BNT_PopupViewer", (dx, dy + 258, dw, 156))
    vs.add(text_input("FI_BNT_ClaimNote", (dx + 18, dy + 262, dw - 36, 36), "Proof for the poster: where, when, how..."))
    half = (dw - 36 - 10) / 2
    vs.add(button("FI_BNT_PopupClaimBtn", (dx + 18, dy + 306, half, 38), "CLAIM BOUNTY"))
    vs.add(button("FI_BNT_PopupContact", (dx + 28 + half, dy + 306, half, 38), "CONTACT POSTER"))
    vs.add(button("FI_BNT_PopupAdminRemove", (dx + 18, dy + 352, dw - 36, 36), "REMOVE BOUNTY (ADMIN)"))
    dlg.add(vs)
    ow = frame("FI_BNT_PopupOwner", (dx, dy + 258, dw, 156), visible=0)
    ow.add(button("FI_BNT_PopupConfirm", (dx + 18, dy + 262, half, 38), "CONFIRM CLAIM"))
    ow.add(button("FI_BNT_PopupReject", (dx + 28 + half, dy + 262, half, 38), "REJECT CLAIM"))
    ow.add(button("FI_BNT_PopupContactClaimer", (dx + 18, dy + 308, half, 36), "CONTACT HUNTER"))
    ow.add(button("FI_BNT_PopupCancel", (dx + 28 + half, dy + 308, half, 36), "CANCEL BOUNTY"))
    dlg.add(ow)
    bp.add(dlg)
    bn.add(bp)
    host.add(bn)

    # DRIVES -----------------------------------------------------------
    dv = frame("FI_DRV_Root", (HX0, HY0, W, HY1 - HY0), visible=0)
    dv.add(box_panel("FI_DRV_Pane", (HX0, HY0, W, HY1 - HY0)))
    dv.add(text("FI_DRV_Title", (HX0 + 18, HY0 + 14, 500, 24), "DRIVES / DATA PORTS", "textBright", FONT_L))
    dv.add(text("FI_DRV_Subtitle", (HX0 + 18, HY0 + 45, W - 180, 16), "INSERT A DRIVE INTO YOUR PDA'S DATA PORTS", "text", FONT_M))
    dv.add(button("FI_DRV_Refresh", (HX1 - 18 - 132, HY0 + 15, 132, 36), "REFRESH"))
    dv.add(hline("FI_DRV_Rule", HX0 + 18, HY0 + 72, W - 36, "line", 1))
    X0 = HX0 + 18
    XW = W - 36
    cw = (XW - 12) / 2
    y0 = HY0 + 84
    ch = 350
    specs = [("Intel", "INTEL DRIVE", "ic_drive"), ("Enc", "ENCRYPTED DRIVE", "ic_lock")]
    for idx, (key, title, icon) in enumerate(specs):
        cx = X0 + idx * (cw + 12)
        pre = "FI_DRV_" + key
        dv.add(box_panel(pre + "Pane", (cx, y0, cw, ch), "card", "line"))
        dv.add(image(pre + "Icon", (cx + 14, y0 + 14, 36, 36), icon, "text"))
        dv.add(text(pre + "Name", (cx + 60, y0 + 14, cw - 74, 18), title, "textBright", FONT_L))
        dv.add(text(pre + "State", (cx + 60, y0 + 36, cw - 74, 14), "NO DRIVE", "textDim", FONT_S))
        dv.add(hline(pre + "Rule", cx + 14, y0 + 60, cw - 28, "lineDim", 1))
        dv.add(mtext(pre + "Summary", (cx + 14, y0 + 70, cw - 28, 66), "Insert a drive.", "text", FONT_M))
        bw_ = cw - 28
        if key == "Intel":
            dv.add(button("FI_DRV_IntelRead", (cx + 14, y0 + 150, bw_, 34), "READ INTEL"))
            dv.add(mtext("FI_DRV_IntelHint", (cx + 14, y0 + 198, bw_, 60), "Recovered field intel behind a one-time cipher. It can be decrypted once; the drive burns out when you close the file.", "textDim", FONT_S))
        else:
            dv.add(button("FI_DRV_EncOpen", (cx + 14, y0 + 150, bw_, 34), "OPEN DRIVE"))
            dv.add(button("FI_DRV_EncWrite", (cx + 14, y0 + 192, bw_, 34), "WRITE DATA..."))
            dv.add(button("FI_DRV_EncWipe", (cx + 14, y0 + 234, bw_, 34), "WIPE DRIVE"))
            dv.add(mtext("FI_DRV_EncHint", (cx + 14, y0 + 282, bw_, 60), "Write once: holders can open or wipe it, never add to it. Stored data degrades a few days after writing.", "textDim", FONT_S))


    # ---- Encrypted Drive file browser (reader)
    def overlay_head(prefix, kind, title):
        o = frame(prefix, (HX0, HY0, W, HY1 - HY0), visible=0)
        o.add(hit(prefix + "Shade", (HX0, HY0, W, HY1 - HY0)))
        o.add(panel(prefix + "BG", (HX0, HY0, W, HY1 - HY0), C["panel"]))
        o.add(border(prefix + "Bd", (HX0, HY0, W, HY1 - HY0), "lineBright", 2))
        o.add(image(prefix + "Icon", (HX0 + 18, HY0 + 16, 30, 30), "ic_lock", "text"))
        o.add(text(prefix + "Kind", (HX0 + 58, HY0 + 12, 420, 14), kind, "accent", FONT_S))
        o.add(text(prefix + "Title", (HX0 + 58, HY0 + 28, W - 290, 22), title, "textBright", FONT_L))
        o.add(button(prefix + "Close", (HX1 - 18 - 40, HY0 + 14, 40, 32), "X"))
        o.add(text(prefix + "Info", (HX0 + 18, HY0 + 58, W - 36, 14), "", "textDim", FONT_S))
        o.add(hline(prefix + "Rule", HX0 + 18, HY0 + 78, W - 36, "line", 1))
        return o

    br = overlay_head("FI_DRV_Br", "ENCRYPTED DRIVE  //  READ-ONLY", "DRIVE:")
    br.add(button("FI_DRV_BrBack", (HX1 - 18 - 40 - 8 - 100, HY0 + 14, 100, 32), "BACK"))
    bx0, by0, bw, bh = HX0 + 18, HY0 + 90, W - 36, HY1 - 14 - (HY0 + 90)

    fv = frame("FI_DRV_BrFolders", (bx0, by0, bw, bh))
    tw, th = (bw - 2 * 16) / 3, 170
    ty = by0 + 34
    for i, (key, label, glyph) in enumerate([("Conv", "CONVERSATIONS", "ic_messages"), ("Group", "GROUP CONVERSATIONS", "ic_groups"), ("Mark", "IMPORTANT MARKERS", "ic_map")]):
        tx = bx0 + i * (tw + 16)
        nm = "FI_DRV_BrDir" + key
        tile = frame(nm + "_Box", (tx, ty, tw, th))
        tile.add(panel(nm + "_BG", (tx, ty, tw, th), C["input"]), border(nm + "_Bd", (tx, ty, tw, th), "line", 2))
        tile.add(image(nm + "_Icon", (tx + tw / 2 - 40, ty + 18, 80, 80), "ic_folder", "text"))
        tile.add(image(nm + "_Glyph", (tx + tw / 2 - 15, ty + 50, 30, 30), glyph, "lcd"))
        tile.add(text(nm + "_Label", (tx + 8, ty + 110, tw - 16, 18), label, "text", FONT_M, "center"))
        tile.add(text(nm + "_Meta", (tx + 8, ty + 136, tw - 16, 14), "0 FILES", "textDim", FONT_S, "center"))
        tile.add(hit(nm, (tx, ty, tw, th)))
        fv.add(tile)
    fv.add(text("FI_DRV_BrFoldersHint", (bx0, ty + th + 26, bw, 16), "Select a folder to browse its files.", "textDim", FONT_M, "center"))
    br.add(fv)

    fl = frame("FI_DRV_BrFiles", (bx0, by0, bw, bh), visible=0)
    lst, _ = row_list("FI_DRV_BrList", bx0, by0, bw, bh, 34, 6, True, 170)
    fl.add(lst)
    br.add(fl)

    cv = frame("FI_DRV_BrChatView", (bx0, by0, bw, bh), visible=0)
    area = (bx0, by0, bw - 30, bh)
    ca = frame("FI_DRV_BrChat_Cards", area, clipchildren=1, ignorepointer=1)
    cy = area[1]
    for i in range(12):
        ca.add(card("FI_DRV_BrChat", i, (area[0], cy, area[2], 60)))
        cy += 71
    cv.add(ca)
    cv.add(scrollbar("FI_DRV_BrChat", bx0 + bw - 17, by0, bh))
    br.add(cv)

    av = frame("FI_DRV_BrAct", (bx0, by0, bw, bh), visible=0)
    aw_, ah_ = 460, 250
    ax, ay = bx0 + (bw - aw_) / 2, by0 + 30
    av.add(box_panel("FI_DRV_BrActPane", (ax, ay, aw_, ah_), "card", "line"))
    av.add(image("FI_DRV_BrActIcon", (ax + aw_ / 2 - 24, ay + 18, 48, 48), "ic_map", "text"))
    av.add(text("FI_DRV_BrActName", (ax + 16, ay + 76, aw_ - 32, 22), "MARKERS", "textBright", FONT_L, "center"))
    av.add(text("FI_DRV_BrActMeta", (ax + 16, ay + 104, aw_ - 32, 16), "", "text", FONT_M, "center"))
    bw2 = (aw_ - 32 - 12) / 2
    av.add(button("FI_DRV_BrImport", (ax + 16, ay + 136, bw2, 36), "IMPORT TO MY MAP"))
    av.add(button("FI_DRV_BrView", (ax + 16 + bw2 + 12, ay + 136, bw2, 36), "VIEW MARKERS"))
    av.add(mtext("FI_DRV_BrActNote", (ax + 16, ay + 186, aw_ - 32, 50), "", "textDim", FONT_S))
    br.add(av)

    mv = frame("FI_DRV_BrMarks", (bx0, by0, bw, bh), visible=0)
    lw_ = 250
    mlst, _ = row_list("FI_DRV_BrMarkList", bx0, by0, lw_, bh - 46, 30, 5, True, 70)
    mv.add(mlst)
    mv.add(button("FI_DRV_BrImport2", (bx0, by0 + bh - 36, lw_, 36), "IMPORT TO MY MAP"))
    mx = bx0 + lw_ + 16
    mbox = (mx, by0, bx0 + bw - mx, bh)
    mv.add(panel("FI_DRV_BrMapBG", mbox, C["input"]))
    mv.add(N("MapWidgetClass", "FI_DRV_BrMap", (mx + 2, by0 + 2, mbox[2] - 4, bh - 4), dict(clipchildren=1)))
    mv.add(border("FI_DRV_BrMapBd", mbox, "line", 2))
    br.add(mv)

    xv = frame("FI_DRV_BrCorrupt", (bx0, by0, bw, bh), visible=0)
    xv.add(image("FI_DRV_BrCorruptIcon", (bx0 + bw / 2 - 28, by0 + 36, 56, 56), "ic_warning", "warn"))
    xv.add(mtext("FI_DRV_BrCorruptText", (bx0 + 60, by0 + 110, bw - 120, bh - 130), "", "warn", FONT_L))
    br.add(xv)

    br.add(text("FI_DRV_BrLoading", (bx0, by0 + bh / 2 - 10, bw, 20), "READING DRIVE...", "text", FONT_M, "center"))
    dv.add(br)

    # ---- Encrypted Drive writer
    wr = overlay_head("FI_DRV_Wr", "ENCRYPTED DRIVE  //  WRITE ONCE", "SELECT DATA TO WRITE")
    tab_w = 176
    for i, (key, label) in enumerate([("Conv", "CONVERSATIONS"), ("Group", "GROUP CHATS"), ("Mark", "MARKERS")]):
        wr.add(button("FI_DRV_WrTab" + key, (HX0 + 18 + i * (tab_w + 8), HY0 + 88, tab_w, 30), label))
    c0x, c0w = HX0 + 18, 190
    c1x, c1w = c0x + c0w + 12, 300
    c2x = c1x + c1w + 12
    c2w = HX1 - 18 - c2x
    top = HY0 + 128
    wr.add(text("FI_DRV_WrSrcLabel", (c0x, top, c0w, 14), "CONVERSATIONS", "textDim", FONT_S))
    slst, _ = row_list("FI_DRV_WrSrc", c0x, top + 18, c0w, HY1 - 14 - (top + 18), 30, 4, True, 34)
    wr.add(slst)

    wr.add(text("FI_DRV_WrMsgLabel", (c1x, top, c1w, 14), "SELECT MESSAGES", "textDim", FONT_S))
    mlst2, _ = row_list("FI_DRV_WrMsg", c1x, top + 18, c1w, 196, 24, 3, True, 44)
    wr.add(mlst2)
    qw = (c1w - 4 * 4) / 5
    for i, (key, label) in enumerate([("Last10", "LAST 10"), ("Last25", "LAST 25"), ("Last50", "LAST 50"), ("All", "ALL"), ("Clear", "CLEAR")]):
        wr.add(button("FI_DRV_Wr" + key, (c1x + i * (qw + 4), top + 222, qw, 26), label, None, 12))
    wr.add(text("FI_DRV_WrSel", (c1x, top + 254, c1w, 14), "Click a first and a last message.", "textDim", FONT_S))
    wr.add(button("FI_DRV_WrAdd", (c1x, HY1 - 14 - 34, c1w, 34), "ADD TO DRIVE"))

    wr.add(text("FI_DRV_WrFilesLabel", (c2x, top, c2w, 14), "DRIVE CONTENTS  0 / 12", "textDim", FONT_S))
    flst, _ = row_list("FI_DRV_WrFiles", c2x, top + 18, c2w, 196, 28, 4, True, 46)
    wr.add(flst)
    wr.add(button("FI_DRV_WrRemove", (c2x, top + 222, c2w, 26), "REMOVE FILE", None, 12))
    wr.add(text("FI_DRV_WrCommitHint", (c2x, top + 254, c2w, 14), "Read-only once written.", "textDim", FONT_S))
    wr.add(button("FI_DRV_WrCommit", (c2x, HY1 - 14 - 34, c2w, 34), "WRITE TO DRIVE"))
    dv.add(wr)

    rd = frame("FI_DRV_Reader", (HX0, HY0, W, HY1 - HY0), visible=0)
    rd.add(panel("FI_DRV_ReaderDim", (HX0, HY0, W, HY1 - HY0), rgb(0, 0, 0, 170)))
    rd.add(hit("FI_DRV_ReaderShade", (HX0, HY0, W, HY1 - HY0)))
    dw, dh = 580, 410
    dx = HX0 + (W - dw) / 2
    dy = HY0 + 20
    rdl = frame("FI_DRV_ReaderDialog", (dx, dy, dw, dh))
    rdl.add(panel("FI_DRV_ReaderDialog_BG", (dx, dy, dw, dh), C["panel"]), border("FI_DRV_ReaderDialog_Bd", (dx, dy, dw, dh), "lineBright", 2))
    rdl.add(text("FI_DRV_ReaderKind", (dx + 18, dy + 14, dw - 90, 14), "DRIVE", "accent", FONT_S))
    rdl.add(button("FI_DRV_ReaderClose", (dx + dw - 18 - 40, dy + 10, 40, 30), "X"))
    rdl.add(text("FI_DRV_ReaderTitle", (dx + 18, dy + 36, dw - 36, 24), "TITLE", "textBright", FONT_L))
    rdl.add(hline("FI_DRV_ReaderRule", dx + 18, dy + 70, dw - 36, "lineDim", 1))
    rdl.add(box_panel("FI_DRV_ReaderBodyPane", (dx + 18, dy + 80, dw - 36, 270), "card", "lineDim"))
    rdl.add(mtext("FI_DRV_ReaderBody", (dx + 30, dy + 90, dw - 60, 250), "", "text", FONT_M))
    rdl.add(button("FI_DRV_ReaderAction", (dx + 18, dy + 360, dw - 36, 36), "CLOSE"))
    rd.add(rdl)
    dv.add(rd)

    # ---- Intel decryption: one-time warning, then a 10 s progress bar
    dc = frame("FI_DRV_Dec", (HX0, HY0, W, HY1 - HY0), visible=0)
    dc.add(panel("FI_DRV_DecDim", (HX0, HY0, W, HY1 - HY0), rgb(0, 0, 0, 170)))
    dc.add(hit("FI_DRV_DecShade", (HX0, HY0, W, HY1 - HY0)))
    dw, dh = 540, 300
    dx = HX0 + (W - dw) / 2
    dy = HY0 + 60
    dd = frame("FI_DRV_DecDialog", (dx, dy, dw, dh))
    dd.add(panel("FI_DRV_DecDialog_BG", (dx, dy, dw, dh), C["panel"]), border("FI_DRV_DecDialog_Bd", (dx, dy, dw, dh), "lineBright", 2))
    dd.add(image("FI_DRV_DecIcon", (dx + 20, dy + 18, 40, 40), "ic_warning", "warn"))
    dd.add(text("FI_DRV_DecKind", (dx + 74, dy + 16, dw - 94, 14), "INTEL DRIVE  //  ONE-TIME CIPHER", "accent", FONT_S))
    dd.add(text("FI_DRV_DecTitle", (dx + 74, dy + 34, dw - 94, 24), "SINGLE-USE DECRYPTION", "textBright", FONT_L))
    dd.add(hline("FI_DRV_DecRule", dx + 20, dy + 70, dw - 40, "lineDim", 1))
    dd.add(mtext("FI_DRV_DecBody", (dx + 20, dy + 80, dw - 40, 86), "", "text", FONT_S))
    bar = (dx + 20, dy + 174, dw - 40, 22)
    dd.add(panel("FI_DRV_DecBarBG", bar, C["input"]))
    dd.add(border("FI_DRV_DecBarBd", bar, "line", 1))
    dd.add(panel("FI_DRV_DecFill", (bar[0] + 3, bar[1] + 3, bar[2] - 6, bar[3] - 6), C["accent"]))
    dd.add(text("FI_DRV_DecPct", (dx + 20, dy + 202, dw - 40, 16), "", "textBright", FONT_M))
    dd.add(text("FI_DRV_DecHex", (dx + 20, dy + 222, dw - 40, 14), "", "textDim", FONT_S))
    dbw = (dw - 40 - 12) / 2
    dd.add(button("FI_DRV_DecGo", (dx + 20, dy + dh - 54, dbw, 38), "DECRYPT"))
    dd.add(button("FI_DRV_DecCancel", (dx + 20 + dbw + 12, dy + dh - 54, dbw, 38), "CANCEL"))
    dc.add(dd)
    dv.add(dc)
    host.add(dv)

    mp = frame("FI_MAP_Root", (HX0, HY0, W, HY1 - HY0), visible=0)
    mp.add(box_panel("FI_MAP_Pane", (HX0, HY0, W, HY1 - HY0)))
    mp.add(text("FI_MAP_Title", (HX0 + 18, HY0 + 14, W - 36, 24), "MAP / FIELD NAVIGATION", "textBright", FONT_L))
    mp.add(text("FI_MAP_Coords", (HX0 + 18, HY0 + 18, W - 36, 18), "GRID --- ---", "textBright", FONT_M, "right"))
    mp.add(text("FI_MAP_Subtitle", (HX0 + 18, HY0 + 45, W - 36, 16), "LOADING TERRAIN...", "text", FONT_M))
    mp.add(hline("FI_MAP_Rule", HX0 + 18, HY0 + 72, W - 36, "line", 1))
    X0 = HX0 + 18
    mw, mh = 520, 350
    mapbox = (X0, HY0 + 84, mw, mh)
    mp.add(panel("FI_MAP_BG", mapbox, C["input"]))
    # Nothing can be drawn over a MapWidget in game (not as a sibling, not as
    # a child), so markers are engine map marks with .paa icons and the GRID
    # readout sits in the title row (v8.4.2).
    mp.add(N("MapWidgetClass", "FI_MAP_Widget", (X0 + 2, HY0 + 86, mw - 4, mh - 4), dict(clipchildren=1)))
    mp.add(border("FI_MAP_Bd", mapbox, "line", 2))
    rx = X0 + mw + 16
    rw = HX1 - 18 - rx
    mp.add(text("FI_MAP_MarksLabel", (rx, HY0 + 86, rw, 14), "MARKERS", "textDim", FONT_S))
    lst, n_marks = row_list("FI_MAP_Marks", rx, HY0 + 104, rw, 180, 30, 5)
    mp.add(lst)
    mp.add(text_input("FI_MAP_MarkName", (rx, HY0 + 292, rw, 34), "Marker name"))
    mp.add(button("FI_MAP_AddHere", (rx, HY0 + 332, rw, 30), "MARK MY POSITION"))
    mp.add(button("FI_MAP_Center", (rx, HY0 + 366, rw, 30), "CENTER ON ME"))
    hw = (rw - 8) / 2
    mp.add(button("FI_MAP_Rename", (rx, HY0 + 400, hw, 30), "RENAME"))
    mp.add(button("FI_MAP_Delete", (rx + hw + 8, HY0 + 400, hw, 30), "DELETE"))
    host.add(mp)


    sy = frame("FI_SYS_Root", (HX0, HY0, W, HY1 - HY0), visible=0)
    sy.add(box_panel("FI_SYS_Pane", (HX0, HY0, W, HY1 - HY0)))
    sy.add(*page_header("FI_SYS", HX0, HY0, W, "SYSTEM / TERMINAL CONTROL", "UNIT STATUS, DISPLAY, COMPASS, S.O.S AND SOUNDS"))
    iw = 246
    iy = HY0 + 86
    ih = HY1 - 14 - iy
    sy.add(box_panel("FI_SYS_InfoPane", (HX0 + 18, iy, iw, ih), "card", "line"))
    sy.add(text("FI_SYS_InfoTitle", (HX0 + 32, iy + 12, iw - 28, 22), "UNIT & NETWORK", "textBright", FONT_L))
    sy.add(hline("FI_SYS_InfoRule", HX0 + 32, iy + 42, iw - 28, "lineDim", 1))
    sy.add(mtext("FI_SYS_Info", (HX0 + 32, iy + 52, iw - 28, ih - 108), "UNIT: FI-PDA-01\nPDA ID: --\nMEMORY: --\nCONTACTS ONLINE: --\nPDA USERS: --\nUNREAD: --\nBATTERY: --\nCLOCK: --", "text", FONT_M))
    sy.add(button("FI_SYS_Logout", (HX0 + 32, iy + ih - 48, iw - 28, 36), "LOG OUT"))

    rx = HX0 + 18 + iw + 14
    rw = HX1 - 18 - rx
    tw4 = (rw - 24) / 4
    for i, (key, label) in enumerate([("Display", "DISPLAY"), ("Compass", "COMPASS"), ("Sos", "S.O.S"), ("Sound", "SOUNDS")]):
        sy.add(button("FI_SYS_Tab" + key, (rx + i * (tw4 + 8), iy, tw4, 30), label))
    cy0 = iy + 40
    ch = HY1 - 14 - cy0

    def stepper(root, prefix, x, y, w, label):
        root.add(text(prefix + "Label", (x, y + 7, 170, 16), label, "text", FONT_M))
        bx = x + w - 214
        root.add(button(prefix + "Prev", (bx, y, 34, 28), "<"))
        root.add(panel(prefix + "ValBG", (bx + 40, y, 134, 28), C["input"]))
        root.add(border(prefix + "ValBd", (bx + 40, y, 134, 28), "lineDim", 1))
        root.add(text(prefix + "Value", (bx + 44, y + 6, 126, 16), "--", "textBright", FONT_M, "center"))
        root.add(button(prefix + "Next", (bx + 180, y, 34, 28), ">"))

    # DISPLAY
    dp = frame("FI_SYS_DisplayView", (rx, cy0, rw, ch))
    dp.add(text("FI_SYS_PresetLabel", (rx, cy0, rw, 14), "THEME PRESET", "textDim", FONT_S))
    pw = (rw - 4 * 8) / 5
    for i in range(10):
        px = rx + (i % 5) * (pw + 8)
        py = cy0 + 18 + (i // 5) * 48
        nm = f"FI_SYS_Pre{i}"
        tile = frame(nm + "_Box", (px, py, pw, 42))
        tile.add(panel(nm + "_BG", (px, py, pw, 42), C["input"]), border(nm + "_Bd", (px, py, pw, 42), "line", 2))
        tile.add(panel(nm + "Swatch", (px + 6, py + 6, pw - 12, 9), rgb(255, 255, 255)))
        tile.add(text(nm + "_Label", (px + 3, py + 20, pw - 6, 15), "PRESET", "text", FONT_S, "center"))
        tile.add(hit(nm, (px, py, pw, 42)))
        dp.add(tile)
    sy_ = cy0 + 124
    for j, (key, label) in enumerate([("Hue", "COLOR HUE"), ("Sat", "SATURATION"), ("Bright", "BRIGHTNESS"), ("Back", "BACKLIGHT")]):
        stepper(dp, "FI_SYS_" + key, rx, sy_ + j * 36, rw, label)
    dp.add(button("FI_SYS_DisplayReset", (rx, cy0 + ch - 32, 190, 32), "RESET DISPLAY"))
    dp.add(mtext("FI_SYS_DisplayHint", (rx + 204, cy0 + ch - 34, rw - 204, 36), "Changes apply instantly and are saved on this computer.", "textDim", FONT_S))
    sy.add(dp)

    # COMPASS
    cp = frame("FI_SYS_CompassView", (rx, cy0, rw, ch), visible=0)
    rows = [("CmpStyle", "STYLE"), ("CmpOn", "COMPASS HUD"), ("CmpPos", "POSITION"), ("CmpSize", "SIZE"), ("CmpAlpha", "OPACITY"),
            ("CmpColor", "COLOR"), ("CmpHue", "CUSTOM HUE"), ("CmpMarks", "SHOW MARKERS"), ("CmpDist", "SHOW DISTANCES"), ("CmpDeg", "BEARING NUMBERS")]
    for j, (key, label) in enumerate(rows):
        stepper(cp, "FI_SYS_" + key, rx, cy0 + j * 30, rw, label)
    sy.add(cp)

    # SOUNDS (v8.5): which incoming traffic plays a sound, and muted chats
    snd = frame("FI_SYS_SoundView", (rx, cy0, rw, ch), visible=0)
    stepper(snd, "FI_SYS_SndChats", rx, cy0, rw, "CHAT SOUNDS")
    snd.add(text("FI_SYS_SndForLabel", (rx, cy0 + 38, rw, 14), "PLAY A SOUND FOR", "textDim", FONT_S))
    gw = (rw - 8) / 2
    for i, (key, label) in enumerate([("SndDirect", "DIRECT MESSAGES"), ("SndChannels", "OPEN CHANNELS"), ("SndGroups", "GROUP CHANNELS"),
                                      ("SndAnn", "ANNOUNCEMENTS"), ("SndBounty", "BOUNTY BOARD"), ("SndSos", "S.O.S ALARM")]):
        bx = rx + (i % 2) * (gw + 8)
        by = cy0 + 56 + (i // 2) * 36
        snd.add(button("FI_SYS_" + key, (bx, by, gw, 30), label))
    snd.add(text("FI_SYS_SndMutedLabel", (rx, cy0 + 168, rw, 14), "MUTED CHATS", "textDim", FONT_S))
    mlst, _ = row_list("FI_SYS_SndMuted", rx, cy0 + 186, rw, 86, 26, 4, True, 120)
    snd.add(mlst)
    snd.add(button("FI_SYS_SndUnmute", (rx, cy0 + ch - 32, gw, 32), "UNMUTE SELECTED"))
    snd.add(button("FI_SYS_SndUnmuteAll", (rx + gw + 8, cy0 + ch - 32, gw, 32), "UNMUTE ALL"))
    sy.add(snd)

    # S.O.S
    sp = frame("FI_SYS_SosView", (rx, cy0, rw, ch), visible=0)
    stepper(sp, "FI_SYS_SosMode", rx, cy0, rw, "SEND S.O.S TO")
    sp.add(text("FI_SYS_SosListLabel", (rx, cy0 + 38, rw, 14), "SELECT UP TO 5 CONTACTS", "textDim", FONT_S))
    slst, _ = row_list("FI_SYS_SosList", rx, cy0 + 56, rw, 162, 28, 5, True, 90)
    sp.add(slst)
    sp.add(button("FI_SYS_SosSend", (rx, cy0 + 228, 200, 40), "SEND S.O.S"))
    sp.add(mtext("FI_SYS_SosStatus", (rx + 214, cy0 + 228, rw - 214, 40), "", "text", FONT_S))
    sp.add(text("FI_SYS_SosHint", (rx, cy0 + 280, rw, 14), "Burns out this PDA, its battery and drives.  Hotkey: double-tap S.O.S.", "textDim", FONT_S))
    sy.add(sp)

    # S.O.S confirmation
    sc = frame("FI_SYS_SosConfirm", (HX0, HY0, W, HY1 - HY0), visible=0)
    sc.add(hit("FI_SYS_SosShade", (HX0, HY0, W, HY1 - HY0)))
    sc.add(panel("FI_SYS_SosDim", (HX0, HY0, W, HY1 - HY0), rgb(0, 0, 0, 180)))
    dw, dh = 480, 250
    dx, dy = HX0 + (W - dw) / 2, HY0 + 90
    sc.add(panel("FI_SYS_SosDlgBG", (dx, dy, dw, dh), C["panel"]))
    sc.add(border("FI_SYS_SosDlgBd", (dx, dy, dw, dh), "lineBright", 2))
    sc.add(image("FI_SYS_SosIcon", (dx + dw / 2 - 26, dy + 16, 52, 52), "ic_warning", "warn"))
    sc.add(text("FI_SYS_SosTitle", (dx + 16, dy + 76, dw - 32, 24), "SEND S.O.S SIGNAL?", "textBright", FONT_L, "center"))
    sc.add(mtext("FI_SYS_SosBody", (dx + 24, dy + 108, dw - 48, 76), "", "text", FONT_S))
    bw2 = (dw - 48 - 12) / 2
    sc.add(button("FI_SYS_SosConfirmSend", (dx + 24, dy + dh - 52, bw2, 36), "SEND S.O.S"))
    sc.add(button("FI_SYS_SosConfirmCancel", (dx + 24 + bw2 + 12, dy + dh - 52, bw2, 36), "CANCEL"))
    sy.add(sc)
    host.add(sy)

    disp.add(host)

    # ---- login screen (covers the whole display while the PDA is locked)
    lg = frame("FI_LOGIN_Root", (0, 0, DW, DH), visible=0)
    lg.add(hit("FI_LOGIN_Shade", (0, 0, DW, DH)))
    lg.add(image("FI_LOGIN_BG", (0, 0, DW, DH), "ui_bezel", "lcd"))   # rounded, like the bezel
    lg.add(border("FI_LOGIN_Frame", (14, 8, DW - 28, DH - 16), "lineDim", 2))
    brand_block(lg, "FI_LOGIN_", (DW - 435) / 2, 20)
    lg.add(text("FI_LOGIN_Os", (14, 92, DW - 28, 15), "FIELD OS v8.8  //  SECURE ACCESS TERMINAL", "textDim", FONT_S, "center"))
    cw_, ch_ = 540, 404
    cx_, cy_ = (DW - cw_) / 2, 118
    lg.add(box_panel("FI_LOGIN_Card", (cx_, cy_, cw_, ch_), "panel", "line"))
    lg.add(image("FI_LOGIN_Icon", (cx_ + 20, cy_ + 16, 36, 36), "ic_lock", "text"))
    lg.add(text("FI_LOGIN_Title", (cx_ + 68, cy_ + 14, cw_ - 88, 24), "AUTHENTICATION REQUIRED", "textBright", FONT_L))
    lg.add(text("FI_LOGIN_Sub", (cx_ + 68, cy_ + 41, cw_ - 88, 15), "THIS PDA IS LOCKED", "text", FONT_S))
    lg.add(hline("FI_LOGIN_Rule", cx_ + 20, cy_ + 66, cw_ - 40, "line", 1))
    lg.add(text("FI_LOGIN_UserLabel", (cx_ + 20, cy_ + 80, 150, 15), "OPERATOR", "textDim", FONT_S))
    lg.add(text("FI_LOGIN_User", (cx_ + 170, cy_ + 78, cw_ - 190, 18), "--", "textBright", FONT_M))
    lg.add(text("FI_LOGIN_DeviceLabel", (cx_ + 20, cy_ + 104, 150, 15), "DEVICE", "textDim", FONT_S))
    lg.add(text("FI_LOGIN_Device", (cx_ + 170, cy_ + 102, cw_ - 190, 18), "FI-PDA-01", "text", FONT_M))
    lg.add(box_panel("FI_LOGIN_StatusPane", (cx_ + 20, cy_ + 130, cw_ - 40, 70), "card", "lineDim"))
    lg.add(mtext("FI_LOGIN_Status", (cx_ + 34, cy_ + 138, cw_ - 68, 56), "No active session.", "text", FONT_S))
    stepper(lg, "FI_LOGIN_Hours", cx_ + 20, cy_ + 212, cw_ - 40, "SESSION LENGTH")
    lg.add(button("FI_LOGIN_Login", (cx_ + 20, cy_ + 254, cw_ - 40, 42), "LOG IN"))
    lbw = (cw_ - 40 - 12) / 2
    lg.add(button("FI_LOGIN_View", (cx_ + 20, cy_ + 304, lbw, 36), "VIEW READ-ONLY"))
    lg.add(button("FI_LOGIN_Power", (cx_ + 20 + lbw + 12, cy_ + 304, lbw, 36), "POWER OFF"))
    lg.add(mtext("FI_LOGIN_Hint", (cx_ + 20, cy_ + 350, cw_ - 40, 44), "A session ends when you log out, when its time runs out or when the server restarts. Anyone holding a logged-in PDA can read it.", "textDim", FONT_S))
    disp.add(lg)

    # ---- device container (script sizes it to a 16:9 pixel box)
    device = N("FrameWidgetClass", "FI_Device", None, dict(), exact="device")
    device.add(N("ImageWidgetClass", "FI_Frame", None, {
        "ignorepointer": 1, "imageTexture": "{4E3729401E914930}FENR_PDA/PDA/gui/pdaframe.edds",
        "mode": "blend", '"src alpha"': 1, "stretch": 1}, exact="full"))
    # Theme-coloured backing for the frame's rounded screen opening (same
    # shape as the cut in pdaframe.edds).  Rect in 1600x900 frame px.
    bz_rect = json.load(open(_os.path.join(TOOLS, "bezel_rect.json")))   # written by make_textures.py
    BEZEL = (bz_rect["x"] / 1600, bz_rect["y"] / 900, bz_rect["w"] / 1600, bz_rect["h"] / 900)
    for name, tex_, col in (("FI_Bezel", "ui_bezel", "lcd"), ("FI_BezelLine", "ui_bezel_line", "lineDim")):
        bz = N("ImageWidgetClass", name, None, {
            "ignorepointer": 1, "image0": f"FENR_PDA/PDA/gui/os/textures/{tex_}.edds", "mode": "blend",
            '"src alpha"': 1, '"no wrap"': 1, "stretch": 1, "color": C[col]}, exact="frac")
        bz.frac = BEZEL
        device.add(bz)
    disp.rect_glass = True
    device.add(disp)
    root = N("FrameWidgetClass", "FI_OS_Root", None, dict(visible=1, inheritalpha=1, keepsafezone=0), exact="root")
    root.add(device)
    counts = dict(bmine=n_bmine, mine=n_mine, adm=n_adm, inbox=n_inbox, ann=n_ann, grp=n_grp, mem=n_mem, con=n_con, cl=n_cl)
    return root, counts


# ------------------------------------------------------------------ serialize
def fmt(v):
    if isinstance(v, tuple):
        return " ".join(fmt(x) for x in v)
    if isinstance(v, float):
        s = f"{v:.5f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    return str(v)


def geom(node, parent_rect):
    """Return attribute string for position/size/alignment."""
    if node.exact == "root":
        return "position 0 0 size 1 1 halign center_ref valign center_ref"
    if node.exact == "device":
        return "position 0 0 size 1600 900 halign center_ref valign center_ref hexactsize 1 vexactsize 1"
    if node.exact == "full":
        return "position 0 0 size 1 1"
    if node.exact == "pxi":
        # image: fractional position (script sets it), pixel size
        return "position 0 0 size 16 16 hexactpos 0 vexactpos 0 hexactsize 1 vexactsize 1"
    if node.exact == "px":
        return "position 0 0 size 16 16 hexactpos 1 vexactpos 1 hexactsize 1 vexactsize 1"
    if node.exact == "frac":
        fx, fy, fw, fh = node.frac
        return f"position {fmt(fx)} {fmt(fy)} size {fmt(fw)} {fmt(fh)}"
    if getattr(node, "rect_glass", False):
        x, y, w, h = GLASS
        return f"position {fmt(x)} {fmt(y)} size {fmt(w)} {fmt(h)}"
    px, py, pw, ph = parent_rect
    if isinstance(node.exact, dict):
        # exact pixel line
        parts = []
        if node.rect is None:
            w = node.exact.get("w")
            h = node.exact.get("h")
            sw = f"{w}" if w else "1"
            sh = f"{h}" if h else "1"
            parts.append(f"position 0 0 size {sw} {sh}")
            parts.append(f"hexactpos 0 vexactpos 0 hexactsize {1 if w else 0} vexactsize {1 if h else 0}")
        else:
            x, y, w, h = node.rect
            rx = (x - px) / pw
            ry = (y - py) / ph
            if "h" in node.exact:
                parts.append(f"position {fmt(rx)} {fmt(ry)} size {fmt(w / pw)} {node.exact['h']}")
                parts.append("hexactpos 0 vexactpos 0 hexactsize 0 vexactsize 1")
            else:
                parts.append(f"position {fmt(rx)} {fmt(ry)} size {node.exact['w']} {fmt(h / ph)}")
                parts.append("hexactpos 0 vexactpos 0 hexactsize 1 vexactsize 0")
        if node.align:
            ha, va = node.align
            if ha != "left":
                parts.append(f"halign {ha}")
            if va != "top":
                parts.append(f"valign {va}")
        return " ".join(parts)
    if node.rect is None:
        return "position 0 0 size 1 1"
    x, y, w, h = node.rect
    return f"position {fmt((x - px) / pw)} {fmt((y - py) / ph)} size {fmt(w / pw)} {fmt(h / ph)}"


def own_rect(node, parent_rect):
    if node.rect is not None and not getattr(node, "rect_glass", False):
        return node.rect
    if getattr(node, "rect_glass", False):
        return (0, 0, DW, DH)
    return parent_rect


BARE = {"style", "mode", '"text halign"', '"text valign"'}


def serialize(node, parent_rect=(0, 0, DW, DH), depth=0):
    ind = " " * depth
    attrs = []
    for k in ("visible",):
        if k in node.attrs:
            attrs.append(f"{k} {fmt(node.attrs[k])}")
    attrs.append(geom(node, parent_rect))
    for k, v in node.attrs.items():
        if k == "visible":
            continue
        if k == "color":
            attrs.append("color " + " ".join(fmt(float(c)) if c not in (0, 1) else str(int(c)) for c in v))
        elif k in BARE:
            attrs.append(f"{k} {v}")
        else:
            attrs.append(f"{k} {fmt(v)}")
    line = f"{ind}{node.cls} {node.name} {{\n{ind} " + " ".join(attrs)
    if node.children:
        mine = own_rect(node, parent_rect)
        if node.exact in ("root", "device"):
            mine = (0, 0, DW, DH)
        kids = "".join(serialize(c, mine, depth + 2) for c in node.children)
        line += f"\n{ind} {{\n{kids}{ind} }}"
    line += f"\n{ind}}}\n"
    return line


def walk(node, out=None):
    out = [] if out is None else out
    out.append(node)
    for c in node.children:
        walk(c, out)
    return out


if __name__ == "__main__":
    root, counts = build()
    names = [n.name for n in walk(root)]
    dup = {x for x in names if names.count(x) > 1}
    assert not dup, dup
    out = sys.argv[1] if len(sys.argv) > 1 else _os.path.join(MOD, "gui", "os", "FI_OS_Shell.layout")
    open(out, "w").write(serialize(root))
    json.dump(counts, open(_os.path.join(BUILD, "counts.json"), "w"))
    print("widgets:", len(names), counts)
