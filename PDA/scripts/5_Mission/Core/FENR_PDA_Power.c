/*
    Fenrir Industries PDA
    Copyright: Fenr.EXE
    Maintainer: Fenr.EXE

    Battery drain (server side).  Every tick the server drains the 9V cell
    of each PDA in use by a configurable percentage per minute.  A powered
    PDA in hands always counts as open; clients also report the map view.
*/

class FENR_PDA_Power
{
    static const int MODE_CLOSED = 0;
    static const int MODE_OPEN = 1;
    static const int MODE_MAP = 2;
    static const int TICK_MS = 10000;

    protected static ref map<string, int> s_Usage;
    protected static bool s_Initialized = false;

    static void Init()
    {
        if (s_Initialized || !GetGame().IsServer())
            return;
        s_Usage = new map<string, int>();
        s_Initialized = true;
        GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(PowerTick, TICK_MS, true);
    }

    static void SetUsage(PlayerIdentity identity, int mode)
    {
        if (!identity)
            return;
        if (!s_Usage)
            s_Usage = new map<string, int>();

        string id = identity.GetPlainId();
        if (mode <= MODE_CLOSED)
            s_Usage.Remove(id);
        else
            s_Usage.Set(id, mode);
    }

    // A player left: their report goes.
    static void Forget(string steam64)
    {
        if (s_Usage)
            s_Usage.Remove(steam64);
    }

    // v8.8: the server decides.  A powered PDA in a player's hands drains at
    // the "open" rate whatever the client reports (the PDA is only opened
    // from hands); the client's report can only add to that (map view, or a
    // PDA left open after it was put away).
    static void PowerTick()
    {
        if (!FENR_PDA_Storage.BatteryDrainEnabled())
            return;

        float openRate = FENR_PDA_Storage.BatteryDrainOpenPerMinute();
        float mapRate = FENR_PDA_Storage.BatteryDrainMapPerMinute();
        float tickMinutes = TICK_MS / 60000.0;
        if (!s_Usage)
            s_Usage = new map<string, int>();

        array<Man> players = new array<Man>();
        GetGame().GetPlayers(players);
        foreach (Man man : players)
        {
            PlayerBase player = PlayerBase.Cast(man);
            if (!player || !player.GetIdentity() || !player.IsAlive())
                continue;

            string id = player.GetIdentity().GetPlainId();
            int mode = MODE_CLOSED;
            if (s_Usage.Contains(id))
                mode = s_Usage.Get(id);

            EntityAI battery = null;
            FENR_PDA_Device hands = FENR_PDA_Device.Cast(player.GetItemInHands());
            if (hands && FENR_PDA_Server.IsWorkingDevice(hands))
            {
                if (mode < MODE_OPEN)
                    mode = MODE_OPEN;
                battery = DeviceBattery(hands);
            }
            else if (mode > MODE_CLOSED)
            {
                battery = FENR_PDA_Server.FindDeviceBattery(player);
            }
            if (mode <= MODE_CLOSED || !battery || !battery.GetCompEM())
                continue;

            float percent = openRate;
            if (mode == MODE_MAP)
                percent += mapRate;

            float drain = battery.GetCompEM().GetEnergyMax() * (percent / 100.0) * tickMinutes;
            if (drain > 0)
                battery.GetCompEM().AddEnergy(-drain);
        }
    }

    protected static EntityAI DeviceBattery(FENR_PDA_Device device)
    {
        EntityAI battery = device.FindAttachmentBySlotName("BatteryD");
        if (!battery && device.GetCompEM())
            battery = device.GetCompEM().GetEnergySource();
        return battery;
    }
};
