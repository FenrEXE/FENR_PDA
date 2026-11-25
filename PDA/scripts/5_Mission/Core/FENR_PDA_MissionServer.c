/*
    Fenrir Industries PDA
    Copyright: Fenr.EXE
    Maintainer: Fenr.EXE

    Writes pending PDA memory and groups to disk when the server mission
    ends, sends the server's PDA branding to each player as they connect,
    and drops per-player request state when they leave.
*/

modded class MissionServer
{
    override void InvokeOnConnect(PlayerBase player, PlayerIdentity identity)
    {
        super.InvokeOnConnect(player, identity);
        FENR_PDA_Server.SendBrand(identity);
    }

    override void PlayerDisconnected(PlayerBase player, PlayerIdentity identity, string uid)
    {
        if (identity)
        {
            string steam64 = identity.GetPlainId();
            FENR_PDA_Server.ForgetPlayer(steam64);
            FENR_PDA_Admin.Forget(steam64);
            FENR_PDA_Power.Forget(steam64);
        }
        super.PlayerDisconnected(player, identity, uid);
    }

    override void OnMissionFinish()
    {
        FENR_PDA_AccountStore.Flush();
        FENR_PDA_Groups.Flush();
        super.OnMissionFinish();
    }
}
