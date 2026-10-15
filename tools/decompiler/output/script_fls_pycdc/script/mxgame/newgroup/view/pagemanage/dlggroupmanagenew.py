# pycdc 交叉复核产物 · script.fls entry 924
# co_filename(原始)='script/mxgame/newgroup/view/pagemanage/dlggroupmanagenew.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_924.pyc (Python 2.5)

'''
pagegroupmanage.py
create by xian90 2019/5/25 14:09
\xc4\xa3\xbf\xe9\xb9\xa6\xc4\xdc\xcb\xb5\xc3\xf7:
'''
import combdialog
import interface
import slot
import groupdefines
import clickcounter

class CGroupManageDialog(combdialog.CCombDialog, slot.ISignalSubject):
    SS_ClickCloseBtn = 'SS_ClickCloseBtn'
    SS_SwitchToPage = 'SS_SwitchToPage(iType)'
    
    def __init__(self, pContext, sSelectBtnName = 'btn_neizheng', \xc4\xe5\xd8\xd4\xd2a = None):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/group_new/group_manage/group_manage.dlg')
        self.ssInit()
        interface.Center(self)
        self.m_dType2Page = {
            groupdefines.E_PAGE_ARRANGE_TASK: None,
            groupdefines.E_PAGE_XINFA_MANAGE: None,
            groupdefines.E_PAGE_SKILL_RESEARCH: None,
            groupdefines.E_PAGE_PERSON_STRUCTURE: None,
            groupdefines.E_PAGE_BUILD_MANAGE: None,
            groupdefines.E_PAGE_COMBINE_MANAGE: None }
        import delegategroupmanage
        self.m_pDelegate = delegategroupmanage.CDeleageteGroupManage(pContext, self, sSelectBtnName, \xc4\xe5\xd8\xd4\xd2a)
        self.InitDlg()

    
    def InitDlg(self):
        self.RefreshBtnState()

    
    def RefreshBtnState(self):
        import groupcontext
        pGroup = groupcontext.GetGroupDataMgr()
        isTopLeader = pGroup.IsGroupTopLeader()
        self.GetObject('btn_task').SetShow(isTopLeader)
        self.GetObject('btn_xinfa').SetShow(isTopLeader)
        self.GetObject('btn_task').SetShow(isTopLeader)
        self.GetObject('btn_skillresearch').SetShow(isTopLeader)
        self.GetObject('btn_quanxian').SetShow(True)
        if not isTopLeader:
            (x, y, _, _) = self.GetLocData('btn_task')
            self.GetObject('btn_quanxian').SetPos(x, y)
        
        self.GetObject('btn_combine').SetShow(isTopLeader)

    
    def HideAllChild(self):
        for pPage in self.m_dType2Page.itervalues():
            if pPage:
                pPage.SetShow(False)
                continue
        

    
    def SetDefaultSelect(self, sSelectBtnName, \xc4\xe5\xd8\xd4\xd2a = None):
        oBtn = self.GetObject(sSelectBtnName)
        oBtn.LeftUp()
        if \xc4\xe5\xd8\xd4\xd2a is not None:
            for pPage in self.m_dType2Page.itervalues():
                if pPage and pPage.GetShow():
                    pFunc = getattr(pPage, 'OnExtraMessage', None)
                    if pFunc and callable(pFunc):
                        pFunc(\xc4\xe5\xd8\xd4\xd2a)
                    
                callable(pFunc)
            
        

    
    def SetRedPointShow(self, bShow):
        self.GetObject('img_red').SetShow(bShow)

    
    def SwitchToPage(self, iType, pContext):
        self.HideAllChild()
        if iType not in self.m_dType2Page:
            return None
        
        pPage = self.m_dType2Page[iType]
        if not pPage:
            self.CreatePage(iType, pContext)
        else:
            pPage.SetShow(True)
            if iType == groupdefines.E_PAGE_SKILL_RESEARCH:
                pPage.RefreshView()
            

    
    def CreatePage(self, iType, pContext):
        import grouparrangetaskview
        import dlggrouppersonstructureview
        import groupskillresearchview
        import groupxinfamanageview
        import dlggroupbuildnew
        import dlggroupcombineview
        dType2Creator = {
            groupdefines.E_PAGE_ARRANGE_TASK: grouparrangetaskview.CGroupArrangeTaskDlg,
            groupdefines.E_PAGE_XINFA_MANAGE: groupxinfamanageview.CGroupXinFaManageDlg,
            groupdefines.E_PAGE_SKILL_RESEARCH: groupskillresearchview.CGroupSkillResearchDlg,
            groupdefines.E_PAGE_PERSON_STRUCTURE: dlggrouppersonstructureview.CGroupPersonStructureDlg,
            groupdefines.E_PAGE_BUILD_MANAGE: dlggroupbuildnew.CGroupBuildDlg,
            groupdefines.E_PAGE_COMBINE_MANAGE: dlggroupcombineview.CGroupCombineDlg }
        if iType not in dType2Creator:
            return None
        
        self.m_dType2Page[iType] = dType2Creator[iType](self, pContext)

    
    def Destroy(self):
        for pPage in self.m_dType2Page.itervalues():
            if pPage:
                pPage.Destroy()
                continue
        

    
    def CloseWindow(self):
        self.Destroy()
        self.ssEmit(self.SS_ClickCloseBtn)

    
    def OnMessage(self, iMsgId):
        if iMsgId == 1:
            self.CloseWindow()
        elif iMsgId in xrange(11, 17):
            self.ssEmit(self.SS_SwitchToPage, iMsgId - 10)
            clickcounter.Log(groupdefines.MANAGER_PAGEBTN_TO_CLICKTEXT.get(iMsgId - 10, '\xa5\xbc\xaa\xbe\xad\xb6%d' % (iMsgId - 10)))
