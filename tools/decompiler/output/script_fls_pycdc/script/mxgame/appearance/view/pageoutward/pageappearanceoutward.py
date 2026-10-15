# pycdc 交叉复核产物 · script.fls entry 3766
# co_filename(原始)='script/mxgame/appearance/view/pageoutward/pageappearanceoutward.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3766.pyc (Python 2.5)

'''
================================================================================
\xd7\xf7\xd5\xdf: jiangweichao
\tpageappearanceoutward\xa3\xba\xd1\xd5\xd6\xb5\xb9\xdd\xcd\xe2\xb9\xdb\xb7\xd6\xd2\xb3\xbd\xe7\xc3\xe6
================================================================================
'''
import appearancepagebase
import combdialog
import delegateappearanceoutward
import appearancedefine
import slot
import delegateroleview
import permission

def CanOpenOutwardDlg():
    return True


class CPageOutWard(appearancepagebase.CAppearancePageBase, combdialog.CCombSubWnd, slot.ISignalSubject):
    S_TOP_BTN_NAME_TUPLE = ('btn_heroshape', 'btn_wing', 'btn_back', 'btn_aura', 'btn_footprint', 'btn_weapon')
    
    def __init__(self, pContext, pMainDlg):
        appearancepagebase.CAppearancePageBase.__init__(self, pContext, pMainDlg)
        if permission.IsTestServerByNewYanzhiguan():
            combdialog.CCombSubWnd.__init__(self, pMainDlg, 'dialog4/appearance_newstyle/appearance/appearance_main.dlg')
        else:
            combdialog.CCombSubWnd.__init__(self, pMainDlg, 'dialog4/appearance/appearance/appearance_main.dlg')
        self.m_lTopBtnPos = []
        self.InitTopBtnPosList()
        self.m_pDelegate = delegateappearanceoutward.CDelegateOutward(self, pContext)
        self.m_oDelegateRoleView = delegateroleview.CDelegateRoleView(self, pContext)
        self.m_dSubPage = { }
        self.m_nPage = None
        self.SetIgnoreEsc(True)

    
    def VOpenPage(self, dExtend = None):
        self.m_pDelegate.OnOpenPage(dExtend)

    
    def VClose(self):
        self.m_pDelegate.OnClose()

    
    def GetCurPageID(self):
        return self.m_nPage

    
    def GetPage(self, nPage):
        return self.m_dSubPage.get(nPage, None)

    
    def GetPageCreateIfNeeded(self, nPage):
        '''\xc0\xf2\xb1opage \xa6p\xaaG\xa4\xa3\xa6s\xa6b\xabh\xb3\xd0\xab\xd8
\t\t:param int nPage: \xa4\xc0\xad\xb6ID
\t\t:return:CPageBase oPage
\t\t'''
        import appearancepagefactory
        pPage = self.GetPage(nPage)
        if not pPage:
            pContext = self.GetContext()
            pPage = appearancepagefactory.CreateOutwardPage(nPage, self, pContext)
            self.m_dSubPage[nPage] = pPage
        
        return pPage

    
    def OpenSubPage(self, nPage, dExData = None):
        '''\xa5\xb4\xb6}\xa4\xc0\xad\xb6
\t\t:param int nPage:\t\xa4\xc0\xad\xb6ID
\t\t:param dict dExData:\xa4\xc0\xad\xb6\xbc\xc6\xbe\xda
\t\t:return: CPageBase oPage
\t\t'''
        pContext = self.GetContext()
        pContext.RecordLastExtend('subpage', nPage)
        if self.m_nPage != nPage:
            pPage = self.GetPage(self.m_nPage)
            if pPage:
                pPage.VClose()
            
            self.m_nPage = nPage
            pPage = self.GetPage(self.m_nPage)
            if not pPage:
                pPage = self.GetPageCreateIfNeeded(nPage)
            
            if pPage:
                pPage.VOpenPage(dExData)
            
        else:
            self.m_nPage = nPage
            pPage = self.GetPage(self.m_nPage)
            if not pPage:
                pPage = self.GetPageCreateIfNeeded(nPage)
            
            if pPage:
                pPage.VOpenPage(dExData)
            
        self.RefreshBtnState()

    
    def RefreshBtnState(self):
        PAGE2PAGEBTN = {
            appearancedefine.SUB_PAGE_HERO: self.S_TOP_BTN_NAME_TUPLE[0],
            appearancedefine.SUB_PAGE_WEAPON: self.S_TOP_BTN_NAME_TUPLE[5],
            appearancedefine.SUB_PAGE_WING: self.S_TOP_BTN_NAME_TUPLE[1],
            appearancedefine.SUB_PAGE_AURA: self.S_TOP_BTN_NAME_TUPLE[3],
            appearancedefine.SUB_PAGE_FOOTPRINT: self.S_TOP_BTN_NAME_TUPLE[4],
            appearancedefine.SUB_PAGE_BACKDECORATION: self.S_TOP_BTN_NAME_TUPLE[2] }
        for v in PAGE2PAGEBTN.values():
            btnObj = self.GetObject(v)
            btnObj.Enable(True)
            btnObj.SetSelect(False)
        
        btn = self.GetObject(PAGE2PAGEBTN[self.m_nPage])
        btn.SetSelect(True)
        btn.Enable(False)

    
    def InitTopBtnPosList(self):
        for sName in self.S_TOP_BTN_NAME_TUPLE:
            self.m_lTopBtnPos.append(self.GetObject(sName).GetPos())
        
        self.m_lTopBtnPos.sort(key = (lambda x: x[0]))

    
    def ShowOutWardTabBtn(self, lShowList):
        BTNNAME2PAGE = {
            self.S_TOP_BTN_NAME_TUPLE[0]: appearancedefine.SUB_PAGE_HERO,
            self.S_TOP_BTN_NAME_TUPLE[5]: appearancedefine.SUB_PAGE_WEAPON,
            self.S_TOP_BTN_NAME_TUPLE[1]: appearancedefine.SUB_PAGE_WING,
            self.S_TOP_BTN_NAME_TUPLE[3]: appearancedefine.SUB_PAGE_AURA,
            self.S_TOP_BTN_NAME_TUPLE[4]: appearancedefine.SUB_PAGE_FOOTPRINT,
            self.S_TOP_BTN_NAME_TUPLE[2]: appearancedefine.SUB_PAGE_BACKDECORATION }
        iShowNum = 0
        for sName in self.S_TOP_BTN_NAME_TUPLE:
            if BTNNAME2PAGE[sName] in lShowList:
                self.GetObject(sName).SetShow(True)
                self.GetObject(sName).SetPos(*self.m_lTopBtnPos[iShowNum])
                iShowNum += 1
                continue
            self.GetObject(sName).SetShow(False)
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.m_pDelegate.OnSwitchPage(appearancedefine.SUB_PAGE_HERO)
        elif iMsgID == 2:
            if self.m_pDelegate.OnSwitchPage:
                pass
            elif iMsgID == 3:
                self.m_pDelegate.OnSwitchPage(appearancedefine.SUB_PAGE_WING)
            elif iMsgID == 4:
                self.m_pDelegate.OnSwitchPage(appearancedefine.SUB_PAGE_AURA)
            elif iMsgID == 5:
                self.m_pDelegate.OnSwitchPage(appearancedefine.SUB_PAGE_FOOTPRINT)
            elif iMsgID == 6:
                self.m_pDelegate.OnSwitchPage(appearancedefine.SUB_PAGE_BACKDECORATION)
