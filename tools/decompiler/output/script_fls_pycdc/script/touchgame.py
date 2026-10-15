# pycdc 交叉复核产物 · script.fls entry 4207
# co_filename(原始)='script/touchgame.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4207.pyc (Python 2.5)

import C_sys
import interface
import wrapcallback
g_Mode = None
g_OperateID = None
g_RemainTime = 0
g_RemainTimeCB = None
g_FlagTime = 0
g_AllRemainTime = 0
g_RemainTimer = None
g_Point = 0
g_PrePoint = 0
g_PointCB = None
g_TopScore = None
g_Turn = None
g_PlayerInfo = None
g_PlayerInfoCB = None
g_HpCB = None
g_SkillCB = None
g_OperateCB = None
g_FriendRankList = None
g_RankCB = None

def ModuleReset():
    global g_Mode, g_OperateID, g_RemainTime, g_RemainTimeCB, g_FlagTime, g_AllRemainTime, g_RemainTimer, g_Point, g_PrePoint, g_PointCB, g_TopScore, g_Turn, g_PlayerInfo, g_PlayerInfoCB, g_HpCB, g_SkillCB, g_OperateCB, g_FriendRankList, g_RankCB
    g_Mode = None
    g_OperateID = None
    g_RemainTime = 0
    g_RemainTimeCB = None
    g_FlagTime = 0
    g_AllRemainTime = 0
    g_RemainTimer = None
    g_Point = 0
    g_PrePoint = 0
    g_PointCB = None
    g_TopScore = None
    g_Turn = None
    g_PlayerInfo = None
    g_PlayerInfoCB = None
    g_HpCB = None
    g_SkillCB = None
    g_OperateCB = None
    g_FriendRankList = None
    g_RankCB = None

MODE_SELF = 0
MODE_DOUBLE = 1

def Clear():
    ClearRemainTime()
    ClearPoint()
    ClearTopScore()
    ClearGameMode()
    ClearOperate()
    ClearPlayer()
    EndRemainTimer()
    ClearRankData()


def GetPoint():
    return g_Point


def GetPrePoint():
    return g_PrePoint


def GetPointCB():
    global g_PointCB
    if g_PointCB is None:
        g_PointCB = wrapcallback.CreateCallBackBase()
    
    return g_PointCB


def SetPoint(point):
    global g_PrePoint, g_Point
    g_PrePoint = g_Point
    g_Point = point
    GetPointCB().DoCallBack()


def ClearPoint():
    global g_Point, g_PointCB
    g_Point = 0
    g_PointCB = None


def SetTopScore(topScore):
    global g_TopScore
    g_TopScore = topScore


def GetTopScore():
    return g_TopScore


def ClearTopScore():
    global g_TopScore
    g_TopScore = None


def GetRemainTime():
    return g_RemainTime


def SetRemainTime(remainTime, frame = 15):
    global g_RemainTime, g_AllRemainTime, g_FlagTime
    g_RemainTime = remainTime
    g_AllRemainTime = remainTime
    g_FlagTime = C_sys.GetTime()
    GetRemainTimeCB().DoCallBack()
    StratRemainTimer(frame)


def GetRemainTimeCB():
    global g_RemainTimeCB
    if g_RemainTimeCB is None:
        g_RemainTimeCB = wrapcallback.CreateCallBackBase()
    
    return g_RemainTimeCB


def ClearRemainTime():
    global g_RemainTime, g_RemainTimeCB
    g_RemainTime = 0
    g_RemainTimeCB = None


def ReduceRemainTime(obj):
    global g_RemainTime
    g_RemainTime = g_AllRemainTime - (C_sys.GetTime() - g_FlagTime) / 10
    g_RemainTimeCB.DoCallBack()
    return ()


def EndRemainTimer():
    global g_RemainTimer
    if g_RemainTimer:
        g_RemainTimer.Release()
        g_RemainTimer = None
    


def StratRemainTimer(frame = 15):
    global g_RemainTimer
    EndRemainTimer()
    g_RemainTimer = interface.CBaseObject(None)
    g_RemainTimer.CreatePyCommand(frame, ReduceRemainTime)


def ClearGameMode():
    global g_Mode
    g_Mode = None


def SetGameMode(mode = 0):
    global g_Mode
    g_Mode = mode


def IsOnlySelfMode():
    return g_Mode == MODE_SELF


def IsBattleMode():
    return g_Mode == MODE_DOUBLE


def IsMyTurn():
    import hero
    if IsOnlySelfMode():
        return True
    elif g_OperateID == hero.g_ID:
        return True
    
    return False


def SetOperate(ID):
    global g_OperateID
    g_OperateID = ID
    GetOperateCB().DoCallBack()


def GetOperate():
    return g_OperateID


def GetOperateCB():
    global g_OperateCB
    if g_OperateCB is None:
        g_OperateCB = wrapcallback.CreateCallBackBase()
    
    return g_OperateCB


def ClearOperate():
    global g_OperateID, g_OperateCB
    g_OperateID = None
    g_OperateCB = None


def ID2Type(pID):
    import hero
    pType = None if pID == hero.g_ID else 'right'
    return pType


def SetHp(pID, hp):
    pType = ID2Type(pID)
    g_PlayerInfo[pType]['prehp'] = g_PlayerInfo[pType]['hp']
    g_PlayerInfo[pType]['hp'] = hp
    GetHpCB().DoCallBack()


def SetHp2PreHp(pType = 'left'):
    g_PlayerInfo[pType]['prehp'] = g_PlayerInfo[pType]['hp']


def GetHp(pType = 'left'):
    return g_PlayerInfo[pType]['hp']


def GetMaxHp(pType = 'left'):
    return g_PlayerInfo[pType]['maxhp']


def GetPreHp(pType = 'left'):
    return g_PlayerInfo[pType]['prehp']


def GetHurtHp(pType = 'left'):
    return GetPreHp() - GetHp()


def GetHpCB():
    global wrapcallback, g_HpCB
    if g_HpCB is None:
        wrapcallback = None
        g_HpCB = None.CreateCallBackBase()
    
    return g_HpCB


def AddSkill(pID, skillID):
    pType = ID2Type(pID)
    skillDct = g_PlayerInfo[pType]['skill']
    if skillID in skillDct:
        skillDct[skillID] += 1
    else:
        skillDct[skillID] = 1
    GetSkillCB().DoCallBack()
    print 'touchgame\xbcW\xa5[\xa7\xde\xaf\xe0', skillID


def RuduceSkill(pID, skillID):
    pType = ID2Type(pID)
    skillDct = g_PlayerInfo[pType]['skill']
    skillDct[skillID] -= 1
    if skillDct[skillID] < 0:
        skillDct[skillID] = 0
    
    GetSkillCB().DoCallBack()
    print '\xb4\xee\xa4\xd6\xa7\xde\xaf\xe0', skillID


def GetSkill(pType = 'left'):
    return g_PlayerInfo[pType]['skill']


def GetSkillCB():
    global g_SkillCB
    if g_SkillCB is None:
        g_SkillCB = wrapcallback.CreateCallBackBase()
    
    return g_SkillCB


def InitPlayerInfo(playerInfo):
    global g_PlayerInfo
    playerInfo['left']['skill'] = { }
    playerInfo['right']['skill'] = { }
    playerInfo['left']['maxhp'] = playerInfo['left']['hp']
    playerInfo['right']['maxhp'] = playerInfo['right']['hp']
    playerInfo['left']['prehp'] = playerInfo['left']['hp']
    playerInfo['right']['prehp'] = playerInfo['right']['hp']
    g_PlayerInfo = playerInfo


def ClearPlayer():
    global g_PlayerInfoCB, g_PlayerInfo, g_SkillCB, g_HpCB
    g_PlayerInfoCB = None
    g_PlayerInfo = None
    g_SkillCB = None
    g_HpCB = None


def GetPlayerInfo():
    return g_PlayerInfo


def SetRankData(rankList):
    global g_FriendRankList
    g_FriendRankList = rankList


def GetRankData():
    return g_FriendRankList


def GetRankCB():
    global g_RankCB
    if g_RankCB is None:
        g_RankCB = wrapcallback.CreateCallBackBase()
    
    return g_RankCB


def ClearRankData():
    global g_FriendRankList, g_RankCB
    g_FriendRankList = None
    g_RankCB = None


def GameModeSelfStart(remainTime, topScore):
    import touchmain
    import touchaction
    SetPoint(0)
    SetTopScore(topScore)
    SetGameMode(MODE_SELF)
    touchmain.ShowModeSelfDlg(True)
    touchaction.StartFrameTimer()
    SetRemainTime(remainTime * 1000)


def GameModeDoubleStart(playerInfo):
    import touchmain
    import touchaction
    SetGameMode(MODE_DOUBLE)
    InitPlayerInfo(playerInfo)
    touchmain.ShowModeDoubleDlg(True)
    touchaction.StartFrameTimer()


def IsGameOver():
    return g_Mode is None


def InGame():
    return g_Mode is not None


def GameEnd(iType = None):
    import touchmain
    import touchaction
    Clear()
    touchmain.Clear()
    touchaction.Clear()


def ForceEnd():
    import nettouch
    GameEnd()
    nettouch.C2SForceEnd()
