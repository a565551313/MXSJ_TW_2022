# pycdc 交叉复核产物 · script.fls entry 1275
# co_filename(原始)='script/debug/getmagictime.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1275.pyc (Python 2.5)

from testwar import *
import warbugrecord
import war
import usermacro
import C_sys
import commoncb
TRY_TIME = 3
MultiAttack_ID = {
    1136: 10,
    1139: 10,
    1140: 10,
    1599: 3,
    1698: 3 }
PHY_MULTI_ZHAOSHI = [
    1210,
    1314]
g_MagicTimeMgr = None
g_StaticMgr = None
g_TimeChecker = None

def ModuleReset():
    global g_MagicTimeMgr, g_StaticMgr, g_TimeChecker
    g_MagicTimeMgr = None
    g_StaticMgr = None
    g_TimeChecker = None


def GetSkillTime(iSkillID = 0, iMaxSkillID = 0):
    if iSkillID == 0:
        GetStaticMgr().GetAllSkillTime()
    elif iMaxSkillID == 0:
        GetStaticMgr().GetSingleSkillTime(iSkillID)
    else:
        GetStaticMgr().GetRangeSkillTime(iSkillID, iMaxSkillID)


def GetTimeChecker():
    global g_TimeChecker
    if not g_TimeChecker:
        g_TimeChecker = CTimeChecker()
    
    return g_TimeChecker


class CMagictimeStatic(object):
    
    def __init__(self):
        self.m_sFilePath = 'magictime.desc'
        self.m_sFileMgr = CPfmFileMgr()
        self.m_sFileMgr.SetInput(self.m_sFilePath)
        self.m_sFileMgr.SetOutput(self.m_sFilePath)
        self.m_PreRunList = []
        self.m_RuningList = []

    
    def GetRangeSkillTime(self, iMinSkillID, iMaxSkillID):
        import magicdata
        for iSkillID in range(iMinSkillID, iMaxSkillID + 1):
            if iSkillID in magicdata.DATA:
                self.m_PreRunList.append(iSkillID)
                continue
        
        self.StartRun()

    
    def GetSingleSkillTime(self, iSkillID):
        self.m_PreRunList.append(iSkillID)
        self.StartRun()

    
    def GetAllSkillTime(self):
        import magicdata
        self.m_PreRunList = magicdata.DATA.keys()
        self.StartRun()

    
    def StartRun(self):
        for iSkillID in self.m_PreRunList:
            self.m_RuningList.append(iSkillID)
            GetMagicTimeMgr().GetPerformTime(iSkillID, self.OnSkillTimeUpdate)
        
        self.m_PreRunList = []

    
    def OnSkillTimeUpdate(self, iSkillID, iTime):
        import usermacro
        if iSkillID in self.m_RuningList:
            self.m_RuningList.remove(iSkillID)
            usermacro.NORMAL_MSG('\xbds\xb8\xb9%s\xa1A\xb5\xb2\xaaG\xacO %s' % (iSkillID, iTime))
            self.m_sFileMgr.RefreshSkillTime(iSkillID, iTime)
            if not self.m_RuningList:
                self.m_sFileMgr.Output()
                usermacro.NORMAL_MSG('\xbe\xc9\xaa\xed\xa7\xb9\xa6\xa8\xa1I\xa1I\xa1I\xa1I')
                continue
        



class CMagicTimeMgr(object):
    TYPE2EQUIP = {
        11: 1,
        12: 2,
        13: 3,
        14: 4,
        15: 5,
        16: 6 }
    
    def __init__(self):
        self.m_RunDict = { }
        self.m_CurSkillID = 0
        self.m_LastTime = 0
        self.InitWar()
        self.ReplacePerform()
        commoncb.RegistCB(commoncb.WAR_TURNCNTCHANGED, self, 'OnTurnOut')

    
    def GetPerformTime(self, iSkillID, oResultCB):
        self.m_RunDict[iSkillID] = {
            'oCB': oResultCB,
            'iRunTime': 0,
            'iTotalRunTime': TRY_TIME,
            'fRet': 0 }
        self.PlaySkill(iSkillID, TRY_TIME)

    
    def PlaySkill(self, iSkillID, iTimes):
        dSkillInfo = self.GetSkillPeformData(iSkillID)
        if dSkillInfo['iSourceType'] == 0:
            iSourceID = 3
        else:
            iSourceID = dSkillInfo['iSourceType']
        if dSkillInfo['iTargetType'] == 2:
            iTargetID = iSourceID
            iHpChg = -101
            iWard = war.WARRIOR_WARD_NONE
        elif dSkillInfo['iTargetType'] == 3:
            iTargetID = (iSourceID - 2) % 6 + 1
            iHpChg = -101
            iWard = war.WARRIOR_WARD_NONE
        else:
            iTargetID = 10
            iHpChg = 101
            iWard = war.WARRIOR_WARD_HIT
        for i in range(iTimes):
            Perform(iSourceID, iSkillID, [
                iTargetID])
            if dSkillInfo['bPhy']:
                AttackNormal(iSourceID, iTargetID)
            
            State(iTargetID, iWard, war.WARRIOR_LIFE_NORMAL, war.WARRIOR_HURT_NONE, iHpChg)
            if dSkillInfo['bPhy']:
                AttackNormalEnd()
            
            Turn()
        

    
    def InitWar(self):
        warbugrecord.GetMgr().StartWar()
        Start(2001, 1000, 800, 1, 0)
        Add('\xa8\xcf\xbcC\xaa\xba\xb5{\xa7\xc7', 1, 111, 1, 2, 1, 0, 0, 1717980270)
        Add('\xa8\xcf\xb5\xa7\xaa\xba\xb5{\xa7\xc7', 2, 111, 1, 2, 1, 0, 0, 21000)
        Add('\xa8\xcf\xae\xb1\xaa\xba\xb5{\xa7\xc7', 3, 111, 1, 2, 1, 0, 0, 31240)
        Add('\xa8\xcf\xa4M\xaa\xba\xb5{\xa7\xc7', 4, 111, 1, 2, 1, 0, 0, 41480)
        Add('\xa8\xcf\xbaj\xaa\xba\xb5{\xa7\xc7', 5, 111, 1, 2, 1, 0, 0, 51720)
        Add('\xa8\xcf\xb7t\xbe\xb9\xaa\xba\xb5{\xa7\xc7', 6, 111, 1, 2, 1, 0, 0, 61960)
        Add('\xb5\xa6\xa6E\xaa\xa8\xaa\xa8', 10, 111, 0, 2, 1, 0, 0, 10760)
        Turn()

    
    def GetSkillPeformData(self, iSkillID):
        '''
\t\t\xc0\xf2\xa8\xfa\xa4@\xad\xd3\xa7\xde\xaf\xe0\xbb\xdd\xadn\xaa\xba\xa4\xe8\xa4\xe8\xad\xb1\xad\xb1\xbc\xc6\xbe\xda
\t\t:param iSkillID:
\t\t:rtype: dict
\t\t'''
        import zhaoshidata
        import magicdata
        import magicperformdata
        dInfo = { }
        dInfo['iTargetType'] = zhaoshidata.GetData(iSkillID)
        dInfo['iSourceType'] = self.TYPE2EQUIP.get(magicdata.GetData(iSkillID)['type'], 0)
        if iSkillID in magicdata.PHYSICS_LIST:
            pass
        dInfo['bPhy'] = iSkillID not in PHY_MULTI_ZHAOSHI
        dInfo['iPerformCmdCount'] = 0
        for dEach in magicperformdata.PERFORMDATA.itervalues():
            if dEach['iMgcID'] == iSkillID:
                dInfo['iPerformCmdCount'] += 1
                continue
        
        return dInfo

    
    def OnTurnOut(self, iTurnCount):
        if self.m_CurSkillID:
            if self.m_CurSkillID in self.m_RunDict:
                fDiff = (C_sys.GetTime() - self.m_LastTime) / 10
                dInfo = self.m_RunDict[self.m_CurSkillID]
                dInfo['iRunTime'] += 1
                if fDiff > dInfo['fRet']:
                    dInfo['fRet'] = fDiff
                
                if dInfo['iTotalRunTime'] == dInfo['iRunTime']:
                    dInfo['oCB'](self.m_CurSkillID, dInfo['fRet'])
                    del self.m_RunDict[self.m_CurSkillID]
                    self.m_CurSkillID = 0
                
            
        

    
    def NewPerform(self, cmd):
        self.m_CurSkillID = cmd.pid
        self.m_LastTime = C_sys.GetTime()
        war.old_Perform(cmd)

    
    def ReplacePerform(self):
        if not hasattr(war, 'old_Perform'):
            war.old_Perform = war.Perform
        
        war.Perform = misc.Functor(self.NewPerform)



class CPfmFileMgr(object):
    ORDER = 0
    NAME = 1
    MAGIC = 2
    TIME = 3
    
    def __init__(self):
        self.m_InputPath = None
        self.m_OutputPath = None
        self.m_UpdateList = []
        self.m_Data = []
        self.m_HasInit = False

    
    def SetInput(self, sInputPath):
        import os
        if os.path.lexists(sInputPath):
            self.m_HasInit = True
        else:
            usermacro.PROMPT_MSG('\xbd\xd0\xa7\xe2magictime.desc\xa9\xf1\xae\xda\xa5\xd8\xbf\xfd')
            self.m_HasInit = False
        self.m_InputPath = sInputPath
        self.Input()

    
    def SetOutput(self, sOutputPath):
        self.m_OutputPath = sOutputPath

    
    def IsInit(self):
        return self.m_HasInit

    
    def Input(self):
        if not self.m_HasInit:
            return None
        
        if not self.m_InputPath:
            return None
        
        oFile = open(self.m_InputPath, 'r')
        sFile = oFile.read()
        oFile.close()
        LineList = sFile.split('\n')
        self.m_Data = []
        for idx, line in enumerate(LineList):
            if line:
                (iID, iTime) = line.split('\t')
                self.m_Data.append([
                    int(iID),
                    int(iTime)])
                continue
        

    
    def Output(self):
        if not self.m_HasInit:
            return None
        
        if not self.m_OutputPath:
            return None
        
        oFile = open(self.m_OutputPath, 'wb')
        LineList = []
        for data in self.m_Data:
            (iID, iTime) = data
            LineList.append('\t'.join([
                str(iID),
                str(iTime)]))
        
        sFile = '\n'.join(LineList)
        oFile.write(sFile)
        oFile.close()

    
    def RefreshSkillTime(self, iMagicID, iTime):
        if not self.m_Data:
            return None
        
        for data in self.m_Data:
            if data[0] == iMagicID:
                data[1] = iTime
                break
                continue
        
        print '==========', '\xa7\xf3\xb7s\xaak\xb3N\xae\xc9\xb6\xa1\xa1G\xaak\xb3Nid\xa1G%s \xae\xc9\xb6\xa1\xa1G%s' % (iMagicID, iTime)

    
    def GetSkillList(self):
        lList = []
        for data in self.m_Data:
            lList.append(int(data[self.MAGIC]))
        
        return lList



class CTimeChecker(object):
    
    def __init__(self):
        self.m_iClientEndTime = 0
        self.m_iServerEndTime = 0
        self.m_bClientReady = False
        self.m_bServerReady = False
        self.m_iClentStartTime = 0
        self.m_iServerStartTime = 0
        commoncb.RegistCB(commoncb.WAR_SERVER_TURNCNTCHANGE, self, 'OnServerTurnUpdate')
        commoncb.RegistCB(commoncb.WAR_TURNCNTCHANGED, self, 'OnClientTurnEnd')

    
    def OnServerTurnUpdate(self):
        self.m_bClientReady = False
        self.m_bServerReady = False
        self.m_iClentStartTime = C_sys.GetTime()
        self.m_iServerStartTime = C_sys.GetTime()

    
    def OnClientTurnEnd(self, iTurnCount):
        self.m_iClientEndTime = C_sys.GetTime()
        self.m_bClientReady = True
        self.Check()

    
    def OnServerTurnEnd(self):
        self.m_iServerEndTime = C_sys.GetTime()
        self.m_bServerReady = True
        self.Check()

    
    def Check(self):
        if not (self.m_bClientReady) or not (self.m_bServerReady):
            return None
        
        if self.m_iServerEndTime and self.m_iClientEndTime:
            iDiff = (self.m_iServerEndTime - self.m_iClientEndTime) / 10
            iClientTime = (self.m_iClientEndTime - self.m_iClentStartTime) / 10
            iServerTime = (self.m_iServerEndTime - self.m_iServerStartTime) / 10
            if iDiff > 0:
                self.ShowChat('\xaaA\xb0\xc8\xbe\xb9\xa4\xf1\xab\xc8\xa4\xe1\xba\xdd\xbaC\xa4F%s\xb2@\xac\xed, \xab\xc8\xa4\xe1\xba\xdd\xa5\xce\xae\xc9\xa1G%d, \xaaA\xb0\xc8\xbe\xb9\xa5\xce\xae\xc9\xa1G%d' % (iDiff, iClientTime, iServerTime))
            elif iDiff < 0:
                self.ShowChat('\xaaA\xb0\xc8\xbe\xb9\xa4\xf1\xab\xc8\xa4\xe1\xba\xdd\xa7\xd6\xa4F%s\xb2@\xac\xed, \xab\xc8\xa4\xe1\xba\xdd\xa5\xce\xae\xc9\xa1G%d, \xaaA\xb0\xc8\xbe\xb9\xa5\xce\xae\xc9\xa1G%d' % (abs(iDiff), iClientTime, iServerTime))
            else:
                self.ShowChat('\xaaA\xb0\xc8\xbe\xb9\xa9M\xab\xc8\xa4\xe1\xba\xdd\xa7\xb9\xa5\xfe\xa6P\xa8B, \xab\xc8\xa4\xe1\xba\xdd\xa5\xce\xae\xc9\xa1G%d, \xaaA\xb0\xc8\xbe\xb9\xa5\xce\xae\xc9\xa1G%d' % (iClientTime, iServerTime))
        

    
    def ShowChat(self, sMsg):
        usermacro.NORMAL_MSG(sMsg)



def GetStaticMgr():
    global g_StaticMgr
    if not g_StaticMgr:
        g_StaticMgr = CMagictimeStatic()
    
    return g_StaticMgr


def GetMagicTimeMgr():
    global g_MagicTimeMgr
    if not g_MagicTimeMgr:
        g_MagicTimeMgr = CMagicTimeMgr()
    
    return g_MagicTimeMgr
