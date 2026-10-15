# pycdc 交叉复核产物 · script.fls entry 2865
# co_filename(原始)='script/protocol/csladderrankallstar.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2865.pyc (Python 2.5)

import net
import protocolcount
import netladderrankallstar
import avatar

def GS2COpenCreatTeamUI(oNetObj):
    iTeamType = oNetObj.UnpackInt(1)
    bShow = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=1', 'GS2COpenCreatTeamUI(iTeamType=%s,bShow=%s)' % (iTeamType, bShow))
    netladderrankallstar.OnOpenCreatTeamUI(iTeamType, bShow)


def GS2COpenTeamMemberUI(oNetObj):
    iTeamState = oNetObj.UnpackInt(1)
    iTeamId = oNetObj.UnpackInt(2)
    sTeamName = oNetObj.UnpackPS(1)
    lstMemberInfo = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iPlayerID = oNetObj.UnpackInt(4)
        sPlayerName = oNetObj.UnpackPS(1)
        iLevel = oNetObj.UnpackInt(1)
        iZhiye = oNetObj.UnpackInt(1)
        iDuanwei = oNetObj.UnpackInt(1)
        iWinPoint = oNetObj.UnpackInt(2)
        iStatus = oNetObj.UnpackInt(1)
        lstPhoto = avatar.UnpackPhotoInt4(oNetObj)
        iFrm = avatar.UnpackAvatarFrm(iPlayerID)(oNetObj)
        lstMemberInfo.append([
            iPlayerID,
            sPlayerName,
            iLevel,
            iZhiye,
            iDuanwei,
            iWinPoint,
            iStatus,
            lstPhoto,
            iFrm])
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=2', 'GS2COpenTeamMemberUI(iTeamState=%s,iTeamId=%s,sTeamName=%s,lstMemberInfo=%s)' % (iTeamState, iTeamId, sTeamName, lstMemberInfo))
    netladderrankallstar.OnOpenTeamMemberUI(iTeamState, iTeamId, sTeamName, lstMemberInfo)


def GS2COpenAllTeam(oNetObj):
    iTeamType = oNetObj.UnpackInt(1)
    iMyTeamId = oNetObj.UnpackInt(2)
    sMyName = oNetObj.UnpackPS(1)
    iMyServerId = oNetObj.UnpackInt(2)
    iMyDanRank = oNetObj.UnpackInt(1)
    iMyWinPoint = oNetObj.UnpackInt(2)
    lstAllTeamInfo = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iTeamId = oNetObj.UnpackInt(2)
        sName = oNetObj.UnpackPS(1)
        iServerId = oNetObj.UnpackInt(2)
        iDanRank = oNetObj.UnpackInt(1)
        iWinPoint = oNetObj.UnpackInt(2)
        lstAllTeamInfo.append([
            iTeamId,
            sName,
            iServerId,
            iDanRank,
            iWinPoint])
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=3', 'GS2COpenAllTeam(iTeamType=%s,iMyTeamId=%s,sMyName=%s,iMyServerId=%s,iMyDanRank=%s,iMyWinPoint=%s,lstAllTeamInfo=%s)' % (iTeamType, iMyTeamId, sMyName, iMyServerId, iMyDanRank, iMyWinPoint, lstAllTeamInfo))
    netladderrankallstar.OnOpenAllTeam(iTeamType, iMyTeamId, sMyName, iMyServerId, iMyDanRank, iMyWinPoint, lstAllTeamInfo)


def GS2CAllRankInfo(oNetObj):
    iTeamType = oNetObj.UnpackInt(1)
    dAllRankInfo = { }
    for _index in xrange(oNetObj.UnpackInt(1)):
        iMatchType = oNetObj.UnpackInt(2)
        iState = oNetObj.UnpackInt(1)
        iWinTeamID = oNetObj.UnpackInt(2)
        lAllRankInfo = []
        for _index in xrange(oNetObj.UnpackInt(1)):
            iTeamId = oNetObj.UnpackInt(2)
            sTeamName = oNetObj.UnpackPS(1)
            iServerId = oNetObj.UnpackInt(2)
            lAllRankInfo.append([
                iTeamId,
                sTeamName,
                iServerId])
        
        dAllRankInfo[iMatchType] = [
            iState,
            iWinTeamID,
            lAllRankInfo]
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=4', 'GS2CAllRankInfo(iTeamType=%s,dAllRankInfo=%s)' % (iTeamType, dAllRankInfo))
    netladderrankallstar.OnAllRankInfo(iTeamType, dAllRankInfo)


def GS2COpenMatchScheduleUI(oNetObj):
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=5', 'GS2COpenMatchScheduleUI()')
    netladderrankallstar.OnOpenMatchScheduleUI()


def GS2COpenompetitionRewardUI(oNetObj):
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=6', 'GS2COpenompetitionRewardUI()')
    netladderrankallstar.OnOpenompetitionRewardUI()


def GS2COpenCDPanel(oNetObj):
    iBattleOfIdx = oNetObj.UnpackInt(1)
    iTimer = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=7', 'GS2COpenCDPanel(iBattleOfIdx=%s,iTimer=%s)' % (iBattleOfIdx, iTimer))
    netladderrankallstar.OnOpenCDPanel(iBattleOfIdx, iTimer)


def GS2CCloseMatchUI(oNetObj):
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=8', 'GS2CCloseMatchUI()')
    netladderrankallstar.OnCloseMatchUI()


def GS2COpenGuessUI(oNetObj):
    iGroup = oNetObj.UnpackInt(1)
    lstGuess = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iGameID = oNetObj.UnpackInt(4)
        iStartTime = oNetObj.UnpackInt(4)
        iState = oNetObj.UnpackInt(1)
        iMatchState = oNetObj.UnpackInt(1)
        iWinTeam = oNetObj.UnpackInt(4)
        iTeamA = oNetObj.UnpackInt(4)
        iTeamAGroup = oNetObj.UnpackInt(1)
        iTeamACoin = oNetObj.UnpackInt(4)
        iTeamAName = oNetObj.UnpackPS(1)
        iTeamAServerName = oNetObj.UnpackPS(1)
        iTeamASupportTicket = oNetObj.UnpackInt(4)
        iTeamB = oNetObj.UnpackInt(4)
        iTeamBGroup = oNetObj.UnpackInt(1)
        iTeamBCoin = oNetObj.UnpackInt(4)
        iTeamBName = oNetObj.UnpackPS(1)
        iTeamBServerName = oNetObj.UnpackPS(1)
        iTeamBSupportTicket = oNetObj.UnpackInt(4)
        lstGuess.append([
            iGameID,
            iStartTime,
            iState,
            iMatchState,
            iWinTeam,
            iTeamA,
            iTeamAGroup,
            iTeamACoin,
            iTeamAName,
            iTeamAServerName,
            iTeamASupportTicket,
            iTeamB,
            iTeamBGroup,
            iTeamBCoin,
            iTeamBName,
            iTeamBServerName,
            iTeamBSupportTicket])
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=100', 'GS2COpenGuessUI(iGroup=%s,lstGuess=%s)' % (iGroup, lstGuess))
    netladderrankallstar.OnOpenGuessUI(iGroup, lstGuess)


def GS2COpenChampionGuessUI(oNetObj):
    iGroup = oNetObj.UnpackInt(1)
    lstTeam = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iTeam = oNetObj.UnpackInt(4)
        iTeamGroup = oNetObj.UnpackInt(1)
        iCoin = oNetObj.UnpackInt(1)
        sTeamName = oNetObj.UnpackPS(1)
        sServerName = oNetObj.UnpackPS(1)
        iServerNum = oNetObj.UnpackInt(2)
        lstTeam.append([
            iTeam,
            iTeamGroup,
            iCoin,
            sTeamName,
            sServerName,
            iServerNum])
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=101', 'GS2COpenChampionGuessUI(iGroup=%s,lstTeam=%s)' % (iGroup, lstTeam))
    netladderrankallstar.OnOpenChampionGuessUI(iGroup, lstTeam)


def GS2CRefreshCoin(oNetObj):
    iCoin = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=102', 'GS2CRefreshCoin(iCoin=%s)' % iCoin)
    netladderrankallstar.OnRefreshCoin(iCoin)


def GS2CRefreshScore(oNetObj):
    iScore = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=103', 'GS2CRefreshScore(iScore=%s)' % iScore)
    netladderrankallstar.OnRefreshScore(iScore)


def GS2CSendMyGuessList(oNetObj):
    lstGuess = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iGameID = oNetObj.UnpackInt(4)
        iStartTime = oNetObj.UnpackInt(4)
        iWinTeam = oNetObj.UnpackInt(4)
        iMatchState = oNetObj.UnpackInt(1)
        iTeamA = oNetObj.UnpackInt(4)
        iTeamACoin = oNetObj.UnpackInt(4)
        iTeamAName = oNetObj.UnpackPS(1)
        iTeamB = oNetObj.UnpackInt(4)
        iTeamBCoin = oNetObj.UnpackInt(4)
        iTeamBName = oNetObj.UnpackPS(1)
        lstGuess.append([
            iGameID,
            iStartTime,
            iWinTeam,
            iMatchState,
            iTeamA,
            iTeamACoin,
            iTeamAName,
            iTeamB,
            iTeamBCoin,
            iTeamBName])
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=104', 'GS2CSendMyGuessList(lstGuess=%s)' % lstGuess)
    netladderrankallstar.OnSendMyGuessList(lstGuess)


def GS2CZhuWeiInfo(oNetObj):
    iGameID = oNetObj.UnpackInt(4)
    iTeamA = oNetObj.UnpackInt(4)
    iTeamACoin = oNetObj.UnpackInt(4)
    iTeamAName = oNetObj.UnpackPS(1)
    iTeamAServerName = oNetObj.UnpackPS(1)
    iTeamB = oNetObj.UnpackInt(4)
    iTeamBCoin = oNetObj.UnpackInt(4)
    iTeamBName = oNetObj.UnpackPS(1)
    iTeamBServerName = oNetObj.UnpackPS(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=105', 'GS2CZhuWeiInfo(iGameID=%s,iTeamA=%s,iTeamACoin=%s,iTeamAName=%s,iTeamAServerName=%s,iTeamB=%s,iTeamBCoin=%s,iTeamBName=%s,iTeamBServerName=%s)' % (iGameID, iTeamA, iTeamACoin, iTeamAName, iTeamAServerName, iTeamB, iTeamBCoin, iTeamBName, iTeamBServerName))
    netladderrankallstar.OnZhuWeiInfo(iGameID, iTeamA, iTeamACoin, iTeamAName, iTeamAServerName, iTeamB, iTeamBCoin, iTeamBName, iTeamBServerName)


def GS2CGuessShopItem(oNetObj):
    lstItem = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iItem = oNetObj.UnpackInt(4)
        iPrice = oNetObj.UnpackInt(2)
        sDesc = oNetObj.UnpackPS(1)
        lstItem.append([
            iItem,
            iPrice,
            sDesc])
    
    iScore = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=106', 'GS2CGuessShopItem(lstItem=%s,iScore=%s)' % (lstItem, iScore))
    netladderrankallstar.OnGuessShopItem(lstItem, iScore)


def GS2CGuessTips(oNetObj):
    iTeamID = oNetObj.UnpackInt(4)
    iServerID = oNetObj.UnpackInt(2)
    sTeamName = oNetObj.UnpackPS(1)
    sLeaderName = oNetObj.UnpackPS(1)
    lstMemberInfo = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        sMemberName = oNetObj.UnpackPS(1)
        lstMemberInfo.append(sMemberName)
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=107', 'GS2CGuessTips(iTeamID=%s,iServerID=%s,sTeamName=%s,sLeaderName=%s,lstMemberInfo=%s)' % (iTeamID, iServerID, sTeamName, sLeaderName, lstMemberInfo))
    netladderrankallstar.OnGuessTips(iTeamID, iServerID, sTeamName, sLeaderName, lstMemberInfo)

g_NetFunction = {
    1: GS2COpenCreatTeamUI,
    2: GS2COpenTeamMemberUI,
    3: GS2COpenAllTeam,
    4: GS2CAllRankInfo,
    5: GS2COpenMatchScheduleUI,
    6: GS2COpenompetitionRewardUI,
    7: GS2COpenCDPanel,
    8: GS2CCloseMatchUI,
    100: GS2COpenGuessUI,
    101: GS2COpenChampionGuessUI,
    102: GS2CRefreshCoin,
    103: GS2CRefreshScore,
    104: GS2CSendMyGuessList,
    105: GS2CZhuWeiInfo,
    106: GS2CGuessShopItem,
    107: GS2CGuessTips }

def OnCommand(oNetObj):
    iSub = oNetObj.UnpackInt(1)
    func = g_NetFunction.get(iSub)
    if not func:
        protocolcount.ErrorLog('net.GS2C_HUODONG_OP', '\xdb"\xc4\x05\xd6\xbf\xc4<N)=\\-1&;ODONG_OP=0xce \xaa\xba\xa4l\xa8\xf3\xc4\xb3\xa1G%s' % iSub)
        return None
    
    func(oNetObj)


def C2GSCreateTeam(sTeamName):
    oNetObj = GetHuoDongNetObj(1)
    oNetObj.PacketAddPS(sTeamName, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=1', 'C2GSCreateTeam(sTeamName=%s)' % sTeamName)


def C2GSAllTeamType(iTeamType):
    oNetObj = GetHuoDongNetObj(2)
    oNetObj.PacketAddI(iTeamType, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=2', 'C2GSAllTeamType(iTeamType=%s)' % iTeamType)


def C2GSTeamInfo(iTeamState, iTeamId):
    oNetObj = GetHuoDongNetObj(3)
    oNetObj.PacketAddI(iTeamState, 1)
    oNetObj.PacketAddI(iTeamId, 2)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=3', 'C2GSTeamInfo(iTeamState=%s,iTeamId=%s)' % (iTeamState, iTeamId))


def C2GSAllRankInfo(iTeamType):
    oNetObj = GetHuoDongNetObj(4)
    oNetObj.PacketAddI(iTeamType, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=4', 'C2GSAllRankInfo(iTeamType=%s)' % iTeamType)


def C2GSWatchViedo(iTeamType, iMatchType, iTeamId):
    oNetObj = GetHuoDongNetObj(5)
    oNetObj.PacketAddI(iTeamType, 1)
    oNetObj.PacketAddI(iMatchType, 2)
    oNetObj.PacketAddI(iTeamId, 2)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=5', 'C2GSWatchViedo(iTeamType=%s,iMatchType=%s,iTeamId=%s)' % (iTeamType, iMatchType, iTeamId))


def C2GSCloseZhuwei():
    oNetObj = GetHuoDongNetObj(6)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=6', 'C2GSCloseZhuwei()')


def C2GSOpenGuessUI(iGroup):
    oNetObj = GetHuoDongNetObj(100)
    oNetObj.PacketAddI(iGroup, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=100', 'C2GSOpenGuessUI(iGroup=%s)' % iGroup)


def C2GSOpenChampionGuessUI(iGroup):
    oNetObj = GetHuoDongNetObj(101)
    oNetObj.PacketAddI(iGroup, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=101', 'C2GSOpenChampionGuessUI(iGroup=%s)' % iGroup)


def C2GSGuessGame(iGameID, iTeamID, iCoin):
    oNetObj = GetHuoDongNetObj(102)
    oNetObj.PacketAddI(iGameID, 4)
    oNetObj.PacketAddI(iTeamID, 4)
    oNetObj.PacketAddI(iCoin, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=102', 'C2GSGuessGame(iGameID=%s,iTeamID=%s,iCoin=%s)' % (iGameID, iTeamID, iCoin))


def C2GSGuessChampion(iGroup, iTeamID):
    oNetObj = GetHuoDongNetObj(103)
    oNetObj.PacketAddI(iGroup, 1)
    del PacketAddI
    None(oNetObj.PacketAddI, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=103', 'C2GSGuessChampion(iGroup=%s,iTeamID=%s)' % (iGroup, iTeamID))


def C2GSGuessBuyItem(iItem, iAmount):
    oNetObj = GetHuoDongNetObj(104)
    oNetObj.PacketAddI(iItem, 4)
    oNetObj.PacketAddI(iAmount, 2)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=104', 'C2GSGuessBuyItem(iItem=%s,iAmount=%s)' % (iItem, iAmount))


def C2GSZhuwei(iTeamID, iGameID):
    oNetObj = GetHuoDongNetObj(105)
    oNetObj.PacketAddI(iTeamID, 4)
    oNetObj.PacketAddI(iGameID, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=105', 'C2GSZhuwei(iTeamID=%s,iGameID=%s)' % (iTeamID, iGameID))


def C2GSOpenShop():
    oNetObj = GetHuoDongNetObj(106)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=106', 'C2GSOpenShop()')


def C2GSMyGuessUI():
    oNetObj = GetHuoDongNetObj(107)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=107', 'C2GSMyGuessUI()')


def C2GSGuessTips(iTeamID, iServerID):
    oNetObj = GetHuoDongNetObj(108)
    oNetObj.PacketAddI(iTeamID, 4)
    oNetObj.PacketAddI(iServerID, 2)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=108', 'C2GSGuessTips(iTeamID=%s,iServerID=%s)' % (iTeamID, iServerID))


def C2GSOpenFirstGuess():
    oNetObj = GetHuoDongNetObj(109)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=109', 'C2GSOpenFirstGuess()')


def GetHuoDongNetObj(iSub):
    import nethuodong
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_HUODONG)
    oNetObj.PacketAddI(len(nethuodong.LADDERRANKALLSTAR), 1)
    oNetObj.PacketAddS(nethuodong.LADDERRANKALLSTAR, len(nethuodong.LADDERRANKALLSTAR))
    oNetObj.PacketAddI(iSub, 1)
    return oNetObj
