# pycdc 交叉复核产物 · script.fls entry 4774
# co_filename(原始)='script/mxgame/racinggift/view/dlgnewserverrace.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4774.pyc (Python 2.5)

import newserverracedefine
import dgtnewserverrace
import combdialog
import slot
import interface
import ui
import misc
import avatar
g_oNewSeverRaceMain = None

def ModuleReset():
    global g_oNewSeverRaceMain
    g_oNewSeverRaceMain = None


def BuildSubWnd(oParent):
    return CNewServerRaceDlg(oParent)


def Show():
    global g_oNewSeverRaceMain
    g_oNewSeverRaceMain = CNewServerRaceDlg(interface.DialogPanel)


def Hide():
    global g_oNewSeverRaceMain
    g_oNewSeverRaceMain = None


def GetServerRaceClass():
    return CNewServerRaceDlg


class CNewServerRaceDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_OnBtnOpenRankClick = 'OnBtnOpenRankClick()'
    SS_OnBtnPreRewardItemClick = 'SS_OnBtnPreRewardItemClick'
    SS_OnBtnGetRewardItemClick = 'SS_OnBtnGetRewardItemClick'
    Preview_Reward_Num = 6
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/new_player_present/racing/racing_main.dlg')
        self.ssInit()
        self.m_DelegateList = []
        self.oRaceItemList = []
        self.m_oPreviewRewardList = []
        self.InitDelegate()
        self.SetIgnoreEsc(True)
        self.m_oTimer = None

    
    def InitDelegate(self):
        self.m_DelegateList = [
            dgtnewserverrace.CNewServerRaceDgt(self)]

    
    def SetActive(self, bShow):
        self.SetShow(bShow)

    
    def InitPreviewReward(self):
        pass

    
    def OnPreviewItemClick(self, iType, iStage):
        self.ssEmit(self.SS_OnBtnPreRewardItemClick, iType, iStage)

    
    def OnGetItemClick(self, iType, iStage):
        self.ssEmit(self.SS_OnBtnGetRewardItemClick, iType, iStage)

    
    def InitRaceList(self, dRaceDataLst):
        for iType, dRaceData in dRaceDataLst.iteritems():
            oRaceListItem = CRaceListItem(self.GetObject('loc_racing%d' % iType), iType, misc.Functor(self.OnBtnOpenRankClick))
            oRaceListItem.InitStepText(dRaceData)
            self.oRaceItemList.append(oRaceListItem)
        

    
    def UpdateRaceList(self, dRaceDatas):
        for dRaceData in dRaceDatas:
            if dRaceData['iRaceType'] - 1 < len(self.oRaceItemList):
                oRaceListItem = self.oRaceItemList[dRaceData['iRaceType'] - 1]
                oRaceListItem.SetData(dRaceData)
                continue
        

    
    def SetEndTime(self, iTime):
        import dlgdouble12shop
        if iTime > 0:
            self.m_oTimer = dlgdouble12shop.CCountdown(self.GetObject('txt_time'), iTime, 1)
        else:
            self.m_oTimer = None
            self.GetObject('txt_time').SetText('\xac\xa1\xb0\xca\xb5\xb2\xa7\xf4')

    
    def CloseWindow(self):
        global g_oNewSeverRaceMain
        g_oNewSeverRaceMain = None

    
    def OnBtnOpenRankClick(self, iRaceType):
        self.ssEmit(self.SS_OnBtnOpenRankClick, iRaceType)

    
    def OnMessage(self, iMsg):
        pass



class CRaceListItem(combdialog.CCombSubWnd):
    REWARD_STEP_NUM = 5
    
    def __init__(self, oParent, iRaceType, OnClickRankCallBack):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/new_player_present/racing/racing_listitem.dlg')
        self.m_iRaceType = iRaceType
        self.m_iCurSum = 0
        self.m_dRaceData = { }
        self.m_OnClickRankCallBack = OnClickRankCallBack
        self.m_oPreviewItem = None
        self.m_oIcon = None
        self.m_dStepData = []
        combdialog = None
        self.m_oGetItemLst = None
        self.m_oTips = None
        self.m_FlashObj = None
        self.SetIgnoreEsc(True)
        self.Init()

    
    def Init(self):
        self.GetObject('tips_rancing').SetTips(newserverracedefine.TYPE2TIPS.get(self.m_iRaceType, ''))
        self.GetObject('txt_racingname').SetText(newserverracedefine.TYPE2TITLE.get(self.m_iRaceType, ''))
        self.m_oPreviewItem = CPreviewItem(self, self.m_iRaceType, 0, misc.Functor(self.GetParent().GetParent().OnPreviewItemClick))
        self.UpdatePreviewReward(1)

    
    def UpdatePreviewReward(self, idx):
        '''
\t\t:param idx:\xa4U\xbc\xd0\xb1q1\xb6}\xa9l
\t\t:return:
\t\t'''
        (x, y) = self.GetObject('loc_step%d' % idx).GetPos()
        (w, h) = self.GetObject('loc_step%d' % idx).GetSize()
        if self.m_oPreviewItem:
            self.m_oPreviewItem.SetPos(x, y - h)
        

    
    def UpdateIconPos(self, idx):
        self.m_oIcon = avatar.CreateSmallHeroAvatarPhoto(self.GetObject('loc_step%d' % idx), 1)
        interface.Center(self.m_oIcon)

    
    def UpdateSumText(self):
        self.GetObject('txt_num').SetText('\xb7\xed\xabe:' + str(self.m_iCurSum) + newserverracedefine.TYPE2SIGN.get(self.m_iRaceType, ''))

    
    def SetData(self, dRaceData):
        self.m_dRaceData = dRaceData
        self.m_iCurSum = dRaceData['iCurSum']
        self.UpdateCurSum()
        self.UpdateStepColor()
        self.RefreshGetIcon()
        self.UpdateStepColor()

    
    def RefreshGetIcon(self):
        self.m_oGetItemLst = []
        for idx in range(1, self.REWARD_STEP_NUM + 1):
            if idx in self.m_dRaceData['iRewardList']:
                oGetItem = CPreviewItem(self, self.m_iRaceType, idx, misc.Functor(self.GetParent().GetParent().OnGetItemClick))
                (x, y) = self.GetObject('loc_step%d' % idx).GetPos()
                (w, h) = self.GetObject('loc_step%d' % idx).GetSize()
                oGetItem.SetPos(x, y - h)
                oGetItem.InitIcon(True)
                oGetItem.SetFlash(True)
                import m_oGetItemLst(oGetItem)
                continue
        

    
    def UpdateCurSum(self):
        self.UpdateSumText()
        self.UpdatePlayerIconPos()

    
    def InitStepText(self, dStepData):
        self.m_dStepData = dStepData
        for idx in range(self.REWARD_STEP_NUM):
            iNeed = dStepData[idx]['iLevel']
            None(self.GetObject('txt_step%d' % (idx + 1)).SetText if iNeed >= 10000 else str(iNeed) + newserverracedefine.TYPE2SIGN.get(self.m_iRaceType, ''))
        

    
    def GetStepNeedByIdx(self, idx):
        return self.m_dStepData[idx]['iLevel']

    
    def UpdatePlayerIconPos(self):
        if self.m_iCurSum >= self.GetStepNeedByIdx(self.REWARD_STEP_NUM - 1):
            self.m_oPreviewItem = None
            return None
        
        iIdx = 0
        for idx in range(0, self.REWARD_STEP_NUM):
            iIdx += 1
            if self.m_iCurSum < self.GetStepNeedByIdx(idx):
                break
                continue
        
        self.UpdatePreviewReward(iIdx)
        self.UpdateIconPos(iIdx - 1)

    
    def UpdateStepColor(self):
        '''
\t\t\xb9F\xa8\xec\xadn\xa8D\xaa\xba\xae\xe6\xa4l\xb3]\xb8m\xac\xb0\xb6\xc0\xa6\xe2
\t\t:return:
\t\t'''
        for idx in range(0, self.REWARD_STEP_NUM):
            self.GetObject('img_finish%d' % (idx + 1)).SetShow(self.m_iCurSum >= self.GetStepNeedByIdx(idx))
        

    
    def OnBtnRankClick(self):
        if self.m_OnClickRankCallBack:
            self.m_OnClickRankCallBack(self.m_iRaceType)
        

    
    def OnMessage(self, iMsg):
        if iMsg == 1:
            self.OnBtnRankClick()
        



class CPreviewItem(combdialog.CCombSubWnd):
    
    def __init__(self, oParent, iRaceType, iStage, oLeftUpCB):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/new_player_present/racing/racing_previewitem.dlg')
        self.m_iRewardStage = iStage
        self.m_iRaceType = iRaceType
        self.m_oIcon = None
        self.m_oLeftUpCB = oLeftUpCB
        self.m_oFlashItem = None
        self.InitIcon()
        self.SetIgnoreEsc(True)

    
    def InitIcon(self, bLock = False):
        
        try:
            if bLock:
                self.m_oIcon = ui.CImage(self.GetObject('loc_item'), 'item44/73491.png', 'item')
            else:
                self.m_oIcon = ui.CImage(self.GetObject('loc_item'), 'item44/73492.png', 'item')
        except:
            pass


    
    def SetFlash(self, bFlash):
        if bFlash:
            (w, h) = self.GetObject('loc_item').GetSize()
            flashObj = interface.CStretchSpriteObject(self.GetObject('loc_item'), 'item44/select.spr', 'item')
            (w1, h1) = flashObj.GetSize()
            flashObj.SetPos(w / 2, h / 2)
            flashObj.SetZ(2)
            flashObj.SetScale(float(w) / w1)
            flashObj.CreateCommand(1, 'animation')
        else:
            flashObj = None
        self.m_FlashObj = flashObj

    
    def LeftUp(self):
        self.m_oLeftUpCB(self.m_iRaceType, self.m_iRewardStage)

    
    def LeftDown(self):
        pass
