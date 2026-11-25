/*
    Fenrir Industries PDA
    Copyright: Fenr.EXE
    Maintainer: Fenr.EXE

    VPP-backed administration. The archive is read-only from this layer:
    admins can search it, inspect online users and send broadcasts.
*/

class FENR_PDA_Admin
{
    static const ref array<string> ADMIN_PERMISSIONS = {
        "MenuPlayerManager",
        "MenuItemManager",
        "MenuTeleportManager",
        "EspToolsMenu",
        "MenuCommandsConsole",
        "MenuServerManager",
        "MenuWeatherManager",
        "MenuObjectManager",
        "MenuBansManager",
        "MenuPermissionsEditor",
        "MenuWebHooks",
        "MenuXMLEditor",
        "MenuSpectateTools"
    };

    // VPP answers are reused for CACHE_MS (a permission change applies
    // within a minute).
    static const int CACHE_MS = 60000;
    protected static ref map<string, bool> s_Allowed;
    protected static ref map<string, int> s_CheckedAt;

    static bool IsAuthorized(PlayerIdentity identity)
    {
        if (!identity)
            return false;

        string steam64 = identity.GetPlainId();
        if (steam64 == "")
            return false;

        if (!s_Allowed)
        {
            s_Allowed = new map<string, bool>();
            s_CheckedAt = new map<string, int>();
        }
        int now = GetGame().GetTime();
        if (s_CheckedAt.Contains(steam64) && now - s_CheckedAt.Get(steam64) < CACHE_MS)
            return s_Allowed.Get(steam64);

        FENR_PDA_Storage.RememberIdentity(identity);
        bool allowed = CheckVpp(steam64);
        s_Allowed.Set(steam64, allowed);
        s_CheckedAt.Set(steam64, now);
        return allowed;
    }

    protected static bool CheckVpp(string steam64)
    {
        PermissionManager permissions = GetPermissionManager();
        if (!permissions)
            return false;

        foreach (string permission : ADMIN_PERMISSIONS)
        {
            if (permissions.VerifyPermission(steam64, permission, "", false))
                return true;
        }
        return false;
    }

    // A player left: forget their cached answer.
    static void Forget(string steam64)
    {
        if (!s_Allowed)
            return;
        s_Allowed.Remove(steam64);
        s_CheckedAt.Remove(steam64);
    }

    static ref FENR_PDA_AdminSearchResult BuildSearch(string query, string typeFilter, int page)
    {
        ref FENR_PDA_AdminSearchResult result = new FENR_PDA_AdminSearchResult();
        if (page < 0)
            page = 0;

        ref FENR_PDA_MessageSearch filter = new FENR_PDA_MessageSearch();
        filter.Query = query;
        if (typeFilter != "" && typeFilter != "ALL")
            filter.Type = typeFilter;

        int pageSize = FENR_PDA_Storage.SearchPageSize();
        ref array<ref FENR_PDA_MessageRecord> records = FENR_PDA_Storage.SearchMessages(filter, page * pageSize, pageSize, result.Total);

        foreach (FENR_PDA_MessageRecord record : records)
        {
            result.Headers.Insert(FormatHeader(record));
            result.Bodies.Insert(record.Message);
        }

        return result;
    }

    static string FormatHeader(FENR_PDA_MessageRecord record)
    {
        if (!record)
            return "";

        string shortTime = record.Timestamp;
        if (shortTime.Length() >= 16)
            shortTime = shortTime.Substring(5, 5) + " " + shortTime.Substring(11, 5);

        if (record.Type == FENR_PDA_MessageType.BROADCAST)
            return shortTime + " | " + record.SenderName + " > Broadcast";

        string target = record.TargetName;
        if (record.Type == FENR_PDA_MessageType.GROUP || record.Type == FENR_PDA_MessageType.CHANNEL)
            target = "#" + target;

        return shortTime + " | " + record.SenderName + " > " + target;
    }

    static void BuildOnlinePlayerRows(array<string> ids, array<string> rows)
    {
        if (!ids || !rows)
            return;

        ids.Clear();
        rows.Clear();

        ref array<Man> players = new array<Man>();
        GetGame().GetPlayers(players);

        // Who is using which logged-in PDA, in one pass over the sessions.
        ref array<PlayerBase> holders = new array<PlayerBase>();
        ref array<string> owners = new array<string>();
        FENR_PDA_Sessions.LiveHolders(holders, owners);

        foreach (Man man : players)
        {
            PlayerBase player = PlayerBase.Cast(man);
            if (!player || !player.GetIdentity())
                continue;

            string state = "NO PDA";
            int held = holders.Find(player);
            if (held != -1 && owners[held] == player.GetIdentity().GetPlainId())
                state = "LOGGED IN";
            else if (held != -1)
                state = "USING " + FENR_PDA_Storage.ResolvePlayerName(owners[held]) + "'S PDA";
            else if (FENR_PDA_Server.HasWorkingDevice(player))
                state = "PDA LOCKED";

            PlayerIdentity identity = player.GetIdentity();
            FENR_PDA_Storage.RememberIdentity(identity);
            ids.Insert(identity.GetPlainId());
            rows.Insert(identity.GetName() + " | " + identity.GetPlainId() + " | " + state);
        }
    }

    static bool Broadcast(PlayerIdentity admin, string message)
    {
        if (!admin || !IsAuthorized(admin) || message == "")
            return false;

        if (message.LengthUtf8() > FENR_PDA_Limits.ADMIN_BROADCAST)
            message = message.SubstringUtf8(0, FENR_PDA_Limits.ADMIN_BROADCAST);

        ref FENR_PDA_MessageRecord broadcastRecord = new FENR_PDA_MessageRecord();
        broadcastRecord.Type = FENR_PDA_MessageType.BROADCAST;
        broadcastRecord.SenderSteam64 = admin.GetPlainId();
        broadcastRecord.SenderName = admin.GetName();
        broadcastRecord.TargetID = "BROADCAST";
        broadcastRecord.TargetName = "Broadcast";
        broadcastRecord.Message = message;
        broadcastRecord.Seq = FENR_PDA_History.NextSeq();
        broadcastRecord.GameTime = FENR_PDA_UI_Kit.GameTime();
        FENR_PDA_Messages.Record(broadcastRecord);

        // Player-facing label stays anonymous/simple while the audit record keeps
        // the actual admin identity.
        FENR_PDA_Messages.BroadcastAnnouncement("Broadcast", message, broadcastRecord.Seq);
        FENR_PDA_Storage.LogAdmin(admin.GetName(), admin.GetPlainId(), "BROADCAST", "ALL PDA USERS", message);
        return true;
    }
};
