/*
    Fenrir Industries PDA
    Copyright: Fenr.EXE
    Maintainer: Fenr.EXE

    Client display settings (theme + compass HUD).  These are personal
    preferences, so they live on the player's machine, not on the PDA:
        $profile:\PDA\Settings.json
*/

class FENR_PDA_SettingsStore
{
    static const string SETTINGS_FILE = "$profile:\\PDA\\Settings.json";

    protected static ref FENR_PDA_Settings s_Settings;

    static FENR_PDA_Settings Get()
    {
        if (!s_Settings)
            Load();
        return s_Settings;
    }

    static void Load()
    {
        s_Settings = new FENR_PDA_Settings();
        if (FileExist(SETTINGS_FILE))
            JsonFileLoader<ref FENR_PDA_Settings>.JsonLoadFile(SETTINGS_FILE, s_Settings);
        if (!s_Settings)
            s_Settings = new FENR_PDA_Settings();
        Normalize();
        ApplyTheme();
    }

    protected static void Normalize()
    {
        if (!s_Settings.MutedChats)
            s_Settings.MutedChats = new array<string>();
        if (!s_Settings.MutedNames)
            s_Settings.MutedNames = new array<string>();
        while (s_Settings.MutedNames.Count() < s_Settings.MutedChats.Count())
            s_Settings.MutedNames.Insert("");
        while (s_Settings.MutedNames.Count() > s_Settings.MutedChats.Count())
            s_Settings.MutedNames.Remove(s_Settings.MutedNames.Count() - 1);
        s_Settings.Hue = WrapHue(s_Settings.Hue);
        s_Settings.CompassHue = WrapHue(s_Settings.CompassHue);
        s_Settings.Saturation = Math.Clamp(s_Settings.Saturation, 0, 150);
        s_Settings.Brightness = Math.Clamp(s_Settings.Brightness, 50, 130);
        s_Settings.Backlight = Math.Clamp(s_Settings.Backlight, 40, 250);
        s_Settings.CompassPosition = Math.Clamp(s_Settings.CompassPosition, 0, 1);
        s_Settings.CompassSize = Math.Clamp(s_Settings.CompassSize, 0, 2);
        s_Settings.CompassStyle = Math.Clamp(s_Settings.CompassStyle, 0, FENR_PDA_CompassHud.STYLE_COUNT - 1);
        s_Settings.CompassOpacity = Math.Clamp(s_Settings.CompassOpacity, 20, 100);
    }

    static int WrapHue(int hue)
    {
        int result = hue;
        while (result < 0) result += 360;
        while (result >= 360) result -= 360;
        return result;
    }

    static void Save()
    {
        if (!s_Settings)
            return;
        MakeDirectory(FENR_PDA_Paths.PROFILE_ROOT);
        JsonFileLoader<ref FENR_PDA_Settings>.JsonSaveFile(SETTINGS_FILE, s_Settings);
    }

    static void ApplyTheme()
    {
        FENR_PDA_UI_Theme.Build(s_Settings.Hue, s_Settings.Saturation, s_Settings.Brightness, s_Settings.Backlight);
    }

    // Call after changing any setting: saves, rebuilds the palette and
    // recolours everything that is on screen.
    static void Changed()
    {
        Normalize();
        Save();
        ApplyTheme();
        if (FENR_PDA_Menu.GetInstance())
            FENR_PDA_Menu.GetInstance().OnThemeChanged();
        FENR_PDA_Toast.OnThemeChanged();
        FENR_PDA_CompassHud.OnSettingsChanged();
    }

    // ------------------------------------------------------------------
    // Sounds (v8.5)
    // ------------------------------------------------------------------
    static const int SOUND_DIRECT = 0;
    static const int SOUND_CHANNEL = 1;
    static const int SOUND_GROUP = 2;
    static const int SOUND_ANNOUNCE = 3;
    static const int SOUND_BOUNTY = 4;
    static const int SOUND_SOS = 5;

    static string GroupKey(string groupID)
    {
        return "G:" + groupID;
    }

    static bool IsChatMuted(string key)
    {
        if (key == "") return false;
        return Get().MutedChats.Find(key) != -1;
    }

    static void SetChatMuted(string key, string name, bool muted)
    {
        if (key == "") return;
        FENR_PDA_Settings settings = Get();
        int index = settings.MutedChats.Find(key);
        if (muted && index == -1)
        {
            settings.MutedChats.Insert(key);
            settings.MutedNames.Insert(name);
        }
        else if (!muted && index != -1)
        {
            settings.MutedChats.Remove(index);
            settings.MutedNames.Remove(index);
        }
        else if (muted && name != "")
        {
            settings.MutedNames.Set(index, name);
        }
        SaveSounds();
    }

    static void UnmuteAll()
    {
        FENR_PDA_Settings settings = Get();
        settings.MutedChats.Clear();
        settings.MutedNames.Clear();
        SaveSounds();
    }

    static void SaveSounds()
    {
        Normalize();
        Save();
    }

    // Should incoming traffic of this kind (and chat key) play a sound?
    static bool SoundAllowed(int kind, string key = "")
    {
        FENR_PDA_Settings settings = Get();
        if (kind == SOUND_SOS) return settings.SoundSos;
        if (!settings.SoundChats) return false;
        if (kind == SOUND_DIRECT && !settings.SoundDirect) return false;
        if (kind == SOUND_CHANNEL && !settings.SoundChannels) return false;
        if (kind == SOUND_GROUP && !settings.SoundGroups) return false;
        if (kind == SOUND_ANNOUNCE && !settings.SoundAnnouncements) return false;
        if (kind == SOUND_BOUNTY && !settings.SoundBounties) return false;
        return !IsChatMuted(key);
    }

    static void ApplyPreset(FENR_PDA_ThemePreset preset)
    {
        if (!preset)
            return;
        FENR_PDA_Settings settings = Get();
        settings.Preset = preset.Name;
        settings.Hue = preset.Hue;
        settings.Saturation = preset.Saturation;
        Changed();
    }

    static void ResetDisplay()
    {
        FENR_PDA_Settings settings = Get();
        FENR_PDA_Settings defaults = new FENR_PDA_Settings();
        settings.Preset = defaults.Preset;
        settings.Hue = defaults.Hue;
        settings.Saturation = defaults.Saturation;
        settings.Brightness = defaults.Brightness;
        settings.Backlight = defaults.Backlight;
        Changed();
    }

    static void ResetCompass()
    {
        FENR_PDA_Settings settings = Get();
        FENR_PDA_Settings defaults = new FENR_PDA_Settings();
        settings.CompassEnabled = defaults.CompassEnabled;
        settings.CompassPosition = defaults.CompassPosition;
        settings.CompassSize = defaults.CompassSize;
        settings.CompassOpacity = defaults.CompassOpacity;
        settings.CompassMatchTheme = defaults.CompassMatchTheme;
        settings.CompassHue = defaults.CompassHue;
        settings.CompassMarkers = defaults.CompassMarkers;
        settings.CompassDistances = defaults.CompassDistances;
        settings.CompassBearing = defaults.CompassBearing;
        Changed();
    }
};
