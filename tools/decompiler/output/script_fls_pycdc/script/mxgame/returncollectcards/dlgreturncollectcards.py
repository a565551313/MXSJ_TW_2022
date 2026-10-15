# pycdc 交叉复核产物 · script.fls entry 3808
# co_filename(原始)='script/mxgame/returncollectcards/dlgreturncollectcards.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3808.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/5/17 16:13
\xd7\xf7\xd5\xdf: 
\xce\xc4\xbc\xfe: dlgreturncollectcards
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import slot
import misc
import interface
import item
import wrapinterface
import returncollectcardsdefines
import usermacro
import timer
import showlogic_dlgreturncollectcards
import newschedulecom
import pagedlgbase

class CReturnCollectCardsDlg(combdialog.CCombSubWnd, slot.ISignalSubject, pagedlgbase.COnePageDlgBase):
    dOpenUIConfig = {
        'KEY_IS_IGNORE_ESC': True }
    SS_ClickRewardCard = 'SS_ClickRewardCard(iRewardID, iState)'
    SS_ClickBigRewardCard = 'SS_ClickBigRewardCard(iRewardID)'
    SS_ClickFrontCard = 'SS_ClickFrontCard(iMapID, iType)'
    SS_AniEnd = 'SS_AniEnd()'
    SS_ClickLotteryBtn = 'SS_ClickLotteryBtn()'
    SS_ClickCloseAniBtn = 'SS_ClickCloseAniBtn()'
    sUIName = 'dialog4/returnreward/huigui_jika.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent)
        pagedlgbase.COnePageDlgBase.__init__(self)
        self.ssInit()
        self.m_oRewardTableView = None
        self.m_iPlayAniCount = 0
        self.m_iTick = 1
        self.m_oTimer = None
        self.m_oBigRewardIcon = None
        self.m_fDelayTime = 0.1
        self.m_DelegateList = []
        self.InitDlg()
        self.InitDelegate()

    
    def VOpenPage(self, dExtend = None):
        self.ssEmit(self.SS_OpenDlg, dExtend)

    
    def VClose(self):
        self.ssEmit(self.SS_CloseDlg)

    
    def InitDlg(self):
        self.GetObject('spr_shine1').SetShow(False)
        self.GetObject('btn_guanb1').SetClickNotSetFrame(True)
        self.GetObject('btn_guanb3').SetClickNotSetFrame(True)
        self.GetObject('btn_guanb5').SetClickNotSetFrame(True)
        (iX, iY) = self.GetObject('loc_djiangli').GetPos()
        self.m_oBigRewardIcon = wrapinterface.CItemIcon(self, returncollectcardsdefines.BIG_REWARD_SHAPE, 1, 9)
        self.m_oBigRewardIcon.SetPos(iX, iY)
        self.m_oBigRewardIcon.SetEnterCB(misc.Functor(self.m_oBigRewardIcon.ShowTips))
        self.m_oBigRewardIcon.SetLeaveCB(misc.Functor(self.m_oBigRewardIcon.HideTips))
        self.InitTableView()

    
    def InitTableView(self):
        self.m_oRewardTableView = CTbViewPart(misc.WeakRef(self.GetObject('tbview_jiangli')), misc.Functor(self.ClickReward), misc.Functor(self.ClickFrontCardCB))

    
    def InitShowLogic(self):
        self.m_oShowLogic = showlogic_dlgreturncollectcards.CDgtReturnCollectCardLogic(self)

    
    def InitDelegate(self):
        import dgtreturncollectcards
        self.m_DelegateList = [
            dgtreturncollectcards.CReturnCollectCardsDgt(self)]

    
    def RefreshRightRegionView(self, dDlgShowInfo):
        self.GetObject('btn_guanb1').SetSelect(dDlgShowInfo['bLogin'])
        self.GetObject('rtxt_cishu5').SetText(dDlgShowInfo['sLoginCountText'])
        self.GetObject('btn_guanb3').SetSelect(dDlgShowInfo['bHuoyue100'])
        self.GetObject('rtxt_cishu6').SetText(dDlgShowInfo['sHuoyue100CountText'])
        self.GetObject('btn_guanb5').SetSelect(dDlgShowInfo['bHuoyue200'])
        self.GetObject('rtxt_cishu7').SetText(dDlgShowInfo['sHuoyue200CountText'])
        self.GetObject('rtxt_cishu8').SetText(dDlgShowInfo['sChargeCountText'])
        self.GetObject('rtxt_shengyu1').SetText(str(dDlgShowInfo['iDrawCardCount']))
        self.GetObject('rtxt_shengyu2').SetText(str(dDlgShowInfo['iRepeatCardsNum']))
        self.SetShowObject('img_finish1', dDlgShowInfo['iMysticalRewardState'] == returncollectcardsdefines.CARD_STATE_HAVERECEIVE)
        self.SetShowObject('spr_shine2', dDlgShowInfo['iMysticalRewardState'] == returncollectcardsdefines.CARD_STATE_CANRECEIVE)

    
    def UpdateTableView(self, dItemInfoList):
        dItemInfoList = misc.DeepCopy(dItemInfoList)
        self.m_oRewardTableView.RefreshRewardTableView(dItemInfoList)

    
    def ShowLotteryDrawAni(self, iRewardTarget, lCardState, bGuarantee):
        self.SetShowObject('spr_shine1', True)
        self.ReleaseTimer()
        self.SafeCapture(True)
        self.m_iTick = 1
        self.m_iPlayAniCount = 0
        self.m_fDelayTime = round(2 / (returncollectcardsdefines.BOX_NUM + iRewardTarget), 2)
        if bGuarantee:
            oFunc = misc.Functor(misc.Functor(self.PlayNormolGuaranteeAni, iRewardTarget, lCardState))
        else:
            oFunc = misc.Functor(misc.Functor(self.PlayNormolAni, iRewardTarget))
        self.m_oTimer = timer.Timer(self.m_fDelayTime, oFunc, iRepeat = -1, oRelayObj = self)

    
    def PlayNormolAni(self, iRewardTarget):
        '''
\t\t\xa5\xbf\xb1`\xb3t\xab\xd7\xbc\xbd\xa9\xf1\xb0\xca\xb5e
\t\t:param iRewardTarget: \xa5\xd8\xbc\xd0
\t\t'''
        self.AniRunning(self.m_iTick)
        self.m_iTick += 1
        if self.m_iTick > returncollectcardsdefines.BOX_NUM:
            self.m_iTick = 1
        
        if self.m_iTick == (iRewardTarget + returncollectcardsdefines.BOX_NUM) / 2:
            self.ReleaseTimer()
            self.m_fDelayTime *= 2
            oFunc = misc.Functor(self.PlaySlowDownAni, iRewardTarget)
            self.m_oTimer = timer.Timer(self.m_fDelayTime, oFunc, iRepeat = -1, oRelayObj = self)
            return None
        

    
    def PlaySlowDownAni(self, iRewardTarget):
        '''
\t\t\xb4\xee\xb3t\xbc\xbd\xa9\xf1\xb0\xca\xb5e
\t\t'''
        self.AniRunning(self.m_iTick)
        self.m_iTick += 1
        if self.m_iTick > returncollectcardsdefines.BOX_NUM:
            self.m_iTick = 1
        
        if self.m_iTick == iRewardTarget:
            self.AniEnd(iRewardTarget)
            return None
        

    
    def PlayNormolGuaranteeAni(self, iRewardTarget, lCardState):
        '''
\t\t\xa5\xbf\xb1`\xb3t\xab\xd7\xbc\xbd\xa9\xf1\xabO\xa9\xb3\xb0\xca\xb5e
\t\t'''
        self.m_iPlayAniCount += 1
        iTick = self.GetRecentBackCardTick(lCardState)
        self.AniRunning(iTick)
        iTick += 1
        if iTick > returncollectcardsdefines.BOX_NUM:
            iTick = 1
        
        self.m_iTick = iTick
        if self.m_iPlayAniCount == returncollectcardsdefines.GUARANTEE_ANI_SLOW_COUNT:
            self.ReleaseTimer()
            self.m_fDelayTime *= 2
            oFunc = misc.Functor(self.PlaySlowDownGuaranteeAni, iRewardTarget, lCardState)
            self.m_oTimer = timer.Timer(self.m_fDelayTime, oFunc, iRepeat = -1, oRelayObj = self)
            return None
        

    
    def PlaySlowDownGuaranteeAni(self, iRewardTarget, lCardState):
        '''
\t\t\xb4\xee\xb3t\xbc\xbd\xa9\xf1\xabO\xa9\xb3\xb0\xca\xb5e
\t\t'''
        iTick = self.GetRecentBackCardTick(lCardState)
        self.AniRunning(iTick)
        iTick += 1
        if iTick > returncollectcardsdefines.BOX_NUM:
            iTick = 1
        
        self.m_iTick = iTick
        if iTick == iRewardTarget:
            self.AniEnd(iRewardTarget)
            return None
        

    
    def GetRecentBackCardTick(self, lCardState):
        '''
\t\t\xc0\xf2\xa8\xfa\xa4U\xa4@\xadB"];`;+<\xd8< 4\xf55h4I-A
\t\t:param lCardState:
\t\t:return:
\t\t'''
        iTick = self.m_iTick
        for _ in xrange(1, returncollectcardsdefines.BOX_NUM + 1):
            iState = lCardState[iTick - 1]
            if iState == returncollectcardsdefines.CARD_TYPE_BACK:
                return iTick
            
            iTick += 1
            if iTick > returncollectcardsdefines.BOX_NUM:
                iTick = 1
                continue
        
        return iTick

    
    def AniRunning(self, iTarget):
        (iX, iY) = self.GetObject('loc_tujian').GetArryPosByIdx(iTarget - 1)
        self.GetObject('spr_shine1').SetPos(iX + 27, iY + 27)

    
    def AniEnd(self, iRewardTarget):
        self.SafeCapture(False)
        self.ReleaseTimer()
        self.ssEmit(self.SS_AniEnd, iRewardTarget)

    
    def ReleaseTimer(self):
        if self.m_oTimer:
            self.m_oTimer.Release()
            self.m_oTimer = None
        

    
    def DirectLottery(self, iRewardTarget):
        '''
\t\t\xa4\xa3\xbc\xbd\xa9\xf1\xb0\xca\xb5e\xaa\xbd\xb1\xb5\xa9\xe2\xbc\xfa
\t\t:param iRewardTarget:
\t\t:return:
\t\t'''
        self.SetShowObject('spr_shine1', True)
        self.AniRunning(iRewardTarget)
        self.ssEmit(self.SS_AniEnd, iRewardTarget)

    
    def SetPlayAniSelect(self, bSelect):
        self.GetObject('btn_guanbi').SetSelect(bSelect)

    
    def ClickReward(self, iRewardID, iState):
        self.ssEmit(self.SS_ClickRewardCard, iRewardID, iState)

    
    def ClickBigReward(self):
        self.ssEmit(self.SS_ClickBigRewardCard)

    
    def ClickFrontCardCB(self, iMapID):
        self.ssEmit(self.SS_ClickFrontCard, iMapID, returncollectcardsdefines.CLICK_OPEN_CARDDLG)

    
    def OnClickLotteryBtn(self):
        if not self.m_oTimer:
            self.ssEmit(self.SS_ClickLotteryBtn)
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.OnClickLotteryBtn()
        elif iMsgID == 5:
            self.ssEmit(self.SS_ClickCloseAniBtn)
        elif iMsgID == 9:
            self.ClickBigReward()
        



class CTbViewPart(object):
    '''
\t\xb4_\xa5\xce\xaa\xed\xae\xe6\xaa\xba\xaa\xed\xb2{\xb2\xd5\xa5\xf3
\t'''
    
    def __init__(self, oWeakTbView, oClickRewardCB, oFrontCardCB):
        self.m_oClickRewardCB = oClickRewardCB
        self.m_oFrontCardCB = oFrontCardCB
        self.m_oTableView = oWeakTbView
        self.InitTableView()

    
    def InitTableView(self):
        oTableView = self.m_oTableView.Get()
        oTableView.SetAutoHideScrollBar(True)
        oTableView.SetShowRowLine(False)
        oTableView.SetDelegateNewCellOfData(misc.Functor(self.OnDelegateNewCellOfData))
        oTableView.SetDelegateUpdateCellOfData(misc.Functor(self.OnDelegateUpdateCellOfData))
        oTableView.SetDelegateAlignOfData(misc.Functor(self.OnDelegateAlignOfData))
        oTableView.SetDelegateIdentifierOfData(misc.Functor(self.OnDelegateIdentifierOfData))

    
    def RefreshRewardTableView(self, dItemInfoList):
        oTableView = self.m_oTableView.Get()
        oTableView.SetDataSource(dItemInfoList)
        oTableView.Reload()

    
    def OnDelegateNewCellOfData(self, oParent, dData):
        iCardType = dData['iType']
        if iCardType == returncollectcardsdefines.CARD_TYPE_BACK:
            oCell = CBackCard(oParent)
        elif iCardType == returncollectcardsdefines.CARD_TYPE_FRONT:
            oCell = CFrontCard(oParent, misc.Functor(self.m_oFrontCardCB))
        else:
            oCell = CRewardCard(oParent, misc.Functor(self.m_oClickRewardCB))
        oCell.SetItemInfo(dData)
        return oCell

    
    def OnDelegateUpdateCellOfData(self, oCell, dData, bReUes):
        if bReUes:
            oCell.SetItemInfo(dData)
        

    
    def OnDelegateIdentifierOfData(self, dData):
        return str(dData['iType'])

    
    def OnDelegateAlignOfData(self, data):
        return interface.ALIGN_CENTER_MIDDLE



class CFrontCard(combdialog.CCombSubWnd):
    sUIName = 'dialog4/returnreward/huigui_jika_item1.dlg'
    dOpenUIConfig = {
        'KEY_IS_IGNORE_ESC': True }
    
    def __init__(self, oParent, oFrontCardCB):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.m_oIcon = None
        self.m_iMapID = 0
        self.m_iState = 0
        self.m_oFrontCardCB = oFrontCardCB
        self.SetShowObject('img_select', False)

    
    def SetItemInfo(self, dData):
        iShape = dData['iShape']
        iState = dData.get('iState', 0)
        sCardName = dData['sCardName']
        self.m_iMapID = dData['iMap']
        self.SetItemIcon(iShape, iState)
        self.GetObject('text_renwu').SetText(sCardName)

    
    def SetItemIcon(self, iShape, iState):
        self.m_iState = iState
        iRealShape = newschedulecom.GetLimitIcon(iShape)
        self.m_oIcon = item.CreateItem44OnlyImage(self.GetObject('loc_tujian'), iRealShape)
        (iX, iY) = self.GetObject('loc_tujian').GetPos()
        self.m_oIcon.SetPos(iX, iY)

    
    def LeftUp(self):
        combdialog.CCombSubWnd.LeftUp(self)
        if self.m_oFrontCardCB:
            self.m_oFrontCardCB(self.m_iMapID)
        

    
    def Enter(self):
        combdialog.CCombSubWnd.Enter(self)
        self.SetShowObject('img_select', True)

    
    def Leave(self):
        combdialog.CCombSubWnd.Leave(self)
        self.SetShowObject('img_select', False)



class CBackCard(combdialog.CCombSubWnd):
    sUIName = 'dialog4/returnreward/huigui_jika_item3.dlg'
    dOpenUIConfig = {
        'KEY_IS_IGNORE_ESC': True }
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.SetShowObject('img_select', False)

    
    def SetItemInfo(self, dData):
        pass

    
    def LeftUp(self):
        combdialog.CCombSubWnd.LeftUp(self)
        usermacro.PROMPT_MSG('\xc1\xd9\xa5\xbc\xa9\xe2\xa4\xa4\xb8\xd3\xa5d\xa1A\xa5i\xa6b\xac\xc9\xad\xb1\xa5k\xb0\xbc\xc1A\xb8\xd1\xa6p\xa6\xf3\xbcW\xa5[\xa9\xe2\xbc\xfa\xa6\xb8\xbc\xc6')

    
    def Leave(self):
        combdialog.CCombSubWnd.Leave(self)
        self.SetShowObject('img_select', False)



class CRewardCard(combdialog.CCombSubWnd):
    sUIName = 'dialog4/returnreward/huigui_jika_item2.dlg'
    dOpenUIConfig = {
        'KEY_IS_IGNORE_ESC': True }
    
    def __init__(self, oParent, oClickRewardCB):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.m_oClickRewardCB = oClickRewardCB
        self.m_oIcon = None
        self.m_iState = 0
        self.m_iRewardID = 0

    
    def SetItemInfo(self, dData):
        iShape = dData['iShape']
        iNum = dData['iNum']
        iState = dData.get('iState', 0)
        iRewardID = dData.get('iRewardID', 0)
        self.m_iState = iState
        self.m_iRewardID = iRewardID
        self.m_oIcon = wrapinterface.CItemIcon(self, iShape, iNum, 1)
        (iX, iY) = self.GetObject('loc_tujian').GetPos()
        self.m_oIcon.SetPos(iX, iY)
        self.m_oIcon.SetEnterCB(misc.Functor(self.m_oIcon.ShowTips))
        self.m_oIcon.SetLeaveCB(misc.Functor(self.m_oIcon.HideTips))
        self.m_oIcon.SetZ(self.GetObject('loc_tujian').GetZ())
        self.SetShowObject('img_heise', iState == returncollectcardsdefines.CARD_STATE_HAVERECEIVE)
        self.SetShowObject('spr_shine1', iState == returncollectcardsdefines.CARD_STATE_CANRECEIVE)

    
    def CreatItemIcon(self, iShape, iNum):
        self.m_oIcon = wrapinterface.CItemIcon(self.GetObject('loc_tujian'), iShape, iNum, 1)

    
    def OnClickReward(self, iRewardID, iState):
        self.m_oClickRewardCB(iRewardID, iState)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.OnClickReward(self.m_iRewardID, self.m_iState)
