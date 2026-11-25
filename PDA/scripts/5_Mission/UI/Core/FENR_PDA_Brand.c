/*
    Fenrir Industries PDA
    Copyright: Fenr.EXE
    Maintainer: Fenr.EXE

    Server branding (v8.3), client side.

    The server config sets the name, tagline, pop-up network label, logo and
    an optional full banner image (FENR_PDA_Config.Brand*).  The server sends
    them on connect and whenever a PDA is opened; until then the built-in
    Fenrir branding is shown.

    Header / login brand block widgets (<p> = "FI_" or "FI_LOGIN_"):
      <p>BrandLogo    logo: built-in wolf, the server's image, or hidden
      <p>Brand        built-in "FENRIR INDUSTRIES" text art (default text only)
      <p>BrandName    server name as live text
      <p>BrandTag     server tagline as live text
      <p>BrandBanner  server banner image, replaces everything above
*/
class FENR_PDA_Brand
{
    static const string DEFAULT_NAME = "FENRIR INDUSTRIES";
    static const string DEFAULT_TAGLINE = "SECURE FIELD NETWORK";
    static const string DEFAULT_NETWORK = "FENRIR SECURE NETWORK";
    static const string DEFAULT_LOGO = "FENR_PDA/PDA/gui/os/textures/brand_logo.edds";

    // Layout ratios (gen_layout.py brand_block): the text starts 83.27 ref px
    // from the left of the block; the logo is 73.07 px wide.
    static const float TEXT_OFFSET = 1.1396;   // 83.27 / 73.07 logo widths

    protected static bool s_Received;
    protected static string s_Name;
    protected static string s_Tagline;
    protected static string s_Network;
    protected static string s_Logo;
    protected static bool s_Untinted;      // BrandLogoTinted = false
    protected static string s_Banner;

    // Name text fitting (a long name shrinks to fit its box).
    protected static int s_FitFrames;

    static void Receive(array<string> fields)
    {
        if (!fields || fields.Count() < 6)
            return;
        s_Received = true;
        s_Name = fields[0];
        s_Tagline = fields[1];
        s_Network = fields[2];
        s_Logo = fields[3];
        s_Untinted = fields[4] == "0";
        s_Banner = fields[5];
    }

    static string Name()
    {
        if (!s_Received || s_Name == "")
            return DEFAULT_NAME;
        return s_Name;
    }

    // "" = no tagline.
    static string Tagline()
    {
        if (!s_Received)
            return DEFAULT_TAGLINE;
        return s_Tagline;
    }

    static string Network()
    {
        if (!s_Received || s_Network == "")
            return DEFAULT_NETWORK;
        return s_Network;
    }

    // "OFFICIAL SECURE FIELD NETWORK BULLETIN"
    static string BulletinLabel()
    {
        string tag = Tagline();
        if (tag == "")
            tag = Network();
        return "OFFICIAL " + tag + " BULLETIN";
    }

    protected static bool DefaultText()
    {
        return Name() == DEFAULT_NAME && Tagline() == DEFAULT_TAGLINE;
    }

    // ------------------------------------------------------------------
    // Widgets
    // ------------------------------------------------------------------
    // Call after the theme colours are applied (the logo / banner colour
    // depends on BrandLogoTinted).
    static void Apply(Widget root, string p)
    {
        if (!root)
            return;
        ImageWidget logo = ImageWidget.Cast(root.FindAnyWidget(p + "BrandLogo"));
        ImageWidget art = ImageWidget.Cast(root.FindAnyWidget(p + "Brand"));
        TextWidget nameW = TextWidget.Cast(root.FindAnyWidget(p + "BrandName"));
        TextWidget tagW = TextWidget.Cast(root.FindAnyWidget(p + "BrandTag"));
        ImageWidget banner = ImageWidget.Cast(root.FindAnyWidget(p + "BrandBanner"));
        if (!logo || !art)
            return;

        // The text art keeps the theme colour; it is the tint for images.
        int tint = art.GetColor();
        int white = ARGB(255, 255, 255, 255);

        // Banner: one image instead of everything else.
        bool useBanner = false;
        if (banner)
        {
            if (s_Received && s_Banner != "" && banner.LoadImageFile(0, s_Banner))
            {
                banner.SetImage(0);
                useBanner = true;
                if (s_Untinted)
                    banner.SetColor(white);
                else
                    banner.SetColor(tint);
            }
            banner.Show(useBanner);
        }

        // Logo.
        bool showLogo = !useBanner;
        bool customLogo = false;
        if (s_Received && s_Logo == "none")
            showLogo = false;
        if (showLogo)
        {
            if (s_Received && s_Logo != "" && logo.LoadImageFile(0, s_Logo))
            {
                customLogo = true;
            }
            else
            {
                logo.LoadImageFile(0, DEFAULT_LOGO);
            }
            logo.SetImage(0);
            if (customLogo && s_Untinted)
                logo.SetColor(white);
            else
                logo.SetColor(tint);
        }
        logo.Show(showLogo);

        // Text moves left into the logo's place when there is no logo.
        float lx, ly, lw, lh;
        logo.GetPos(lx, ly);
        logo.GetSize(lw, lh);
        float offset = lw * TEXT_OFFSET;
        float shift = 0;
        if (!showLogo)
            shift = offset;

        float ax, ay;
        art.GetPos(ax, ay);
        art.SetPos(lx - shift, ay);

        bool defaultText = DefaultText();
        art.Show(!useBanner && defaultText);

        float tx, ty;
        if (nameW)
        {
            nameW.GetPos(tx, ty);
            nameW.SetPos(lx + offset - shift, ty);
            nameW.SetText(Name());
            nameW.Show(!useBanner && !defaultText);
        }
        if (tagW)
        {
            tagW.GetPos(tx, ty);
            tagW.SetPos(lx + offset - shift, ty);
            tagW.SetText(Tagline());
            tagW.Show(!useBanner && !defaultText && Tagline() != "");
        }
        s_FitFrames = 4;
    }

    // Called every frame while the PDA is open: shrinks a long name to fit
    // its box (text sizes are only known after a frame has been drawn).
    static void FitStep(Widget root)
    {
        if (s_FitFrames <= 0 || !root)
            return;
        s_FitFrames--;
        FitName(TextWidget.Cast(root.FindAnyWidget("FI_BrandName")));
        FitName(TextWidget.Cast(root.FindAnyWidget("FI_LOGIN_BrandName")));
    }

    // Frame 3: set the name to full height.  Frame 2: measure it and
    // shrink it if it is wider than its box.
    protected static void FitName(TextWidget nameW)
    {
        if (!nameW || !nameW.IsVisible())
            return;
        float bw, bh;
        nameW.GetScreenSize(bw, bh);
        if (bw <= 0 || bh <= 0)
            return;
        int full = Math.Round(bh * 0.9);
        if (full < 8)
            full = 8;
        if (s_FitFrames == 3)
        {
            nameW.SetTextExactSize(full);
            return;
        }
        if (s_FitFrames != 2)
            return;
        int tw, th;
        nameW.GetTextSize(tw, th);
        if (tw <= 0 || tw <= bw)
            return;
        int size = Math.Floor(full * bw * 0.97 / tw);
        if (size < 8)
            size = 8;
        nameW.SetTextExactSize(size);
    }

    // Screen size changed: fit again.
    static void Refit()
    {
        s_FitFrames = 4;
    }
};
