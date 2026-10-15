# pycdc 交叉复核产物 · script.fls entry 2687
# co_filename(原始)='script/yard/yardmap/mainui/yardfurlistdlg.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2687.pyc (Python 2.5)

import combdialog
import delegateyardfurlistdlg
import interface
g_FurListDlg = None

def ModuleReset():
    global g_FurListDlg
    g_FurListDlg = None


def SwitchOpeFurListDlg(lData):
    global g_FurListDlg
    if not g_FurListDlg:
        g_FurListDlg = CYardFurListDlg()
    
    g_FurListDlg.RefreshData(lData)


def CloseDlg():
    global g_FurListDlg
    g_FurListDlg = None


class CYardFurListDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog4/yard/furniturelist.dlg')
        self.m_oTitleTableView = None
        interface.Center(self)
        self.m_oDelegate = delegateyardfurlistdlg.CDelegateYardFurListDlg(self)

    
    def RefreshData(self, lData):
        self.m_oDelegate.OnEventRefreshData(lData)

    
    def GetTableView(self):
        if not self.m_oTitleTableView:
            oTitleTableView = self.GetObject('fur_tableview')
            self.m_oTitleTableView = oTitleTableView
            self.m_oTitleTableView.SetDefaultCellSize(60)
            self.m_oTitleTableView.SetSelectMode(1)
            oTitleTableView.SetDelegateNewCellOfData(self.TbDelegateNewCellOfData)
            oTitleTableView.SetDelegateUpdateCellOfData(self.TbDelegateUpdateCellOfData)
        
        return self.m_oTitleTableView

    
    def TbDelegateUpdateCellOfData(self, oCell, oData, bReused):
        oCell.SetData(oData, self.m_oTitleTableView.GetColumnWidths(), self.m_oTitleTableView.GetDataSource())
        return oCell

    
    def TbDelegateNewCellOfData(self, oContainer, oData):
        import yardeditstatisticmapfurniture
        oCell = self.m_oTitleTableView.CreateTitleTableCell(oContainer, yardeditstatisticmapfurniture.CFurCell)
        return oCell

    
    def GetSelectData(self):
        lResult = None().GetTableView().GetSelectedData()
        oSelectData = None if not lResult else lResult[0]
        return oSelectData

    
    def RefreshTableView(self, lSort, iSelect):
        oTitleTableView = self.GetTableView()
        oTitleTableView.SetDataSource(lSort)
        oTitleTableView.Reload()
        if iSelect != -1:
            oTitleTableView.SelectIndex(iSelect, True)
        else:
            oTitleTableView.ClearSelect()

    
    def RefreshNumTxt(self, sTxt):
        self.GetObject('richtxt_furnum').SetText(sTxt)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 3:
            CloseDlg()
