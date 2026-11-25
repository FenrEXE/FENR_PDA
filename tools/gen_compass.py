"""Writes FI_Compass.layout (compass HUD) and FI_SOS_Prompt.layout.
Screen-relative layouts (like FI_Toast.layout); script positions the pooled
compass elements every frame."""
import os as _os
TOOLS = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(TOOLS)
MOD = _os.path.join(REPO, "PDA")
BUILD = _os.path.join(TOOLS, "build")          # generated files (not part of the mod)
_os.makedirs(BUILD, exist_ok=True)


OUT = _os.path.join(MOD, "gui", "os") + _os.sep
TEX = "FENR_PDA/PDA/gui/os/textures/"
FS = "gui/fonts/Metron14"
FM = "gui/fonts/metronlight16"
FL = "gui/fonts/metronlight22"

# reference palette (green), same values as the shell layout
LCD = "0.00784 0.07059 0.04314"
PANEL = "0 0.08627 0.05098"
INPUT = "0 0.04706 0.02745"
LINE = "0.13333 0.54118 0.34510"
LINEB = "0.31373 0.86275 0.58824"
TEXT = "0.58824 0.92549 0.72549"
TEXTB = "0.80392 1 0.88235"
TEXTD = "0.36078 0.71373 0.51765"
ACC = "0.23529 0.84314 0.37255"
WARN = "0.90196 0.66667 0.23529"


def w(cls, name, attrs, kids=None, ind=1):
    pad = " " * ind
    s = f"{pad}{cls} {name} {{\n{pad} {attrs}\n"
    if kids:
        s += f"{pad} {{\n" + "".join(kids) + f"{pad} }}\n"
    s += f"{pad}}}\n"
    return s


def compass():
    """v8.2: one full-screen frame of pooled, pixel-positioned elements.
    FENR_PDA_CompassHud places them for the chosen style (7 styles)."""
    X = "hexactpos 1 vexactpos 1 hexactsize 1 vexactsize 1 ignorepointer 1 inheritalpha 1"
    # Images: fractional position (set by script), exact pixel size.
    XI = "hexactpos 0 vexactpos 0 hexactsize 1 vexactsize 1 ignorepointer 1 inheritalpha 1"
    def panel(name):
        return w("PanelWidgetClass", name, f"visible 0 position 0 0 size 10 10 {X} color {LINE} 1 style rover_sim_colorable", ind=2)
    def image(name, tex, color=TEXT):
        return w("ImageWidgetClass", name, f'visible 0 position 0 0 size 16 16 {XI} image0 "{TEX}{tex}.edds" mode blend "src alpha" 1 "no wrap" 1 stretch 1 color {color} 1', ind=2)
    def text(name, halign="center", font=FS, color=TEXT):
        return w("TextWidgetClass", name, f'visible 0 position 0 0 size 400 16 {X} text "" font "{font}" color {color} 1 "text halign" {halign} "text valign" center', ind=2)
    k = []
    # back to front
    k.append(image("FI_CMP_Disc", "cmp_disc", LCD))
    k.append(image("FI_CMP_Fade", "cmp_fade", LCD))
    for i in range(24):
        k.append(panel(f"FI_CMP_P{i}"))
    k.append(image("FI_CMP_FadeLine", "cmp_fade", LINE))
    k.append(image("FI_CMP_Ring", "cmp_ring", LINE))
    for i in range(72):
        k.append(panel(f"FI_CMP_TS{i}"))
    for i in range(72):
        k.append(panel(f"FI_CMP_T{i}"))
    for i in range(24):
        k.append(text(f"FI_CMP_NS{i}", font=FS))
    for i in range(24):
        k.append(text(f"FI_CMP_N{i}", font=FS))
    for i in range(8):
        k.append(text(f"FI_CMP_LS{i}", font=FS))
    for i in range(8):
        k.append(text(f"FI_CMP_L{i}", font=FS))
    k.append(image("FI_CMP_Arrow", "cmp_arrow", ACC))
    k.append(image("FI_CMP_CaretA", "ic_caret", ACC))
    k.append(image("FI_CMP_CaretB", "cmp_caret_up", ACC))
    k.append(text("FI_CMP_HeadS", font=FM))
    k.append(text("FI_CMP_Head", font=FM))
    k.append(text("FI_CMP_X0", "left", FS))
    k.append(text("FI_CMP_X1", "left", FM))
    k.append(text("FI_CMP_X2", "right", FS))
    k.append(text("FI_CMP_X3", "right", FM))
    for n in ("TagBG", "TagT", "TagB", "TagL", "TagR"):
        k.append(panel("FI_CMP_" + n))
    for i in range(40):
        k.append(image(f"FI_CMP_M{i}", "ic_cmp_pin", WARN))
    for i in range(40):
        k.append(text(f"FI_CMP_MS{i}"))
    for i in range(40):
        k.append(text(f"FI_CMP_MT{i}"))
    for i in range(6):
        k.append(image(f"FI_CMP_S{i}", "ic_cmp_beacon", "0.88235 0.31373 0.27451"))
    for i in range(6):
        k.append(text(f"FI_CMP_STS{i}"))
    for i in range(6):
        k.append(text(f"FI_CMP_ST{i}", color="0.88235 0.31373 0.27451"))
    root = w("FrameWidgetClass", "FI_CMP_Root", "visible 0 position 0 0 size 1 1 ignorepointer 1 inheritalpha 1", k, ind=0)
    open(OUT + "FI_Compass.layout", "w").write(root)


def border(name, color, ind):
    return [
        w("PanelWidgetClass", name + "_T", f"position 0 0 size 1 2 hexactpos 0 vexactpos 0 hexactsize 0 vexactsize 1 color {color} 1 style rover_sim_colorable ignorepointer 1", ind=ind),
        w("PanelWidgetClass", name + "_B", f"position 0 0 size 1 2 hexactpos 0 vexactpos 0 hexactsize 0 vexactsize 1 valign bottom_ref color {color} 1 style rover_sim_colorable ignorepointer 1", ind=ind),
        w("PanelWidgetClass", name + "_L", f"position 0 0 size 2 1 hexactpos 0 vexactpos 0 hexactsize 1 vexactsize 0 color {color} 1 style rover_sim_colorable ignorepointer 1", ind=ind),
        w("PanelWidgetClass", name + "_R", f"position 0 0 size 2 1 hexactpos 0 vexactpos 0 hexactsize 1 vexactsize 0 halign right_ref color {color} 1 style rover_sim_colorable ignorepointer 1", ind=ind),
    ]


def button(name, pos, size, label, ind):
    kids = [
        w("PanelWidgetClass", name + "_BG", f"position 0 0 size 1 1 color {INPUT} 1 style rover_sim_colorable ignorepointer 1", ind=ind + 2),
        w("FrameWidgetClass", name + "_Bd", "position 0 0 size 1 1 ignorepointer 1", border(name + "_Bd", LINE, ind + 4), ind=ind + 2),
        w("TextWidgetClass", name + "_Label", f'position 0 0.25 size 1 0.5 ignorepointer 1 text "{label}" font "{FM}" color {TEXT} 1 "text halign" center "text valign" center', ind=ind + 2),
        w("ButtonWidgetClass", name, 'position 0 0 size 1 1 style Default color 0 0 0 0 text ""', ind=ind + 2),
    ]
    return w("FrameWidgetClass", name + "_Box", f"position {pos} size {size}", kids, ind=ind)


def prompt():
    k = []
    k.append(w("PanelWidgetClass", "FI_SOSP_Dim", "position 0 0 size 1 1 color 0 0 0 0.55 style rover_sim_colorable ignorepointer 1", ind=2))
    dlg = []
    dlg.append(w("PanelWidgetClass", "FI_SOSP_BG", f"position 0 0 size 1 1 color {PANEL} 0.97 style rover_sim_colorable ignorepointer 1", ind=4))
    dlg.append(w("FrameWidgetClass", "FI_SOSP_Bd", "position 0 0 size 1 1 ignorepointer 1", border("FI_SOSP_Bd", LINEB, 6), ind=4))
    dlg.append(w("ImageWidgetClass", "FI_SOSP_Icon", f'position 0 0.06 size 48 48 hexactpos 0 vexactpos 0 hexactsize 1 vexactsize 1 halign center_ref ignorepointer 1 image0 "{TEX}ic_warning.edds" mode blend "src alpha" 1 "no wrap" 1 stretch 1 color {WARN} 1', ind=4))
    dlg.append(w("TextWidgetClass", "FI_SOSP_Title", f'position 0.05 0.3 size 0.9 0.12 ignorepointer 1 text "SEND S.O.S SIGNAL?" font "{FL}" color {TEXTB} 1 "text halign" center "text valign" center', ind=4))
    dlg.append(w("MultilineTextWidgetClass", "FI_SOSP_Body", f'position 0.07 0.44 size 0.86 0.3 ignorepointer 1 text "" font "{FS}" color {TEXT} 1 wrap 1 "exact text" 1', ind=4))
    dlg.append(button("FI_SOSP_Send", "0.06 0.78", "0.42 0.15", "SEND S.O.S", 4))
    dlg.append(button("FI_SOSP_Cancel", "0.52 0.78", "0.42 0.15", "CANCEL", 4))
    k.append(w("FrameWidgetClass", "FI_SOSP_Dialog", "position 0 0 size 0.32 0.3 halign center_ref valign center_ref", dlg, ind=2))
    root = w("FrameWidgetClass", "FI_SOSP_Root", "position 0 0 size 1 1", k, ind=0)
    open(OUT + "FI_SOS_Prompt.layout", "w").write(root)


compass()
prompt()
print("ok")
