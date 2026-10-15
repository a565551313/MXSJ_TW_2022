# pycdc 交叉复核产物 · script.fls entry 4426
# co_filename(原始)='script/dialog/skillmagic/combineskill/dgtcombineskill.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4426.pyc (Python 2.5)

import combineskilldefine
import delegatebase
import hero
import pagexinfa

class CCombineSkillDgt(delegatebase.CDelegateBase):
    
    def Init(self):
        '''
\t\t\xaa\xec\xa9l\xa4\xc6\xa8\xe7\xbc\xc6\xa1A\xb9\xea\xa8\xd2\xa4\xc6\xb8\xd3dgt\xae\xc9\xb7|\xb0\xf5\xa6\xe6\xa4@\xa6\xb8
\t\t:return:
\t\t'''
        self.m_iCurTab = combineskilldefine.TAB_PAGE_FIGHT
        self.m_iCurXinfa = pagexinfa.S_PAGE_BASE_MSGID + 101
        self.InitSigal()
        self.InitTab()

    
    def InitTab(self):
        oView = self.GetView()
        oView.OnTabFightLeftUp()

    
    def InitSigal(self):
        '''
\t\t\xaa\xec\xa9l\xa4\xc6\xabH\xb8\xb9\xa1A\xb8j\xa9w\xba\xca\xc5\xa5\xa6U\xba\xd8\xabH\xb8\xb9
\t\t:return:
\t\t'''
        oView = self.GetView()
        oView.ssConnect(oView.SS_OnBtnTabClick, self.OnBtnTabClick)
        continue
        None(oView.ssConnect.SS_OnOpenPageClick, self.OnOpenPageClick)
        oView.ssConnect(oView.SS_ClickGroupXinfa, self.OnClickGroupXinfa)
        pData = pagexinfa.GetXinfaPageData()
        if pData.IsHasGroup():
            import netgroup
            netgroup.C2SGroupGetXinfa()
        

    
    def GetClsByPage(self, iPage):
        import pageskill
        dPage2Cls = {
            combineskilldefine.PAGE_FIGHT_SKILL: pageskill.CPageSkill,
            combineskilldefine.PAGE_ASSIST_SKILL: pagexinfa.CPageXinfa }
        return dPage2Cls[iPage]

    
    def GetPageByTab(self, iTab):
        if iTab == 1:
            return combineskilldefine.PAGE_FIGHT_SKILL
        else:
            return combineskilldefine.PAGE_ASSIST_SKILL

    
    def ShowPage(self):
        oView = self.GetView()
        iPage = self.GetPageByTab(self.m_iCurTab)
        dData = None if iPage == combineskilldefine.TAB_PAGE_FIGHT else {
            'subpage': self.GetRealTab(self.m_iCurTab),
            'recieved': True }
        dInfo = {
            'iPage': iPage,
            'dData': dData }
        if self.CheckPageIsCreate(iPage):
            oView.ShowSkillPage(dInfo)
        else:
            dInfo['oClsPage'] = self.GetClsByPage(iPage)
            oView.CreateSkillPage(dInfo)

    
    def CheckPageIsOpen(self, iPage):
        oPageDict = self.GetView().GetPageSkillDict()
        if iPage in oPageDict:
            pass
        return oPageDict[iPage].GetShow()

    
    def CheckPageIsCreate(self, iPage):
        oPageDict = self.GetView().GetPageSkillDict()
        return iPage in oPageDict

    
    def GetRealTab(self, iTab):
        import pageskill
        iPage = self.GetPageByTab(self.m_iCurTab)
        if iPage == combineskilldefine.PAGE_FIGHT_SKILL:
            return pageskill.S_TYPE_ALL
        elif iPage == combineskilldefine.PAGE_ASSIST_SKILL:
            return iTab - pagexinfa.S_PAGE_BASE_MSGID
        

    
    def OnBtnTabClick(self, iMsg):
        oView = self.GetView()
        iPage = self.GetPageByTab(iMsg)
        iPrePage = self.GetPageByTab(self.m_iCurTab)
        if iPrePage != iPage:
            if self.CheckPageIsOpen(iPrePage):
                pass
            oView.CloseSkillPage(iPrePage)
        
        if iMsg > pagexinfa.S_PAGE_BASE_MSGID + pagexinfa.S_GROUP_DETAIL_BASEPAGE:
            self.m_iCurXinfa = iMsg
        
        self.m_iCurTab = iMsg
        self.ShowPage()

    
    def OnOpenPageClick(self, iMsg):
        if iMsg - pagexinfa.S_PAGE_BASE_MSGID in pagexinfa.PAGE2BTN:
            sBtnName = pagexinfa.PAGE2BTN[iMsg - pagexinfa.S_PAGE_BASE_MSGID]
            self.GetView().SetSelectTabBtn(sBtnName)
        else:
            self.GetView().SetSelectTabBtn('btn_fight')
        self.OnBtnTabClick(iMsg)

    
    def OnClickGroupXinfa(self):
        if self.GetView().IsGroupXinfaExpand():
            self.OnOpenPageClick(self.m_iCurXinfa)
