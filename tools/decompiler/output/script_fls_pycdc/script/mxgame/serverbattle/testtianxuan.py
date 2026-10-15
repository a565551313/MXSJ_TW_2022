# pycdc 交叉复核产物 · script.fls entry 2727
# co_filename(原始)='script/mxgame/serverbattle/testtianxuan.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2727.pyc (Python 2.5)

import allstarinterface
g_CShitugTest = None

def GetServerBattleTest():
    global g_CShitugTest
    if not g_CShitugTest:
        g_CShitugTest = CServerBattleTest()
    
    return g_CShitugTest

import mdsbasroll
import mdserverbattleteam

def S2CRefreshDragonInfo():
    '''
import testtianxuan as ti
ti.S2CRefreshDragonInfo()
\t:return:
\t'''
    import dragonpk
    iLenOrg = 1
    sOrgName = 'xxxxxxxxx'
    orgHP = 1
    iOrgMaxHp = 2
    iTowerNum = 3
    iTowerLimit = 4
    dragonpk.RefreshDragonPanel([
        sOrgName,
        orgHP,
        iOrgMaxHp,
        iTowerNum,
        iTowerLimit])


def S2CTeamInfo():
    '''
\t\xa5\xb4\xb6}\xac\xc9\xad\xb1\xaa\xba\xabH\xae\xa7
\t#c2s-1, s2c-1
\t:return:
import testtianxuan as ti
ti.S2CTeamInfo()
import testtianxuan as ti
ti.S2CTeamRecord()
import testtianxuan as ti
ti.S2CTeamRank()
\tti.S2CTeamManagerInfo()
\t'''
    import misc
    import random
    iTeamGroup = random.randint(1, 3)
    iTeamID = 10001
    iBattleRank = 110
    iPowerRank = 220
    iCaptainID = 10001
    iTeamPowerPoint = 300000
    iTeamBattlePoint = 40000
    sTeamName = 'wdnmd'
    sBuildTime = misc.GetServerCurrentTime()
    PlayerNum = 5
    dictPlayerData = { }
    for i in range(PlayerNum):
        dictPlayer = { }
        iID = i + 10001
        dictPlayer['iSex'] = random.randint(1, 2)
        dictPlayer['iGroup'] = random.randint(1, 2)
        dictPlayer['iLevel'] = random.randint(50, 200)
        dictPlayer['sName'] = 'dnm%d' % i
        dictPlayer['PhotoLst'] = [
            (250539758, 250539758, 250539758, 250539631)]
        dictPlayer['iFightPoint'] = random.randint(1000, 10000)
        dictPlayer['iJob'] = 1
        dictPlayerData[iID] = dictPlayer
    
    import dlgserverbattleteam
    dlgserverbattleteam.ShowTeamMainX()
    mdserverbattleteam.GetServerBattleModel().UpdateTeamInfo(iTeamGroup, iTeamID, 101, iBattleRank, iPowerRank, iCaptainID, iTeamPowerPoint, iTeamBattlePoint, sTeamName, sBuildTime, dictPlayerData)

g_map = None

def S2CInsertBattle(isub = 2):
    import dlgserverbattle
    import random
    if isub == 1:
        pid = random.randint(10000, 20000)
        ivote = random.randint(100, 200)
        iMemberLen = random.randint(1, 20)
        lstMemberName = []
        for iIdx in xrange(iMemberLen):
            sName = '\xa6W\xa6r_%d' % iIdx
            lstMemberName.append(sName)
        
        iReadyLen = random.randint(1, 10)
        lstReadyName = []
        for iIdx in xrange(iReadyLen):
            sName = '\xb4\xc0\xb8\xc9\xa6W\xa6r_%d' % iIdx
            lstReadyName.append(sName)
        
        Score = random.randint(10000, 20000)
        iHasPass = random.randint(0, 1)
        Desc = '\xa4z\xb4N\xa7\xb9\xa8\xc6\xa8\xe0\xa4F%d' % pid
        iTeamID = random.randint(10000, 12000)
        sTeamName = '\xbe\xd4\xb6\xa4mingzi%d' % iTeamID
        arr = [
            pid,
            lstMemberName,
            lstReadyName,
            Desc,
            ivote,
            Score,
            iHasPass,
            iTeamID,
            sTeamName]
        dlgserverbattle.Insert(arr)
    elif isub in (2, 3):
        iMemberLen = random.randint(1, 20)
        lstMemberName = []
        for iIdx in xrange(iMemberLen):
            sName = '\xa6W\xa6r_%d' % iIdx
            lstMemberName.append(sName)
        
        iReadyLen = random.randint(1, 10)
        lstReadyName = []
        for iIdx in xrange(iReadyLen):
            sName = '\xb4\xc0\xb8\xc9\xa6W\xa6r_%d' % iIdx
            lstReadyName.append(sName)
        
        price = random.randint(10000, 12000)
        iTeamID = random.randint(10000, 12000)
        sTeamName = '\xbe\xd4\xb6\xa4mingzi%d' % iTeamID
        arr = [
            lstMemberName,
            lstReadyName,
            price,
            iTeamID,
            sTeamName]
        dlgserverbattle.InsertBidTeam(arr)
    


def S2CTeamRecord():
    '''
\t\xbe\xd4\xb6\xa4\xb0O\xbf\xfd#c2s-2, s2c-2
\t:return:
\t'''
    iRecordLen = 100
    dicRecords = { }
    for idx in range(iRecordLen):
        dicRecord = { }
        import random
        iType = random.randint(1, 3)
        dicRecord['iType'] = iType
        iPeriod = idx
        dicRecord['iPeriod'] = iPeriod
        iWinNumber = idx + 3
        dicRecord['iWinNumber'] = iWinNumber
        iLoseNumber = idx
        dicRecord['iLoseNumber'] = iLoseNumber
        dicRecord['iGroup'] = random.randint(1, 3)
        sGameStage = '\xb2^\xa8O'
        dicRecord['sGameStage'] = sGameStage
        iTeamMatesLen = 7
        dicMates = { }
        index = 0
        for iTeamMate in range(iTeamMatesLen):
            iTeamMateID = index + 1003
            sTeamMateName = '%d_' % index
            dicMates[iTeamMateID] = sTeamMateName
            index += 1
        
        dicRecord['dicMates'] = dicMates
        dicRecords[idx] = dicRecord
    
    import dlgteamrecord
    dlgteamrecord.ShowTeamRecord()
    mdserverbattleteam.GetServerBattleRecord().UpdateRecordInfo(dicRecords)


def S2CTeamRank():
    '''
\t\xb1\xc6\xa6\xe6\xba]\xb0O\xbf\xfd
\t:return:
\t'''
    iRecordLen = 100
    iType = 1
    dicRecords = { }
    for idx in range(iRecordLen):
        dicRecord = { }
        iTeamID = idx
        dicRecord['iTeamID'] = iTeamID
        import random
        iType = random.randint(1, 3)
        dicRecord['iType'] = iType
        iGroup = random.randint(1, 3)
        dicRecord['iGroup'] = iGroup
        iRank = idx
        dicRecord['iRank'] = iRank
        sTeamName = 'xxx%s' % idx
        dicRecord['sTeamName'] = sTeamName
        sServerName = 'NB'
        dicRecord['sServerName'] = sServerName
        sCaptainName = 'Me%s' % idx
        dicRecord['sCaptainName'] = sCaptainName
        iScore = idx * 100
        dicRecord['iScore'] = iScore
        iPowerScore = idx + 100
        dicRecord['iPowerScore'] = iPowerScore
        iTeamMatesLen = 6
        lstName = []
        for iTeamMate in range(iTeamMatesLen):
            sTeamMateName = '\xbd\xde\xb6\xa4\xa4\xcd'
            lstName.append(sTeamMateName)
        
        dicRecord['lstMate'] = lstName
        dicRecords[idx] = dicRecord
    
    import dlgbattlerank
    dlgbattlerank.ShowServerRank()
    mdserverbattleteam.GetRankModel().UpdateRankInfo(dicRecords, iType)


def S2CTeamManagerInfo():
    '''
\t\xbe\xd4\xb6\xa4\xba\xde\xb2z\xaa\xf0\xa6^#c2s-7, s2c-6
\t:return:
\t'''
    import random
    iTeamProState = random.randint(0, 1)
    iTeamDissolveState = random.randint(0, 1)
    mdserverbattleteam.GetServerBattleModel().UpdateTeamManagerInfo(iTeamProState, iTeamDissolveState)


def S2CTeamReport():
    '''
import testtianxuan as ti
ti.S2CTeamReport()
\t:return:
\t'''
    iteamid = 10001
    iteamname = 'JTeam'
    icapid = 99699
    icapname = 'jay'
    import netserverbattleteam
    netserverbattleteam.C2SOpenTeamReport(iteamid, iteamname, icapid, icapname)


def GetAllStarNetObj(iSub):
    '''
import netallstarguess as nas
nas.C2SRequestMatchGuess()
\t:param iSub:
\t:return:
\t'''
    import netserverbattleallstart
    return netserverbattleallstart.GetNetObj(iSub)


def C2SOpenMainDlg():
    '''
import testtianxuan as ti
ti.C2SOpenMainDlg()
\t\xa5\xb4\xb6}\xc4v\xb2q\xa4\xf1\xc1\xc9\xa5D\xac\xc9\xad\xb1
\t:return:
\t'''
    S2COpenMainDlg()


def S2COpenMainDlg():
    iGuessScore = 500
    import dlgallstarguess
    import mdallstarguess
    dlgallstarguess.ShowGuessMain()
    mdallstarguess.GetGuessMianModel().UpdateMainData(iGuessScore, 0)


def C2SRequestMatchGuess():
    '''
\t\xa5\xb4\xb6}\xc4v\xb2q\xa4\xf1\xc1\xc9\xac\xc9\xad\xb1
import testtianxuan as ti
ti.C2SRequestMatchGuess()
ti.S2COpenGuessRankDlg()
ti.C2SRequestChampoinGuess()
ti.C2SRequestMatchGuess()
ti.S2CGuseeTradeDlg()

\tti.S2CTeamRank()
\tti.S2CTeamManagerInfo()
\t:return:
\t'''
    S2COpenMatchGuessDlg()


def C2SRequestChampoinGuess():
    '''
\t\xa5\xb4\xb6}\xc4v\xb2q\xaba\xadx\xac\xc9\xad\xb1
\t:return:
\t'''
    S2CChampionGuessDlg()


def C2SGuessChampion(iTeamID):
    '''
\t\xc4v\xb2q\xaba\xadx
\t:return:
\t'''
    netobj = GetAllStarNetObj(12)
    netobj.PacketAddI(iTeamID, 1)
    netobj.PacketSend()


def C2SGuessMatch(iBattle, iTeamID):
    '''
\t\xc4v\xb2q\xa4\xf1\xc1\xc9
\t:param iBattle:\xa4\xf1\xc1\xc9\xbds\xb8\xb9
\t:param iTeamID:\xbe\xd4\xb6\xa4\xbds\xb8\xb9
\t:return:
\t'''
    netobj = GetAllStarNetObj(12)
    netobj.PacketAddI(iBattle, 1)
    netobj.PacketAddI(iTeamID, 1)
    netobj.PacketSend()


def S2CChampionGuessDlg():
    '''
import testtianxuan as t
t.S2CChampionGuessDlg()
\t\xa5\xb4\xb6}\xc4v\xb2q\xaba\xadx\xac\xc9\xad\xb1
\t:return:
\t'''
    import misc
    import random
    iEndTime = misc.GetServerCurrentTime() + 6000
    iTeamLen = len(guessteam)
    dictPlayer = { }
    lstServer = [
        '\xb2\xb1\xa5@\xaa\xf8\xbaq',
        '\xaa\xac\xa4\xb8\xa7{',
        '\xa4j\xc4P\xaei\xaf\xcd',
        '\xa5M\xbcC\xa4\xd1\xa4U',
        '\xaa\xf8\xaae\xb6\xbc\xb0\xa8',
        '\xaa\xe1\xa6n\xa4\xeb\xb6\xea']
    lst = guessteam
    iServerIdx = 0
    iIdx = 0
    for idx in Insert(iTeamLen):
        iTeamGroup = random.randint(1, 5)
        iTeamID = random.randint(10000, 50000)
        sTeamName = lst[iIdx % len(guessteam)]
        iIdx += 1
        if idx == 0:
            iMoney = random.randint(100, 250)
        else:
            iMoney = 0
        sServerName = ''
        dictPlayer[idx] = {
            'iTeamID': iTeamID,
            'iMoney': iMoney,
            'sTeamName': sTeamName,
            'iTeamGroup': iTeamGroup,
            'sServerName': sServerName,
            'iServerID': sServerName }
        iServerIdx += 1
    
    dictGuessMatchData = {
        'iEndTime': iEndTime,
        'dictPlayer': dictPlayer }
    import mdallstarguess
    import dlgallstarguess
    mdallstarguess.GetGuessChampoinModel().OpenGuessChampion(dictGuessMatchData)


def S2COpenMatchGuessDlg():
    '''
import testtianxuan as t
t.S2COpenMatchGuessDlg()
\t\xa5\xb4\xb6}\xc4v\xb2q\xa4\xf1\xc1\xc9\xac\xc9\xad\xb1
\t:return:
\t'''
    import random
    lst = guessteam
    dictGuessMatchData = { }
    iBattleLen = 8
    index = 0
    for iBattleIdx in range(iBattleLen):
        iBattleState = random.randint(1, 8)
        iBattleID = iBattleIdx
        iStartTime = None if iBattleIdx < len(lstTeam) else lsttime[iBattleIdx % len(lsttime)]
        iGuessState = 1
        iGuessStage = 0
        iWinTeam = 0
        iWinTeamIdx = random.randint(0, 1)
        dictPlayer = { }
        for iTeamIdx in range(2):
            iTeamGroup = random.randint(1, 5)
            iTeamID = random.randint(10000, 50000)
            if iWinTeamIdx == iTeamIdx:
                iWinTeam = None if iGuessStage not in (0, 1) else 0
            
            if iBattleIdx == 0:
                iMoney = random.randint(150, 300)
            else:
                iMoney = 0
            sTeamName = lst[index % len(lst)]
            index += 1
            dictPlayer[iTeamIdx] = {
                'iTeamID': iTeamID,
                'sTeamName': sTeamName,
                'iTeamGroup': iTeamGroup,
                'iMoney': iMoney,
                'sServerName': sTeamName }
        
        dictGuessMatchData[iBattleIdx] = {
            'iStartTime': iStartTime,
            'iBattleState': iBattleState,
            'iBattleStage': iBattleID / 10 % 10,
            'iBattleID': iBattleID,
            'iGuessState': iGuessState,
            'iWinTeam': iWinTeam,
            'dictPlayer': dictPlayer,
            'iGuessStage': iGuessStage }
    
    import mdallstarguess
    mdallstarguess.GetGuessMatchModel().UpdateGuessMatchDlg(dictGuessMatchData)


def S2COpenGuessRankDlg():
    '''
import testtianxuan as t
t.S2COpenGuessRankDlg()
\t\xa5\xb4\xb6}\xc4v\xb2q\xa4\xf1\xc1\xc9\xac\xc9\xad\xb1
\t:return:
\t'''
    import random
    lstRankData = []
    iBattleLen = random.randint(10, 20)
    for iBattleIdx in range(iBattleLen):
        iRank = iBattleIdx + 1
        iWinRate = random.randint(0, 100)
        iScore = random.randint(0, 4000)
        sTeamName = 'Player_%d' % iBattleIdx
        lstRankData.append([
            str(iRank),
            sTeamName,
            str(iScore),
            str(iWinRate) + '%'])
    
    import dlgallstarguess
    import mdallstarguess
    dlgallstarguess.ShowGuessRankDlg()
    mdallstarguess.GetGuessRankModel().UpdateGuessRankeDlg(lstRankData)


def S2CGuseeTradeDlg(mode = 106, responseID = 99, iGuessPoint = 400):
    iType = 0
    buyLst = [
        (21300, 65535, 100),
        (21302, 65535, 200),
        (21307, 65535, 100),
        (21309, 65535, 200),
        (21314, 65535, 100),
        (21316, 65535, 200),
        (26844, 65535, 3000),
        (26845, 65535, 1000)]
    import dlgtrade
    dlgtrade.Show(buyLst, iGuessPoint, mode, iType, responseID)


def S2CShowBattleSuportDlg():
    '''
\t\xa5\xb4\xb6}\xa7U\xab\xc2\xac\xc9\xad\xb1
import testtianxuan as ti
ti.S2CShowBattleSuportDlg()
\t:return:
\t'''
    import random
    lstRankData = []
    for iBattleIdx in range(2):
        iTicketA = random.randint(100, 2000)
        iTicketB = random.randint(1000, 20000)
        iTeamID = random.randint(40000, 50000)
        sTeamName = 'Team_%d' % iBattleIdx
        lstRankData.append([
            iTicketA,
            iTeamID,
            sTeamName])
    
    import dlgallstarguess
    dlgallstarguess.ShowBattleSuportDlg()
    import mdallstarguess
    mdallstarguess.GetBattleSuportModel().UpdateGuessRankeDlg(lstRankData, 121)


def S2CCloseBattleSuportDlg():
    '''
\t\xc3\xf6\xb3\xac\xa7U\xab\xc2\xac\xc9\xad\xb1
import testtianxuan as ti
ti.S2CCloseBattleSuportDlg()
\t:return:
\t'''
    import dlgallstarguess
    dlgallstarguess.CloseBattleSuportDlg()


def S2CUpdateTicketNum(iTeamID, iTicketA, iTicketB):
    '''
\t\xa7\xf3\xb7s\xa7U\xab\xc2\xac\xc9\xad\xb1\xbe\xd4\xb6\xa4\xb2\xbc\xbc\xc6
\t:return:
\t'''
    import mdallstarguess
    iTeamID = iTeamID
    iTicketA = iTicketA
    iTicketB = iTicketB
    mdallstarguess.GetBattleSuportModel().UpdateTeamTicket(iTeamID, iTicketB)

guessteam = [
    '\xb1\xeb\xa4\xd1\xa5j\xab\xb0\xb6\xa4',
    '\xb8t\xb2\xaa\xael\xa8\xa6\xb6\xa4',
    '\xc5]\xb4\xb9\xadn\xb6\xeb\xb6\xa4',
    '\xb8\xa8\xb3\xb7\xa6B\xad\xec\xb6\xa4',
    '\xad\xd7\xc3\xb9\xb4\xcb\xaaL\xb6\xa4',
    '\xaa\xf7\xba\xf1\xa8F\xacw\xb6\xa4',
    '\xa8F\xbaz\xb0g\xaec\xb6\xa4',
    '\xae\xfc\xa9\xb3\xaf\xab\xb7\xb5\xb6\xa4',
    '\xa4\xd1\xaa\xc5\xadn\xb6\xeb\xb6\xa4',
    '\xaa\xec\xb6\xb3\xael\xa8\xa6\xb6\xa4',
    '\xb8\xa8\xa4\xe9\xae\xfc\xc6W\xb6\xa4',
    '\xa4\xd1\xa4\xf4\xa5\xad\xad\xec\xb6\xa4',
    '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa4\xb6\xa4',
    '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL\xb6\xa4',
    '\xa4\xd3\xae\xa7\xaaL\xa6a\xb6\xa4',
    '\xaa\xec\xb6\xb3\xa5\xad\xad\xec\xb6\xa4']

def S2CShowMyGuessDlg():
    '''
\t\xa5\xb4\xb6}\xa7\xda\xaa\xba\xc4v\xb2q
import testtianxuan as ti
ti.S2CShowMyGuessDlg()
\t:return:
\t'''
    import random
    lstRankData = []
    iGuessLen = random.randint(8, 10)
    idx = 0
    for iBattleIdx in range(iGuessLen):
        lstTeamInfo = []
        iGameID = iBattleIdx
        iMatchType = 0
        iTime = random.randint(10000000, 0x2540BE400L)
        iMatchState = 2
        iWinTeam = 10000 + iBattleIdx * 100 + 10
        iTeamAID = 10000 + iBattleIdx * 100 + 10
        iGroupAID = 0
        iCoinA = 500
        sTeamAName = guessteam[idx % len(guessteam)]
        idx += 1
        iTeamBID = 10000 + iBattleIdx * 100 + 20
        iGroupBID = 0
        iCoinB = 1000
        sTeamBName = guessteam[idx % len(guessteam)]
        if iCoinA != 0:
            lstRankData.append((iTime, iWinTeam, iTeamAID, sTeamAName, sTeamBName, iCoinA, iMatchState, iTeamAID, iTeamBID))
        
        if iCoinB != 0:
            lstRankData.append((iTime, iWinTeam, iTeamBID, sTeamBName, sTeamAName, iCoinB, iMatchState, iTeamAID, iTeamBID))
            continue
    
    import mdallstarguess
    mdallstarguess.GetMyGuessRecordModel().UpdateMyGuessRocordDlg(lstRankData)


def S2COpenFastIcon():
    '''
\t\xa5\xb4\xb6}\xa7\xda\xaa\xba\xc4v\xb2q
import testtianxuan as ti
ti.S2COpenFastIcon()
\t:return:
\t'''
    import model_activityicon
    model_activityicon.GetMgr().SetActivityIconData(4, True, { })


def S2COpenDZB():
    '''
\t\xa5\xb4\xb6}16\xb1j\xb9\xef\xb0}
import testtianxuan as ti
ti.S2COpenDZB()
\t:return:
\t'''
    import random
    itype = random.randint(1, 3)
    iTurn = 8
    isize = 8
    arr = []
    for j in range(isize):
        iteama = 10000
        iteamb = 10001
        winTeam = random.randint(10000, 10001)
        inamea = '\xaa\xe1\xa6n\xa4\xeb\xb6\xeaWWWW\xb6\xa4'
        inameb = '\xaa\xe1\xa6n\xa4\xeb\xb6\xeaW\xb6\xa4'
        iszhibo = 1
        arr.append([
            iTurn,
            iteama,
            iteamb,
            inamea,
            inameb,
            winTeam,
            iszhibo])
    
    import dlgnewserverbattle
    dlgnewserverbattle.ShowTop16Dlg(itype, iTurn, arr)


def S2COpenYX():
    '''
\t\xa5\xb4\xb6}8\xb1j\xb9\xef\xb0}
import testtianxuan as ti
ti.S2COpenYX()
\t:return:
\t'''
    itype = 1
    iroundcount = 2
    data = []
    for i in range(4):
        arr = []
        iturn = 1
        isize = 24
        for j in range(isize):
            igroup = 1
            iteama = 1
            iteamb = 1
            winTeam = 1
            inamea = '\xb2\xb1\xa5@\xaa\xf8\xbaqWWWWWW'
            inameb = '\xb2\xb1\xa5@\xaa\xf8\xbaqWWWWWW'
            iszhibo = '\xb2\xb1\xa5@\xaa\xf8\xbaqWWWWWW'
            arr.append((igroup, iteama, iteamb, inamea, inameb, winTeam, iszhibo))
        
        data.append(arr)
    
    import dlgnewserverbattle
    dlgnewserverbattle.ShowVsRegular(iroundcount, data, itype)


def S2CTop8Dlg():
    '''
\t\xa5\xb4\xb6}8\xb1j\xb9\xef\xb0}
import testtianxuan as ti
ti.S2CTop8Dlg()
\t:return:
\t'''
    lst = [
        1,
        3,
        2,
        4,
        5,
        7,
        6,
        8,
        1,
        2,
        5,
        8,
        2,
        8,
        1,
        5]
    import random
    import dlgnewserverbattle
    dictGames = { }
    iType = random.randint(1, 3)
    idx = 0
    for i in range(4):
        if i == 0:
            continue
        
        iturn = i + 1
        if iturn == 2:
            ilen = 4
        elif iturn == 3:
            ilen = 2
        else:
            ilen = 2
        turngame = []
        for j in range(ilen):
            igroup = 1
            iteama = lst[idx]
            inamea = str(lst[idx])
            idx += 1
            iteamb = lst[idx]
            inameb = str(lst[idx])
            idx += 1
            iszhibo = random.randint(0, 1)
            dct = {
                'group': igroup,
                'teama': iteama,
                'teamb': iteamb,
                'namea': inamea,
                'nameb': inameb,
                'turn': iturn,
                'zhibo': iszhibo,
                'sServerAName': 'sscg1',
                'sServerBName': 'sscg2' }
            turngame.append(dct)
        
        dictGames[iturn] = turngame
    
    ilen = 3
    print 'ilen = ', ilen
    lstRankData = { }
    lst = [
        1,
        5,
        8]
    for i in range(ilen):
        iRank = i + 1
        iteam = lst[i]
        iname = str(lst[i])
        dct = {
            'name': iname,
            'team': iteam,
            'rank': iRank,
            'sServerName': 'sscg' }
        lstRankData[iRank] = dct
    
    dlgnewserverbattle.ShowVsPlayoff(dictGames, lstRankData, iType)


def S2CNewTop8Dlg():
    '''
\t\xa5\xb4\xb6}8\xb1j\xb9\xef\xb0}
import testtianxuan as ti
ti.S2CNewTop8Dlg()
\t:return:
\t'''
    dictGames = {
        8: [
            {
                'sName': '\xc3\xc0\xc9\xd9\xb8\xbe',
                'sServerName': '\xc6\xdf\xd0\xc7\xd1\xd2',
                'iTurn': 2,
                'iGroup': 1,
                'iTeamID': 330712,
                'bLive': 0,
                'iIndex': 1 },
            {
                'sName': '\xc0\xb2\xc0\xb2\xb6\xd3',
                'sServerName': '\xd7\xb4\xd4\xaa\xb7\xbb',
                'iTurn': 2,
                'iGroup': 1,
                'iTeamID': 330111,
                'bLive': 0,
                'iIndex': 1 },
            {
                'sName': '\xbd\xba\xbc\xba\xc8\xcb',
                'sServerName': '\xd0\xa6\xb0\xc1\xbd\xad\xba\xfe',
                'iTurn': 2,
                'iGroup': 2,
                'iTeamID': 310113,
                'bLive': 0,
                'iIndex': 2 },
            {
                'sName': '\xb3\xac\xd0\xc2\xd0\xc7',
                'sServerName': '\xb2\xca\xd4\xc6\xd7\xb7\xd4\xc2',
                'iTurn': 2,
                'iGroup': 2,
                'iTeamID': 310611,
                'bLive': 0,
                'iIndex': 2 },
            {
                'sName': '\xc5\xae\xc9\xf1\xd3\xea',
                'sServerName': '\xb9\xfa\xc9\xab\xcc\xec\xcf\xe3',
                'iTurn': 2,
                'iGroup': 0,
                'iTeamID': 311411,
                'bLive': 0,
                'iIndex': 0 },
            {
                'sName': '\xb1\xc8\xb3\xe4\xd6\xb5',
                'sServerName': '\xc6\xf8\xcd\xcc\xc9\xbd\xba\xd3',
                'iTurn': 2,
                'iGroup': 0,
                'iTeamID': 339011,
                'bLive': 0,
                'iIndex': 0 },
            {
                'sName': '\xd7\xb7\xc3\xce\xd5\xdf',
                'sServerName': '\xd0\xa6\xb0\xc1\xbd\xad\xba\xfe',
                'iTurn': 2,
                'iGroup': 3,
                'iTeamID': 310112,
                'bLive': 0,
                'iIndex': 3 },
            {
                'sName': '91\xbc\xaf\xcd\xc5',
                'sServerName': '\xcc\xec\xb3\xa4\xb5\xd8\xbe\xc3',
                'iTurn': 2,
                'iGroup': 3,
                'iTeamID': 336312,
                'bLive': 0,
                'iIndex': 3 }],
        2: [
            {
                'sName': '\xbd\xba\xbc\xba\xc8\xcb',
                'sServerName': '\xd0\xa6\xb0\xc1\xbd\xad\xba\xfe',
                'iTurn': 4,
                'iGroup': 1,
                'iTeamID': 310113,
                'bLive': 0,
                'iIndex': 1 },
            {
                'sName': '\xb1\xc8\xb3\xe4\xd6\xb5',
                'sServerName': '\xc6\xf8\xcd\xcc\xc9\xbd\xba\xd3',
                'iTurn': 4,
                'iGroup': 1,
                'iTeamID': 339011,
                'bLive': 0,
                'iIndex': 1 }],
        4: [
            {
                'sName': '\xd7\xb7\xc3\xce\xd5\xdf',
                'sServerName': '\xd0\xa6\xb0\xc1\xbd\xad\xba\xfe',
                'iTurn': 3,
                'iGroup': 0,
                'iTeamID': 310112,
                'bLive': 0,
                'iIndex': 0 },
            {
                'sName': '\xb1\xc8\xb3\xe4\xd6\xb5',
                'sServerName': '\xc6\xf8\xcd\xcc\xc9\xbd\xba\xd3',
                'iTurn': 3,
                'iGroup': 0,
                'iTeamID': 339011,
                'bLive': 0,
                'iIndex': 0 },
            {
                'sName': '\xbd\xba\xbc\xba\xc8\xcb',
                'sServerName': '\xd0\xa6\xb0\xc1\xbd\xad\xba\xfe',
                'iTurn': 3,
                'iGroup': 1,
                'iTeamID': 310113,
                'bLive': 0,
                'iIndex': 1 },
            {
                'sName': '\xc3\xc0\xc9\xd9\xb8\xbe',
                'sServerName': '\xc6\xdf\xd0\xc7\xd1\xd2',
                'iTurn': 3,
                'iGroup': 1,
                'iTeamID': 330712,
                'bLive': 0,
                'iIndex': 1 }],
        5: [
            {
                'sName': '\xc3\xc0\xc9\xd9\xb8\xbe',
                'sServerName': '\xc6\xdf\xd0\xc7\xd1\xd2',
                'iTurn': 4,
                'iGroup': 0,
                'iTeamID': 330712,
                'bLive': 0,
                'iIndex': 0 },
            {
                'sName': '\xd7\xb7\xc3\xce\xd5\xdf',
                'sServerName': '\xd0\xa6\xb0\xc1\xbd\xad\xba\xfe',
                'iTurn': 4,
                'iGroup': 0,
                'iTeamID': 310112,
                'bLive': 0,
                'iIndex': 0 }] }
    lstRankData = {
        1: {
            'sName': '\xbd\xba\xbc\xba\xc8\xcb',
            'sServerName': '\xd0\xa6\xb0\xc1\xbd\xad\xba\xfe',
            'iTurn': 4,
            'iRank': 1,
            'iTeamID': 310113,
            'bLive': 0,
            'iIndex': 1 },
        3: {
            'sName': '\xd7\xb7\xc3\xce\xd5\xdf',
            'sServerName': '\xd0\xa6\xb0\xc1\xbd\xad\xba\xfe',
            'iTurn': 4,
            'iRank': 3,
            'iTeamID': 310112,
            'bLive': 0,
            'iIndex': 0 } }
    if not None:
        import dlgtop8table
        import mdtop8table
        mdtop8table.GetTop8TableModel().UpdateTableInfo(1, dictGames, lstRankData)
        return None


def C2SRequesetScheduleDayNo():
    '''
\t\xa4\xf1\xc1\xc9\xa4\xe9\xb5{,\xbd\xd0\xa8D\xa4\xd1\xbc\xc6
import testtianxuan as ti
ti.S2CScheduleDayNo()
\t:return:
\t'''
    S2CScheduleDayNo()


def S2CScheduleDayNo():
    '''
\t\xc1\xc9\xb5{
import testtianxuan as ti
ti.S2CScheduleDayNo()
\t:return:
\t'''
    iCurDayNo = 0
    lstDayNo = [
        18122,
        18127,
        18128,
        18140]
    import dlgallstarguess
    dlgallstarguess.ShowScheduleDlg()
    import mdallstarguess
    mdallstarguess.GetScheduleModel().OpenScheduleDlg(iCurDayNo, lstDayNo)


def S2COpenScheduleDlg(iDay = 18122):
    '''
\t\xc1\xc9\xb5{
import testtianxuan as ti
ti.S2COpenScheduleDlg()
\t:return:
\t'''
    import random
    iDayNo = iDay
    iBattleLen = random.randint(4, 8)
    dictBattleDic = { }
    lst = ('\xad\xb7\xaf}\xae\xf6\xb6\xa4', '\xaa\xe1\xa6n\xa4\xeb\xb6\xea', '\xaf\xba\xbba\xa5\xcd\xb6\xa4', '\xaf\xba\xb6\xc6\xa6\xbf\xb4\xf2', '\xbe\xd4\xa4\xd1\xb2P\xb6\xa4', '\xae\xfc\xaf\xc7\xa6\xca\xa4t', '\xa4\xf4\xc0s\xa7u\xb6\xa4', '\xb1m\xb6\xb3\xb0l\xa4\xeb', '\xc5\xca\xa4\xa7\xbc\xdc\xb6\xa4', '\xa9h\xc4\xac\xb2\xd3\xabB', '\xc2\xc2\xa4H\xc2k\xb6\xa4', '\xc0A\xc2\xb8\xaae\xa4s', '\xb3p\xbb\xbb\xb4\xe5\xb6\xa4', '\xb0\xea\xa6\xe2\xa4\xd1\xad\xbb', '\xc4\xa3\xa9\xfa\xa4\xeb\xb6\xa4', '\xa7\xd6\xb7N\xae\xa6\xa4\xb3', '\xc5\xa5\xad\xb7\xa7u\xb6\xa4', '\xb6\xaf\xc5Q\xa4\xd1\xa4U', '\xa9]\xb7L\xb2D\xb6\xa4', '\xac\xf5\xb8\xad\xa8\xa6', '\xa9]\xb7L\xb2D\xb6\xa4', '\xac\xf5\xb8\xad\xa8\xa6', '\xafB\xb6\xb3\xa9t\xb6\xa4', '\xa4\xe9\xa4\xeb\xaa\xa7\xbd\xf7', '\xb4H\xa6\xbf\xb3\xb7\xb6\xa4', '\xaa\xac\xa4\xb8\xa7{', '\xc2\xfe\xc6H\xa9\xf6\xb6\xa4', '\xa4C\xacP\xa9\xa5', '\xabL\xab\xc8\xa6\xe6\xb6\xa4', '\xb6\xc9\xab\xb0\xa4\xa7\xc5\xca', '\xabL\xab\xc8\xa6\xe6\xb6\xa4', '\xb6\xc9\xab\xb0\xa4\xa7\xc5\xca', '\xa4M\xb0\xa8\xa5\xb9\xb6\xa4', '\xabL\xb0\xa9\xacX\xb1\xa1', '\xb6\xbc\xb0\xa8\xbaq\xb6\xa4', '\xa4\xd1\xaa\xf8\xa6a\xa4[')
    index = 0
    for iBattleIdx in range(iBattleLen):
        sTime = iDay * 86400 + 3600 * iBattleIdx
        iBattleStage = 1
        sTeamAName = lst[index]
        index += 1
        sServerAName = lst[index]
        index += 1
        sTeamBName = lst[index]
        index += 1
        sServerBName = lst[index]
        index += 1
        iTeamAID = iBattleIdx + 10000
        iTeamBID = iBattleIdx + 20000
        import misc
        misc.GetServerID()
        iServerAID = misc.GetServerID()
        iServerBID = misc.GetServerID()
        iGuessAScore = random.randint(0, 4) * 1000
        iServerBScore = random.randint(0, 4) * 1000
        iWatchType = (iBattleIdx + 1) % 3
        b = random.randint(0, 1)
        iWinID = 0
        if b == 1:
            iWinID = iBattleIdx + 30000
        
        iBattleOfIdx = random.randint(0, 3)
        iLive = random.randint(0, 1)
        dictBattleDic[iBattleIdx] = {
            'iTime': 3333333,
            'iBattleStage': iBattleStage,
            'sTeam1Name': sTeamAName,
            'sTeam2Name': sTeamBName,
            'iTeam1ID': iTeamAID,
            'iTeam2ID': iTeamBID,
            'iServer1ID': iServerAID,
            'iServer2ID': iServerBID,
            'iGuess1Score': iGuessAScore,
            'iGuess2Score': iServerBScore,
            'iWinID': iWinID,
            'iLive': iLive,
            'iBattleOfIdx': iBattleOfIdx,
            'iWatchType': iWatchType,
            'iBattleID': iBattleIdx,
            'iBattleTurn': iBattleIdx }
        import dlgallstarguess
        dlgallstarguess.ShowScheduleDlg()
        import mdallstarguess
        mdallstarguess.GetScheduleModel().UpdateScheduleDlg(dictBattleDic, iDayNo)
    


def S2COpenDM():
    '''
\t\xbf\xef\xbe\xdc\xbcu\xb9\xf5\xc0W\xb9D
import testtianxuan as ti
ti.S2COpenDM()
\t:return:
\t'''
    import channel
    channel.SetChannel(17)


def S2CCloseDM():
    '''
\t\xbf\xef\xbe\xdc\xbcu\xb9\xf5\xc0W\xb9D
import testtianxuan as ti
ti.S2CCloseDM()
\t:return:
\t'''
    import main
    import chatoutput
    import barrage
    main.RegisterChannelHotKey()
    chatoutput.RefreshChnSwitch()
    barrage.CloseBarrage()


def S2CFDM():
    '''
\t\xbf\xef\xbe\xdc\xbcu\xb9\xf5\xc0W\xb9D
import testtianxuan as ti
ti.S2CFDM()
\t:return:
\t'''
    import netchat
    import barrage
    netchat.S2CPlayerChat1(17, 2, '#(5930101,Test5930101,0,100010)#dsda')
    barrage.ReplaceChat('#(5930101,Test5930101,0,100010)#dsda')


def S2CReceiveBarrageInfo():
    '''
\t\xb5o\xbcu\xb9\xf5
import testtianxuan as ti
ti.S2CReceiveBarrageInfo()
\t:return:
\t'''
    isopen = 1
    coloridx = 2
    word = 'netobjaaaaa'
    import re
    import chatoutput
    result = re.compile('#\\((?P<ID>\\d+),').search(word)
    if result and chatoutput.IsBanBarrage(int(result.group('ID'))):
        return None
    
    import netchat
    if netchat.IsShenHeHideChat(word):
        return None
    
    netchat.S2CPlayerChat1(17, 2, word)
    import barrage
    barrage.ShowBarrage(word, coloridx, isopen)


def S2COpenCDPanel():
    '''
\t\xa4\xd1\xbf\xefcd
import testtianxuan as ti
ti.S2COpenCDPanel()
\t:return:
\t'''
    import random
    import misc
    iBattleOfIdx = random.randint(1, 3)
    iTimer = misc.GetServerCurrentTime() + 66
    import dlgminipanel
    dlgminipanel.CreateTXAllStarPanel(iTimer, iBattleOfIdx)


class CServerBattleTest(object):
    
    def TestTeamListDlg(self):
        '''
\t\t\xb4\xfa\xb8\xd5\xb6\xa4\xa5\xee\xa6C\xaa\xed\xac\xc9\xad\xb1
import testtianxuan
testtianxuan.GetServerBattleTest().TestTeamListDlg()
\t\t'''
        dTeamInfoList = [
            {
                'bIsMyTeam': True,
                'iRank': 21,
                'sTeamName': '\xb6\xa4\xa5\xee21',
                'iTeamID': 1,
                'iServerID': 30103,
                'iZBSAverageScore': 121,
                'iTeamAverageScore': 121 },
            {
                'bIsMyTeam': False,
                'iRank': 20,
                'iTeamID': 2,
                'sTeamName': '\xb6\xa4\xa5\xee20',
                'iServerID': 30103,
                'iZBSAverageScore': 120,
                'iTeamAverageScore': 120 },
            {
                'bIsMyTeam': False,
                'iRank': 19,
                'iTeamID': 3,
                'sTeamName': '\xb6\xa4\xa5\xee19',
                'iServerID': 30103,
                'iZBSAverageScore': 119,
                'iTeamAverageScore': 119 },
            {
                'bIsMyTeam': False,
                'iRank': 18,
                'iTeamID': 4,
                'sTeamName': '\xb6\xa4\xa5\xee18',
                'iServerID': 30103,
                'iZBSAverageScore': 118,
                'iTeamAverageScore': 118 },
            {
                'bIsMyTeam': False,
                'iRank': 17,
                'iTeamID': 5,
                'sTeamName': '\xb6\xa4\xa5\xee17',
                'iServerID': 30103,
                'iZBSAverageScore': 117,
                'iTeamAverageScore': 117 },
            {
                'bIsMyTeam': False,
                'iRank': 16,
                'sTeamName': '\xb6\xa4\xa5\xee16',
                'iServerID': 30103,
                'iZBSAverageScore': 116,
                'iTeamAverageScore': 116 },
            {
                'bIsMyTeam': False,
                'iRank': 15,
                'iTeamID': 6,
                'sTeamName': '\xb6\xa4\xa5\xee115',
                'iServerID': 30103,
                'iZBSAverageScore': 115,
                'iTeamAverageScore': 115 },
            {
                'bIsMyTeam': False,
                'iRank': 14,
                'iTeamID': 7,
                'sTeamName': '\xb6\xa4\xa5\xee14',
                'iServerID': 30103,
                'iZBSAverageScore': 114,
                'iTeamAverageScore': 114 },
            {
                'bIsMyTeam': False,
                'iRank': 13,
                'iTeamID': 8,
                'sTeamName': '\xb6\xa4\xa5\xee13',
                'iServerID': 30103,
                'iZBSAverageScore': 113,
                'iTeamAverageScore': 113 },
            {
                'bIsMyTeam': False,
                'iRank': 12,
                'iTeamID': 9,
                'sTeamName': '\xb6\xa4\xa5\xee12',
                'iServerID': 30103,
                'iZBSAverageScore': 112,
                'iTeamAverageScore': 112 },
            {
                'bIsMyTeam': False,
                'iRank': 11,
                'iTeamID': 10,
                'sTeamName': '\xb6\xa4\xa5\xee11',
                'iServerID': 30103,
                'iZBSAverageScore': 111,
                'iTeamAverageScore': 111 },
            {
                'bIsMyTeam': False,
                'iRank': 10,
                'iTeamID': 11,
                'sTeamName': '\xb6\xa4\xa5\xee10',
                'iServerID': 30103,
                'iZBSAverageScore': 110,
                'iTeamAverageScore': 110 },
            {
                'bIsMyTeam': False,
                'iRank': 9,
                'iTeamID': 12,
                'sTeamName': '\xb6\xa4\xa5\xee9',
                'iServerID': 30103,
                'iZBSAverageScore': 109,
                'iTeamAverageScore': 109 },
            {
                'bIsMyTeam': False,
                'iRank': 8,
                'iTeamID': 13,
                'sTeamName': '\xb6\xa4\xa5\xee8',
                'iServerID': 30103,
                'iZBSAverageScore': 108,
                'iTeamAverageScore': 108 },
            {
                'bIsMyTeam': False,
                'iRank': 7,
                'iTeamID': 14,
                'sTeamName': '\xb6\xa4\xa5\xee07',
                'iServerID': 30103,
                'iZBSAverageScore': 107,
                'iTeamAverageScore': 107 },
            {
                'bIsMyTeam': False,
                'iRank': 6,
                'iTeamID': 15,
                'sTeamName': '\xb6\xa4\xa5\xee06',
                'iServerID': 30103,
                'iZBSAverageScore': 106,
                'iTeamAverageScore': 106 },
            {
                'bIsMyTeam': False,
                'iRank': 5,
                'iTeamID': 16,
                'sTeamName': '\xb6\xa4\xa5\xee05',
                'iServerID': 30103,
                'iZBSAverageScore': 105,
                'iTeamAverageScore': 105 },
            {
                'bIsMyTeam': False,
                'iRank': 4,
                'iTeamID': 17,
                'sTeamName': '\xb6\xa4\xa5\xee04',
                'iServerID': 30103,
                'iZBSAverageScore': 104,
                'iTeamAverageScore': 104 },
            {
                'bIsMyTeam': False,
                'iRank': 3,
                'iTeamID': 18,
                'sTeamName': '\xb6\xa4\xa5\xee03',
                'iServerID': 30103,
                'iZBSAverageScore': 103,
                'iTeamAverageScore': 103 },
            {
                'bIsMyTeam': False,
                'iRank': 2,
                'iTeamID': 19,
                'sTeamName': '\xc0H\xabK\xa5\xb4\xb3\xa3\xc4\xb9',
                'iServerID': 30103,
                'iZBSAverageScore': 102,
                'iTeamAverageScore': 102 },
            {
                'bIsMyTeam': False,
                'iRank': 29,
                'iTeamID': 2012,
                'sTeamName': '\xb1M\xaav\xa6U\xba\xd8\xa4\xa3\xaaA3',
                'iServerID': 30103,
                'iZBSAverageScore': 101,
                'iTeamAverageScore': 101 },
            {
                'bIsMyTeam': False,
                'iRank': 28,
                'iTeamID': 201,
                'sTeamName': '\xb1M\xaav\xa6U\xba\xd8\xa4\xa3\xaaA2',
                'iServerID': 30103,
                'iZBSAverageScore': 101,
                'iTeamAverageScore': 101 },
            {
                'bIsMyTeam': False,
                'iRank': 27,
                'iTeamID': 203,
                'sTeamName': '\xb1M\xaav\xa6U\xba\xd8\xa4\xa3\xaaA1',
                'iServerID': 30103,
                'iZBSAverageScore': 101,
                'iTeamAverageScore': 101 }]
        import dlgsbteamlist
        dlgsbteamlist.ShowTeamListDlg(dTeamInfoList)

    
    def TestRollDlg(self):
        '''
\t\t\xb4\xfa\xb8\xd5\xa9\xe2\xc5\xd2\xac\xc9\xad\xb1
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestRollDlg()
\t\t'''
        dMatchInfo = { }
        dRankInfo = { }
        for i in range(1, 5):
            for j in range(1, 5):
                iRank = (i - 1) * 4 + j
                iTeamID = i * 10 + j
                dRankInfo[iRank] = iTeamID
                dInfo = { }
                dInfo['iTeamID'] = iTeamID
                dInfo['iServerID'] = 30103
                dInfo['sTeamName'] = 'T%s' % (i * 10 + j)
                dInfo['iRank'] = iRank
                if iRank > 6:
                    dInfo['iTeamType'] = 0
                    dInfo['iPos'] = 0
                else:
                    dInfo['iTeamType'] = i
                    dInfo['iPos'] = j
                dMatchInfo[iTeamID] = dInfo
            
        
        sChatList = [
            '#Y\xc1\xca\xb6R\xb1\xf8\xa5\xf3\xa1G#n#r\xc7\xe9\xaaA\xb0\xc8\xbe\xb9\xb5\xa5\xaf\xc5\xa1\xd955#r\xc7\xea\xa4H\xaa\xab\xb5\xa5\xaf\xc5\xa1\xd955#r#Y\xc1\xca\xb6R\xae\xf8\xaf\xd3\xa1G#n#r#s(3,26116,)\xa1\xd19#r#s(3,25431,)\xa1\xd110',
            '#s(8)\xa8t\xb2\xce\xabH\xae\xa71...']
        oModel = mdsbasroll.GetRollModel()
        oModel.SetMatchInfo(dMatchInfo)
        oModel.SetRankInfo(dRankInfo)
        oModel.SetChatList(sChatList)
        oModel.SetCanDraw(False)
        import dlgsbasroll
        dlgsbasroll.ShowRollDlg()

    
    def TestRollInfoChg(self):
        '''
\t\t\xb4\xfa\xb8\xd5\xa9\xe2\xc5\xd2\xbc\xc6\xbe\xda\xa7\xef\xc5\xdc
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestRollInfoChg()
\t\t'''
        sChatList = [
            '#Y\xc1\xca\xb6R\xb1\xf8\xa5\xf3\xa1G#n#r\xc7\xe9\xaaA\xb0\xc8\xbe\xb9\xb5\xa5\xaf\xc5\xa1\xd955#r\xc7\xea\xa4H\xaa\xab\xb5\xa5\xaf\xc5\xa1\xd955#r#Y\xc1\xca\xb6R\xae\xf8\xaf\xd3\xa1G#n#r#s(3,26116,)\xa1\xd19#r#s(3,25431,)\xa1\xd110',
            '#s(8)\xa8t\xb2\xce\xabH\xae\xa71...',
            '#s(8)\xa8t\xb2\xce\xabH\xae\xa72...']
        dMatchInfo = {
            31: {
                'iRank': 9,
                'iTeamID': 31,
                'iServerID': 30103,
                'iTeamType': 3,
                'iPos': 1,
                'sTeamName': 'T31' },
            32: {
                'iRank': 10,
                'iTeamID': 32,
                'iServerID': 30103,
                'iTeamType': 3,
                'iPos': 2,
                'sTeamName': 'T32' } }
        oModel = mdsbasroll.GetRollModel()
        oModel.UpdateMatchInfo(dMatchInfo)
        oModel.AddChatList(sChatList)

    
    def TestTeamTips(self, iTeamID = None, iServerID = None):
        '''
\t\t\xb4\xfa\xb8\xd5\xb6\xa4\xa5\xeetips
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestTeamTips()
\t\t'''
        iTeamID = None if iTeamID else 1
        iServerID = None if iServerID else 30103
        sTips = '\xbe\xd4\xb6\xa4\xa6W\xba\xd9#r\xaaA\xb0\xc8\xbe\xb9:\xb7\xb3\xaa\xba\xb5o\xa4\xe5#r\xb6\xa4\xaa\xf8:#r#cffff00\xaa\xb1\xaea\xa6W\xa6r\xa4C\xad\xd3\xa6r#n#r\xa6\xa8\xad\xfb:#r\xaa\xb1\xaea\xa6W\xa6r\xa4C\xad\xd3\xa6r#r\xaa\xb1\xaea\xa6W\xa6r\xa4C\xad\xd3\xa6r#r\xaa\xb1\xaea\xa6W\xa6r\xa4C\xad\xd3\xa6r#r\xc2I\xc0\xbb\xacd\xac\xdd\xbe\xd4\xb0\xab\xb8\xd4\xb2\xd3\xabH\xae\xa7'
        import dlgsbasroll
        dlgsbasroll.ShowTeamInfoTips(iTeamID, iServerID, sTips)

    
    def TestTeamTips2(self):
        '''
\t\t\xb4\xfa\xb8\xd5\xb6\xa4\xa5\xeetips
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestTeamTips2()
\t\t'''
        import usermacro
        sTxt = '\xb3o\xacO\xb6\xa4\xa5\xee\xabH\xae\xa7\xc3\xec\xb1\xb5#s(154,1,30103,\xbe\xd4\xb6\xa4\xa6W\xa6r)'
        usermacro.SYSTEM_MSG(sTxt)

    
    def TestRollLastTime1(self):
        '''
\t\t\xb4\xfa\xb8\xd5\xa9\xe2\xc5\xd2\xb3\xd1\xa7E\xae\xc9\xb6\xa1
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestRollDlg()
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestRollLastTime1()
\t\t'''
        iState = 1
        iLastTime = 20
        LOG_DEBUG('>\xa9\xe2\xc5\xd2\xb3\xd1\xa7E\xae\xc9\xb6\xa1>', iState, iLastTime)
        oModel = mdsbasroll.GetRollModel()
        oModel.SetLastTime(iState, iLastTime)
        if iState == 2:
            import dlgsbasroll
            dlgsbasroll.ShowDrawLotsDlg(iLastTime, oModel.GetFullGroupList())
        

    
    def TestRollLastTime2(self):
        '''
\t\t\xb4\xfa\xb8\xd5\xa9\xe2\xc5\xd2\xb3\xd1\xa7E\xae\xc9\xb6\xa1
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestRollLastTime2()
\t\t'''
        iState = 2
        iLastTime = 30
        LOG_DEBUG('>\xa9\xe2\xc5\xd2\xb3\xd1\xa7E\xae\xc9\xb6\xa1>', iState, iLastTime)
        oModel = mdsbasroll.GetRollModel()
        oModel.SetLastTime(iState, iLastTime)
        if iState == 2:
            import dlgsbasroll
            dlgsbasroll.ShowDrawLotsDlg(iLastTime, oModel.GetFullGroupList())
        

    
    def TestDrawLots(self):
        '''
\t\t\xb4\xfa\xb8\xd5\xa9\xe2\xc5\xd2
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestDrawLots()
\t\t'''
        import dlgsbasroll
        dlgsbasroll.ShowDrawLotsDlg(20, [
            1,
            4])

    
    def TestDrawLotsResult(self):
        '''
\t\t\xb4\xfa\xb8\xd5\xa9\xe2\xc5\xd2
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestDrawLotsResult()
\t\t'''
        import dlgsbasroll
        dlgsbasroll.ShowDrawLotsResult(2, 2)

    
    def TestBattleTable(self):
        '''
\t\t\xb4\xfa\xb8\xd5\xb9\xef\xb0}\xaa\xed
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestBattleTable()
\t\t'''
        import dlgsbasbattletable
        dlgsbasbattletable.ShowBattleTableMainDlg(0, 1)

    
    def TestBattleTableGroup(self):
        '''
\t\t\xb4\xfa\xb8\xd5\xb9\xef\xb0}\xaa\xed(\xa4\xc0\xb2\xd5)
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestBattleTableGroup()
\t\t'''
        import serverbattledefine
        import mdsbasbattletable
        import dlgsbasbattletable
        dTeamInfo = { }
        iTableType = serverbattledefine.ALL_START_BTYPE_FINALS
        for iGroup in range(1, 5):
            dTeamInfo[iGroup] = { }
            for iPos in range(1, 5):
                iTeamID = iGroup * 10 + iPos
                sTeamName = 'Team%d_%d' % (iGroup, iPos)
                dTeamInfo[iGroup][iTeamID] = dInfo = { }
                dInfo['iTeamID'] = iTeamID
                dInfo['iServerID'] = 30103
                dInfo['iTeamType'] = iGroup
                dInfo['iPos'] = iPos
                dInfo['sTeamName'] = sTeamName
                if iTeamID == 14:
                    dInfo['iState'] = 2
                    continue
                if iTeamID == 22:
                    dInfo['iState'] = 1
                    continue
                dInfo['iState'] = 0
            
        
        mdsbasbattletable.GetBattleTableModel().SetTeamInfo(iTableType, dTeamInfo)
        dlgsbasbattletable.ShowBattleTableMainDlg(iTableType, serverbattledefine.BATTLE_TABLE_PAGE_TEAM)

    
    def TestBattleTableBattle(self, iType):
        '''
\t\t\xb4\xfa\xb8\xd5\xb9\xef\xb0}\xaa\xed(\xb9\xef\xb0})
\t\t# \xaa\xc5
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestBattleTableBattle(1)

\t\t# \xba\xa1
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestBattleTableBattle(2)

\t\t# \xa4@\xa5b
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestBattleTableBattle(3)
\t\t'''
        import mdsbasbattletable
        import serverbattledefine
        dTeamInfo = { }
        iGroup = 3
        iTableType = serverbattledefine.ALL_START_BTYPE_GROUP
        iTmpList = []
        for iPos in range(1, 5):
            iTeamID = iGroup * 10 + iPos
            iTmpList.append(iTeamID)
            sTeamName = 'Team%d_%d' % (iGroup, iPos)
            dTeamInfo[iTeamID] = dInfo = { }
            dInfo['iTeamID'] = iTeamID
            dInfo['iServerID'] = 30103
            dInfo['iTeamType'] = iGroup
            dInfo['iPos'] = iPos
            dInfo['sTeamName'] = sTeamName
            dInfo['iState'] = None if iTeamID == 34 or iTeamID == 31 else 1
        
        if iType == 1:
            iWin1ID = 0
            iWin2ID = 0
            iLose1ID = 0
            iLose2ID = 0
            iPrimaryWinList = []
            iPrimaryLoseList = []
            iPromotedWin = 0
            iPromotedLose = 0
            iWeedOutWin = 0
            iLastWin = 0
        elif iType == 2:
            iWin1ID = 31
            iWin2ID = 33
            iLose1ID = 32
            iLose2ID = 34
            iPrimaryWinList = [
                iWin1ID,
                iWin2ID]
            iPrimaryLoseList = [
                iLose1ID,
                iLose2ID]
            iPromotedWin = 33
            iPromotedLose = 31
            iWeedOutWin = 32
            iLastWin = 32
        else:
            iWin1ID = 31
            iWin2ID = 33
            iLose1ID = 32
            iLose2ID = 34
            iPrimaryWinList = [
                iWin1ID,
                iWin2ID]
            iPrimaryLoseList = [
                iLose1ID,
                iLose2ID]
            iPromotedWin = 0
            iPromotedLose = 0
            iWeedOutWin = 32
            iLastWin = 0
        dBattleInfo = { }
        dBattleInfo['iPrimaryWinList'] = iPrimaryWinList
        dBattleInfo['iPrimaryLoseList'] = iPrimaryLoseList
        dBattleInfo['iPromotedWin'] = iPromotedWin
        dBattleInfo['iPromotedLose'] = iPromotedLose
        dBattleInfo['iWeedOutWin'] = iWeedOutWin
        dBattleInfo['iLastWin'] = iLastWin
        dTurnInfo = {
            1: [
                iTmpList[0],
                iTmpList[3]],
            2: [
                iTmpList[1],
                iTmpList[2]],
            3: [
                iWin1ID,
                iWin2ID],
            4: [
                iLose1ID,
                iLose2ID],
            5: [
                iPromotedLose,
                iWeedOutWin] }
        import time
        import random
        dMatchInfoDict = { }
        for iMatchIdx in range(1, 6):
            dMatchInfo = { }
            dMatchInfo['iTime'] = time.time() + iMatchIdx * 100
            dMatchInfo['iMatchID'] = (iMatchIdx + 1) * 100
            dMatchInfo['iMatchState'] = random.randint(0, 2)
            dMatchInfo['iTeamIDList'] = dTurnInfo[iMatchIdx]
            dMatchInfoDict[iMatchIdx] = dMatchInfo
        
        oModel = mdsbasbattletable.GetBattleTableModel()
        oModel.UpdateTeamInfo(iTableType, {
            iGroup: dTeamInfo })
        oModel.UpdateBattleInfo(iGroup, dBattleInfo)
        oModel.UpdateMatchInfo(iGroup, dMatchInfoDict)
        oModel.UpdateTrunInfo(iGroup, dTurnInfo)
        import dlgsbasbattletable
        dlgsbasbattletable.ShowBattleTableMainDlg(iTableType, serverbattledefine.BATTLE_TABLE_PAGE_BATTLE)

    
    def TestBattleTableGroup14(self):
        '''
\t\t\xb4\xfa\xb8\xd5\xb9\xef\xb0}\xaa\xed(\xa4\xc0\xb2\xd5)
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestBattleTableGroup14()
\t\t'''
        import mdsbasbattletable
        import serverbattledefine
        import dlgsbasbattletable
        iTableType = serverbattledefine.ALL_START_BTYPE_14
        dTeamInfo = { }
        for iGroup in range(5, 7):
            dTeamInfo[iGroup] = { }
            for iPos in range(1, 5):
                iTeamID = iGroup * 10 + iPos
                sTeamName = 'Team%d_%d' % (iGroup, iPos)
                dTeamInfo[iGroup][iTeamID] = dInfo = { }
                dInfo['iTeamID'] = iTeamID
                dInfo['iTeamType'] = iGroup
                dInfo['iServerID'] = 30103
                dInfo['iPos'] = iPos
                dInfo['sTeamName'] = sTeamName
                if iTeamID == 54:
                    dInfo['iState'] = 2
                    continue
                if iTeamID == 62:
                    dInfo['iState'] = 1
                    continue
                dInfo['iState'] = 0
            
        
        mdsbasbattletable.GetBattleTableModel().SetTeamInfo(iTableType, dTeamInfo)
        dlgsbasbattletable.ShowBattleTableMainDlg(iTableType, serverbattledefine.BATTLE_TABLE_PAGE_TEAM)

    
    def TestBattleTableBattle14(self, iType):
        '''
\t\t\xb4\xfa\xb8\xd5\xb9\xef\xb0}\xaa\xed(\xb9\xef\xb0})
\t\t# \xaa\xc5
import testtianxuan
testtianxuan.GetServerBattleTest().TestBattleTableBattle14(1)

\t\t# \xba\xa1
import testtianxuan
testtianxuan.GetServerBattleTest().TestBattleTableBattle14(2)

\t\t# \xa4@\xa5b
import testtianxuan
testtianxuan.GetServerBattleTest().TestBattleTableBattle14(3)
\t\t'''
        import mdsbasbattletable
        import serverbattledefine
        import dlgsbasbattletable
        iTableType = serverbattledefine.ALL_START_BTYPE_14
        dTeamInfo = { }
        iGroup = 5
        iTmpList = []
        for iPos in range(1, 5):
            iTeamID = iGroup * 10 + iPos
            iTmpList.append(iTeamID)
            sTeamName = 'Team%d_%d' % (iGroup, iPos)
            dTeamInfo[iTeamID] = dInfo = { }
            dInfo['iTeamID'] = iTeamID
            dInfo['iServerID'] = 30103
            dInfo['iTeamType'] = iGroup
            dInfo['iPos'] = iPos
            dInfo['sTeamName'] = sTeamName
            dInfo['iState'] = None if iTeamID == 54 or iTeamID == 51 else 0
        
        if iType == 1:
            iWin1ID = 0
            iWin2ID = 0
            iLose1ID = 0
            iLose2ID = 0
            iPrimaryWinList = []
            iPrimaryLoseList = []
            iPromotedWin = 0
            iPromotedLose = 0
            iWeedOutWin = 0
            iLastWin = 0
        elif iType == 2:
            iWin1ID = 51
            iWin2ID = 53
            iLose1ID = 52
            iLose2ID = 54
            iPrimaryWinList = [
                iWin1ID,
                iWin2ID]
            iPrimaryLoseList = [
                iLose1ID,
                iLose2ID]
            iPromotedWin = 53
            iPromotedLose = 51
            iWeedOutWin = 52
            iLastWin = 52
        else:
            iWin1ID = 51
            iWin2ID = 53
            iLose1ID = 52
            iLose2ID = 54
            iPrimaryWinList = [
                iWin1ID,
                iWin2ID]
            iPrimaryLoseList = [
                iLose1ID,
                iLose2ID]
            iPromotedWin = 0
            iPromotedLose = 0
            iWeedOutWin = 52
            iLastWin = 0
        dBattleInfo = { }
        dBattleInfo['iPrimaryWinList'] = iPrimaryWinList
        dBattleInfo['iPrimaryLoseList'] = iPrimaryLoseList
        dBattleInfo['iPromotedWin'] = iPromotedWin
        dBattleInfo['iPromotedLose'] = iPromotedLose
        dBattleInfo['iWeedOutWin'] = iWeedOutWin
        dBattleInfo['iLastWin'] = iLastWin
        dTurnInfo = {
            1: [
                iTmpList[0],
                iTmpList[3]],
            2: [
                iTmpList[1],
                iTmpList[2]],
            3: [
                iWin1ID,
                iWin2ID],
            4: [
                iLose1ID,
                iLose2ID],
            5: [
                iPromotedLose,
                iWeedOutWin] }
        import time
        import random
        dMatchInfoDict = { }
        for i in range(1, 6):
            dMatchInfo = { }
            dMatchInfo['iTime'] = time.time() + i * 100
            dMatchInfo['iMatchID'] = (i + 1) * 100
            dMatchInfo['iMatchState'] = random.randint(0, 2)
            dMatchInfo['iTeamIDList'] = dTurnInfo[i]
            dMatchInfoDict[i] = dMatchInfo
        
        oModel = mdsbasbattletable.GetBattleTableModel()
        oModel.UpdateTeamInfo(iTableType, {
            iGroup: dTeamInfo })
        oModel.UpdateBattleInfo(iGroup, dBattleInfo)
        oModel.UpdateMatchInfo(iGroup, dMatchInfoDict)
        oModel.UpdateTrunInfo(iGroup, dTurnInfo)
        dlgsbasbattletable.ShowBattleTableMainDlg(iTableType, serverbattledefine.BATTLE_TABLE_PAGE_BATTLE)

    
    def TestFinalsBattleTableBattle(self, iType):
        '''
\t\t\xb4\xfa\xb8\xd5\xb9\xef\xb0}\xaa\xed(\xb9\xef\xb0})
\t\t# \xaa\xc5
import testtianxuan
testtianxuan.GetServerBattleTest().TestFinalsBattleTableBattle(1)

\t\t# \xba\xa1
import testtianxuan
testtianxuan.GetServerBattleTest().TestFinalsBattleTableBattle(2)

\t\t# \xa4@\xa5b
import testtianxuan
testtianxuan.GetServerBattleTest().TestFinalsBattleTableBattle(3)
\t\t'''
        import copy
        import mdsbasbattletable
        import serverbattledefine
        import dlgsbasbattletable
        iTableType = serverbattledefine.ALL_START_BTYPE_FINALS
        iWinList = []
        iLoseList = []
        dTeamInfo = { }
        dTeamInfo41 = { }
        dAllTeamInfo = { }
        iGroup = serverbattledefine.ALL_START_GROUP_TEAM_FOUR1
        for iPos in range(1, 3):
            dInfo = { }
            dInfo['iTeamID'] = iTeamID = 70 + iPos
            dInfo['iServerID'] = 30103
            dInfo['sTeamName'] = 'Team%d_%d' % (iGroup, iPos)
            if iType == 1:
                dInfo['iState'] = 0
            elif iType == 2:
                dInfo['iState'] = 1
            elif iTeamID == 71:
                pass
            
            dInfo['iState'] = 2
            if dInfo['iState'] == 1:
                iWinList.append(iTeamID)
            else:
                iLoseList.append(iTeamID)
            dInfo['iTeamType'] = iGroup
            dInfo['iPos'] = iPos
            dTeamInfo41[iTeamID] = dInfo
            dAllTeamInfo[iTeamID] = dInfo
        
        dTeamInfo[iGroup] = dTeamInfo41
        dTeamInfo42 = { }
        iGroup = serverbattledefine.ALL_START_GROUP_TEAM_FOUR2
        for iPos in range(1, 3):
            dInfo = { }
            dInfo['iTeamID'] = iTeamID = 70 + iPos + 2
            dInfo['iServerID'] = 30103
            dInfo['sTeamName'] = 'Team%d_%d' % (iGroup, iPos)
            if iType == 1:
                dInfo['iState'] = 0
            elif iType == 2:
                dInfo['iState'] = 2
            else:
                dInfo['iState'] = 0
            if dInfo['iState'] == 1:
                iWinList.append(iTeamID)
            else:
                iLoseList.append(iTeamID)
            dInfo['iTeamType'] = iGroup
            dInfo['iPos'] = iPos
            dTeamInfo42[iTeamID] = dInfo
            dAllTeamInfo[iTeamID] = dInfo
        
        dTeamInfo[iGroup] = dTeamInfo42
        iLWin = 0
        dTeamInfo3 = { }
        iGroup = serverbattledefine.ALL_START_GROUP_TEAM_THIRD
        for iPos in range(1, 3):
            iTeamID = 70 + iPos + 2
            iState = None if iTeamID == 73 else 2
            if iTeamID not in dAllTeamInfo:
                LOG('[tx-as]>\xa8M\xc1\xc9\xb9\xef\xb0}\xaa\xed\xbc\xc6\xbe\xda\xb2\xa7\xb1`', dAllTeamInfo, iTeamID)
                continue
            
            dInfo = copy.deepcopy(dAllTeamInfo[iTeamID])
            dInfo['iState'] = iState
            dInfo['iTeamType'] = iGroup
            dInfo['iPos'] = iPos
            dTeamInfo3[iTeamID] = dInfo
            if iState == 1:
                iLWin = iTeamID
                continue
        
        dTeamInfo[iGroup] = dTeamInfo3
        iWWin = 0
        dTeamInfo1 = { }
        iGroup = serverbattledefine.ALL_START_GROUP_TEAM_FINALS
        for iPos in range(1, 3):
            iTeamID = 70 + iPos
            iState = None if iTeamID == 71 else 2
            if iTeamID not in dAllTeamInfo:
                LOG('[tx-as]>\xa8M\xc1\xc9\xb9\xef\xb0}\xaa\xed\xbc\xc6\xbe\xda\xb2\xa7\xb1`', dAllTeamInfo, iTeamID)
                continue
            
            dInfo = copy.deepcopy(dAllTeamInfo[iTeamID])
            dInfo['iState'] = iState
            dInfo['iTeamType'] = iGroup
            dInfo['iPos'] = iPos
            dTeamInfo1[iTeamID] = dInfo
            if dInfo['iState'] == 1:
                iWWin = iTeamID
                continue
        
        dTeamInfo[iGroup] = dTeamInfo1
        if iType == 1:
            del dTeamInfo[serverbattledefine.ALL_START_GROUP_TEAM_THIRD]
            del dTeamInfo[serverbattledefine.ALL_START_GROUP_TEAM_FINALS]
            dBattleInfo = { }
            dBattleInfo['iPrimaryWinList'] = []
            dBattleInfo['iPrimaryLoseList'] = []
            dBattleInfo['iThirdWin'] = 0
            dBattleInfo['iLastWin'] = 0
        elif iType == 2:
            dBattleInfo = { }
            dBattleInfo['iPrimaryWinList'] = iWinList
            dBattleInfo['iPrimaryLoseList'] = iLoseList
            dBattleInfo['iThirdWin'] = iLWin
            dBattleInfo['iLastWin'] = iWWin
        else:
            del dTeamInfo[serverbattledefine.ALL_START_GROUP_TEAM_THIRD]
            del dTeamInfo[serverbattledefine.ALL_START_GROUP_TEAM_FINALS]
            dBattleInfo = { }
            dBattleInfo['iPrimaryWinList'] = iWinList
            dBattleInfo['iPrimaryLoseList'] = iLoseList
            dBattleInfo['iThirdWin'] = 0
            dBattleInfo['iLastWin'] = 0
        oModel = mdsbasbattletable.GetBattleTableModel()
        oModel.UpdateTeamInfo(iTableType, dTeamInfo)
        oModel.SetFinalsBattleInfo(dBattleInfo)
        dlgsbasbattletable.ShowFinalsBattleTableDlg()

    
    def TestMatchInfoDlg(self):
        '''
\t\t\xa4\xf1\xc1\xc9\xabH\xae\xa7\xac\xc9\xad\xb1
\t\timport testtianxuan
\t\ttesttianxuan.GetServerBattleTest().TestMatchInfoDlg()
\t\t'''
        import time
        import random
        iGroup = 8
        dMatchInfoDict = { }
        for i in range(1, 4):
            dMatchInfo = { }
            dMatchInfo['iTime'] = time.time() + i * 100
            dMatchInfo['iMatchID'] = (i + 1) * 100
            dMatchInfo['iMatchState'] = random.randint(0, 2)
            dMatchInfoDict[i] = dMatchInfo
        
        import mdsbasbattletable
        mdsbasbattletable.GetBattleTableModel().UpdateMatchInfo(iGroup, dMatchInfoDict)
        import dlgsbasbattletable
        dlgsbasbattletable.ShowMatchInfoDlg(iGroup)


import mdsbasbattletable
import serverbattledefine
lstTeam = [
    '\xbe\xd4\xb6\xa4\xa6WA',
    '\xbe\xd4\xb6\xa4\xa6WB',
    '\xbe\xd4\xb6\xa4\xa6WC',
    '\xbe\xd4\xb6\xa4\xa6WD']
LstState = [
    1,
    2,
    2,
    1]
import time
lsttime = [
    time.mktime((2020, 8, 1, 16, 0, 0, 0, 0, 0)),
    time.mktime((2020, 8, 1, 16, 30, 0, 0, 0, 0)),
    time.mktime((2020, 8, 1, 17, 0, 0, 0, 0, 0)),
    time.mktime((2020, 8, 1, 17, 30, 0, 0, 0, 0)),
    time.mktime((2020, 8, 1, 19, 50, 0, 0, 0, 0)),
    time.mktime((2020, 8, 1, 20, 30, 0, 0, 0, 0))]

def S2CBattleTableBattleInfo(iGroup):
    '''
import testtianxuan as t
t.S2CBattleTableBattleInfo(5)
\t:return:
\t'''
    dTeamInfo = { }
    if iGroup in serverbattledefine.ALL_START_GROUP_TEAM_LIST:
        iTableType = serverbattledefine.ALL_START_BTYPE_GROUP
    else:
        iTableType = serverbattledefine.ALL_START_BTYPE_14
    iTmpList = []
    for iPos in range(1, 5):
        dInfo = { }
        dInfo['iTeamID'] = iPos
        dInfo['iServerID'] = iPos
        dInfo['sTeamName'] = lstTeam[iPos - 1]
        dInfo['iState'] = LstState[iPos - 1]
        dInfo['iTeamType'] = iGroup
        dInfo['iPos'] = iPos
        dTeamInfo[iPos] = dInfo
        iTmpList.append(iPos)
    
    dBattleInfo = { }
    iWin1ID = iTmpList[0]
    iWin2ID = iTmpList[2]
    iLose1ID = iTmpList[3]
    iLose2ID = iTmpList[1]
    iPrimaryWinList = [
        iWin1ID,
        iWin2ID]
    iPrimaryLoseList = [
        iLose1ID,
        iLose2ID]
    iPromotedWin = iWin1ID
    iPromotedLose = iWin2ID
    iWeedOutWin = iLose1ID
    iLastWin = iWin2ID
    dTurnInfo = {
        1: [
            iTmpList[0],
            iTmpList[3]],
        2: [
            iTmpList[1],
            iTmpList[2]],
        3: [
            iWin1ID,
            iWin2ID],
        4: [
            iLose1ID,
            iLose2ID],
        5: [
            iPromotedLose,
            iWeedOutWin] }
    dMatchInfoDict = { }
    for iMatchIdx in range(1, 6):
        dMatchInfo = { }
        dMatchInfo['iTime'] = lsttime[iMatchIdx - 1]
        dMatchInfo['iMatchID'] = iMatchIdx
        dMatchInfo['iMatchState'] = 2
        dMatchInfo['iMatchStage'] = 2
        dMatchInfo['iRemindID'] = 1
        dMatchInfo['iTeamIDList'] = dTurnInfo[iMatchIdx]
        dMatchInfoDict[iMatchIdx] = dMatchInfo
    
    dBattleInfo['iPrimaryWinList'] = iPrimaryWinList
    dBattleInfo['iPrimaryLoseList'] = iPrimaryLoseList
    dBattleInfo['iPromotedWin'] = iPromotedWin
    dBattleInfo['iPromotedLose'] = iPromotedLose
    dBattleInfo['iWeedOutWin'] = iWeedOutWin
    dBattleInfo['iLastWin'] = iLastWin
    mdsbasbattletable.GetBattleTableModel().UpdateTeamInfo(iTableType, {
        iGroup: dTeamInfo })
    mdsbasbattletable.GetBattleTableModel().UpdateBattleInfo(iGroup, dBattleInfo)
    mdsbasbattletable.GetBattleTableModel().UpdateMatchInfo(iGroup, dMatchInfoDict)
    mdsbasbattletable.GetBattleTableModel().UpdateTrunInfo(iGroup, dTurnInfo)

lstFinal = [
    1,
    2,
    3,
    4]
lstState = [
    1,
    2,
    1,
    2]

def S2CBattleTableBattleInfoFinals():
    '''
import testtianxuan as t
t.S2CBattleTableBattleInfoFinals()
\t:return:
\t'''
    import copy
    iLoseList = []
    iWinList = []
    dTeamInfo = { }
    dAllTeamInfo = { }
    dTeamInfo41 = { }
    iGroup = 7
    lstTeam1 = [
        1,
        3]
    lstState1 = [
        1,
        2]
    lstResult = [
        [
            2,
            1],
        [
            1,
            2]]
    for iPos in range(1, 3):
        dInfo = { }
        iTeamID = lstTeam1[iPos - 1]
        dInfo['iTeamID'] = iTeamID
        dInfo['iServerID'] = iTeamID
        dInfo['sTeamName'] = lstTeam[iTeamID - 1]
        dInfo['iState'] = lstState1[iPos - 1]
        dInfo['iWin'] = lstResult[iPos - 1][0]
        dInfo['iLose'] = lstResult[iPos - 1][1]
        if dInfo['iState'] == serverbattledefine.PROMOTED_STATE_IN:
            iWinList.append(iTeamID)
        else:
            iLoseList.append(iTeamID)
        dInfo['iTeamType'] = iGroup
        dInfo['iPos'] = iPos
        dTeamInfo41[iTeamID] = dInfo
        dAllTeamInfo[iTeamID] = dInfo
    
    dTeamInfo[iGroup] = dTeamInfo41
    dTeamInfo42 = { }
    iGroup = 8
    lstTeam1 = [
        2,
        4]
    lstState1 = [
        1,
        2]
    lstResult = [
        [
            2,
            1],
        [
            1,
            2]]
    for iPos in range(1, 3):
        dInfo = { }
        iTeamID = lstTeam1[iPos - 1]
        dInfo['iTeamID'] = iTeamID
        dInfo['iServerID'] = iTeamID
        dInfo['sTeamName'] = lstTeam[iTeamID - 1]
        dInfo['iState'] = lstState1[iPos - 1]
        dInfo['iWin'] = lstResult[iPos - 1][0]
        dInfo['iLose'] = lstResult[iPos - 1][1]
        if dInfo['iState'] == serverbattledefine.PROMOTED_STATE_IN:
            iWinList.append(iTeamID)
        else:
            iLoseList.append(iTeamID)
        dInfo['iTeamType'] = iGroup
        dInfo['iPos'] = iPos
        dTeamInfo42[iTeamID] = dInfo
        dAllTeamInfo[iTeamID] = dInfo
    
    dTeamInfo[iGroup] = dTeamInfo42
    iLWin = 0
    dTeamInfo3 = { }
    iGroup = 9
    lstJJ = [
        3,
        4]
    lstState1 = [
        1,
        2]
    lstResult = [
        [
            2,
            1],
        [
            1,
            2]]
    for iPos in range(1, 3):
        iTeamID = lstJJ[iPos - 1]
        iState = lstState1[iPos - 1]
        if iTeamID not in dAllTeamInfo:
            LOG('[tx-as]>\xa8M\xc1\xc9\xb9\xef\xb0}\xaa\xed\xbc\xc6\xbe\xda\xb2\xa7\xb1`', dAllTeamInfo, iTeamID)
            continue
        
        dInfo = copy.deepcopy(dAllTeamInfo[iTeamID])
        dInfo['iState'] = iState
        dInfo['iTeamType'] = iGroup
        dInfo['iPos'] = iPos
        dTeamInfo3[iTeamID] = dInfo
        dInfo['iWin'] = lstResult[iPos - 1][0]
        dInfo['iLose'] = lstResult[iPos - 1][1]
        if iState == 1:
            iLWin = iTeamID
            continue
    
    dTeamInfo[iGroup] = dTeamInfo3
    iWWin = 0
    dTeamInfo1 = { }
    iGroup = 10
    lstJJ = [
        1,
        2]
    lstState1 = [
        1,
        2]
    for iPos in range(1, 3):
        iTeamID = lstJJ[iPos - 1]
        iState = lstState1[iPos - 1]
        if iTeamID not in dAllTeamInfo:
            LOG('[tx-as]>\xa8M\xc1\xc9\xb9\xef\xb0}\xaa\xed\xbc\xc6\xbe\xda\xb2\xa7\xb1`', dAllTeamInfo, iTeamID)
            continue
        
        dInfo = copy.deepcopy(dAllTeamInfo[iTeamID])
        dInfo['iState'] = iState
        dInfo['iTeamType'] = iGroup
        dInfo['iPos'] = iPos
        dInfo['iWin'] = lstResult[iPos - 1][0]
        dInfo['iLose'] = lstResult[iPos - 1][1]
        dTeamInfo1[iTeamID] = dInfo
        if dInfo['iState'] == 1:
            iWWin = iTeamID
            continue
    
    dTeamInfo[iGroup] = dTeamInfo1
    dBattleInfo = { }
    dBattleInfo['iPrimaryWinList'] = iWinList
    dBattleInfo['iPrimaryLoseList'] = iLoseList
    dBattleInfo['iThirdWin'] = iLWin
    dBattleInfo['iLastWin'] = iWWin
    S2CFinalsMatchInfo()
    oModel = mdsbasbattletable.GetBattleTableModel()
    oModel.UpdateTeamInfo(serverbattledefine.ALL_START_BTYPE_FINALS, dTeamInfo)
    oModel.SetFinalsBattleInfo(dBattleInfo)


def S2CFinalsMatchInfo():
    import misc
    iGroup = serverbattledefine.ALL_START_GROUP_TEAM_FINALS
    dMatchInfoDict = { }
    for iMatchIdx in range(1, 4):
        dInfo = { }
        dInfo['iTime'] = misc.GetServerCurrentTime()
        dInfo['iMatchID'] = 1
        dInfo['iMatchState'] = 2
        dInfo['iMatchStage'] = 2
        dInfo['iRemindID'] = 1
        dMatchInfoDict[iMatchIdx] = dInfo
    
    mdsbasbattletable.GetBattleTableModel().UpdateMatchInfo(iGroup, dMatchInfoDict)


def S2CRefreshRemindInfo(iWatchID, iRemind):
    '''
import testtianxuan as t
t.S2CRefreshRemindInfo(150,0)
\t:return:
\t'''
    mdsbasbattletable.GetBattleTableModel().UpdateMatchRemind(iRemind, iWatchID)


def S2COpenMainDialog():
    '''
import testtianxuan as t
t.S2COpenMainDialog()
\t:return:
\t'''
    import allstarinterface
    import dlgallstartgameguessmain
    dUIData = { }
    dUIData['RightTable'] = 2
    dUIData['UpTable'] = 1
    dUIData['OpenState'] = 5
    allstarinterface.OpenAllstarDlg(dUIData)


def S2CActivityIcon():
    '''
import testtianxuan as t
t.S2CActivityIcon()
\t:return:
\t'''
    iShow = 1
    iActivityID = 18
    extData = { }
    import model_activityicon
    model_activityicon.GetMgr().SetActivityIconData(iActivityID, iShow == 1, extData)
