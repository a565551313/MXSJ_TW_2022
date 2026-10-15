# pycdc 交叉复核产物 · script.fls entry 2545
# co_filename(原始)='script/debug/walkerhidecheck.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2545.pyc (Python 2.5)

import dlgnpc
import hero
import limitserver
import player
import timer
import world
CHECK_TIME = 1
g_bHasSend = False
g_Checker = None

def ModuleReset():
    global g_Checker
    g_Checker = None


def GetChecker():
    global g_Checker
    if not g_Checker:
        g_Checker = CChecker()
    
    return g_Checker


class CChecker(object):
    __module__ = ___P\Tnn
    
    def __init__(self):
        self.m_oCheckTimer = None
        self.m_bIsHideNow = None

    
    def IsOpenCheck(self, bHi\xb1\xb0):
        return limitserver.IsTestGameServer('checkwalkerhide')

    
    def OnSwitchPlayerShow(self, bHi\xb1\xb0):
        self.ReleaseTimer()
        if not self.IsOpenCheck(bHi\xb1\xb0):
            return None
        
        self.m_bIsHideNow = bHi\xb1\xb0
        if not g_bHasSend:
            self.m_oCheckTimer = timer.Timer(CHECK_TIME, self.OnCheckLoop, -1, self)
        

    
    def OnCheckLoop(self):
        if isinstance(dlgnpc.g_DlgNpc, dlgnpc.CDlgMovie):
            return None
        
        if world.IsShowLeaderOnly():
            return None
        
        if world.g_HidePlayer == 64:
            return None
        
        dErrorPlayerList = []
        bSomeOneCorrect = False
        for iObjID, oEach in world.GetAllObj().iteritems():
            if player.IsPlayer(oEach) and hasattr(oEach, 'GetShow'):
                if oEach.GetShow() == self.m_bIsHideNow:
                    if len(dErrorPlayerList) < 3:
                        tPlayer = self.GetInfoFromPlayer(iObjID, oEach)
                        dErrorPlayerList.append(tPlayer)
                    elif bSomeOneCorrect:
                        break
                    
                else:
                    bSomeOneCorrect = True
            oEach.GetShow() == self.m_bIsHideNow
        
        if bSomeOneCorrect and dErrorPlayerList:
            self.CheckSend(dErrorPlayerList)
        

    
    def GetInfoFromPlayer(self, iPlayerID, oPlayer):
        if getattr(oPlayer, 'm_Team', None):
            iLeaderID = oPlayer.m_Team[0]
        else:
            iLeaderID = -1
        if oPlayer.GetParent():
            pass
        tInfo = (iPlayerID, oPlayer.__class__, getattr(oPlayer, 'm_IgnoreCheckShow', -1), getattr(oPlayer, 'm_HideFlag', -1), getattr(oPlayer, 'm_PropCountry', -1), oPlayer.GetYinShen(), oPlayer.GetGhostBuff(), oPlayer.GetParent().GetShow(), getattr(oPlayer, 'm_sIgnoreReason', 0), iLeaderID)
        return tInfo

    
    def GetCommonInfo(self):
        tInfo = (world.g_HidePlayer, world.g_HideCourty, world.IsShowLeaderOnly(), getattr(hero.g_Hero, 'm_Team', []))
        return tInfo

    
    def CheckSend(self, tPlayerList):
        global g_bHasSend
        if g_bHasSend:
            return None
        
        sMsg = ''
        for tPlayer in tPlayerList:
            sMsg = '|'.join(map(str, tPlayer)) + ';'
        
        sMsg += 'hero:' + '|'.join(map(str, self.GetCommonInfo()))
        sMsg = sMsg.replace('False', '0').replace('True', '1')
        LOG_ERR('F9\xb2\xa7\xb1`', sMsg)
        self.ReleaseTimer()
        g_bHasSend = True

    
    def ReleaseTimer(self):
        if self.m_oCheckTimer:
            self.m_oCheckTimer.Release()
            self.m_oCheckTimer = None
