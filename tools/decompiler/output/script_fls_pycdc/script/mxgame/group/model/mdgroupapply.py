# pycdc 交叉复核产物 · script.fls entry 3449
# co_filename(原始)='script/mxgame/group/model/mdgroupapply.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3449.pyc (Python 2.5)

'''
Author huyuhong01
Create Time 2018/12/18
\xb0\xef\xc5\xc9\xc9\xea\xc7\xeb\xbd\xe7\xc3\xe6\xb5\xc4\xca\xfd\xbe\xdd\xb4\xe6\xb7\xc5
'''
g_oGroupApplyModel = None

def ModuleReset():
    global g_oGroupApplyModel
    if g_oGroupApplyModel:
        g_oGroupApplyModel.Clear()
    
    g_oGroupApplyModel = None


def GetModel():
    global g_oGroupApplyModel
    if not g_oGroupApplyModel:
        g_oGroupApplyModel = CGroupApplyModel()
    
    return g_oGroupApplyModel


class CGroupInfoModel(object):
    
    def __init__(self, tData):
        self.m_iId = 0
        self.m_sName = None
        self.m_sOwner = None
        self.m_iLv = 0
        self.m_iAmount = 0
        self.m_iMaxAmount = 0
        self.m_iFlag = 0
        self.m_sDesc = None
        self.m_iReady = 0
        self.m_iActivity = 0
        self.m_iPride = 0
        self.UpdateData(tData)

    
    def UpdateData(self, tData):
        (self.m_iId, self.m_sName, self.m_sOwner, self.m_iLv, self.m_iAmount, self.m_iMaxAmount, self.m_iFlag, self.m_sDesc, self.m_iReady, self.m_iActivity, self.m_iPride) = tData



class CGroupApplyModel(object):
    
    def __init__(self):
        self.m_oGroupInfoLst = []
        self.m_oSearchLst = []
        self.m_iSelectedGroupIdx = -1
        self.m_bAscNo = True
        self.m_bAscName = True
        self.m_bAscLv = True
        self.m_bAscAmount = True
        self.m_bAscPride = True

    
    def Clear(self):
        self.m_oGroupInfoLst = []

    
    def SetGroupInfoList(self, lstData):
        '''
\t\t\xb3]\xb8m\xc0\xb0\xac\xa3\xabH\xae\xa7\xa6C\xaa\xed
\t\t:param lstData: \xa6C\xaa\xed\xa1A\xba\xf4\xb5\xb8\xb9L\xa8\xd3\xaa\xba\xc0\xb0\xac\xa3\xabH\xae\xa7\xa6C\xaa\xed, [(id, name, owner, lv, amount, maxamount, flag, desc),(.....)]
\t\t:return:
\t\t'''
        self.m_oGroupInfoLst = []
        self.m_oSearchLst = []
        for tData in lstData:
            oGroupInfo = CGroupInfoModel(tData)
            self.m_oGroupInfoLst.append(oGroupInfo)
        

    
    def GetGroupInfoList(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xc0\xb0\xac\xa3\xabH\xae\xa7\xa6C\xaa\xed
\t\t:return: \xa6C\xaa\xed\xa1A \xa5]\xa7tCGroupInfoModel\xb9\xef\xb6H\xaa\xba\xa6C\xaa\xed
\t\t'''
        if self.m_oSearchLst:
            return self.m_oSearchLst
        
        return self.m_oGroupInfoLst

    () =         self.m_iSelectedGroupIdx = -1
        if not sTxt or len(sTxt) == 0:
            self.m_oSearchLst = None
            return []
        
        self.m_oSearchLst = []
        for oGroupInfo in self.m_oGroupInfoLst:
            if sTxt in oGroupInfo.m_sName:
                self.m_oSearchLst.append(oGroupInfo)
            
            if sTxt in str(oGroupInfo.m_iId):
                self.m_oSearchLst.append(oGroupInfo)
                continue
        
        return self.m_oSearchLst

    SearchGroupInfoLise = None
    
    def SetSelectedGroupIndex(self, iIndex):
        if self.m_oSearchLst:
            if iIndex <= iIndex:
                pass
            elif iIndex < len(self.m_oSearchLst):
                self.m_iSelectedGroupIdx = iIndex
                return None
            
        if iIndex <= iIndex:
            pass
        elif iIndex < len(self.m_oGroupInfoLst):
            self.m_iSelectedGroupIdx = iIndex
        

    
    def GetSelectedGroup(self):
        if self.m_iSelectedGroupIdx == -1:
            return None
        
        if self.m_oSearchLst:
            return self.m_oSearchLst[self.m_iSelectedGroupIdx]
        
        return self.m_oGroupInfoLst[self.m_iSelectedGroupIdx]

    
    def GetGroupInfo(self, iIndex):
        if self.m_oSearchLst:
            if self.m_oSearchLst <= self.m_oSearchLst:
                pass
            elif self.m_oSearchLst < len(self.m_oSearchLst):
                return self.m_oSearchLst[iIndex]
            
        if iIndex <= iIndex:
            pass
        elif iIndex < len(self.m_oGroupInfoLst):
            return self.m_oGroupInfoLst[iIndex]
        

    
    def SortReadyAndActivity(self):
        self.m_oGroupInfoLst = sorted(self.m_oGroupInfoLst, cmp = (lambda oX, oY: cmp(oY.m_iActivity + oY.m_iReady * 100000, oX.m_iActivity + oX.m_iReady * 100000)))

    
    def SortNo(self):
        if self.m_bAscNo:
            self.m_oGroupInfoLst = sorted(self.m_oGroupInfoLst, cmp = (lambda oX, oY: cmp(oX.m_iId, oY.m_iId)))
        else:
            self.m_oGroupInfoLst = sorted(self.m_oGroupInfoLst, cmp = (lambda oX, oY: cmp(oY.m_iId, oX.m_iId)))
        self.m_bAscNo = not (self.m_bAscNo)

    
    def SortName(self):
        if self.m_bAscName:
            self.m_oGroupInfoLst = sorted(self.m_oGroupInfoLst, cmp = (lambda oX, oY: cmp(oX.m_sName, oY.m_sName)))
        else:
            self.m_oGroupInfoLst = sorted(self.m_oGroupInfoLst, cmp = (lambda oX, oY: cmp(oY.m_sName, oX.m_sName)))
        self.m_bAscName = not (self.m_bAscName)

    
    def SortLv(self):
        if self.m_bAscLv:
            self.m_oGroupInfoLst = sorted(self.m_oGroupInfoLst, cmp = (lambda oX, oY: cmp(oX.m_iLv, oY.m_iLv)))
        else:
            self.m_oGroupInfoLst = sorted(self.m_oGroupInfoLst, cmp = (lambda oX, oY: cmp(oY.m_iLv, oX.m_iLv)))
        self.m_bAscLv = not (self.m_bAscLv)

    
    def SortAmount(self):
        if self.m_bAscAmount:
            self.m_oGroupInfoLst = sorted(self.m_oGroupInfoLst, cmp = (lambda oX, oY: cmp(oX.m_iAmount, oY.m_iAmount)))
        else:
            self.m_oGroupInfoLst = sorted(self.m_oGroupInfoLst, cmp = (lambda oX, oY: cmp(oY.m_iAmount, oX.m_iAmount)))
        self.m_bAscAmount = not (self.m_bAscAmount)

    
    def SortPride(self):
        if self.m_bAscPride:
            self.m_oGroupInfoLst = sorted(self.m_oGroupInfoLst, cmp = (lambda oX, oY: cmp(oX.m_iPride, oY.m_iPride)))
        else:
            self.m_oGroupInfoLst = sorted(self.m_oGroupInfoLst, cmp = (lambda oX, oY: cmp(oY.m_iPride, oX.m_iPride)))
        self.m_bAscPride = not (self.m_bAscPride)
