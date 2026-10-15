# pycdc 交叉复核产物 · script.fls entry 344
# co_filename(原始)='script/mxgame/avatar/mdavatar.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_344.pyc (Python 2.5)

import slot
g_AvatarModel = None
g_TestFlag = None

def IsTest():
    return True


def ModuleReset():
    global g_AvatarModel
    g_AvatarModel = None


def GetAvatarModel():
    ''':rtype: CAvatarModel'''
    global g_AvatarModel
    if not g_AvatarModel:
        g_AvatarModel = CAvatarModel()
    
    return g_AvatarModel


class CAvatarModel(slot.ISignalSubject):
    SS_StowIntListChange = 'SS_StowIntListChange(lStowIntList)'
    SS_PriceChange = 'SS_PriceChange(iPrice)'
    SS_OpenChildrenStyle = 'SS_OpenChildrenStyle()'
    SS_OpenChristmasStyle = 'SS_OpenChristmasStyle()'
    SS_PhotoChange = 'SS_PhotoChange()'
    SS_TimeLimitChange = 'SS_TimeLimitChange(iTime)'
    SS_SetIsExperience = 'SS_SetIsExperience(bIsExperience, iItemID, iModel)'
    SS_AIAvatarChg = 'SS_AIAvatarChg()'
    SS_ImitateAvatar = 'SS_RefreshPhotoView(iPhotoList, dPhotoDesc)'
    
    def __init__(self):
        self.ssInit()
        self.m_lStowIntList = []
        self.m_dPhotoPrice = {
            '\xac\x82old': 0,
            'iPoint': 0 }
        self.m_bCanOtherPay = False
        self.m_iTimeLimit = 90
        self.m_bIsExperience = False
        self.m_iAIAvatarList = []
        self.m_bOpenChildren = False
        self.m_bOpenChristmas = False
        self.m_bCopy = False
        self.m_iPhotoList = []
        self.m_iOtherSex = 1
        self.m_iStyle = 0

    
    def SetStowIntList(self, lStowIntList):
        import copy
        self.m_lStowIntList = []
        for tPhotoIntList in lStowIntList:
            (iPhotoIntList, dPhotoDesc) = tPhotoIntList
            if iPhotoIntList[0] == 0 and iPhotoIntList[1] == 0 and iPhotoIntList[2] == 0 and iPhotoIntList[3] == 0:
                continue
            
            self.m_lStowIntList.append(tPhotoIntList)
        
        self.ssEmit(self.SS_StowIntListChange, copy.deepcopy(self.m_lStowIntList))

    
    def GetStowIntList(self):
        import copy
        return copy.deepcopy(self.m_lStowIntList)

    
    def RefreshImitateAvatar(self, iPhotoList, dPhotoDesc):
        self.ssEmit(self.SS_ImitateAvatar, iPhotoList, dPhotoDesc)

    
    def SetLogData(self, iPhotoList, iOtherSex, \xf7\xcd\xea\xe7le):
        self.m_bCopy = True
        self.m_iPhotoList = iPhotoList
        self.m_iOtherSex = iOtherSex
        self.m_iStyle = \xf7\xcd\xea\xe7le

    
    def SetIsCopy(self, bCopy):
        self.m_bCopy = bCopy

    
    def GetIsCopy(self):
        return self.m_bCopy

    
    def GetCopyPhotoList(self):
        return self.m_iPhotoList

    
    def GetCopySex(self):
        return self.m_iOtherSex

    
    def GetCopyStyle(self):
        return self.m_iStyle

    
    def SetPhotoPrice(self, \xac\x82old, iPoint):
        self.m_dPhotoPrice['\xac\x82old'] = \xac\x82old
        self.m_dPhotoPrice['iPoint'] = iPoint
        self.ssEmit(self.SS_PriceChange, \xac\x82old, iPoint)

    
    def GetPhotoPrice(self):
        return self.m_dPhotoPrice

    
    def ResetSpecialFlag(self):
        self.m_bOpenChildren = False
        self.m_bOpenChristmas = False

    
    def SetOpenChildren(self):
        self.m_bOpenChildren = True
        self.ssEmit(self.SS_OpenChildrenStyle)

    
    def GetOpenChildren(self):
        return self.m_bOpenChildren

    
    def SetOpenChristmas(self):
        self.m_bOpenChristmas = True
        self.ssEmit(self.SS_OpenChristmasStyle)

    
    def GetOpenChristmas(self):
        return self.m_bOpenChristmas

    
    def SetIsCanOtherPay(self, bCan):
        self.m_bCanOtherPay = bCan

    
    def IsCanOtherPay(self):
        return self.m_bCanOtherPay

    
    def SetPhotoChange(self):
        self.ssEmit(self.SS_PhotoChange)

    
    def SetTimeLimit(self, iDay):
        self.ssEmit(self.SS_TimeLimitChange, iDay)

    
    def SetExperience(self, bFlag, iItemID, iModel):
        self.ssEmit(self.SS_SetIsExperience, bFlag, iItemID, iModel)

    
    def SetAIList(self, iAIList):
        self.m_iAIAvatarList = iAIList
        self.ssEmit(self.SS_AIAvatarChg)

    
    def GetAIList(self):
        return self.m_iAIAvatarList
