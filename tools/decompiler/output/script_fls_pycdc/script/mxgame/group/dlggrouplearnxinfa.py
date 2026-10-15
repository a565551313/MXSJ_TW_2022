# pycdc 交叉复核产物 · script.fls entry 1646
# co_filename(原始)='script/mxgame/group/dlggrouplearnxinfa.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1646.pyc (Python 2.5)

import slot
import interface
import combdialog
import ui
import delegategroup
g_LearnXinfaDlg = None

def ModuleReset():
    global g_LearnXinfaDlg
    g_LearnXinfaDlg = None


def ShowLearnXinfaDlg():
    global g_LearnXinfaDlg
    if g_LearnXinfaDlg is None:
        g_LearnXinfaDlg = CLearnXinfaDlg()
    else:
        g_LearnXinfaDlg.SetShow(True)
        g_LearnXinfaDlg.Topmost()


class CLearnXinfaDlg(combdialog.CCombDialog, slot.ISignalSubject):
    SS_LearnXinfa = 'SS_LearnXinfa(iSkillID)'
    SS_SelectXinfa = 'SS_SelectXinfa(iXinfaID)'
    SS_ShowMyXinfa = 'SS_ShowMyXinfa()'
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/group/newgroup/learn_xinfa.dlg')
        self.ssInit()
        interface.Center(self)
        self.m_DelegateList = []
        self.InitDelegate()
        self.InitCB()
        self.AfterOpenDialog()

    
    def SetCost(self, sCost, iColor):
        self.GetObject('txt_cost').SetText(sCost)
        self.GetObject('txt_cost').SetColor(iColor)

    
    def SetZiCai(self, sZiCai, iColor):
        self.GetObject('txt_zicai').SetText(sZiCai)
        self.GetObject('txt_zicai').SetColor(iColor)

    
    def SetTimes(self, iTimes):
        self.GetObject('txt_times').SetText(str(iTimes))

    
    def RefreshCanLearnXinfaList(self, dSkillInfoList, bClickNew):
        oList = self.GetObject('lst_skills')
        oList.Clear()
        oClickIt = None
        for dSkillInfo in dSkillInfoList:
            oIt = oList.AddBoxItem()
            oIt.m_Real = CXinfaItem(oIt, dSkillInfo['sName'], dSkillInfo['bNew'], dSkillInfo['iXinfaID'])
            if bClickNew and dSkillInfo['bNew']:
                oClickIt = oIt
                continue
        
        if not oClickIt:
            if dSkillInfoList:
                oClickIt = oList.GetItemByIndex(0)
            
        
        if oClickIt:
            pass
        oClickIt.LeftUp()
        oList.ResetItems()
        oList.ResetScrollBar()

    
    def RefreshSkillTable(self, dSkillInfoList):
        oTable = self.GetObject('tab_detail')
        oTable.Clear()
        for dSkillInfo in dSkillInfoList:
            oIt = oTable.AddBoxItem()
            iNameW = oTable.GetItemWidth(0)
            iDescW = oTable.GetItemWidth(2)
            (_, iItemH) = oTable.GetItemSize()
            oName = ui.CTextObjext(oIt, iNameW, iItemH, dSkillInfo['sName'], interface.FontLT14_3, interface.COLOR_1, bAutoNxt = True, iAlign = interface.ALIGN_CENTER_MIDDLE)
            
            try:
                oImg = ui.CImage(oIt, dSkillInfo['sPath'], dSkillInfo['sPack'])
            except:
                oImg = ui.CImage(oIt, '0000.igs', 'passive')

            oDesc = ui.CRichTextObject(oIt, iDescW, iItemH, dSkillInfo['sDesc'], interface.FontLT14_3, interface.COLOR_1)
            oTable.AddItemExtend(oIt, [
                oName,
                oImg,
                oDesc], bChangeColor = False)
        
        oTable.ResetItems()
        oTable.ResetScrollBar()

    
    def SetMyXinfaName(self, sName):
        self.GetObject('txt_my_xinfa').SetText(sName)

    
    def SetMyXinfaOutTime(self, bOutTime):
        self.GetObject('txt_out_time').SetShow(bOutTime)

    
    def ClearXinfaListSelect(self):
        oList = self.GetObject('lst_skills')
        for oItem in oList.GetItems():
            oItem.Select(False)
        

    
    def SetSelectXinfaItem(self, iXinfaID):
        oList = self.GetObject('lst_skills')
        for oItem in oList.GetItems():
            if oItem.m_Real.GetXinfaID() == iXinfaID:
                oItem.LeftUp()
                break
                continue
        

    
    def InitDelegate(self):
        self.m_DelegateList = [
            delegategroup.CLearnXinfaDelegate(self)]

    
    def InitCB(self):
        import commoncb
        commoncb.RegistCB(commoncb.WAR_START, self, 'OnWarStart')

    
    def OnWarStart(self):
        self.CloseWindow()

    
    def LearnXinfa(self):
        self.ssEmit(self.SS_LearnXinfa, self.GetSelectSkillID())

    
    def ShowMyXinfa(self):
        self.ssEmit(self.SS_ShowMyXinfa)

    
    def SelectXinfa(self, iIdx):
        oList = self.GetObject('lst_skills')
        oIt = oList.GetItemByIndex(iIdx)
        if oIt is None:
            return None
        
        self.ssEmit(self.SS_SelectXinfa, oIt.m_Real.GetXinfaID())

    
    def GetSelectSkillID(self):
        oList = self.GetObject('lst_skills')
        oItem = oList.GetSelectItem()
        if not oItem:
            return None
        
        return oItem.m_Real.GetXinfaID()

    
    def CloseWindow(self):
        global g_LearnXinfaDlg
        g_LearnXinfaDlg = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 4:
            self.LearnXinfa()
        elif iMsgID == 5:
            self.ShowMyXinfa()
        elif iMsgID < iMsgID:
            pass
        elif iMsgID < 300:
            self.SelectXinfa(iMsgID - 201)
        



class CXinfaItem(combdialog.CCombDialog):
    
    def __init__(self, oParent, sName, bNew, iXinfaID):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/group/newgroup/learn_xinfa_skill_it.dlg')
        interface.Center(self)
        self.Enable(False)
        self.m_sName = sName
        self.m_bNew = bNew
        self.m_iXinfaID = iXinfaID
        if not self.InitDlg:
            pass
        self.InitDlg
        self.AfterOpenDialog()

    
    def SetName(self, sName):
        self.GetObject('txt_name').SetText(sName)

    
    def SetNew(self, bNew):
        self.GetObject('txt_new').SetShow(bNew)

    
    def GetXinfaID(self):
        return self.m_iXinfaID

    
    def InitDlg(self):
        self.SetName(self.m_sName)
        self.SetNew(self.m_bNew)
