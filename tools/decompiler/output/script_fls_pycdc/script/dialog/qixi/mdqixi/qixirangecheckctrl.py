# pycdc 交叉复核产物 · script.fls entry 3190
# co_filename(原始)='script/dialog/qixi/mdqixi/qixirangecheckctrl.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3190.pyc (Python 2.5)

import chardefine
import hero
import map
import model_mapinfobar
import netqixi
import slot
import teammgr
import timer
import usermacro
import world
import wrapmath
g_oQiXiRangeCheckCtrl = None
g_iHasRestTask = 0
g_iMatchFriend = 0

def ModuleReset():
    global g_oQiXiRangeCheckCtrl, g_iHasRestTask, g_iMatchFriend
    g_oQiXiRangeCheckCtrl = None
    g_iHasRestTask = 0
    g_iMatchFriend = 0


def SetTaskState(iHasRestTask):
    '''
import qixirangecheckctrl
qixirangecheckctrl.SetTaskState(1)
\t:param iHasRestTask:
\t:return:
\t'''
    global g_iHasRestTask
    g_iHasRestTask = iHasRestTask
    if iHasRestTask:
        GetCQixiMainModel().Start()
    else:
        GetCQixiMainModel().EndCheck()


def SetMatchState(iState):
    global g_iMatchFriend
    g_iMatchFriend = iState


def GetCQixiMainModel():
    ''':rtype: CQiXiRangeCheckCtrl'''
    global g_oQiXiRangeCheckCtrl
    if not g_oQiXiRangeCheckCtrl:
        g_oQiXiRangeCheckCtrl = CQiXiRangeCheckCtrl()
    
    return g_oQiXiRangeCheckCtrl


class CQiXiRangeCheckCtrl(slot.ISignalSubject):
    MAX_CHECK = 60
    DEBUG = False
    
    def __init__(self):
        self.ssInit()
        self.m_oCheckTime = None
        self.m_iCorrectStateCount = 0

    
    def Start(self):
        if not self.IsOpenCheck():
            return None
        
        self.BeginCheck()

    
    def BeginCheck(self):
        if not self.IsOpenCheck():
            return None
        
        self.EndCheck()
        self.m_oCheckTime = timer.Timer(1, self.OnDoCheck, -1, oRelayObj = self)

    
    def EndCheck(self):
        if self.m_oCheckTime:
            self.m_oCheckTime.Release()
            self.m_oCheckTime = None
        

    
    def PassInspection(self):
        netqixi.C2GSSendTaskComplete()

    
    def IsOpenCheck(self):
        return g_iHasRestTask

    
    def AddLog(self, sMsg):
        if self.DEBUG:
            usermacro.PROMPT_MSG(sMsg)
        

    
    def IsCorrectState(self):
        if not self.IsInMap():
            self.AddLog('\xa6a\xb9\xcf\xc0\xcb\xacd\xb2\xa7\xb1`')
            return False
        
        if not self.IsInTeam():
            self.AddLog('\xb6\xa4\xa5\xee\xc0\xcb\xacd\xb2\xa7\xb1`')
            return False
        
        if not self.IsDoEmote():
            self.AddLog('\xb0\xca\xa7@\xc0\xcb\xacd\xb2\xa7\xb1`')
            return False
        
        if not self.IsInWithinTheRange():
            self.AddLog('\xb0\xcf\xb0\xec\xc0\xcb\xacd\xb2\xa7\xb1`')
            return False
        
        if not hero.IsTeamLeader():
            return False
        
        return True

    
    def IsInMap(self):
        oMap = map.GetGameMapObject()
        if not oMap:
            return False
        
        sMapName = model_mapinfobar.GetModel().GetMapName()
        if sMapName != '\xa9\xfa\xa4\xeb\xab\xb0':
            return False
        
        return True

    
    def IsInWithinTheRange(self):
        (iChechX, iCheckY) = (32, 225)
        iDRange = 20
        (iPosX, iPosY) = hero.GetServerPos()
        del GetServerPos
        return None(wrapmath.PtInPolygon, ((iPosX, iPosY), (iChechX + iDRange, iCheckY + iDRange), (iChechX + iDRange, iCheckY - iDRange), ((iChechX - iDRange, iCheckY - iDRange) - iDRange, iCheckY + iDRange)))

    
    def IsInTeam(self):
        oTeamMgr = teammgr.GetTeamMgr()
        if not oTeamMgr.IsLeader():
            return False
        
        if oTeamMgr.GetTeamNum() != 2:
            return False
        
        for dInfo in oTeamMgr.GetTeamList():
            if dInfo['leave']:
                return False
                continue
        
        return True

    
    def IsDoEmote(self):
        oTeamMgr = teammgr.GetTeamMgr()
        for dInfo in oTeamMgr.GetTeamList():
            oObj = world.GetObj(dInfo['id'])
            if not oObj:
                return False
            
            if oObj.GetState() != chardefine.STATE_SIT:
                return False
                continue
        
        return True

    
    def OnDoCheck(self):
        if self.IsCorrectState():
            self.m_iCorrectStateCount += 1
            self.AddLog('\xc0\xcb\xacd\xb3q\xb9L\xb0O\xbf\xfd\xbc\xc6\xa5\xd8%s' % self.m_iCorrectStateCount)
            if self.m_iCorrectStateCount % 10 == 0:
                if self.m_iCorrectStateCount < self.m_iCorrectStateCount:
                    pass
                elif self.m_iCorrectStateCount <= 60:
                    netqixi.C2GSSendRestTime(self.m_iCorrectStateCount)
                
            if self.m_iCorrectStateCount >= self.MAX_CHECK:
                self.EndCheck()
                self.PassInspection()
            
        else:
            self.m_iCorrectStateCount = 0

    
    def OnServerEnd(self):
        self.BeginCheck()
