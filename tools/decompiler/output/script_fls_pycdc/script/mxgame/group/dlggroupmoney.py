# pycdc 交叉复核产物 · script.fls entry 3831
# co_filename(原始)='script/mxgame/group/dlggroupmoney.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3831.pyc (Python 2.5)

import combdialog
import interface
import group
g_MoneyDlg = None

def ModuleReset():
    global g_MoneyDlg
    g_MoneyDlg = None


def Show():
    global g_MoneyDlg
    if not g_MoneyDlg:
        g_MoneyDlg = CGroupMoneyDlg()
    


def Refresh(dList, iThisWeekMoney, iLastWeekMoney, tPlayerInfoList):
    if not g_MoneyDlg:
        return None
    
    g_MoneyDlg.RefreshTable(dList, iThisWeekMoney, iLastWeekMoney, tPlayerInfoList)


class CGroupMoneyDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/group/newgroup/wages.dlg')
        self.m_oTable = self.GetObject('tab_member')
        interface.Center(self)
        self.m_tPlayerInfoList = []
        self.m_oHotArea = None
        self.InitHotArea()
        self.AfterOpenDialog()

    
    def InitHotArea(self):
        oPar = self.GetObject('text_devote')
        (w, h) = oPar.GetSize()
        self.m_oHotArea = CHotArea(oPar, w, h, alpha = 0)

    
    def RefreshTable(self, iList, iThisWeekMoney, iLastWeekMoney, tPlayerInfoList):
        self.m_oTable.\x85\xaa\xa3\xa7\xb4()
        self.m_tPlayerInfoList = tPlayerInfoList
        for dInfo in iList:
            oBox = self.m_oTable.AddBoxItem()
            oItemList = []
            sName = dInfo['name']
            iAffair = dInfo['affair']
            sAffair = group.lv2txt(iAffair)
            iLastMoney = dInfo['last']
            iCurMoney = dInfo['cur']
            for sTxt in (sName, sAffair, str(iCurMoney), str(iLastMoney)):
                oItem = interface.CTextObject(oBox, sTxt, interface.FontLT14, interface.COLOR_1)
                oItemList.append(oItem)
            
            dAlignInfo = { }
            dAlignInfo['iAlign'] = interface.ALIGN_CENTER_MIDDLE
            dAlignInfo['tOffset'] = (0, 0)
            self.m_oTable.AddItemExtend(oBox, oItemList, dAlignInfo = dAlignInfo, bChangeColor = False)
        
        self.m_oTable.ResetItems()
        self.m_oTable.ResetScrollBar()
        self.RefreshAllMoney(iThisWeekMoney, iLastWeekMoney)

    
    def RefreshAllMoney(self, iThisWeekMoney, iLastWeekMoney):
        iExraMoney = 0
        if self.m_tPlayerInfoList:
            for sName, iMoney in self.m_tPlayerInfoList:
                iExraMoney += iMoney
            
        
        sTxt = str(iThisWeekMoney)
        if iExraMoney:
            sTxt += ' + %d' % iExraMoney
        
        self.GetObject('text_devote').SetText(sTxt)
        self.GetObject('text_devot1').SetText(str(iLastWeekMoney))

    
    def OnHotEnter(self):
        import wrapinterface
        if not self.m_tPlayerInfoList:
            return None
        
        sTxt = ''
        for sName, iMoney in enumerate(self.m_tPlayerInfoList):
            sTxt += '#G%s#n\xc3B\xa5~\xb5o\xa9\xf1\xa4F%d\xa4u\xb8\xea' % (sName, iMoney)
            if idx != len(self.m_tPlayerInfoList) - 1:
                sTxt += '#r'
                continue
        
        if not sTxt:
            return None
        
        self.m_oTips = wrapinterface.CTextTips(self, -1, sTxt, interface.FontLT14_3, direct = 1)

    
    def OnHotLeave(self):
        self.m_oTips = None

    
    def CloseWindow(self):
        global g_MoneyDlg
        g_MoneyDlg = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 5:
            import netgroup
            netgroup.C2SPackGroupMoney()
        



class CHotArea(interface.CClickBox):
    
    def Enter(self):
        oIt = self.GetParent().GetParent()
        if oIt:
            oIt.OnHotEnter()
        

    
    def Leave(self):
        oIt = self.GetParent().GetParent()
        if oIt:
            oIt.OnHotLeave()
