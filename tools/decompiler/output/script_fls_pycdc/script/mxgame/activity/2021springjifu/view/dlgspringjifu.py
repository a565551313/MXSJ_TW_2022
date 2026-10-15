# pycdc 交叉复核产物 · script.fls entry 53
# co_filename(原始)='script/mxgame/activity/2021springjifu/view/dlgspringjifu.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_53.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/1/12 19:35
\xd7\xf7\xd5\xdf: lzj
\xce\xc4\xbc\xfe: dlgspringjifu
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import interface
import permission
import misc
import slot
import timer
import ui
import usermacro
import wrapinterface
BLESSING_BAG_SHAPE = 73746
TITLE_SHAPE = 73745

def ShowSpringJiFuDlg():
    CSpringJiFuDlg.OpenUI()


def CloseSpringJiFuDlg():
    CSpringJiFuDlg.CloseUI()


def GetSpringJiFuDlg():
    return CSpringJiFuDlg.GetUI()


class CSpringJiFuDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    dOpenUIConfig = {
        'KEY_IS_IGNORE_ESC': True }
    SS_ClickReward = 'SS_ClickReward(iRewardID)'
    SS_AniEnd = 'SS_AniEnd()'
    SS_ClickDrawLottery = 'SS_ClickDrawLottery()'
    SS_OpenDlg = 'SS_OpenDlg()'
    SS_ClearRedDot = 'SS_ClearRedDot()'
    sUIName = 'dialog4/activity/2021Spring/jifu_main.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.ssInit()
        self.SetIgnoreEsc(True)
        self.m_DelegateList = []
        self.m_oTableViewPart = None
        self.m_oBlessingBag = None
        self.m_oTitle = None
        self.m_oHighLine = None
        self.m_oAniBackGround = None
        self.m_oTimer = None
        self.m_iTime = 1
        self.m_iTick = 1
        self.m_fDelayTime = 0.1
        self.InitTableView()
        self.InitDlg()
        self.InitDelegate()
        self.ssEmit(self.SS_OpenDlg)

    
    def InitDelegate(self):
        import dgtspringjifu
        self.m_DelegateList = [
            dgtspringjifu.CSpringJiFuDgt(self)]

    
    def InitTableView(self):
        self.m_oTableViewPart = CTbViewPart(self.GetTableView(), misc.Functor(self.ClickReward))

    
    def SetActive(self, bActive):
        self.SetShow(bActive)
        self.SetShowObject('spr_shine3', False)
        if bActive:
            self.ssEmit(self.SS_ClearRedDot)
        

    
    def GetTableView(self):
        return self.GetObject('tbview_item')

    
    def InitDlg(self):
        self.SetShowObject('img_finish1', False)
        self.SetShowObject('img_finish2', False)
        self.SetShowObject('spr_shine1', False)
        self.SetShowObject('spr_shine2', False)
        self.SetShowObject('spr_shine3', False)
        self.GetObject('btn_done1').SetClickNotSetFrame(True)
        self.GetObject('btn_done2').SetClickNotSetFrame(True)
        self.m_oHighLine = self.GetObject('spr_shine3')
        self.m_oAniBackGround = self.GetObject('loc_dft')
        self.m_oHighLine.SetShow(False)
        self.m_oBlessingBag = CRewardItemIcon(self.GetObject('loc_item2'), BLESSING_BAG_SHAPE, 1, 3001, misc.Functor(self.ClickReward))
        self.m_oTitle = CRewardItemIcon(self.GetObject('loc_item1'), TITLE_SHAPE, 1, 1202, misc.Functor(self.ClickReward))

    
    def UpdateTableView(self, dItemInfoList):
        dItemInfoList = misc.DeepCopy(dItemInfoList)
        self.GetTableView().SetDataSource(dItemInfoList)
        self.GetTableView().Reload()

    
    def RefreshDlg(self, iDailyLogin, iDailyTYF, iFokaAmount, iTicketAmount, iActive, iCharge, iActiveLimit, iChargeLimit, iBlessingBag, iTitleReward):
        self.GetObject('btn_done1').SetSelect(iDailyLogin)
        self.GetObject('btn_done2').SetSelect(iDailyTYF)
        self.GetObject('text_chance').ReplaceText({
            '$num1': str(iTicketAmount) })
        self.GetObject('text_samenum').ReplaceText({
            '$num2': str(iFokaAmount) })
        self.GetObject('text_progress1').SetText('%s/%s' % (iActive, iActiveLimit))
        self.GetObject('text_progress2').SetText('%s/%s' % (iCharge, iChargeLimit))
        self.SetShowObject('spr_shine1', iTitleReward == 1)
        self.SetShowObject('spr_shine2', iBlessingBag == 1)
        self.SetShowObject('img_finish1', iTitleReward == 2)
        self.SetShowObject('img_finish2', iBlessingBag == 2)

    
    def ShowDrawAni(self, iRewardTarget, iTicketAmount):
        self.SetShowObject('spr_shine3', True)
        self.ReleaseTimer()
        self.Capture(0)
        self.Capture(1, 1)
        self.m_iTick = 1
        self.m_iTime = 1
        self.m_fDelayTime = round(3 / (25 + iRewardTarget), 2)
        if iTicketAmount >= 5:
            self.m_fDelayTime /= 2
        
        self.m_oTimer = timer.Timer(self.m_fDelayTime, misc.Functor(self.RewardRunningTimer, iRewardTarget), iRepeat = -1, oRelayObj = self)

    
    def RewardRunningTimer(self, iRewardTarget):
        if self.m_iTime > 0:
            self.AniRunning(self.m_iTick)
        else:
            self.AniRunning(self.m_iTick)
            if self.m_iTick == iRewardTarget:
                self.AniEnd(iRewardTarget)
                return None
            
        self.m_iTick += 1

    
    def AniRunning(self, iTarget):
        (iX, iY) = self.m_oAniBackGround.GetArryPosByIdx(iTarget - 1)
        self.m_oHighLine.SetPos(iX + 27, iY + 27)

    
    def AniEnd(self, iRewardTarget):
        self.SetShow(False)
        self.Capture(0)
        self.SetShow(True)
        self.ReleaseTimer()
        self.ssEmit(self.SS_AniEnd, iRewardTarget)

    
    def ReleaseTimer(self):
        if self.m_oTimer:
            self.m_oTimer.Release()
            self.m_oTimer = None
        

    
    def ClickReward(self, iRewardID):
        self.ssEmit(self.SS_ClickReward, iRewardID)

    
    def OnEditMessage(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_ClickDrawLottery)
        

    
    def OnMessage(self, iMsgID):
        self.OnEditMessage(iMsgID)



class CTbViewPart(object):
    '''
\t\xb4_\xa5\xce\xaa\xed\xae\xe6\xaa\xba\xaa\xed\xb2{\xb2\xd5\xa5\xf3
\t'''
    
    def __init__(self, oTbview, oClickCB):
        self.m_oTbview = oTbview
        self.m_oClickCB = oClickCB
        self.m_oTbview.SetAutoHideScrollBar(True)
        self.m_oTbview.SetShowRowLine(False)
        self.InitTableView()

    
    def GetTbAllView(self):
        return self.m_oTbview

    
    def InitTableView(self):
        self.GetTbAllView().SetDelegateNewCellOfData(misc.Functor(self.OnDelegateNewCellOfData))
        self.GetTbAllView().SetDelegateUpdateCellOfData(misc.Functor(self.OnDelegateUpdateCellOfData))
        self.GetTbAllView().SetDelegateAlignOfData(misc.Functor(self.OnDelegateAlignOfData))
        self.GetTbAllView().SetDelegateIdentifierOfData(misc.Functor(self.OnDelegateIdentifierOfData))

    
    def OnDelegateNewCellOfData(self, oParent, dData):
        sFokaType = dData['sType']
        if sFokaType == '0':
            oCell = CRewardItem(oParent, self.m_oClickCB)
        elif sFokaType == '2':
            oCell = CFokaItem(oParent)
        else:
            oCell = CDefaultFoka(oParent)
        oCell.SetItemInfo(dData)
        return oCell

    
    def OnDelegateUpdateCellOfData(self, oCell, dData, bReUes):
        if bReUes:
            oCell.SetItemInfo(dData)
        

    
    def OnDelegateIdentifierOfData(self, dData):
        return dData['sType']

    
    def OnDelegateAlignOfData(self, data):
        return interface.ALIGN_CENTER_MIDDLE



class CRewardItem(combdialog.CCombSubWnd):
    sUIName = 'dialog4/activity/2021Spring/jifu_item2.dlg'
    dOpenUIConfig = {
        'KEY_IS_IGNORE_ESC': True }
    
    def __init__(self, oParent, oClickCB):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.m_oItemIcon = None
        self.m_oItemTips = None
        self.m_bLiuguangShow = False
        self.m_bAngleMarkShow = False
        self.m_iRewardID = 0
        self.m_iState = 0
        self.m_oClickCB = oClickCB
        self.SetIgnoreEsc(True)
        self.InitDlg()

    
    def InitDlg(self):
        self.SetAngleMarkShow(self.m_bAngleMarkShow)
        self.SetLiuguangShow(self.m_bLiuguangShow)

    
    def SetItemIcon(self, iShape, iNum, iState, iRewardID):
        self.m_iState = iState
        self.m_iRewardID = iRewardID
        self.SetLiuguangShow(iState == 1)
        self.SetAngleMarkShow(iState == 2)
        self.m_oItemIcon = CRewardItemIcon(self.GetObject('loc_reward'), iShape, iNum, iRewardID, misc.Functor(self.OnClickReward))

    
    def SetLiuguangShow(self, bShow):
        self.m_bAngleMarkShow = bShow
        self.SetShowObject('spr_shine1', bShow)

    
    def SetAngleMarkShow(self, bShow):
        self.m_bLiuguangShow = bShow
        self.SetShowObject('img_finish', bShow)

    
    def OnClickReward(self, iReward):
        if self.m_iState == 0:
            usermacro.PROMPT_MSG('\xbb\xdd\xadn\xb6\xb0\xbb\xf4\xa4@\xb1\xf8\xbe\xee\xbdu\xa1B\xbd\xdd\xbdu\xa9\xce\xb9\xef\xa8\xa4\xbdu\xa5i\xbb\xe2\xa8\xfa\xb9\xef\xc0\xb3\xbc\xfa\xc0y')
            return None
        
        self.m_oClickCB(iReward)

    
    def SetItemInfo(self, dData):
        iShape = dData['iShape']
        iNum = dData['iNum']
        iState = dData.get('iState', 0)
        iRewardID = dData['iID']
        self.SetItemIcon(iShape, iNum, iState, iRewardID)



class CFokaItem(combdialog.CCombSubWnd):
    sUIName = 'dialog4/activity/2021Spring/jifu_item3.dlg'
    dOpenUIConfig = {
        'KEY_IS_IGNORE_ESC': True }
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.m_oIcon = None
        self.SetIgnoreEsc(True)

    
    def SetIcon(self, sPath):
        m_oIcon = self

    
    def SetItemInfo(self, dData):
        sPath = dData['sPath']
        self.SetIcon(sPath)



class CDefaultFoka(combdialog.CCombSubWnd):
    sUIName = 'dialog4/activity/2021Spring/jifu_item1.dlg'
    dOpenUIConfig = {
        'KEY_IS_IGNORE_ESC': True }
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.SetIgnoreEsc(True)

    
    def SetItemInfo(self, dData):
        pass



class CRewardItemIcon(wrapinterface.CItemIcon):
    
    def __init__(self, oParent, iShape, iQuantity, iRewardID, oClickCB):
        wrapinterface.CItemIcon.__init__(self, oParent, iShape, iQuantity, iRewardID)
        self.m_oClickCB = oClickCB
        self.m_iRewardID = iRewardID
        self.m_oItemTips = None

    
    def Leave(self):
        wrapinterface.CItemIcon.Leave(self)
        self.m_oItemTips = None

    
    def Enter(self):
        wrapinterface.CItemIcon.Enter(self)
        self.m_oItemTips = wrapinterface.CItemTips(self.m_Shape, self.m_Path, self.m_Name, self.m_Info, self.m_InfoExt, charcount = 32)

    
    def LeftUp(self):
        wrapinterface.CItemIcon.LeftUp(self)
        if self.m_oClickCB:
            self.m_oClickCB(self.m_iRewardID)
        

    
    def LeftDown(self):
        wrapinterface.CItemIcon.LeftDown(self)
