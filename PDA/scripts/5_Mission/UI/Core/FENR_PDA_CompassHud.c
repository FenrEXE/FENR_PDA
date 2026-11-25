/*
    Fenrir Industries PDA - Field OS 8.2
    Compass HUD.

    Shown while the player carries a powered, logged-in PDA (and no menu is
    open); a PDA logged in as someone else shows that player's markers.

    Seven styles (SYSTEM > COMPASS > STYLE):
      CLASSIC   boxed strip with a heading tab (the original look)
      TACTICAL  open tape that fades at both ends, 5 degree ticks, boxed heading
      MINIMAL   no background: outlined letters and ticks over the world
      BEZEL     framed instrument with corner brackets, heading and grid readouts
      ARC       curved tape, things shrink and drop away towards the edges
      RADAR     round dial in the corner, markers all around you
      SLIM      a single thin line with small letters

    FI_Compass.layout is a full-screen frame of pooled elements; everything is
    positioned here in screen pixels.  Markers are amber pins / triangles: the
    one nearest the centre shows its name and distance.  S.O.S pings are red
    beacons, pinned to the edge when behind you.
*/
class FENR_PDA_CompassHud
{
    static const int STYLE_CLASSIC = 0;
    static const int STYLE_TACTICAL = 1;
    static const int STYLE_MINIMAL = 2;
    static const int STYLE_BEZEL = 3;
    static const int STYLE_ARC = 4;
    static const int STYLE_RADAR = 5;
    static const int STYLE_SLIM = 6;
    static const int STYLE_COUNT = 7;

    static const int MAX_DECO = 24;
    static const int MAX_TICKS = 72;
    static const int MAX_NUMBERS = 24;
    static const int MAX_MARKS = 40;
    static const int MAX_PINGS = 6;
    static const float FOCUS_DEGREES = 10.0;

    protected static ref FENR_PDA_CompassHud s_Instance;

    protected Widget m_Root;
    protected ImageWidget m_Disc;
    protected ImageWidget m_Fade;
    protected ImageWidget m_FadeLine;
    protected ImageWidget m_Ring;
    protected ImageWidget m_Arrow;
    protected ImageWidget m_CaretA;
    protected ImageWidget m_CaretB;
    protected TextWidget m_Head;
    protected TextWidget m_HeadS;
    protected ref array<TextWidget> m_Side;
    protected ref array<Widget> m_Deco;
    protected ref array<Widget> m_Ticks;
    protected ref array<Widget> m_TickShadows;
    protected ref array<TextWidget> m_Labels;
    protected ref array<TextWidget> m_LabelShadows;
    protected ref array<TextWidget> m_Numbers;
    protected ref array<TextWidget> m_NumberShadows;
    protected ref array<ImageWidget> m_Dots;
    protected ref array<TextWidget> m_DotTexts;
    protected ref array<TextWidget> m_DotShadows;
    protected ref array<Widget> m_Pings;
    protected ref array<TextWidget> m_PingTexts;
    protected ref array<TextWidget> m_PingShadows;
    protected ref array<Widget> m_Tag;          // bg, top, bottom, left, right

    protected bool m_Failed;
    protected bool m_Visible;
    protected bool m_LayoutDirty = true;
    protected bool m_HasDevice;
    protected float m_CheckTimer;
    protected EntityAI m_LastDevice;
    protected bool m_AwaitingMarkers;
    protected int m_RequestTime;
    protected int m_ScreenW;
    protected int m_ScreenH;

    // Colours
    protected int m_ColText;
    protected int m_ColBright;
    protected int m_ColDim;
    protected int m_ColLine;
    protected int m_ColAccent;
    protected int m_ColBg;
    protected int m_ColAmber;
    protected int m_ColRed;
    protected int m_ColShadow;

    // Geometry of the current style (screen px)
    protected int m_Style = -1;
    protected float m_U = 1;          // 1 reference px (1080p, medium size)
    protected float m_CX;             // centre x
    protected float m_X0;             // tape left edge
    protected float m_W;              // tape width
    protected float m_Y0;             // top of the HUD
    protected float m_Fov = 180;
    protected float m_StripY;         // classic / tactical / bezel: tape top
    protected float m_StripH;         // tape height (ticks stand on its bottom)
    protected float m_Base;           // minimal / arc / slim: tick baseline
    protected float m_MarkY;          // top of the marker icons
    protected float m_DotS;           // marker dot size (dots sit on the strip, v8.5.1)
    protected float m_PinW;
    protected float m_PinH;
    protected float m_BeaconS;
    protected float m_CY;             // radar centre y
    protected float m_R;              // radar radius
    protected bool m_Shadows;         // outlined text and ticks
    protected string m_MarkTex = "";

    // Per-frame pool counters
    protected int m_UsedTicks;
    protected int m_UsedNumbers;

    void FENR_PDA_CompassHud()
    {
        m_Side = new array<TextWidget>();
        m_Deco = new array<Widget>();
        m_Ticks = new array<Widget>();
        m_TickShadows = new array<Widget>();
        m_Labels = new array<TextWidget>();
        m_LabelShadows = new array<TextWidget>();
        m_Numbers = new array<TextWidget>();
        m_NumberShadows = new array<TextWidget>();
        m_Dots = new array<ImageWidget>();
        m_DotTexts = new array<TextWidget>();
        m_DotShadows = new array<TextWidget>();
        m_Pings = new array<Widget>();
        m_PingTexts = new array<TextWidget>();
        m_PingShadows = new array<TextWidget>();
        m_Tag = new array<Widget>();
        m_ColAmber = ARGB(255, 240, 175, 60);
        m_ColRed = ARGB(255, 230, 80, 70);
        m_ColShadow = ARGB(210, 5, 8, 6);
    }

    void ~FENR_PDA_CompassHud()
    {
        if (m_Root) m_Root.Unlink();
    }

    static string StyleName(int style)
    {
        if (style == STYLE_CLASSIC) return "CLASSIC";
        if (style == STYLE_TACTICAL) return "TACTICAL";
        if (style == STYLE_MINIMAL) return "MINIMAL";
        if (style == STYLE_BEZEL) return "BEZEL";
        if (style == STYLE_ARC) return "ARC";
        if (style == STYLE_RADAR) return "RADAR";
        if (style == STYLE_SLIM) return "SLIM";
        return "TACTICAL";
    }

    // Called every frame from MissionGameplay.OnUpdate.
    static void Tick(float timeslice)
    {
        if (!s_Instance) s_Instance = new FENR_PDA_CompassHud();
        s_Instance.Update(timeslice);
    }

    // Mission ending (logout, kick): remove the HUD widgets.
    static void Shutdown()
    {
        s_Instance = null;
    }

    // The server answered a marker request.
    static void OnMarkersReceived()
    {
        if (s_Instance) s_Instance.m_AwaitingMarkers = false;
    }

    static void OnSettingsChanged()
    {
        if (s_Instance) s_Instance.m_LayoutDirty = true;
    }

    // ------------------------------------------------------------------
    // Widgets
    // ------------------------------------------------------------------
    protected TextWidget FindText(string name)
    {
        return TextWidget.Cast(m_Root.FindAnyWidget(name));
    }

    protected ImageWidget FindImage(string name)
    {
        return ImageWidget.Cast(m_Root.FindAnyWidget(name));
    }

    protected bool Ensure()
    {
        if (m_Root) return true;
        if (m_Failed || !GetGame() || !GetGame().GetWorkspace()) return false;
        m_Root = GetGame().GetWorkspace().CreateWidgets("FENR_PDA/PDA/gui/os/FI_Compass.layout");
        if (!m_Root)
        {
            m_Failed = true;
            Print("[FENR_PDA] ERROR: FI_Compass.layout failed to load");
            return false;
        }
        m_Root.SetSort(900);
        m_Disc = FindImage("FI_CMP_Disc");
        m_Fade = FindImage("FI_CMP_Fade");
        m_FadeLine = FindImage("FI_CMP_FadeLine");
        m_Ring = FindImage("FI_CMP_Ring");
        m_Arrow = FindImage("FI_CMP_Arrow");
        m_CaretA = FindImage("FI_CMP_CaretA");
        m_CaretB = FindImage("FI_CMP_CaretB");
        m_Head = FindText("FI_CMP_Head");
        m_HeadS = FindText("FI_CMP_HeadS");
        for (int x = 0; x < 4; x++) m_Side.Insert(FindText("FI_CMP_X" + x.ToString()));
        for (int d = 0; d < MAX_DECO; d++) m_Deco.Insert(m_Root.FindAnyWidget("FI_CMP_P" + d.ToString()));
        for (int t = 0; t < MAX_TICKS; t++)
        {
            m_Ticks.Insert(m_Root.FindAnyWidget("FI_CMP_T" + t.ToString()));
            m_TickShadows.Insert(m_Root.FindAnyWidget("FI_CMP_TS" + t.ToString()));
        }
        for (int l = 0; l < 8; l++)
        {
            m_Labels.Insert(FindText("FI_CMP_L" + l.ToString()));
            m_LabelShadows.Insert(FindText("FI_CMP_LS" + l.ToString()));
        }
        for (int n = 0; n < MAX_NUMBERS; n++)
        {
            m_Numbers.Insert(FindText("FI_CMP_N" + n.ToString()));
            m_NumberShadows.Insert(FindText("FI_CMP_NS" + n.ToString()));
        }
        for (int m = 0; m < MAX_MARKS; m++)
        {
            m_Dots.Insert(FindImage("FI_CMP_M" + m.ToString()));
            m_DotTexts.Insert(FindText("FI_CMP_MT" + m.ToString()));
            m_DotShadows.Insert(FindText("FI_CMP_MS" + m.ToString()));
        }
        for (int p = 0; p < MAX_PINGS; p++)
        {
            m_Pings.Insert(m_Root.FindAnyWidget("FI_CMP_S" + p.ToString()));
            m_PingTexts.Insert(FindText("FI_CMP_ST" + p.ToString()));
            m_PingShadows.Insert(FindText("FI_CMP_STS" + p.ToString()));
        }
        m_Tag.Insert(m_Root.FindAnyWidget("FI_CMP_TagBG"));
        m_Tag.Insert(m_Root.FindAnyWidget("FI_CMP_TagT"));
        m_Tag.Insert(m_Root.FindAnyWidget("FI_CMP_TagB"));
        m_Tag.Insert(m_Root.FindAnyWidget("FI_CMP_TagL"));
        m_Tag.Insert(m_Root.FindAnyWidget("FI_CMP_TagR"));
        m_Root.Show(false);
        return true;
    }

    // ------------------------------------------------------------------
    // Visibility
    // ------------------------------------------------------------------
    protected static bool IsWorking(EntityAI entity)
    {
        FENR_PDA_Device device = FENR_PDA_Device.Cast(entity);
        if (!device || device.IsRuined() || !device.GetCompEM()) return false;
        // v8.1: a locked PDA shows nothing (logging in is synced to clients).
        if (!device.FenrIsLoggedIn()) return false;
        return device.GetCompEM().CanWork();
    }

    protected void CheckDevice()
    {
        m_HasDevice = false;
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        if (!player || !player.IsAlive()) return;

        EntityAI found = null;
        EntityAI inHands = player.GetItemInHands();
        if (IsWorking(inHands)) found = inHands;
        if (!found)
        {
            array<EntityAI> inventory = new array<EntityAI>();
            player.GetInventory().EnumerateInventory(InventoryTraversalType.PREORDER, inventory);
            foreach (EntityAI entity : inventory)
            {
                if (IsWorking(entity))
                {
                    found = entity;
                    break;
                }
            }
        }
        if (!found)
        {
            // Locked or put away: reload markers when a PDA shows up again
            // (it may be logged in as someone else by then).
            m_LastDevice = null;
            return;
        }
        m_HasDevice = true;

        // No answer to the last request (e.g. throttled): ask again.
        if (m_AwaitingMarkers && GetGame().GetTime() - m_RequestTime > 6000)
            m_LastDevice = null;

        // A different PDA: load its markers.
        if (found != m_LastDevice)
        {
            m_LastDevice = found;
            m_AwaitingMarkers = true;
            m_RequestTime = GetGame().GetTime();
            FENR_PDA_Client client = FENR_PDA_Client.Cast(GetPlugin(FENR_PDA_Client));
            if (client) client.RequestHudMarkers();
        }
    }

    // A powered, logged-in PDA in hands or inventory (S.O.S hotkey).
    static bool HasPoweredPda()
    {
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        if (!player || !player.IsAlive()) return false;
        if (IsWorking(player.GetItemInHands())) return true;
        array<EntityAI> inventory = new array<EntityAI>();
        player.GetInventory().EnumerateInventory(InventoryTraversalType.PREORDER, inventory);
        foreach (EntityAI entity : inventory)
        {
            if (IsWorking(entity)) return true;
        }
        return false;
    }

    void Update(float timeslice)
    {
        FENR_PDA_Settings settings = FENR_PDA_SettingsStore.Get();
        m_CheckTimer -= timeslice;
        if (m_CheckTimer <= 0)
        {
            m_CheckTimer = 0.5;
            CheckDevice();
        }

        bool show = settings.CompassEnabled && m_HasDevice && GetGame().GetUIManager().GetMenu() == null;
        if (!show)
        {
            if (m_Root && m_Visible) m_Root.Show(false);
            m_Visible = false;
            return;
        }
        if (!Ensure()) return;
        if (!m_Visible)
        {
            m_Root.Show(true);
            m_Visible = true;
            m_LayoutDirty = true;
        }
        int sw, sh;
        GetScreenSize(sw, sh);
        if (sw != m_ScreenW || sh != m_ScreenH) m_LayoutDirty = true;
        if (m_LayoutDirty) ApplyLayout(settings);
        Draw(settings);
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------
    protected int CompassColor(FENR_PDA_Settings settings, int role)
    {
        if (settings.CompassMatchTheme) return FENR_PDA_UI_Theme.Role(role);
        return FENR_PDA_UI_Theme.RoleForHue(role, settings.CompassHue);
    }

    protected static float Delta(float angle, float heading)
    {
        float d = angle - heading;
        while (d > 180) d -= 360;
        while (d < -180) d += 360;
        return d;
    }

    protected static float Bearing(vector from, float x, float z)
    {
        float b = Math.Atan2(x - from[0], z - from[2]) * Math.RAD2DEG;
        if (b < 0) b += 360;
        return b;
    }

    protected static string Cardinal(float heading)
    {
        string names[8] = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"};
        int index = Math.Round(heading / 45.0);
        if (index >= 8) index = 0;
        if (index < 0) index = 0;
        return names[index];
    }

    protected static float Clamp01(float value)
    {
        if (value < 0) return 0;
        if (value > 1) return 1;
        return value;
    }

    // Images are positioned as screen fractions (their layout position is
    // relative): pixel-positioned ImageWidgets did not draw in game (v8.4.1).
    // Panels and text stay pixel-positioned.
    protected void Place(Widget w, float x, float y, float width, float height, int color)
    {
        if (!w) return;
        if (ImageWidget.Cast(w))
        {
            int screenW, screenH;
            GetScreenSize(screenW, screenH);
            if (screenW > 0 && screenH > 0)
                w.SetPos(x / screenW, y / screenH);
        }
        else
        {
            w.SetPos(x, y);
        }
        w.SetSize(width, height);
        w.SetColor(color);
        w.Show(true);
    }

    // Text centred on (x, y) at `size` px.  Text boxes are wide; the layout
    // aligns the text inside them.
    protected void PlaceText(TextWidget t, string text, float x, float y, float size, int color)
    {
        if (!t) return;
        float boxW = 520 * m_U;
        t.SetText(text);
        t.SetPos(x - boxW * 0.5, y - size * 0.5);
        t.SetSize(boxW, size);
        t.SetColor(color);
        t.Show(true);
    }

    // Left / right aligned side readouts (widgets aligned in the layout).
    protected void PlaceSide(TextWidget t, string text, float x, float y, float size, int color, bool rightAligned)
    {
        if (!t) return;
        float boxW = 200 * m_U;
        float left = x;
        if (rightAligned) left = x - boxW;
        t.SetText(text);
        t.SetPos(left, y - size * 0.5);
        t.SetSize(boxW, size);
        t.SetColor(color);
        t.Show(true);
    }

    // Text with a dark outline copy behind it (when the style uses shadows).
    protected void ShadowText(TextWidget t, TextWidget shadow, string text, float x, float y, float size, int color, bool forceShadow = false)
    {
        PlaceText(t, text, x, y, size, color);
        if (!shadow) return;
        if (m_Shadows || forceShadow)
        {
            float off = Math.Max(1, m_U * 1.3);
            PlaceText(shadow, text, x + off, y + off, size, m_ColShadow);
        }
        else
        {
            shadow.Show(false);
        }
    }

    // Draws the next pooled tick (with its outline in shadow styles).
    protected void AddTick(float x, float y, float width, float height, int color)
    {
        if (m_UsedTicks >= m_Ticks.Count()) return;
        Widget shadow = m_TickShadows[m_UsedTicks];
        if (m_Shadows)
        {
            float pad = Math.Max(1, m_U);
            Place(shadow, x - pad, y - pad, width + pad * 2, height + pad * 2, FENR_PDA_UI_Theme.WithAlpha(m_ColShadow, 150));
        }
        else if (shadow)
        {
            shadow.Show(false);
        }
        Place(m_Ticks[m_UsedTicks], x, y, width, height, color);
        m_UsedTicks++;
    }

    protected void AddNumber(string text, float x, float y, float size, int color)
    {
        if (m_UsedNumbers >= m_Numbers.Count()) return;
        ShadowText(m_Numbers[m_UsedNumbers], m_NumberShadows[m_UsedNumbers], text, x, y, size, color);
        m_UsedNumbers++;
    }

    protected void HideWidget(Widget w)
    {
        if (w) w.Show(false);
    }

    protected void HideAll()
    {
        HideWidget(m_Disc);
        HideWidget(m_Fade);
        HideWidget(m_FadeLine);
        HideWidget(m_Ring);
        HideWidget(m_Arrow);
        HideWidget(m_CaretA);
        HideWidget(m_CaretB);
        HideWidget(m_Head);
        HideWidget(m_HeadS);
        foreach (TextWidget side : m_Side) { if (side) side.Show(false); }
        foreach (Widget deco : m_Deco) { if (deco) deco.Show(false); }
        foreach (Widget tagPart : m_Tag) { if (tagPart) tagPart.Show(false); }
        foreach (Widget tick : m_Ticks) { if (tick) tick.Show(false); }
        foreach (Widget tickShadow : m_TickShadows) { if (tickShadow) tickShadow.Show(false); }
        foreach (TextWidget label : m_Labels) { if (label) label.Show(false); }
        foreach (TextWidget labelShadow : m_LabelShadows) { if (labelShadow) labelShadow.Show(false); }
        foreach (TextWidget number : m_Numbers) { if (number) number.Show(false); }
        foreach (TextWidget numberShadow : m_NumberShadows) { if (numberShadow) numberShadow.Show(false); }
    }

    // ------------------------------------------------------------------
    // Layout: geometry and static decoration of the chosen style
    // ------------------------------------------------------------------
    protected void ApplyLayout(FENR_PDA_Settings settings)
    {
        m_LayoutDirty = false;
        int sw, sh;
        GetScreenSize(sw, sh);
        m_ScreenW = sw;
        m_ScreenH = sh;
        if (sw < 2 || sh < 2) { m_LayoutDirty = true; return; }

        m_Style = settings.CompassStyle;
        if (m_Style < 0 || m_Style >= STYLE_COUNT) m_Style = STYLE_TACTICAL;

        float sizeK = 1.0;
        if (settings.CompassSize == 0) sizeK = 0.82;
        if (settings.CompassSize == 2) sizeK = 1.22;
        m_U = (sh / 1080.0) * sizeK;
        m_CX = sw * 0.5;
        m_Root.SetAlpha(settings.CompassOpacity / 100.0);

        m_ColText = CompassColor(settings, FENR_PDA_UI_Theme.ROLE_TEXT);
        m_ColBright = CompassColor(settings, FENR_PDA_UI_Theme.ROLE_TEXTBRIGHT);
        m_ColDim = CompassColor(settings, FENR_PDA_UI_Theme.ROLE_TEXTDIM);
        m_ColLine = CompassColor(settings, FENR_PDA_UI_Theme.ROLE_LINE);
        m_ColAccent = CompassColor(settings, FENR_PDA_UI_Theme.ROLE_ACCENT);
        m_ColBg = CompassColor(settings, FENR_PDA_UI_Theme.ROLE_LCD);

        HideAll();
        m_Shadows = m_Style == STYLE_MINIMAL || m_Style == STYLE_ARC || m_Style == STYLE_SLIM || m_Style == STYLE_RADAR;
        bool bottom = settings.CompassPosition == 1;
        float u = m_U;

        // Marker icons: dots on the strip (v8.5.1); m_PinW / m_PinH still size
        // the row under the compass where labels and S.O.S beacons go.
        string markTex = "cmp_dot";
        m_PinW = 15 * u;
        m_PinH = 19 * u;
        m_BeaconS = 19 * u;
        if (m_Style == STYLE_MINIMAL || m_Style == STYLE_BEZEL || m_Style == STYLE_SLIM)
        {
            m_PinW = 14 * u;
            m_PinH = 12 * u;
            m_BeaconS = 16 * u;
        }
        if (m_Style == STYLE_SLIM)
        {
            m_PinW = 11 * u;
            m_PinH = 9 * u;
            m_BeaconS = 13 * u;
        }
        m_DotS = 11 * u;
        if (m_Style == STYLE_SLIM) m_DotS = 9 * u;
        if (m_Style == STYLE_RADAR) m_DotS = 12 * u;

        if (markTex != m_MarkTex)
        {
            m_MarkTex = markTex;
            foreach (ImageWidget icon : m_Dots)
            {
                if (!icon) continue;
                if (!icon.LoadImageFile(0, "FENR_PDA/PDA/gui/os/textures/" + markTex + ".edds"))
                    Print("[FENR_PDA] Compass: could not load texture " + markTex + ".edds");
                icon.SetImage(0);
            }
        }

        float total;
        if (m_Style == STYLE_CLASSIC)
        {
            m_W = sw * 0.40 * sizeK;
            float h = sh * 0.085 * sizeK;
            total = h + 44 * u;
            m_Y0 = TopFor(bottom, total, sh);
            m_X0 = m_CX - m_W * 0.5;
            m_Fov = 180;
            m_StripY = m_Y0 + 0.22 * h;
            m_StripH = 0.5 * h;
            m_MarkY = m_Y0 + 0.74 * h;
            Place(m_Deco[0], m_CX - 0.06 * m_W, m_Y0, 0.12 * m_W, 0.2 * h, FENR_PDA_UI_Theme.WithAlpha(m_ColBg, 215));
            Place(m_Deco[1], m_X0, m_StripY, m_W, m_StripH, FENR_PDA_UI_Theme.WithAlpha(m_ColBg, 190));
            Place(m_Deco[2], m_X0, m_StripY, m_W, 1, m_ColLine);
            Place(m_Deco[3], m_X0, m_StripY + m_StripH, m_W, 1, m_ColLine);
            Place(m_CaretA, m_CX - 6 * u, m_StripY, 12 * u, 9 * u, m_ColAccent);
        }
        else if (m_Style == STYLE_TACTICAL)
        {
            m_W = sw * 0.42 * sizeK;
            total = 30 * u + 8 * u + 34 * u + 56 * u;
            m_Y0 = TopFor(bottom, total, sh);
            m_X0 = m_CX - m_W * 0.5;
            m_Fov = 180;
            m_StripY = m_Y0 + 38 * u;
            m_StripH = 34 * u;
            m_MarkY = m_StripY + m_StripH + 6 * u;
            Place(m_Fade, m_X0, m_StripY, m_W, m_StripH, FENR_PDA_UI_Theme.WithAlpha(m_ColBg, 160));
            Place(m_FadeLine, m_X0, m_StripY + m_StripH, m_W, Math.Max(1, u), m_ColLine);
            float bw = 76 * u;
            float bh = 30 * u;
            float bx = m_CX - bw * 0.5;
            Place(m_Deco[0], bx, m_Y0, bw, bh, FENR_PDA_UI_Theme.WithAlpha(m_ColBg, 205));
            Box(1, bx, m_Y0, bw, bh, m_ColAccent);
            Place(m_CaretA, m_CX - 6 * u, m_StripY - 1, 12 * u, 8 * u, m_ColAccent);
            Place(m_Deco[5], m_CX, m_StripY + 7 * u, 1, m_StripH - 7 * u, FENR_PDA_UI_Theme.WithAlpha(m_ColAccent, 140));
        }
        else if (m_Style == STYLE_MINIMAL)
        {
            m_W = sw * 0.36 * sizeK;
            total = 46 * u + 52 * u;
            m_Y0 = TopFor(bottom, total, sh);
            m_X0 = m_CX - m_W * 0.5;
            m_Fov = 150;
            m_Base = m_Y0 + 46 * u;
            m_MarkY = m_Base - 7 * u;
            Place(m_CaretB, m_CX - 7 * u, m_Base + 2 * u, 14 * u, 8 * u, m_ColAccent);
        }
        else if (m_Style == STYLE_BEZEL)
        {
            m_W = sw * 0.44 * sizeK;
            float frameH = 58 * u;
            total = frameH + 44 * u;
            m_Y0 = TopFor(bottom, total, sh);
            float fx = m_CX - m_W * 0.5;
            Place(m_Deco[0], fx, m_Y0, m_W, frameH, FENR_PDA_UI_Theme.WithAlpha(m_ColBg, 180));
            // corner brackets
            float c = 12 * u;
            float t2 = Math.Max(2, 2 * u);
            Place(m_Deco[1], fx, m_Y0, c, t2, m_ColLine);
            Place(m_Deco[2], fx, m_Y0, t2, c, m_ColLine);
            Place(m_Deco[3], fx + m_W - c, m_Y0, c, t2, m_ColLine);
            Place(m_Deco[4], fx + m_W - t2, m_Y0, t2, c, m_ColLine);
            Place(m_Deco[5], fx, m_Y0 + frameH - t2, c, t2, m_ColLine);
            Place(m_Deco[6], fx, m_Y0 + frameH - c, t2, c, m_ColLine);
            Place(m_Deco[7], fx + m_W - c, m_Y0 + frameH - t2, c, t2, m_ColLine);
            Place(m_Deco[8], fx + m_W - t2, m_Y0 + frameH - c, t2, c, m_ColLine);
            // inner tape window
            m_X0 = fx + 100 * u;
            float innerW = m_W - 200 * u;
            m_StripY = m_Y0 + 8 * u;
            m_StripH = frameH - 16 * u;
            Box(9, m_X0, m_StripY, innerW, m_StripH, FENR_PDA_UI_Theme.WithAlpha(m_ColLine, 170));
            m_W = innerW;
            m_Fov = 120;
            m_MarkY = m_Y0 + frameH + 6 * u;
            Place(m_CaretA, m_CX - 6 * u, m_StripY - 9 * u, 12 * u, 8 * u, m_ColAccent);
            Place(m_CaretB, m_CX - 6 * u, m_StripY + m_StripH + 1, 12 * u, 8 * u, m_ColAccent);
            // side readout labels (values are drawn every frame)
            PlaceSide(m_Side[0], "HDG", fx + 12 * u, m_Y0 + frameH * 0.5 - 9 * u, 10 * u, m_ColDim, false);
            PlaceSide(m_Side[2], "GRID", fx + m_W + 200 * u - 12 * u, m_Y0 + frameH * 0.5 - 9 * u, 10 * u, m_ColDim, true);
        }
        else if (m_Style == STYLE_ARC)
        {
            m_W = sw * 0.46 * sizeK;
            total = 24 * u + 10 * u + 34 * u + 18 * u + 50 * u;
            m_Y0 = TopFor(bottom, total, sh);
            m_X0 = m_CX - m_W * 0.5;
            m_Fov = 160;
            m_Base = m_Y0 + 24 * u + 10 * u + 30 * u;
            Place(m_Fade, m_X0, m_Y0 + 28 * u, m_W, 46 * u, FENR_PDA_UI_Theme.WithAlpha(m_ColBg, 110));
            Place(m_Deco[0], m_CX - 38 * u, m_Y0, 76 * u, 24 * u, FENR_PDA_UI_Theme.WithAlpha(m_ColBg, 205));
            Place(m_Deco[1], m_CX - 38 * u, m_Y0 + 24 * u - Math.Max(1, u), 76 * u, Math.Max(1, u), m_ColAccent);
            Place(m_CaretA, m_CX - 6 * u, m_Y0 + 25 * u, 12 * u, 8 * u, m_ColAccent);
        }
        else if (m_Style == STYLE_RADAR)
        {
            m_R = 60 * u;
            m_CX = sw - m_R - 52 * u;
            if (bottom) m_CY = sh * 0.80 - m_R - 56 * u;
            else m_CY = sh * 0.02 + m_R + 18 * u;
            float disc = m_R * 2 + 30 * u;
            Place(m_Disc, m_CX - disc * 0.5, m_CY - disc * 0.5, disc, disc, FENR_PDA_UI_Theme.WithAlpha(m_ColBg, 175));
            Place(m_Ring, m_CX - m_R, m_CY - m_R, m_R * 2, m_R * 2, m_ColLine);
            Place(m_Arrow, m_CX - 10 * u, m_CY - 12 * u, 20 * u, 24 * u, m_ColAccent);
            m_Fov = 360;
        }
        else
        {
            // SLIM
            m_W = sw * 0.34 * sizeK;
            total = 24 * u + 44 * u;
            m_Y0 = TopFor(bottom, total, sh);
            m_X0 = m_CX - m_W * 0.5;
            m_Fov = 170;
            m_Base = m_Y0 + 24 * u;
            m_MarkY = m_Base - 9 * u;
            Place(m_FadeLine, m_X0, m_Base, m_W, Math.Max(1, u), m_ColBright);
            Place(m_CaretB, m_CX - 5 * u, m_Base + 2 * u, 10 * u, 6 * u, m_ColAccent);
        }

        foreach (ImageWidget pin : m_Dots)
        {
            if (pin) pin.SetSize(m_DotS, m_DotS);
        }
        foreach (Widget beaconIcon : m_Pings)
        {
            if (beaconIcon) beaconIcon.SetSize(m_BeaconS, m_BeaconS);
        }
    }

    protected float TopFor(bool bottom, float total, int sh)
    {
        if (bottom) return sh * 0.80 - total;
        return sh * 0.012;
    }

    // Four 1 px lines around a rectangle, using deco slots first..first+3.
    protected void Box(int first, float x, float y, float width, float height, int color)
    {
        float t = Math.Max(1, m_U);
        Place(m_Deco[first], x, y, width, t, color);
        Place(m_Deco[first + 1], x, y + height - t, width, t, color);
        Place(m_Deco[first + 2], x, y, t, height, color);
        Place(m_Deco[first + 3], x + width - t, y, t, height, color);
    }

    // ------------------------------------------------------------------
    // Per-frame drawing
    // ------------------------------------------------------------------
    protected void Draw(FENR_PDA_Settings settings)
    {
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        if (!player) return;
        vector me = player.GetPosition();
        vector dir = GetGame().GetCurrentCameraDirection();
        float heading = Math.Atan2(dir[0], dir[2]) * Math.RAD2DEG;
        if (heading < 0) heading += 360;

        m_UsedTicks = 0;
        m_UsedNumbers = 0;
        if (m_Style == STYLE_RADAR) DrawRadar(settings, me, heading);
        else DrawTape(settings, me, heading);

        for (int t = m_UsedTicks; t < m_Ticks.Count(); t++)
        {
            if (m_Ticks[t]) m_Ticks[t].Show(false);
            if (m_TickShadows[t]) m_TickShadows[t].Show(false);
        }
        for (int n = m_UsedNumbers; n < m_Numbers.Count(); n++)
        {
            if (m_Numbers[n]) m_Numbers[n].Show(false);
            if (m_NumberShadows[n]) m_NumberShadows[n].Show(false);
        }

        FENR_PDA_Client client = FENR_PDA_Client.Cast(GetPlugin(FENR_PDA_Client));
        DrawMarkers(settings, client, me, heading);
        DrawPings(client, me, heading);
    }

    // Horizontal position of a bearing on the tape.
    protected float TapeX(float d)
    {
        return m_X0 + (0.5 + d / m_Fov) * m_W;
    }

    // Arc style: the tape bends down and shrinks towards the edges.
    protected float ArcDrop(float d)
    {
        float q = d / (m_Fov * 0.5);
        return 16 * m_U * q * q;
    }

    protected float ArcScale(float d)
    {
        float q = d / (m_Fov * 0.5);
        return 1.0 - 0.4 * q * q;
    }

    // Fades elements out near the tape ends.
    protected float EdgeAlpha(float d, float fadeDegrees)
    {
        return Clamp01((m_Fov * 0.5 - Math.AbsFloat(d)) / fadeDegrees);
    }

    protected int Faded(int color, float alpha)
    {
        int alphaByte = Math.Round(255 * Clamp01(alpha));
        return FENR_PDA_UI_Theme.WithAlpha(color, alphaByte);
    }

    protected int CardinalColor(int index)
    {
        if (index == 0) return m_ColAccent;
        if (index % 2 == 0) return m_ColBright;
        return m_ColText;
    }

    protected void DrawHeading(float heading, bool withCardinal, float x, float y, float size, int color)
    {
        int shown = Math.Round(heading);
        if (shown >= 360) shown = 0;
        string text = shown.ToStringLen(3);
        if (withCardinal) text += "  " + Cardinal(heading);
        ShadowText(m_Head, m_HeadS, text, x, y, size, color);
    }

    protected void DrawTape(FENR_PDA_Settings settings, vector me, float heading)
    {
        float u = m_U;
        float half = m_Fov * 0.5;
        float line = Math.Max(1, u);
        float tw = Math.Max(2, 2 * u);
        string names[8] = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"};

        // Ticks
        int step = 5;
        if (m_Style == STYLE_CLASSIC || m_Style == STYLE_SLIM) step = 15;
        for (int deg = 0; deg < 360; deg += step)
        {
            float d = Delta(deg, heading);
            if (Math.AbsFloat(d) > half) continue;
            float x = TapeX(d);
            bool major = deg % 15 == 0;
            bool cardinal = deg % 45 == 0;
            if (m_Style == STYLE_CLASSIC)
            {
                float ch = 0.28 * m_StripH;
                if (cardinal) ch = 0.5 * m_StripH;
                AddTick(x, m_StripY + m_StripH - ch, tw, ch, m_ColLine);
            }
            else if (m_Style == STYLE_TACTICAL)
            {
                float a = EdgeAlpha(d, 16);
                float th = 7 * u;
                int col = m_ColText;
                if (major) th = 14 * u;
                if (cardinal) { th = 8 * u; col = CardinalColor(deg / 45); }
                AddTick(x, m_StripY + m_StripH - th, line, th, Faded(col, a));
            }
            else if (m_Style == STYLE_MINIMAL)
            {
                float ma = EdgeAlpha(d, 20);
                float mh = 5 * u;
                if (major) mh = 10 * u;
                AddTick(x, m_Base - mh, line, mh, Faded(m_ColBright, ma * 0.95));
            }
            else if (m_Style == STYLE_BEZEL)
            {
                float ba = EdgeAlpha(d, 8);
                float bh = 6 * u;
                if (major) bh = 12 * u;
                AddTick(x, m_StripY + m_StripH - bh - line, line, bh, Faded(m_ColText, ba * 0.9));
            }
            else if (m_Style == STYLE_ARC)
            {
                float k = ArcScale(d);
                float aa = EdgeAlpha(d, 18);
                float ah = 6 * u * k;
                if (major) ah = 12 * u * k;
                AddTick(x, m_Base + ArcDrop(d) - ah, line, ah, Faded(m_ColBright, aa));
            }
            else
            {
                // SLIM
                float sa = EdgeAlpha(d, 14);
                float sh = 4 * u;
                if (cardinal) sh = 8 * u;
                AddTick(x, m_Base - sh, line, sh, Faded(m_ColBright, sa));
            }
        }

        // Cardinal letters
        for (int i = 0; i < 8; i++)
        {
            TextWidget label = m_Labels[i];
            TextWidget labelShadow = m_LabelShadows[i];
            float dl = Delta(i * 45, heading);
            if (Math.AbsFloat(dl) > half - 3)
            {
                if (label) label.Show(false);
                if (labelShadow) labelShadow.Show(false);
                continue;
            }
            float lx = TapeX(dl);
            bool primary = i % 2 == 0;
            int lc = CardinalColor(i);
            if (m_Style == STYLE_CLASSIC)
                ShadowText(label, labelShadow, names[i], lx, m_StripY + m_StripH * 0.3, m_StripH * 0.42, lc);
            else if (m_Style == STYLE_TACTICAL)
            {
                float tsize = 15 * u;
                if (primary) tsize = 20 * u;
                ShadowText(label, labelShadow, names[i], lx, m_StripY + 13 * u, tsize, Faded(lc, EdgeAlpha(dl, 16)));
            }
            else if (m_Style == STYLE_MINIMAL)
            {
                float msize = 16 * u;
                if (primary) msize = 22 * u;
                ShadowText(label, labelShadow, names[i], lx, m_Base - 26 * u, msize, Faded(lc, EdgeAlpha(dl, 20)));
            }
            else if (m_Style == STYLE_BEZEL)
                ShadowText(label, labelShadow, names[i], lx, m_StripY + 12 * u, 16 * u, Faded(lc, EdgeAlpha(dl, 8)));
            else if (m_Style == STYLE_ARC)
            {
                float ak = ArcScale(dl);
                float asize = 15 * u * ak;
                if (primary) asize = 20 * u * ak;
                ShadowText(label, labelShadow, names[i], lx, m_Base + ArcDrop(dl) - 24 * u * ak, asize, Faded(lc, EdgeAlpha(dl, 18)));
            }
            else
            {
                float ssize = 11 * u;
                if (primary) ssize = 13 * u;
                ShadowText(label, labelShadow, names[i], lx, m_Base - 15 * u, ssize, Faded(lc, EdgeAlpha(dl, 14)));
            }
        }

        // Bearing numbers
        if (settings.CompassBearing && m_Style != STYLE_SLIM)
        {
            int numberStep = 15;
            if (m_Style == STYLE_CLASSIC) numberStep = 30;
            for (int nd = numberStep; nd < 360; nd += numberStep)
            {
                if (nd % 45 == 0) continue;
                float dn = Delta(nd, heading);
                if (Math.AbsFloat(dn) > half - 4) continue;
                float nx = TapeX(dn);
                string numberText = nd.ToString();
                if (m_Style == STYLE_CLASSIC)
                    AddNumber(numberText, nx, m_StripY + m_StripH * 0.33, m_StripH * 0.3, m_ColDim);
                else if (m_Style == STYLE_TACTICAL)
                    AddNumber(numberText, nx, m_StripY + 13 * u, 11 * u, Faded(m_ColDim, EdgeAlpha(dn, 16)));
                else if (m_Style == STYLE_MINIMAL)
                    AddNumber(numberText, nx, m_Base - 22 * u, 11 * u, Faded(m_ColText, EdgeAlpha(dn, 20)));
                else if (m_Style == STYLE_BEZEL)
                    AddNumber(numberText, nx, m_StripY + 12 * u, 10 * u, Faded(m_ColDim, EdgeAlpha(dn, 8)));
                else
                    AddNumber(numberText, nx, m_Base + ArcDrop(dn) - 22 * u * ArcScale(dn), 11 * u * ArcScale(dn), Faded(m_ColText, EdgeAlpha(dn, 18)));
            }
        }

        // Heading readout
        if (m_Style == STYLE_CLASSIC)
            DrawHeading(heading, true, m_CX, m_StripY - 0.11 * m_StripH * 2, m_StripH * 0.34, m_ColBright);
        else if (m_Style == STYLE_TACTICAL)
        {
            DrawHeading(heading, false, m_CX, m_Y0 + 15 * u, 19 * u, m_ColBright);
            PlaceSide(m_Side[1], Cardinal(heading), m_CX + 46 * u, m_Y0 + 15 * u, 18 * u, m_ColAccent, false);
        }
        else if (m_Style == STYLE_MINIMAL)
            DrawHeading(heading, false, m_CX, m_Base + 19 * u, 17 * u, m_ColBright);
        else if (m_Style == STYLE_BEZEL)
        {
            if (m_Head) m_Head.Show(false);
            int shown = Math.Round(heading);
            if (shown >= 360) shown = 0;
            float midY = m_StripY + m_StripH * 0.5 + 6 * u;
            float frameLeft = m_X0 - 100 * u;
            PlaceSide(m_Side[1], shown.ToStringLen(3) + "  " + Cardinal(heading), frameLeft + 12 * u, midY, 15 * u, m_ColBright, false);
            int gx = Math.Floor(me[0] / 100.0);
            int gz = Math.Floor(me[2] / 100.0);
            if (gx < 0) gx = 0;
            if (gz < 0) gz = 0;
            PlaceSide(m_Side[3], gx.ToStringLen(3) + " " + gz.ToStringLen(3), m_X0 + m_W + 100 * u - 12 * u, midY, 15 * u, m_ColBright, true);
        }
        else if (m_Style == STYLE_ARC)
            DrawHeading(heading, true, m_CX, m_Y0 + 12 * u, 15 * u, m_ColBright);
        else
            DrawHeading(heading, false, m_CX, m_Base + 15 * u, 12 * u, m_ColBright);
    }

    protected void DrawRadar(FENR_PDA_Settings settings, vector me, float heading)
    {
        float u = m_U;
        string names[8] = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"};
        // Ticks: a dot every 15 degrees just inside the ring.
        for (int deg = 0; deg < 360; deg += 15)
        {
            float a = Delta(deg, heading) * Math.DEG2RAD;
            float r = m_R - 7 * u;
            float size = 3 * u;
            int color = m_ColLine;
            if (deg % 45 == 0) { size = 5 * u; color = m_ColBright; }
            float x = m_CX + r * Math.Sin(a);
            float y = m_CY - r * Math.Cos(a);
            AddTick(x - size * 0.5, y - size * 0.5, size, size, color);
        }
        for (int i = 0; i < 8; i++)
        {
            float la = Delta(i * 45, heading) * Math.DEG2RAD;
            float lr = m_R - 22 * u;
            float size2 = 12 * u;
            if (i % 2 == 0) size2 = 16 * u;
            ShadowText(m_Labels[i], m_LabelShadows[i], names[i], m_CX + lr * Math.Sin(la), m_CY - lr * Math.Cos(la), size2, CardinalColor(i));
        }
        DrawHeading(heading, true, m_CX, m_CY + m_R + 26 * u, 15 * u, m_ColBright);
    }

    // ------------------------------------------------------------------
    // Markers and S.O.S pings
    // ------------------------------------------------------------------
    // Icon position for a bearing: x/y of the icon's top-left corner.
    // Vertical centre of a marker dot: on the strip / tick line.
    protected float DotY(float d)
    {
        if (m_Style == STYLE_MINIMAL || m_Style == STYLE_SLIM) return m_Base - 2 * m_U;
        if (m_Style == STYLE_ARC) return m_Base + ArcDrop(d) - 2 * m_U;
        return m_StripY + m_StripH * 0.5;
    }

    protected bool IconPos(float d, float iconW, float iconH, out float ix, out float iy)
    {
        if (m_Style == STYLE_RADAR)
        {
            float a = d * Math.DEG2RAD;
            float r = m_R + 13 * m_U;
            ix = m_CX + r * Math.Sin(a) - iconW * 0.5;
            iy = m_CY - r * Math.Cos(a) - iconH * 0.5;
            return true;
        }
        if (Math.AbsFloat(d) > m_Fov * 0.5) return false;
        float x = TapeX(d);
        ix = x - iconW * 0.5;
        iy = m_MarkY;
        if (m_Style == STYLE_ARC) iy = m_Base + ArcDrop(d) + 4 * m_U;
        return true;
    }

    // Tag background behind the focused marker's label (tactical / bezel).
    protected void DrawTag(float x, float y, string text, float size)
    {
        if (m_Style != STYLE_TACTICAL && m_Style != STYLE_BEZEL)
        {
            foreach (Widget part : m_Tag) { if (part) part.Show(false); }
            return;
        }
        float textW = text.Length() * size * 0.62 + 16 * m_U;
        float tagH = size + 8 * m_U;
        float left = x - textW * 0.5;
        float top = y - tagH * 0.5;
        float t = Math.Max(1, m_U);
        Place(m_Tag[0], left, top, textW, tagH, FENR_PDA_UI_Theme.WithAlpha(m_ColBg, 215));
        if (m_Style == STYLE_TACTICAL)
        {
            Place(m_Tag[1], left, top, textW, t, m_ColAmber);
            Place(m_Tag[2], left, top + tagH - t, textW, t, m_ColAmber);
            Place(m_Tag[3], left, top, t, tagH, m_ColAmber);
            Place(m_Tag[4], left + textW - t, top, t, tagH, m_ColAmber);
        }
        else
        {
            if (m_Tag[1]) m_Tag[1].Show(false);
            if (m_Tag[2]) m_Tag[2].Show(false);
            Place(m_Tag[3], left, top, Math.Max(2, 2 * m_U), tagH, m_ColAmber);
            if (m_Tag[4]) m_Tag[4].Show(false);
        }
    }

    protected void DrawMarkers(FENR_PDA_Settings settings, FENR_PDA_Client client, vector me, float heading)
    {
        int used = 0;
        bool tagShown = false;
        if (client && settings.CompassMarkers)
        {
            float u = m_U;
            // The marker nearest the centre shows its name.
            int focus = -1;
            float best = FOCUS_DEGREES;
            if (m_Style == STYLE_RADAR) best = 15;
            for (int f = 0; f < client.m_Markers.Count(); f++)
            {
                FENR_PDA_MapMarker candidate = client.m_Markers[f];
                if (!candidate) continue;
                float fd = Math.AbsFloat(Delta(Bearing(me, candidate.X, candidate.Z), heading));
                if (fd < best)
                {
                    best = fd;
                    focus = f;
                }
            }

            array<float> labelXs = new array<float>();
            float focusX = -100000;
            if (focus >= 0 && m_Style != STYLE_RADAR)
                focusX = TapeX(Delta(Bearing(me, client.m_Markers[focus].X, client.m_Markers[focus].Z), heading));

            for (int k = 0; k < client.m_Markers.Count(); k++)
            {
                FENR_PDA_MapMarker marker = client.m_Markers[k];
                if (!marker || used >= m_Dots.Count()) continue;
                float d = Delta(Bearing(me, marker.X, marker.Z), heading);
                float ix, iy;
                if (!IconPos(d, m_PinW, m_PinH, ix, iy)) continue;
                ImageWidget pin = m_Dots[used];
                TextWidget label = m_DotTexts[used];
                TextWidget labelShadow = m_DotShadows[used];
                used++;
                float alpha = 1.0;
                if (m_Style != STYLE_RADAR && m_Style != STYLE_CLASSIC) alpha = 0.35 + 0.65 * EdgeAlpha(d, 12);
                bool isFocus = k == focus;
                float cx = ix + m_PinW * 0.5;
                // Dot on the strip; the focused one larger.
                float dotS = m_DotS;
                if (isFocus) dotS = m_DotS * 1.4;
                float dotY = iy + m_PinH * 0.5;
                if (m_Style != STYLE_RADAR) dotY = DotY(d);
                Place(pin, cx - dotS * 0.5, dotY - dotS * 0.5, dotS, dotS, Faded(m_ColAmber, alpha));

                float dx = marker.X - me[0];
                float dz = marker.Z - me[2];
                float metres = Math.Sqrt(dx * dx + dz * dz);
                // Label in the row under the compass.
                float ly = iy + 8 * u;
                string text = "";
                int color = m_ColText;
                float size = 12 * u;
                if (isFocus)
                {
                    text = marker.Name;
                    if (settings.CompassDistances) text += "  " + FENR_PDA_UI_Kit.Distance(metres);
                    color = m_ColAmber;
                    size = 13 * u;
                    if (m_Style == STYLE_CLASSIC) color = m_ColBright;
                }
                else if (settings.CompassDistances && m_Style != STYLE_SLIM && m_Style != STYLE_RADAR)
                {
                    // Distances only where they do not collide with other labels.
                    bool clear = Math.AbsFloat(cx - focusX) > 90 * u;
                    foreach (float other : labelXs)
                    {
                        if (Math.AbsFloat(cx - other) < 48 * u) clear = false;
                    }
                    if (clear) text = FENR_PDA_UI_Kit.Distance(metres);
                }

                if (text == "")
                {
                    if (label) label.Show(false);
                    if (labelShadow) labelShadow.Show(false);
                    continue;
                }
                if (m_Style == STYLE_RADAR)
                {
                    // The focused marker's name sits under the heading readout.
                    cx = m_CX;
                    ly = m_CY + m_R + 46 * u;
                }
                if (m_Style == STYLE_MINIMAL || m_Style == STYLE_SLIM)
                    ly = m_Base + 40 * u;
                if (isFocus && m_Style == STYLE_MINIMAL)
                    ly = m_Base + 40 * u;
                if (!isFocus) labelXs.Insert(cx);
                if (isFocus)
                {
                    DrawTag(cx, ly, text, size);
                    tagShown = m_Style == STYLE_TACTICAL || m_Style == STYLE_BEZEL;
                }
                ShadowText(label, labelShadow, text, cx, ly, size, color, !isFocus || !tagShown);
            }
        }
        if (!tagShown)
        {
            foreach (Widget tagPart : m_Tag) { if (tagPart) tagPart.Show(false); }
        }
        for (int i = used; i < m_Dots.Count(); i++)
        {
            if (m_Dots[i]) m_Dots[i].Show(false);
            if (m_DotTexts[i]) m_DotTexts[i].Show(false);
            if (m_DotShadows[i]) m_DotShadows[i].Show(false);
        }
    }

    protected void DrawPings(FENR_PDA_Client client, vector me, float heading)
    {
        int used = 0;
        if (client)
        {
            float u = m_U;
            array<ref FENR_PDA_SosPing> pings = client.ActiveSosPings();
            bool blinkOn = (GetGame().GetTime() / 400) % 2 == 0;
            foreach (FENR_PDA_SosPing ping : pings)
            {
                if (!ping || used >= m_Pings.Count()) continue;
                float d = Delta(Bearing(me, ping.X, ping.Z), heading);
                // Off the tape: pinned to the edge so the player knows which way to turn.
                bool edge = false;
                if (m_Style != STYLE_RADAR)
                {
                    float limit = m_Fov * 0.5 - 3;
                    if (d > limit) { d = limit; edge = true; }
                    if (d < -limit) { d = -limit; edge = true; }
                }
                float ix, iy;
                if (!IconPos(d, m_BeaconS, m_BeaconS, ix, iy)) continue;
                float dx = ping.X - me[0];
                float dz = ping.Z - me[2];
                float metres = Math.Sqrt(dx * dx + dz * dz);
                Widget beacon = m_Pings[used];
                TextWidget label = m_PingTexts[used];
                TextWidget labelShadow = m_PingShadows[used];
                Place(beacon, ix, iy, m_BeaconS, m_BeaconS, m_ColRed);
                if (beacon) beacon.Show(blinkOn || !edge);

                string arrow = "";
                if (edge && d < 0) arrow = "< ";
                if (edge && d > 0) arrow = "> ";
                string text = arrow + "S.O.S  " + ping.Name + "  " + FENR_PDA_UI_Kit.Distance(metres);
                float cx = ix + m_BeaconS * 0.5;
                float ly = iy + m_BeaconS + 10 * u;
                if (m_Style == STYLE_RADAR)
                {
                    cx = m_CX;
                    ly = m_CY + m_R + 64 * u + used * 16 * u;
                }
                else if (m_Style == STYLE_MINIMAL || m_Style == STYLE_SLIM)
                {
                    ly = m_Base + 58 * u;
                }
                ShadowText(label, labelShadow, text, cx, ly, 12 * u, m_ColRed, true);
                used++;
            }
        }
        for (int i = used; i < m_Pings.Count(); i++)
        {
            if (m_Pings[i]) m_Pings[i].Show(false);
            if (m_PingTexts[i]) m_PingTexts[i].Show(false);
            if (m_PingShadows[i]) m_PingShadows[i].Show(false);
        }
    }
}
