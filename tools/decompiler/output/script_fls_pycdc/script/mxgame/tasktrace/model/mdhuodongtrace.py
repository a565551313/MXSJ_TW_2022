# pycdc 交叉复核产物 · script.fls entry 817
# co_filename(原始)='script/mxgame/tasktrace/model/mdhuodongtrace.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_817.pyc (Python 2.5)

import mddailykeju
import slot
import mdhuodongtraceprase
import tasktracedefines
import tasktraceutil
import timer
g_ohHuodongFollowModel = None

def ModuleReset():
    global g_ohHuodongFollowModel
    g_ohHuodongFollowModel = None


def GetModel():
    '''
\t:rtype: CHuodongTraceModel
\t'''
    global g_ohHuodongFollowModel
    if not g_ohHuodongFollowModel:
        g_ohHuodongFollowModel = CHuodongTraceModel()
    
    return g_ohHuodongFollowModel


class CHuodongTraceModel(slot.ISignalSubject):
    SS_HuodongTraceUpdate = 'SS_TaskTraceUpdate(iChangeType, sChangeHuodongList)'
    SS_HuodongTraceHide = 'SS_HuodongTraceHide()'
    SS_HuodongTraceClearHide = 'SS_HuodongTraceClearHide()'
    SS_CurHuodongFontIdxUpdate = 'SS_CurHuodongFontIdxUpdate()'
    SS_HuodongFrameExpandUpdate = 'SS_HuodongExpandUpdate()'
    
    def __init__(self):
        self.ssInit()
        self.m_iCurHuodongFontIdx = 0
        self.m_bHuodongFrameExpand = True
        self.m_dTraceHuodongOriDesc = { }
        self.m_dTraceHuodongDesc = { }
        self.m_sTraceHuodongOrderList = []
        self.m_sHideHuodongOrderList = []
        self.m_sNeedShowTimeList = []
        self.m_oPraseMgr = mdhuodongtraceprase.CHuodongTracePrase()
        self.m_oUpdateTimer = timer.Timer(1, self.OnTimeUpdate, -1, self)
        oModel = mddailykeju.GetModel()
        oModel.ssConnect(oModel.iieoJ^[N_|STSIR}[W_, self.OnKejuFinish)
        self.LoadLocal()

    
    def LoadLocal(self):
        '''
\t\t\xb1q\xa5\xbb\xa6a\xc5\xaa\xa8\xfa\xbc\xc6\xbe\xda
\t\t'''
        self.m_iCurHuodongFontIdx = tasktraceutil.GetHuodongFont()
        self.m_bHuodongFrameExpand = tasktraceutil.GetHuodongRemind()

    
    def SaveLocal(self):
        '''
\t\t\xa7\xe2\xbc\xc6\xbe\xda\xa5\xbb\xa6a\xa4\xc6
\t\t'''
        if self.m_bHuodongFrameExpand:
            iSave = 1
        else:
            iSave = 0
        tasktraceutil.SaveHuodongRemind(iSave)

    
    def GetHuodongOrderList(self):
        return self.m_sTraceHuodongOrderList

    
    def GetHuodongShowOrderList(self):
        if not self.m_sHideHuodongOrderList:
            return self.m_sTraceHuodongOrderList
        
        sTempList = []
        for sHudongName in self.m_sTraceHuodongOrderList:
            if sHudongName not in self.m_sHideHuodongOrderList:
                sTempList.append(sHudongName)
                continue
        
        return sTempList

    
    def GetHuodongDescByID(self, sHuodongName):
        return self.m_dTraceHuodongDesc.get(sHuodongName, None)

    
    def GetAllHudongDesc(self):
        return self.m_dTraceHuodongDesc

    
    def AddHuodongFollow(self, sHuodongName, sHuodongDesc):
        if sHuodongName == 'dailykeju':
            if mddailykeju.GetModel().IsFinishGame():
                return None
            
        
        if sHuodongName == 'localbeauty':
            return None
        
        self.m_dTraceHuodongOriDesc[sHuodongName] = sHuodongDesc
        (iTime, self.m_dTraceHuodongDesc[sHuodongName]) = self.m_oPraseMgr.GetHuodongDesc(sHuodongName, sHuodongDesc)
        if sHuodongName not in self.m_sTraceHuodongOrderList:
            self.m_sTraceHuodongOrderList.append(sHuodongName)
        
        if iTime and sHuodongName not in self.m_sNeedShowTimeList:
            self.m_sNeedShowTimeList.append(sHuodongName)
        
        self.ssEmit(self.SS_HuodongTraceUpdate, tasktracedefines.CHANGETPE_ADD, [
            sHuodongName])

    
    def SwitchTask(self, sHuodongName1, sHuodongName2):
        if sHuodongName1 in self.m_sTraceHuodongOrderList and sHuodongName2 in self.m_sTraceHuodongOrderList:
            self.m_sTraceHuodongOrderList.remove(sHuodongName1)
            iIndex = self.m_sTraceHuodongOrderList.index(sHuodongName2)
            self.m_sTraceHuodongOrderList.insert(iIndex + 1, sHuodongName1)
            self.ssEmit(self.SS_HuodongTraceUpdate, tasktracedefines.CHANGETYPE_ORDER, [
                sHuodongName1,
                sHuodongName2])
        

    
    def SetHuodongFollowHide(self, sHuodongName):
        if sHuodongName not in self.m_sHideHuodongOrderList:
            self.m_sHideHuodongOrderList.append(sHuodongName)
            self.ssEmit(self.SS_HuodongTraceHide)
        

    
    def ClearHuodongFollowHide(self):
        if self.m_sHideHuodongOrderList:
            self.m_sHideHuodongOrderList = []
            self.ssEmit(self.SS_HuodongTraceClearHide)
        

    
    def RemoveHuodongFollow(self, sHuodongName):
        if sHuodongName in self.m_dTraceHuodongOriDesc:
            del self.m_dTraceHuodongOriDesc[sHuodongName]
        
        if sHuodongName in self.m_dTraceHuodongDesc:
            del self.m_dTraceHuodongDesc[sHuodongName]
        
        if sHuodongName in self.m_sTraceHuodongOrderList:
            self.m_sTraceHuodongOrderList.remove(sHuodongName)
        
        if sHuodongName in self.m_sNeedShowTimeList:
            self.m_sNeedShowTimeList.remove(sHuodongName)
        
        self.ssEmit(self.SS_HuodongTraceUpdate, tasktracedefines.CHANGETYPE_DEL, [
            sHuodongName])

    
    def GetCurHuodongFontIdx(self):
        return self.m_iCurHuodongFontIdx

    
    def SetCurHuodongFontIdx(self, iFontIdx):
        if iFontIdx != self.m_iCurHuodongFontIdx:
            self.m_iCurHuodongFontIdx = iFontIdx
            tasktraceutil.SaveHuodongFont(self.m_iCurHuodongFontIdx)
            self.ssEmit(self.SS_CurHuodongFontIdxUpdate)
        

    
    def GetHuodongFrameIsExpand(self):
        return self.m_bHuodongFrameExpand

    
    def SetHuodongFrameIsExpand(self, bExpand, bSaveLocal = True):
        if self.m_bHuodongFrameExpand != bExpand:
            if not bExpand:
                self.ClearHuodongFollowHide()
            
            self.m_bHuodongFrameExpand = bExpand
            self.ssEmit(self.SS_HuodongFrameExpandUpdate)
        
        if bSaveLocal:
            self.SaveLocal()
        

    
    def OnTimeUpdate(self):
        sChangeList = []
        for sHDName in self.m_sNeedShowTimeList:
            if sHDName in self.m_sTraceHuodongOrderList:
                if self.RefreshHuodongDesc(sHDName):
                    sChangeList.append(sHDName)
                
            self.RefreshHuodongDesc(sHDName)
        
        if sChangeList:
            self.ssEmit(self.SS_HuodongTraceUpdate, tasktracedefines.CHANGETYPE_DESC, sChangeList)
        

    
    def OnKejuFinish(self):
        bIsFinish = mddailykeju.GetModel().IsFinishGame()
        sKejuKey = 'dailykeju'
        if bIsFinish and sKejuKey in self.m_sTraceHuodongOrderList:
            self.RemoveHuodongFollow(sKejuKey)
        

    
    def RefreshHuodongDesc(self, sHuodongName):
        sTraceInfo = self.m_dTraceHuodongDesc.get(sHuodongName, None)
        sOriTraceInfo = self.m_dTraceHuodongOriDesc.get(sHuodongName, '')
        self.m_dTraceHuodongDesc[sHuodongName] = self.m_oPraseMgr.GetHuodongDesc(sHuodongName, sOriTraceInfo)[1]
        return sTraceInfo != self.m_dTraceHuodongDesc[sHuodongName]
