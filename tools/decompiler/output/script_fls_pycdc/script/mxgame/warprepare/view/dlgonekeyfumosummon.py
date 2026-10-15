# pycdc 交叉复核产物 · script.fls entry 3361
# co_filename(原始)='script/mxgame/warprepare/view/dlgonekeyfumosummon.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3361.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/5/13 13:23
\xd7\xf7\xd5\xdf: hfl
\xce\xc4\xbc\xfe: dlgonekeyfumosummon
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import slot
import pagedlgbase
import misc
import pet
import interface
UI2PROP = {
    'text_level': 'm_Grade',
    'text_def': 'm_Defense',
    'text_hp': 'm_HP',
    'text_att': 'm_Damage',
    'text_mgc': 'm_Magdef',
    'text_spe': 'm_Speed' }
UI_ADDONEKEY_CONFIG = {
    'iY': 0,
    'iMsgId': -1,
    'iTeam': 0,
    'iX': 0,
    'iRelationNum': 0,
    'lChildren': [],
    'sSoundPath': '',
    'bShow': True,
    'iTipsDirect': 0,
    'sWidgetType': 'CButton',
    'sName': 'ipetID',
    'bLoad': True,
    'sTips': '',
    'iParentHeight': 0,
    'iVersion': 7,
    'lRelationName': [],
    'sFileName': 'combdialog4/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xd0\xa1\xd4\xb2\xc8\xa6\xb9\xb4\xd1\xa1/' }

class COneKeyFumoSummonDlg(combdialog.CCombDialog, slot.ISignalSubject, pagedlgbase.COnePageDlgBase):
    S_UIPATH = 'dialog/warprepare/fumo_summon.dlg'
    SS_ClickBtnAtk = 'SS_ClickBtnAtk'
    SS_ClickBtnMgc = 'SS_ClickBtnMgc'
    SS_ClickBtnDef = 'SS_ClickBtnDef'
    SS_ClickBtnSpeed = 'SS_ClickBtnSpeed'
    SS_ClickBtnOneKeyMode = 'SS_ClickBtnOneKeyMode'
    SS_SelectPet = 'SS_SelectPet'
    SS_Add2OneKeyPet = 'SS_Add2OneKeyPet'
    SS_EnterFumoBtn = 'SS_EnterFumoBtn'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent, self.S_UIPATH)
        pagedlgbase.COnePageDlgBase.__init__(self)
        self.ssInit()
        self.m_DelegateList = []
        self.m_dClickBox = { }
        self.m_lPetID = []
        self.m_lOneKeyPetID = []
        self.m_iSelectPetID = None
        self.m_oTimer = None
        self.m_oTips = None
        self.m_oFumoRangeTips = None
        self.InitDlg()
        self.InitDelegate()

    
    def InitDlg(self):
        self.m_dClickBox = { }
        for sUIName, sProp in UI2PROP.iteritems():
            oRichTextFrame = self.GetObject(sUIName)
            if not oRichTextFrame:
                continue
            
            (iW, iH) = oRichTextFrame.GetSize()
            oClickBox = interface.CClickBox(oRichTextFrame, iW, iH, alpha = 0, msgid = 0)
            self.m_dClickBox[sUIName] = oClickBox
            oFunc = misc.Functor(self.OnEnterProp, sUIName)
            oClickBox.SetEnterCB(oFunc)
            oFunc = misc.Functor(self.OnLeaveProp, sUIName)
            oClickBox.SetLeaveCB(oFunc)
            oClickBox.SetShow(False)
        

    
    def OnItemEnter(self, oItem):
        iPetID = getattr(oItem, 'm_iPetID', None)
        if not iPetID:
            return None
        
        self.m_oFumoRangeTips = iPetID
        self.ssEmit(self.SS_EnterFumoBtn, iPetID)

    
    def OnItemLeave(self, oItem):
        self.m_oFumoRangeTips = None

    
    def SetFumoBtnEnterTips(self, dData):
        import wrapinterface
        if not (self.m_oFumoRangeTips) or self.m_oFumoRangeTips not in dData:
            return None
        
        sTips = dData.get(self.m_oFumoRangeTips)
        if sTips:
            self.m_oFumoRangeTips = wrapinterface.CTextTips(None, -1, sTips, interface.FontLT14_3, direct = 1)
        

    
    def OnEnterProp(self, sUIName, *args):
        import wrapinterface
        import dgtonekeyfumosummon
        sMsg = dgtonekeyfumosummon.GetPetFumoTips(self.m_iSelectPetID)
        self.m_oTips = wrapinterface.CTextTips(None, -1, sMsg, interface.FontLT14_3, direct = 1)

    
    def OnLeaveProp(self, sUIName, *args):
        self.m_oTips = None

    
    def InitDelegate(self):
        import dgtonekeyfumosummon
        self.m_DelegateList = [
            dgtonekeyfumosummon.CDgtOneKeyFumoSummon(self)]

    
    def RefreshPetList(self, lPetID, dAllData, bOneKey, lOneKeyList):
        oPetListView = self.GetObject('petlist')
        oPetListView.Clear()
        self.m_lPetID = []
        for iIndex, iPetID in enumerate(lPetID):
            bSelect = iPetID in lOneKeyList
            dShowData = dAllData[iPetID]
            sTitle = dShowData['sTitle']
            sFumo = dShowData['sFumo']
            oItem = oPetListView.AddTextItem(sTitle)
            None(None, None, None, None, None, None, None, None, None, None, None, None, *iPetID).m_iPetID = None
            oItem.m_MsgID = iIndex + 1
            self.m_lPetID.append(iPetID)
            self.RefrehsOnePetItemView(oItem, iPetID, {
                'bOneKeyMode': bOneKey,
                'bOneKey': bSelect,
                'sFumo': sFumo })
        
        oPetListView.ResetItems()
        oPetListView.ResetScrollBar()

    
    def GetItemViewByPetID(self, iPetID):
        oPetListView = self.GetObject('petlist')
        lItems = oPetListView.GetItems()
        for oItem in lItems:
            if oItem.m_iPetID == iPetID:
                return oItem
                continue
        

    
    def RefreshOnePetListItemView(self, iPetID, dPetShowData):
        oItemView = self.GetItemViewByPetID(iPetID)
        if not oItemView:
            return None
        
        self.RefrehsOnePetItemView(oItemView, iPetID, dPetShowData)

    
    def RefrehsOnePetItemView(self, oItemView, iPetID, dData):
        oItemView.m_iPetID = iPetID
        if 'sFumo' in dData:
            sFumo = dData['sFumo']
            if sFumo:
                oPetListView = self.GetObject('petlist')
                iColor = interface.COLOR_1
                iFont = interface.FontLT14_1
                if interface.IsStyle1():
                    iFont = interface.FontST14
                    iColor = getattr(oPetListView, 'm_EnterTxtColor', interface.COLOR_1)
                
                oItemView.m_oFuMoText = interface.CRichTextObject(oItemView, 1000, iFont, sFumo, iColor = iColor)
                oItemView.m_oFuMoText.SetPos(130, 9)
            else:
                oItemView.m_oFuMoText = None
        
        if 'bOneKeyMode' in dData or 'bOneKey' in dData:
            oBtn = getattr(oItemView, 'm_oAdd2OneKeyBtn', None)
            if not oBtn:
                dInfo = dict(UI_ADDONEKEY_CONFIG)
                oBtn = combdialog.CButton(oItemView, None, dInfo)
                oBtn.m_MsgID = 0
                oBtn.m_TeamCount = 0
                oCallBack = misc.Functor(self.OnAdd2OneKeyPet, iPetID)
                oBtn.SetLeftUpCB(oCallBack)
                oItemView.m_oAdd2OneKeyBtn = oBtn
                interface.Center(oBtn)
                oBtn.SetPos(4, oBtn.GetPos()[1])
            
            if 'bOneKeyMode' in dData:
                oBtn.SetShow(dData['bOneKeyMode'])
            
            if 'bOneKey' in dData:
                oBtn.SetSelect(dData['bOneKey'])
            
        

    
    def RefreshOneKeyMode(self, iSel):
        self.GetObject('btn_select').SetSelect(iSel)
        oPetListView = self.GetObject('petlist')
        lItems = oPetListView.GetItems()
        for oItem in lItems:
            iPetID = oItem.m_iPetID
            self.RefrehsOnePetItemView(oItem, iPetID, {
                'bOneKeyMode': iSel })
        

    
    def RefreshDetailView(self, dData):
        self.m_iSelectPetID = dData['iSelPet']
        for sUIName, sPropKey in UI2PROP.iteritems():
            sValue = dData.get(sPropKey, '')
            bFumo = sValue.find('+') != -1
            oClickBox = self.m_dClickBox[sUIName]
            oClickBox.SetShow(bFumo)
            self.GetObject(sUIName).SetText(sValue)
        

    
    def RefreshPetSelectState(self, iSelPet):
        oPetListView = self.GetObject('petlist')
        lItems = oPetListView.GetItems()
        for oItem in lItems:
            iPetID = oItem.m_iPetID
            bSelect = iPetID == iSelPet
            oItem.Select(bSelect)
        

    
    def RefreshOneKeyPet(self, lPet):
        import timer
        self.m_lOneKeyPetID = lPet
        if self.m_oTimer:
            return None
        
        self.m_oTimer = timer.Timer(0.1, self.RealRefreshOneKeySelectPet)

    
    def RealRefreshOneKeySelectPet(self):
        if self.m_oTimer:
            self.m_oTimer.Release()
            self.m_oTimer = None
        
        lPet = self.m_lOneKeyPetID
        oPetListView = self.GetObject('petlist')
        lItems = oPetListView.GetItems()
        for oItem in lItems:
            iPetID = oItem.m_iPetID
            bOneKey = iPetID in lPet
            self.RefrehsOnePetItemView(oItem, iPetID, {
                'bOneKey': bOneKey })
        

    
    def OnAdd2OneKeyPet(self, iPetID):
        LOG('OnAdd2OneKeyPet:', iPetID)
        self.ssEmit(self.SS_Add2OneKeyPet, iPetID)

    
    def VOpenPage(self, dExtend = None):
        self.ssEmit(self.SS_OpenDlg, dExtend)

    
    def VClose(self):
        self.ssEmit(self.SS_CloseDlg)

    
    def OnSelectPetEvent(self, iPet):
        self.ssEmit(self.SS_SelectPet, iPet)

    
    def OnRightOpenPetDlg(self, iPetID):
        import dlggetinfo
        import pet
        oPet = pet.GetPet(iPetID)
        iShape = oPet.GetProp('m_Shape')
        sName = oPet.GetProp('m_Name')
        (x, y) = self.GetPos()
        dlggetinfo.ShowSummonInfo(self, 200 - x, 50 - y, 0, iPetID, iShape, sName)

    
    def OnMessage(self, iMsgID):
        LOG('OnMessage:', iMsgID)
        if iMsgID == 1:
            self.ssEmit(self.SS_ClickBtnAtk)
        elif iMsgID == 2:
            self.ssEmit(self.SS_ClickBtnMgc)
        elif iMsgID == 3:
            self.ssEmit(self.SS_ClickBtnDef)
        elif iMsgID == 4:
            self.ssEmit(self.SS_ClickBtnSpeed)
        elif iMsgID == 5:
            self.ssEmit(self.SS_ClickBtnOneKeyMode)
        elif iMsgID <= iMsgID:
            pass
        elif iMsgID < 1001 + len(self.m_lPetID):
            iIndex = iMsgID - 1001
            iPetID = self.m_lPetID[iIndex]
            self.OnSelectPetEvent(iPetID)
        elif iMsgID > interface.RIGHT_BUTTON_MESSAGE:
            iIndex = iMsgID - interface.RIGHT_BUTTON_MESSAGE - 1001
            if iIndex < 0:
                return None
            
            if iIndex > len(self.m_lPetID):
                return None
            
            iPetID = self.m_lPetID[iIndex]
            self.OnRightOpenPetDlg(iPetID)
