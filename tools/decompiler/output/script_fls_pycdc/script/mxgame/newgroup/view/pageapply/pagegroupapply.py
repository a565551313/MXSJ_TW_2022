# pycdc 交叉复核产物 · script.fls entry 2062
# co_filename(原始)='script/mxgame/newgroup/view/pageapply/pagegroupapply.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2062.pyc (Python 2.5)

import grouppagebase
import combdialog
import delegategroupapplylistpage
import pagedlgbase
import slot
import timer
import misc
import interface
import groupdefines
import wrapinterface

class CGroupPageApply(grouppagebase.CGroupPageBase, combdialog.CCombSubWnd, slot.ISignalSubject, pagedlgbase.COnePageDlgBase):
    SS_ClickTuiJianBtn = 'SS_ClickTuiJianBtn'
    SS_ClickRefreshListBtn = 'SS_ClickRefreshListBtn'
    SS_ClickClearListBtn = 'SS_ClickClearListBtn'
    SS_PageOpen = 'SS_PageOpen(dExtend)'
    SS_PageClose = 'SS_PageClose'
    SS_SelectTableRow = 'SS_SelectTableRow(iIndex, iId)'
    SS_HotBoxClick = 'SS_HotBoxClick(iIndex)'
    SS_ClickRefuseBtn = 'SS_ClickRefuseBtn'
    
    def __init__(self, pContext, pMainDlg):
        grouppagebase.CGroupPageBase.__init__(self, pContext, pMainDlg)
        combdialog.CCombSubWnd.__init__(self, pMainDlg, 'dialog/group_new/group_applylist/group_applylist.dlg')
        self.SetIgnoreEsc(True)
        self.ssInit()
        self.m_bToMemberEnabled = False
        self.m_bToXueTuEnabled = False
        self.m_bRefuseEnabled = False
        self.m_bClearEnabled = False
        self.m_pTimer = None
        self.m_HotBoxTips = None
        self.InitDelegate(pContext)

    
    def InitShowLogic(self):
        import showlogic_groupapply
        self.m_oShowLogic = showlogic_groupapply.CShowLogicGroupApply(self)

    
    def InitDelegate(self, pContext):
        self.m_pDelegate = delegategroupapplylistpage.CDelegateGroupApplyListPage(self, pContext)

    
    def VInit(self):
        pass

    
    def VOpenPage(self, dExtend = None):
        self.ssEmit(self.SS_PageOpen, dExtend)

    
    def VClose(self):
        self.ssEmit(self.SS_PageClose)

    
    def OnPageHide(self):
        self.SelectFirstLine()

    
    def SetToMemberEnabled(self, bEnabled):
        self.m_bToMemberEnabled = bEnabled

    
    def SetToXueTuEnabled(self, bEnabled):
        self.m_bToXueTuEnabled = bEnabled

    
    def SetRefuseEnabled(self, bEnabled):
        self.m_bRefuseEnabled = bEnabled
        self.GetObject('btn_refuse').SetShow(bEnabled)

    
    def SetClearEnabled(self, bEnabled):
        self.m_bClearEnabled = bEnabled
        self.GetObject('btn_clear').SetShow(bEnabled)

    
    def OnSetGrantFinish(self):
        iNum = 0
        for sBtn in ('btn_clear', 'btn_refuse'):
            if self.GetObject(sBtn).GetShow():
                iNum += 1
                continue
        
        if iNum == 0:
            vPos = self.GetObject('btn_clear').GetPos()
            self.GetObject('btn_tj').SetPos(*vPos)
        elif iNum == 1:
            if self.m_bRefuseEnabled:
                pass
            elif self.m_bClearEnabled:
                vPos = self.GetObject('loc_middlebtn').GetPos()
                self.GetObject('btn_clear').SetPos(*vPos)
            
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 6:
            self.ssEmit(self.SS_ClickTuiJianBtn)
        elif iMsgID == 8:
            self.ssEmit(self.SS_ClickRefreshListBtn)
        elif iMsgID == 9:
            self.ssEmit(self.SS_ClickClearListBtn)
        elif iMsgID == 10:
            self.ssEmit(self.SS_ClickRefuseBtn)
        elif iMsgID > iMsgID:
            pass
        elif iMsgID > 2000:
            iIndex = iMsgID - 2001
            pTableUIObj = self.GetTableUIObj()
            it = pTableUIObj.m_Items[iIndex]
            self.ssEmit(self.SS_SelectTableRow, iIndex, it.m_MemId)
        elif iMsgID > interface.RIGHT_BUTTON_MESSAGE + 2000:
            iIndex = iMsgID - interface.RIGHT_BUTTON_MESSAGE - 2001
            self.OnRightItem(iIndex)
        

    
    def SetBangZhongNum(self, iNum, iMaxNum):
        self.GetObject('text_member').SetText('%s/%s' % (iNum, iMaxNum))

    
    def SetJiMingNum(self, iNum, iMaxNum):
        self.GetObject('text_apprentice_num').SetText('%s/%s' % (iNum, iMaxNum))

    
    def SetXueTuNum(self, iNum, iMaxNum):
        self.GetObject('text_temp_num').SetText('%s/%s' % (iNum, iMaxNum))

    
    def OnRightItem(self, iIndex):
        import dlgfriend
        oTab = self.GetTableUIObj()
        oItem = oTab.GetItem(iIndex)
        dlgfriend.FindPlayerWithID(oItem.m_MemId, 1)

    
    def GetTableUIObj(self):
        return self.GetObject('tab_join')

    
    def RefreshApplyList(self, vAllShowInfo, iLastSelectIndex, iLastApplyCount = 0, bNeedDelay = True):
        import grouppagefactory
        pTableUIObj = self.GetTableUIObj()
        vBarPos = pTableUIObj.m_VScrollBar.GetPos()
        pTableUIObj.Clear()
        iIndex = 0
        for iId, vOneShowInfo, iExIconIdxLst in vAllShowInfo:
            it = pTableUIObj.AddTextItem(*vOneShowInfo)
            pTableUIObj.AlignItem(it.m_TextObjects[0], 0, interface.ALIGN_LEFT_MIDDLE, (50, 0))
            it.m_Data = vOneShowInfo
            it.m_MemId = iId
            it.m_MemIdnex = iIndex
            it.m_ApplyTypeName = vOneShowInfo[0][2]
            it.m_BtnCell = None
            iIndex += 1
            it.m_oAvatar = grouppagefactory.CreateAvatar(it.m_TextObjects[0], iId, {
                'offx': 5,
                'type': 'groupapply' })
            it.m_iExIconIdxLst = iExIconIdxLst
            if iExIconIdxLst:
                self.CreateExIcon(it.m_TextObjects[0], iExIconIdxLst)
                continue
        
        pTableUIObj.ResetItems()
        pTableUIObj.ResetScrollBar()
        pTableUIObj.m_VScrollBar.SetBarPos(vBarPos)
        iCurLen = len(vAllShowInfo)
        if bNeedDelay and iCurLen < iLastApplyCount:
            self.DelaySelectNextItem(iLastSelectIndex)
        

    
    def CreateExIcon(self, oParent, iExIconIdxLst):
        oParent.m_oExBtnLst = []
        for iIdx, iExIconIdx in enumerate(iExIconIdxLst):
            oExBtn = CExIconButton(oParent, iExIconIdx)
            oParent.m_oExBtnLst.append(oExBtn)
            (_, iPH) = oParent.GetSize()
            (iW, iH) = oExBtn.GetSize()
            iY = (iPH - iH) / 2
            iX = 100 + (iW + 5) * iIdx
            oExBtn.SetPos(iX, iY)
            oExBtn.SetZ(100)
        

    
    def DelaySelectNextItem(self, iIndex):
        pTableUIObj = self.GetTableUIObj()
        iLen = len(pTableUIObj.GetItems())
        if iIndex < iLen:
            self.m_pTimer = timer.Timer(0.5, misc.Functor(self.OnLeftUpNextItem, iIndex))
        

    
    def OnLeftUpNextItem(self, iIndex):
        pTableUIObj = self.GetTableUIObj()
        oItem = pTableUIObj.GetItem(iIndex)
        if oItem:
            oItem.LeftUp()
        
        self.ClearTimer()

    
    def ClearTimer(self):
        if self.m_pTimer:
            self.m_pTimer.Release()
            self.m_pTimer = None
        

    
    def ClearApplyList(self):
        pass

    
    def RemoveApply(self, iId):
        pTableUIObj = self.GetTableUIObj()
        vLastMember = []
        iIndex = 0
        for idx, it in enumerate(pTableUIObj.m_Items):
            if it.m_MemId != iId:
                vLastMember.append((it.m_MemId, it.m_Data, it.m_iExIconIdxLst))
                continue
            iIndex = idx
        
        pos = pTableUIObj.m_VScrollBar.GetPos()
        pTableUIObj.Clear()
        self.RefreshApplyList(vLastMember, iIndex, bNeedDelay = False)
        pTableUIObj.ResetItems(pos)
        pTableUIObj.ResetScrollBar()
        pTableUIObj.m_VScrollBar.SetBarPos(pos)
        self.DelaySelectNextItem(iIndex)

    
    def OnChangeSelectRow(self, iOldId, iNewId):
        pTableUIObj = self.GetTableUIObj()
        for idx, it in enumerate(pTableUIObj.m_Items):
            if it.m_MemId == iOldId:
                self.OnItemLeave(it)
                break
                continue
        
        for idx, it in enumerate(pTableUIObj.m_Items):
            if it.m_MemId == iNewId:
                self.OnItemEnter(it)
                break
                continue
        

    
    def SelectFirstLine(self):
        self.OnLeftUpNextItem(0)
        pTableUIObj = self.GetTableUIObj()
        oItem = pTableUIObj.GetItem(0)
        if oItem:
            self.OnItemEnter(oItem)
        

    
    def OnHotBoxEnter(self, hotbox):
        if hotbox.m_Index in (0, 1, 2, 3):
            self.m_HotBoxTips = wrapinterface.CTextTips(None, 80, '\xc2I\xc0\xbb\xa5i\xb1\xc6\xa7\xc7', interface.FontLT14_3)
        

    
    def OnHotBoxLeave(self, hotbox):
        self.m_HotBoxTips = None

    
    def OnHotBoxClick(self, hotbox):
        iIndex = hotbox.m_Index
        if iIndex in (0, 1, 2, 3):
            self.ssEmit(self.SS_HotBoxClick, iIndex)
        

    
    def OnItemEnter(self, it):
        if not (self.m_bToMemberEnabled) and not (self.m_bToXueTuEnabled):
            return None
        
        pTableUIObj = self.GetTableUIObj()
        oItem = pTableUIObj.GetItem(0)
        if oItem:
            if oItem != it:
                self.OnItemLeave(oItem)
            
        
        if it.m_BtnCell:
            it.m_BtnCell.SetShow(True)
        else:
            pTableUIObj = self.GetTableUIObj()
            iItemWidth = pTableUIObj.GetItemWidth(-1)
            iItemHeight = pTableUIObj.GetItemSize()[1]
            it.m_BtnCell = CButtonCell(it, it.m_ApplyTypeName, it.m_MemId, iItemWidth, iItemHeight, self.m_bToMemberEnabled, self.m_bToXueTuEnabled)
            it.m_BtnCell.SetPos(pTableUIObj.GetItemX(len(pTableUIObj.m_Widths) - 1), 0)

    
    def OnItemLeave(self, it):
        if not (self.m_bToMemberEnabled) and not (self.m_bToXueTuEnabled):
            return None
        
        if it.m_MemId == self.m_pDelegate.GetSelectID():
            return None
        
        if it.m_BtnCell:
            it.m_BtnCell.SetShow(False)
        



class CButtonCell(interface.CBaseObject):
    
    def __init__(self, oParent, sTypeName, iId, iW, iH, bToMemberEnabled, bToXueTuEnabled):
        interface.CBaseObject.__init__(self, oParent)
        self.m_iId = iId
        dPngInfo = {
            interface.STYLE1_KEY: ('combdialog\\\xb0\xb4\xc5\xa5\\\xb0\xb4\xc5\xa6\xcb\xc4\xd7\xd6.igs', '0'),
            interface.STYLE2_KEY: ('combdialog2\\\xb0\xb4\xc5\xa5\\\xb0\xb4\xc5\xa6\xcb\xc4\xd7\xd6.igs', '0'),
            interface.STYLE3_KEY: ('combdialog3\\\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5\\\xc0\xb6\xc9\xab\xb0\xb4\xc5\xa5\\', '23'),
            interface.STYLE4_KEY: ('combdialog4\\\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5\\\xd2\xbb\xbc\xb6\xb0\xb4\xc5\xa5\xc0\xb6\\', '50'),
            interface.STYLE5_KEY: ('combdialog4\\\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5\\\xd2\xbb\xbc\xb6\xb0\xb4\xc5\xa5\xc0\xb6\\', '50') }
        iStyle = interface.GetStyle()
        vBtnName = [
            '\xa7\xe5\xad\xe3\xa4J\xc0\xb0']
        vSize = [
            70,
            27]
        if interface.IsNewStyle():
            vArgs1 = [
                dPngInfo[iStyle][1],
                dPngInfo[iStyle][0],
                vBtnName[0],
                '70',
                '1',
                '0',
                '0',
                '0']
        else:
            vArgs1 = [
                dPngInfo[iStyle][1],
                dPngInfo[iStyle][0],
                vBtnName[0],
                '1',
                '0',
                '0',
                '0']
        vArgs1.reverse()
        self.m_oBtn1 = CTextButtonForGroupApply(self, misc.Functor(oParent.Enter), misc.Functor(oParent.\xf4\xdd\xd9\xcee), vArgs1)
        iX = 50
        iY = (iH - vSize[1]) / 2
        self.m_oBtn1.SetPos(iX, iY)

    
    def OnMessage(self, iMsgID):
        if iMsgID not in (1, 2):
            return None
        
        import groupviewsignal
        groupviewsignal.Emit(groupviewsignal.SS_ApplyPageAccecpt, self.m_iId)



class CTextButtonForGroupApply(combdialog.CTextButton):
    
    def __init__(self, pParent, pEnter, pLeave, *vArgs):
        combdialog.CTextButton.__init__(self, pParent, *vArgs)
        self.m_pEnter = pEnter
        self.m_pLeave = pLeave

    
    def Enter(self):
        combdialog.CTextButton.Enter(self)
        if self.m_pEnter:
            self.m_pEnter()
        

    
    def \xf4\xdd\xd9\xcee(self):
        combdialog.CTextButton.\xf4\xdd\xd9\xcee(self)
        if self.m_pLeave:
            self.m_pLeave()
        



class CExIconButton(interface.CButton):
    
    def __init__(self, oParent, iExIconIdx):
        sImgPathList = [
            'combdialog4/\xd4\xd3\xcd\xbc/\xb5\xe3\xb5\xe3\xd0\xa1\xcd\xbc\xb1\xea.png',
            'combdialog/\xd0\xc2\xba\xec\xb0\xfc\xbd\xe7\xc3\xe6/\xd0\xa1\xba\xec\xb0\xfc\xbf\xaa.igs']
        interface.CButton.__init__(self, oParent, sImgPathList[iExIconIdx - 1], 0, 0, 1000)
        self.m_iExIconIdx = iExIconIdx
        self.m_oTips = None
        self.SetEnterCB(misc.Functor(self.OnBtnEnter))
        self.SetLeaveCB(misc.Functor(self.OnBtnLeave))

    
    def OnBtnEnter(self):
        sTipsLst = [
            '\xbe\xd6\xa6\xb3\xc2I\xc2I\xaa\xba\xa4\xd6\xabL',
            '\xaa\xf1\xb4\xc1\xb5o\xa9\xf1\xb9L\xac\xf5\xa5]\xaa\xba\xa4\xd6\xabL']
        self.m_oTips = wrapinterface.CTextTips(None, -1, sTipsLst[self.m_iExIconIdx - 1], interface.FontLT14_3, direct = 1)

    
    def OnBtnLeave(self):
        self.m_oTips = None
