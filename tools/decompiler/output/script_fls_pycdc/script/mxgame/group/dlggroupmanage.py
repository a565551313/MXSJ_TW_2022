# pycdc 交叉复核产物 · script.fls entry 3286
# co_filename(原始)='script/mxgame/group/dlggroupmanage.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3286.pyc (Python 2.5)

import combdialog
import interface
import netgroup
import groupmgr
import group
g_GroupMangeDlg = None

def ModuleReset():
    global g_GroupMangeDlg
    g_GroupMangeDlg = None


def GetGroupMangeDlg():
    return g_GroupMangeDlg


def SetShow(bShow, sSelectBtnName = 'btn_tang'):
    global g_GroupMangeDlg, g_GroupMangeDlg
    oMgr = groupmgr.GetMgr()
    if not oMgr.GetOpenShuYuan() and not oMgr.IsGroupLeader():
        return None
    
    if bShow:
        if not g_GroupMangeDlg:
            g_GroupMangeDlg = CGroupManageDialog(sSelectBtnName)
        
        g_GroupMangeDlg.SetShow(True)
    else:
        g_GroupMangeDlg = None


def RefreshSkill(skillID):
    if not g_GroupMangeDlg:
        return None
    
    g_GroupMangeDlg.RefreshOneSkill(skillID)


def RefreshZicai(iTotalZicai):
    if not g_GroupMangeDlg:
        return None
    
    g_GroupMangeDlg.OnRefreshTotalZicai(iTotalZicai)


def RefreshArrangeTaskList(tTaskList):
    if not g_GroupMangeDlg:
        return None
    
    g_GroupMangeDlg.RefreshArrangeTaskList(tTaskList)


class CGroupManageDialog(combdialog.CCombDialog):
    
    def __init__(self, sSelectBtnName):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/group/newgroup/dlggroupmanage.dlg')
        interface.Center(self)
        self.m_oArrangeTaskDlg = None
        self.m_oResearchSkill = None
        self.m_oMangeXinfaDlg = None
        self.m_oLearnSkill = None
        self.m_oSkillStudy = None
        self.SetDefaultSelect(sSelectBtnName)
        self.ShowLimitBtn()
        self.SetShowRedPoint()

    
    def OnRefreshResearch(self, skill):
        if self.m_oResearchSkill:
            self.m_oResearchSkill.Refresh(skill)
        

    
    def OnRefreshSkill(self, skilllist):
        if self.m_oLearnSkill:
            self.m_oLearnSkill.RefreshList(skilllist)
        

    
    def OnRefreshTotalZicai(self, iTotalZicai):
        if self.m_oLearnSkill:
            self.m_oLearnSkill.SetTotalZicai(iTotalZicai)
        

    
    def OnSetActiveSkill(self, iSkillID):
        if self.m_oResearchSkill:
            self.m_oResearchSkill.SetActiveSkill(iSkillID)
        

    
    def RefreshOneSkill(self, iSkillID):
        if self.m_oLearnSkill:
            self.m_oLearnSkill.Refresh(iSkillID)
        
        self.AfterOpenDialog()

    
    def HideAllChild(self):
        if self.m_oArrangeTaskDlg:
            self.m_oArrangeTaskDlg.SetShow(False)
        
        if self.m_oResearchSkill:
            self.m_oResearchSkill.SetShow(False)
        
        if self.m_oMangeXinfaDlg:
            self.m_oMangeXinfaDlg.SetShow(False)
        
        if self.m_oLearnSkill:
            self.m_oLearnSkill.SetShow(False)
        
        if self.m_oSkillStudy:
            self.m_oSkillStudy.SetShow(False)
        

    
    def SetDefaultSelect(self, sSelectBtnName):
        oBtn = self.GetObject(sSelectBtnName)
        oBtn.LeftUp()

    
    def SetShowRedPoint(self):
        oRedPointImg = self.GetObject('img_red')
        oMgr = groupmgr.GetMgr()
        bIsLeader = oMgr.IsGroupLeader()
        bHasRedPoint = oMgr.HasRedPoint()
        if bIsLeader and bHasRedPoint:
            oRedPointImg.SetShow(True)
            oMgr.SetGroupDataByKey('iRed', 0)
        else:
            oRedPointImg.SetShow(False)

    
    def ShowLimitBtn(self):
        oMgr = groupmgr.GetMgr()
        bIsLeader = oMgr.IsGroupTopLeader()
        if bIsLeader:
            self.GetObject('btn_tang').SetText('\xa9e\xa5\xf4\xa5\xf4\xb0\xc8')
            self.GetObject('btn_record').SetText('\xba\xde\xb2z\xa4\xdf\xaak')
            self.GetObject('btn_Task').SetText('\xbe\xc7\xb2\xdf\xa7\xde\xaf\xe0')
        else:
            self.GetObject('btn_tang').SetText('\xbe\xc7\xb2\xdf\xa7\xde\xaf\xe0')
            self.GetObject('btn_SkillStudy').SetShow(False)
            self.GetObject('btn_Task').SetShow(False)
            self.GetObject('btn_record').SetShow(False)

    
    def OnCloseWindow(self):
        global g_GroupMangeDlg
        if self.m_oLearnSkill:
            self.m_oLearnSkill.OnCloseWindow()
        
        g_GroupMangeDlg = None

    
    def OnArrangeTask(self):
        import dlggrouptask
        self.HideAllChild()
        if not self.m_oArrangeTaskDlg:
            self.m_oArrangeTaskDlg = dlggrouptask.CDeputeDialog(self)
            (x, y, _, _) = self.GetLocData('loc_child')
            self.m_oArrangeTaskDlg.SetPos(x, y)
        
        self.m_oArrangeTaskDlg.SetShow(True)
        netgroup.C2SOpenDepute()
        None.dlggrouptask.SetShowRedPoint()

    
    def OnResearchSkill(self):
        import dlgresearchxskill
        self.HideAllChild()
        if not self.m_oResearchSkill:
            self.m_oResearchSkill = dlgresearchxskill.CResearchSkillDlg(self)
            (x, y, _, _) = self.GetLocData('loc_child')
            self.m_oResearchSkill.SetPos(x, y)
        
        netgroup.C2SOpenResearchSkill()
        self.m_oResearchSkill.SetShow(True)
        self.SetShowRedPoint()

    
    def OnMangeXinfa(self):
        import dlggroupmgrxinfa
        self.HideAllChild()
        if not self.m_oMangeXinfaDlg:
            self.m_oMangeXinfaDlg = dlggroupmgrxinfa.CLearnXinfaDlg(self)
            (x, y, _, _) = self.GetLocData('loc_child')
            self.m_oMangeXinfaDlg.SetPos(x, y)
        
        netgroup.C2SOpenManageXinfa()
        self.m_oMangeXinfaDlg.SetShow(True)

    
    def OnGroupSkillStudy(self):
        '''\xa7\xde\xaf\xe0\xac\xe3\xa8s'''
        self.HideAllChild()
        import dlggroupskillstudy
        if not self.m_oSkillStudy:
            self.m_oSkillStudy = dlggroupskillstudy.CGroupSkillStudy(self)
        else:
            self.m_oSkillStudy.RefreshView()
        self.m_oSkillStudy.SetShow(True)

    
    def OnLearnSkill(self):
        import dlgresearchxskill
        self.HideAllChild()
        if not self.m_oLearnSkill:
            self.m_oLearnSkill = dlgresearchxskill.CLearnSkillDlg(self)
            (x, y, _, _) = self.GetLocData('loc_child')
            self.m_oLearnSkill.SetPos(x, y)
        
        netgroup.C2SOpenLearnSkill()
        self.m_oLearnSkill.SetShow(True)
        self.SetShowRedPoint()

    
    def ID2Function(self, iMsgid):
        oMgr = groupmgr.GetMgr()
        bIsLeader = oMgr.IsGroupTopLeader()
        if iMsgid == 3:
            if bIsLeader:
                self.OnArrangeTask()
            else:
                self.OnLearnSkill()
        elif iMsgid == 5:
            self.OnMangeXinfa()
        elif iMsgid == 2:
            self.OnLearnSkill()
        elif iMsgid == 4:
            self.OnResearchSkill()
        

    
    def OnMessage(self, iMsgId):
        if iMsgId == 1:
            self.OnCloseWindow()
        elif iMsgId in xrange(2, 6):
            self.ID2Function(iMsgId)
        elif iMsgId == 6:
            self.OnGroupSkillStudy()
