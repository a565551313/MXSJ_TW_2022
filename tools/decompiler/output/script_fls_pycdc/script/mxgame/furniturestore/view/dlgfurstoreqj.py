# pycdc 交叉复核产物 · script.fls entry 4624
# co_filename(原始)='script/mxgame/furniturestore/view/dlgfurstoreqj.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4624.pyc (Python 2.5)

import combdialog
import interface
import slot
import delegatefurstoreqj
import newfurnituredata
import autonumedit
import dlgfuritem
import combmacro

class CFurStoreQJDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    S_PATH = 'dialog4/yard/furstore/tradefurniture_qj.dlg'
    SS_BUY = 'SS_Buy'
    SS_SHOW_SUBPAGE = 'SS_ShowSubPage'
    SS_OPEN_MAXPREDLG = 'SS_OpenMaxPreViewDlg'
    SS_SELECTINDEX = 'SS_SelectIndex(iIndex)'
    SS_BUYNUMCHANGED = 'SS_BuyNumChanged(iNum)'
    
    def __init__(self, pMainDlg):
        combdialog.CCombSubWnd.__init__(self, pMainDlg, self.S_PATH)
        self.ssInit()
        self.m_oTableView = None
        self.m_lTableData = []
        self.m_wrSelectItem = None
        self.m_oBuyAmountEdit = None
        self.m_oFurObj = None
        self.m_oDelegate = delegatefurstoreqj.CDelegateFurStoreQJDlg(self)
        self.m_oDelegate.InitDelegate()

    
    def GetSelectData(self):
        return self.m_oDelegate.GetSelectData()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 17:
            self.ssEmit(self.SS_OPEN_MAXPREDLG)
        elif iMsgID == 4:
            self.ssEmit(self.SS_BUY)
        elif iMsgID in (10, 11, 12, 13, 14, 15, 16):
            dMsgID2Type = {
                10: 0,
                11: newfurnituredata.FUR_SHOWTYPE_NORMAL,
                12: newfurnituredata.FUR_SHOWTYPE_ZHIWU,
                14: newfurnituredata.FUR_SHOWTYPE_DIZHUAN,
                15: newfurnituredata.FUR_SHOWTYPE_SHUIJING,
                16: newfurnituredata.FUR_SHOWTYPE_WALL }
            nPage = dMsgID2Type[iMsgID]
            self.ssEmit(self.SS_SHOW_SUBPAGE, nPage)
        

    
    def RefreshSubPageBtnState(self, iCurPage):
        PAGE2PAGEBTN = {
            0: 'btn_all',
            newfurnituredata.FUR_SHOWTYPE_NORMAL: 'btn_jianzhu',
            newfurnituredata.FUR_SHOWTYPE_ZHIWU: 'btn_zhiwu',
            newfurnituredata.FUR_SHOWTYPE_DIZHUAN: 'btn_dizhuan',
            newfurnituredata.FUR_SHOWTYPE_SHUIJING: 'btn_shuijing',
            newfurnituredata.FUR_SHOWTYPE_WALL: 'btn_menqiang' }
        for _, sName in PAGE2PAGEBTN.iteritems():
            btnObj = self.GetObject(sName)
            if not btnObj:
                continue
            
            btnObj.SetSelect(False)
        
        btn = self.GetObject(PAGE2PAGEBTN[iCurPage])
        btn.SetSelect(True)

    
    def GetNumberEdit(self):
        ''':rtype: autonumedit.CAutoEdit'''
        if not self.m_oBuyAmountEdit:
            self.m_oBuyAmountEdit = combmacro.CEDIT(autonumedit.CAutoEdit, 'amount_edit', self, 16777215, interface.FontLT14, 16777215)
            self.m_oBuyAmountEdit.Active(True)
            self.m_oBuyAmountEdit.SetNumChangedCallBack(self.OnNumEditChangedCallBack)
        
        return self.m_oBuyAmountEdit

    
    def GetTableData(self):
        return self.m_lTableData

    
    def GetTableView(self):
        ''':rtype: ui.CTableView'''
        if not self.m_oTableView:
            oTableView = self.GetObject('tableview')
            self.m_oTableView = oTableView
            self.m_oTableView.SetDefaultCellSize(55)
            oTableView.SetDefaultCellAlign(interface.ALIGN_LEFT)
            oTableView.SetDelegateNumberOfCells(self.TableViewDelegateNumberOfCells)
            oTableView.SetDelegateNewCellOfIndex(self.TableViewDelegateNewCellOfIndex)
            oTableView.SetDelegateUpdateCellOfIndex(self.TableViewDelegateUpdateCellOfIndex)
            oTableView.SetShowRowLine(False)
            oTableView.SetShowBgLine(False)
        
        return self.m_oTableView

    
    def TableViewDelegateNumberOfCells(self):
        lData = self.GetTableData()
        nLen = len(lData)
        if nLen < 21:
            return 21
        else:
            return ((nLen + 2) / 3) * 3

    
    def TableViewDelegateUpdateCellOfIndex(self, oCell, iIndex, bReused):
        lData = self.GetTableData()
        oData = None
        if iIndex < len(lData):
            oData = lData[iIndex]
        
        oCell.SetFurInfo(oData, iIndex, self.GetSelectData() == oData)
        return oCell

    
    def TableViewDelegateNewCellOfIndex(self, oContainer, iIndex):
        lData = self.GetTableData()
        oData = None
        if iIndex < len(lData):
            oData = lData[iIndex]
        
        oCell = dlgfuritem.CFurItem(oContainer)
        oCell.SetSelectCallBack(self.TbOnSelectCallBack)
        oCell.SetFurInfo(oData, iIndex, self.GetSelectData() == oData)
        return oCell

    
    def TbOnSelectCallBack(self, iIndex, bAdd):
        self.RefreshSelectCellView(iIndex)
        self.ssEmit(self.SS_SELECTINDEX, iIndex, bAdd)

    
    def RefreshSelectCellView(self, iIndex):
        dCell = self.GetTableView().GetAllCell()
        for _, oCell in dCell.iteritems():
            bSelect = iIndex == oCell.GetIndex()
            oCell.SetSelect(bSelect)
        

    
    def RefreshTableView(self, lData, iDestIndex = -1):
        self.m_lTableData = lData
        oTableView = self.GetTableView()
        oTableView.Reload(iDestIndex)

    
    def RefreshSelectView(self, dResult):
        iIndex = dResult['index']
        self.RefreshSelectCellView(iIndex)
        sCost = dResult.get('cost', '')
        sGold = dResult.get('gold', '0')
        iMaxNum = dResult.get('maxnum', 0)
        nShapeID = dResult['shapeID']
        self.GetObject('txt_totalprice').SetText(sCost)
        self.GetObject('txt_curgold').SetText(sGold)
        sCurText = self.GetNumberEdit().GetText()
        sNum = dResult.get('num', '')
        self.GetNumberEdit().SetMaxNum(iMaxNum)
        if sCurText != sNum:
            self.GetNumberEdit().SetText(sNum)
        
        self.RefreshSelectItemView(nShapeID)

    
    def RefreshSelectItemView(self, nShapeID):
        import yardfurniturepreview
        import yarddefines
        for sUIName in ('bg_water', 'bg_preview'):
            oObj = self.GetObject(sUIName)
            oObj.SetShow(False)
        
        bScale = False
        if hasattr(self.m_oFurObj, 'IsScale'):
            bScale = self.m_oFurObj.IsScale()
        
        self.SetShowObject('btn_MaxPreview', bScale)

    
    def OnNumEditChangedCallBack(self, iNum):
        self.ssEmit(self.SS_BUYNUMCHANGED, iNum)
