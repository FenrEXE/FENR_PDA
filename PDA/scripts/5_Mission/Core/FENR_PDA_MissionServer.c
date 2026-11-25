/*
    Fenrir Industries PDA
    Copyright: Fenr.EXE
    Maintainer: Fenr.EXE

    Writes pending PDA memory to disk when the server mission ends, and
    sends the server's PDA branding to each player as they connect.
*/

modded class MissionServer
{
    override void InvokeOnConnect(PlayerBase player, PlayerIdentity identity)
    {
        super.InvokeOnConnect(player, identity);
        FENR_PDA_Server.SendBrand(identity);
    }

    override void OnMissionFinish()
    {
        FENR_PDA_AccountStore.Flush();
        super.OnMissionFinish();
    }
}
