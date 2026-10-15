# pycdc 交叉复核产物 · script.fls entry 4308
# co_filename(原始)='script/mxgame/newgroup/view/pagewelfare/pagegroupwelfare.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4308.pyc (Python 2.5)

import misc
import grouppagebase
import delegategroupwelfare
import combdialog
import groupdefines
import pagedgtbase
import pagedlgbase
import slot
import clickcounter

class CGroupPageWelfare(grouppagebase.CGroupPageBase, combdialog.CCombSubWnd, pagedlgbase.CPageDlgBase, slot.ISignalSubject):
    SS_OnOpenDlg = 'OnOpenDlg(dExtend)'
    
    def __init__(self, pContext, pMainDlg):
        grouppagebase.CGroupPageBase.__init__(self, pContext, pMainDlg)
        pagedlgbase.CPageDlgBase.__init__(self)
        combdialog.CCombSubWnd.__init__(self, pMainDlg, 'dialog/group_new/group_fuli/group_fulimain.dlg')
        self.ssInit()
        self.m_pDelegate = None
        self.InitDelegate(pContext)

    
    def InitShowLogic(self):
        import sh\xb8\xa0\xbb\xb8\xb0\xbe\xb4\x88\xb0\xa5\xb8\xa2\xa7\xa0\xb2\xbb\xb1\xb6\xa5\xb2
        self.m_oShowLogic = sh\xb8\xa0\xbb\xb8\xb0\xbe\xb4\x88\xb0\xa5\xb8\xa2\xa7\xa0\xb2\xbb\xb1\xb6\xa5\xb2.CShowLogicGroupWelfare(self)

    
    def InitDelegate(self, pContext):
        self.m_pDelegate = delegategroupwelfare.CDelegateGroupWelfare(self, pContext, [
            'btn_shop',
            'btn_fuli',
            'btn_wages',
            'btn_wages_001',
            'btn_skill',
            'btn_xinfa'])

    
    def VOpenPage(self, dExtend = None):
        self.ssEmit(self.SS_OnOpenDlg, dExtend)

    
    def VClose(self):
        self.ssEmit(self.SS_CloseDlg)

    
    def GetCurPageID(self):
        return self.m_nPage

    
    def GetPage(self, nPage):
        return self.m_dSubPage.get(nPage, None)

    
    def GetPageCreateIfNeeded(self, nPage):
        '''\xc0\xf2\xb1opage \xa6p\xaaG\xa4\xa3\xa6s\xa6b\xabh\xb3\xd0\xab\xd8
\t\t:param int nPage: \xa4\xc0\xad\xb6ID
\t\t:return:CPageBase oPage
\t\t'''
        import grouppagefactory
        pPage = self.GetPage(nPage)
        if not pPage:
            pContext = self.GetContext()
            pPage = grouppagefactory.CreateWarefarePage(nPage, self, pContext)
            self.m_dSubPage[nPage] = pPage
        
        return pPage

    
    def CheckIdOpenSkillPage(self):
        import groupcontext
        oDateMgr = groupcontext.Get().GetGroupDataMgr()
        oBuildData = oDateMgr.GetBuildData()
        bShow = False
        if oBuildData.get(groupdefines.ROOM_STUDY):
            oAcademeLevel = oBuildData[groupdefines.ROOM_STUDY][0]
            bShow = oAcademeLevel >= 1
        
        for sUIBtn in ('btn_skill', 'btn_xinfa'):
            pBtn = self.GetObject(sUIBtn)
            if pBtn:
                pBtn.SetShow(bShow)
                continue
        

    
    def OnMessage(self, iMessageID):
        if iMessageID in (2, 3, 4, 5, 6, 7):
            self.ssEmit(self.SS_ClickBtn, iMessageID)
            clickcounter.Log(groupdefines.WELFARE_PAGEBTN_TO_CLICKTEXT.get(iMessageID, '\xa5\xbc\xaa\xbe\xad\xb6%s' % iMessageID))
