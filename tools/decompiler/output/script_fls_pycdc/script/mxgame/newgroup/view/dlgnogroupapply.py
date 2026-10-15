# pycdc 交叉复核产物 · script.fls entry 226
# co_filename(原始)='script/mxgame/newgroup/view/dlgnogroupapply.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_226.pyc (Python 2.5)

'''
\xb0\xef\xc5\xc9\xc9\xea\xc7\xeb\xbd\xe7\xc3\xe6
'''
import combdialog
import combmacro
import guidectrl
import guidedefine
import interface
import slot
import delegatenogroupapply
import wrapinterface
import style
import wrapedit
import hero
import ui

class CGroupApplyDlgNew(combdialog.CCombDialog, slot.ISignalSubject):
    SS_ClickClose = 'OnClose'
    SS_ClickGroupCreate = 'OnCreateGroup'
    SS_ClickGroupApply = 'OnGroupApply'
    SS_ClickGroupApplyAll = 'OnGroupApplyAll'
    SS_ClickSortNo = 'OnClickSortNo'
    SS_ClickSortName = 'OnClickSortName'
    SS_ClickSortLv = 'OnClickSortLv'
    SS_ClickSortAmount = 'OnClickSortAmount'
    SS_ClickSortPride = 'OnClickSortPride'
    SS_EnterSearchGroup = 'OnSearchGroup'
    SS_SelectGroup = 'OnSelectGroup'
    SS_ResponseGroup = 'OnResponseGroup'
    SS_UpdateTableView = 'UpdateTableView'
    SS_OnClickHongBao = 'SS_OnClickHongBao'
    SS_OnClickReport = 'SS_OnClickReport'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/group_new/newgroup/groupapply.dlg')
        interface.Center(self)
        self.m_oTxtDesc = None
        self.m_oSearchEdit = None
        self.m_oDelegate = None
        self.m_oResponseBtnLst = []
        self.m_oTable = self.GetObject('table_list')
        self.m_oBtnApply = self.GetObject('btn_apply')
        self.m_oBtnCreate = self.GetObject('btn_create')
        self.m_oBtnHongBao = self.GetObject('btn_hongbao')
        self.m_oHongBaoImgList = []
        self.ssInit()
        self.InitDelegate()
        self.CreateSearchEdit()
        for sName in ('btn_applyall',):
            guidectrl.GetGuideCtrl().AddWefOrdObj(self, guidedefine.GUIDE_GROUP_APPLY, sName, self.GetObject(sName))
        

    
    def RefreashWindow(self):
        self.ssEmit(self.SS_UpdateTableView)

    
    def InitDelegate(self):
        self.m_oDelegate = delegatenogroupapply.CGroupApplyDelegate(self)

    
    def GetDelegate(self):
        return self.m_oDelegate

    
    def CreateSearchEdit(self):
        self.m_oSearchEdit = combmacro.CEDIT(wrapedit.CPlaceHoldEdit, 'hfrm_search', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        self.m_oSearchEdit.SetPlaceHold('\xc2I\xc0\xbb\xacd\xa7\xe4\xc0\xb0\xac\xa3', interface.FontLT14_3, interface.COLOR_5)
        self.m_oSearchEdit.SetMsgId(21)
        self.m_oSearchEdit.SetCharChangeCB(self.OnSearchEditChange)

    
    def UpdateTable(self, lstGroupInfo):
        iIdx = 0
        self.m_oTable.Clear()
        oMyGroupInfo = None
        self.m_oHongBaoImgList = []
        for oGroupInfo in lstGroupInfo:
            if oGroupInfo.m_iFlag == 1:
                iItemColor = interface.COLOR_86
            else:
                iItemColor = interface.COLOR_29
            if oGroupInfo.m_iReady == 1:
                sId = '\xb7s\xab\xd8'
            else:
                sId = '%d' % oGroupInfo.m_iId
            oBox = self.m_oTable.AddBoxItem()
            listObj = []
            stxtId = sId
            stxtName = oGroupInfo.m_sName
            stxtLvl = '%d' % oGroupInfo.m_iLv
            stxtMount = '%d/%d' % (oGroupInfo.m_iAmount, oGroupInfo.m_iMaxAmount)
            stxtPride = str(oGroupInfo.m_iPride)
            (_, h) = self.m_oTable.GetItemSize()
            txtId = CTeamTextItem(oBox, 40, h, iItemColor, stxtId)
            w = self.m_oTable.GetItemWidth(4)
            txtName = CTeamNameItem(oBox, w, h, iItemColor, stxtName)
            txtName.ShowRedPacket(oGroupInfo.m_bWelcomeHB == 1)
            txtLvl = CTeamTextItem(oBox, 10, h, iItemColor, stxtLvl)
            txtMount = CTeamTextItem(oBox, 40, h, iItemColor, stxtMount)
            txtPride = CTeamTextItem(oBox, 30, h, iItemColor, stxtPride)
            listObj.append(txtId)
            listObj.append(txtName)
            listObj.append(txtLvl)
            listObj.append(txtMount)
            listObj.append(txtPride)
            oTxtItem = self.m_oTable.AddItemExtend(oBox, listObj)
            if oGroupInfo.m_iReady == 1:
                iBtnWidth = 0
                if interface.IsStyle3() or interface.IsStyle4():
                    iBtnWidth = 60
                
                oTxtAmount = oTxtItem.m_TextObjects[4]
                if oGroupInfo.m_iFlag == 1:
                    oBtnResponse = wrapinterface.CTextButtonWithTips(oTxtItem, style.GetPath('combdialog/button'), 0, 0, '\xa8\xfa\xae\xf8', interface.COLOR_29, interface.FontLT14_3, msgid = 10001 + iIdx, width = iBtnWidth)
                    oBtnResponse.SetTips('\xc2I\xc0\xbb\xa8\xfa\xae\xf8\xc5T\xc0\xb3\xc0\xb0\xac\xa3')
                else:
                    oBtnResponse = wrapinterface.CTextButtonWithTips(oTxtItem, style.GetPath('combdialog/button'), 0, 0, '\xc5T\xc0\xb3', interface.COLOR_29, interface.FontLT14_3, msgid = 10001 + iIdx, width = iBtnWidth)
                    oBtnResponse.SetTips('\xc2I\xc0\xbb\xc5T\xc0\xb3\xc0\xb0\xac\xa3')
                interface.AlignObjects(oBtnResponse, oTxtAmount, interface.ALIGN_CENTER_MIDDLE)
                (iBtnW, _) = oBtnResponse.GetSize()
                oTxtAmount.SetShow(False)
                oBtnResponse.SetZ(1)
                self.m_oResponseBtnLst.append(oBtnResponse)
                iMyId = hero.GetHeroID()
                if oGroupInfo.m_iOwnerId == iMyId:
                    oMyGroupInfo = oGroupInfo
                
            
            oTxtItem.m_iIdx = iIdx
            iIdx += 1
        
        if oMyGroupInfo:
            if oMyGroupInfo.m_bHasHongBao:
                self.m_oBtnCreate.SetShow(True)
                self.m_oBtnHongBao.SetShow(False)
            else:
                self.m_oBtnCreate.SetShow(False)
                self.m_oBtnHongBao.SetShow(True)
        else:
            self.m_oBtnCreate.SetShow(True)
            self.m_oBtnHongBao.SetShow(False)
        self.m_oTable.ResetItems()
        self.m_oTable.ResetScrollBar()

    
    def UpdateItemApplyStatus(self, iIdx):
        oItem = self.m_oTable.m_Items[iIdx]
        for oTextObj in oItem.m_TextObjects:
            if hasattr(oTextObj, 'SetTextColor'):
                oTextObj.SetTextColor(interface.COLOR_86)
                continue
            oTextObj.SetColor(interface.COLOR_86)
        

    
    def UpdateDesc(self, sDesc):
        if sDesc:
            self.m_oTxtDesc = combmacro.CRICHTEXT(interface.CRichTextObject, 'frm_faith', self, sDesc, interface.FontLT14_3, interface.COLOR_4)
        else:
            self.m_oTxtDesc = None

    
    def UpdateApplyBtnState(self, bEnable, sTxt):
        self.m_oBtnApply.SetText(sTxt)
        self.m_oBtnApply.Enable(bEnable)

    
    def OnSearchEditChange(self):
        self.OnMessage(21)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_ClickClose)
        elif iMsgID == 2:
            self.ssEmit(self.SS_ClickGroupApply)
        elif iMsgID == 3:
            self.ssEmit(self.SS_OnClickReport)
        elif iMsgID == 4:
            self.ssEmit(self.SS_ClickGroupCreate)
        elif iMsgID == 5:
            self.ssEmit(self.SS_ClickGroupApplyAll)
            guidectrl.GetGuideCtrl().ClickOrdObj(guidedefine.GUIDE_GROUP_APPLY, 'btn_applyall')
        elif iMsgID == 6:
            self.ssEmit(self.SS_ClickSortNo)
        elif iMsgID == 7:
            self.ssEmit(self.SS_ClickSortName)
        elif iMsgID == 8:
            self.ssEmit(self.SS_ClickSortLv)
        elif iMsgID == 9:
            self.ssEmit(self.SS_ClickSortAmount)
        elif iMsgID == 10:
            self.ssEmit(self.SS_ClickSortPride)
        elif iMsgID == 21:
            self.ssEmit(self.SS_EnterSearchGroup, self.m_oSearchEdit.GetText())
        elif iMsgID - 100 < iMsgID - 100:
            pass
        elif iMsgID - 100 <= len(self.m_oTable.m_Items):
            oItem = self.m_oTable.m_Items[iMsgID - 100 - 1]
            self.ssEmit(self.SS_SelectGroup, oItem.m_iIdx)
        elif iMsgID - 10100 < iMsgID - 10100:
            pass
        elif iMsgID - 10100 <= len(self.m_oTable.m_Items):
            oItem = self.m_oTable.m_Items[iMsgID - 10100 - 1]
            self.ssEmit(self.SS_ResponseGroup, oItem.m_iIdx)
        elif iMsgID == 11:
            self.ssEmit(self.SS_OnClickHongBao)
        

    
    def CloseWindow(self):
        import popupmgr
        import popupdefine
        self.m_oTxtDesc = None
        self.m_oSearchEdit = None
        self.m_oDelegate = None
        self.m_oResponseBtnLst = []
        self.m_oHongBaoImgList = []
        if self.m_oDelegate:
            self.m_oDelegate.Destroy()
        
        popupmgr.GetPopupMgr().CloseUI(popupdefine.CGroupApplyDlgNew)



class CTeamNameItem(interface.CBoxObject):
    
    def __init__(self, parent, w, h, txtColor, sTxt):
        interface.CBoxObject.__init__(self, parent, w, h, 0, 0)
        self.SetPos(0, 0)
        (_, h) = self.GetSize()
        self.oHongBaoImg = None
        self.oTextName = interface.CTextObject(self, sTxt, interface.FontLT14_3, txtColor)
        self.oTextName.SetPos(0, h / 4)

    
    def ShowRedPacket(self, bShow):
        if bShow:
            self.oHongBaoImg = wrapinterface.CImageWithTips(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xba\xec\xb0\xfc/\xd0\xa1\xba\xec\xb0\xfc.igs', '\xa6\xa8\xac\xb0\xb8\xd3\xc0\xb0\xa6\xa8\xad\xfb\xa5i\xc0\xf2\xb1o\xac\xf5\xa5]')
            (_, iH) = self.GetSize()
            (iImgW, _) = self.oHongBaoImg.GetSize()
            self.oHongBaoImg.SetPos(-iImgW, iH / 4 - 2)
            self.oTextName.SetPos(0, iH / 4)
        

    
    def SetTextColor(self, iColor):
        self.oTextName.SetColor(iColor)



class CTeamTextItem(interface.CBoxObject):
    
    def __init__(self, parent, w, h, txtColor, sTxt):
        interface.CBoxObject.__init__(self, parent, w, h, 0, 0)
        self.SetPos(0, 0)
        (_, h) = self.GetSize()
        self.oTextName = interface.CTextObject(self, sTxt, interface.FontLT14_3, txtColor)
        self.oTextName.SetPos(0, h / 4)

    
    def SetTextColor(self, iColor):
        self.oTextName.SetColor(iColor)
