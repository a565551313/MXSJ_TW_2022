# pycdc 交叉复核产物 · script.fls entry 4750
# co_filename(原始)='script/dialog/mail/delegate/dgtmailcenter.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4750.pyc (Python 2.5)

import delegatebase
import dlgdailyteammain
import maildefines
import mddailyteam
import misc

class CFriendDlgDelegate(delegatebase.CDelegateBase):
    '''
\t\xa6n\xa4\xcd\xac\xc9\xad\xb1\xa4\xa4\xaa\xba\xc5\xde\xbf\xe8\xb1\xb1\xa8\xee
\t'''
    
    def Init(self):
        oView = self.GetView()
        self.m_oModel = GetModel()
        self.m_oModel.ssConnect(maildefines.SS_MD_HasSysMailStateChange, self.OnHasSysMailStateChange)
        oView.ssConnect(maildefines.SS_DlgFriend_RefreshSysMailState, self.onRefreshSysMailState)
        oView.ssConnect(oView.SS_OnBtnSearchClick, self.OnBtnSearchClick)
        oView.ssConnect(oView.SS_OnBtnTeamClick, self.OnBtnTeamClick)
        oView.ssConnect(oView.SS_OnBtnShituClick, self.OnBtnShituClick)
        oView.ssConnect(oView.SS_OnBtnAudioCardClick, self.OnBtnAudioCardClick)
        oModel = mddailyteam.GetWarTeamInfoModel()
        oModel.ssConnect(oModel.SS_UpdateTeamLeader, self.OnDailyTeamLeaderUpdate)
        oModel.ssConnect(oModel.SS_UpdateTeamApple, self.OnUpdateDailyTeamApply)
        self.In\xdc\xc1\xf1\xd9\xd2()

    
    def In\xdc\xc1\xf1\xd9\xd2(self):
        self.OnUpdateDailyTeamApply()

    
    def OnBtnSearchClick(self):
        import commonfriend
        import netfriend
        import dlgsearchfriendmain
        import searchfrienddefine
        if commonfriend.GetUnReadAmount() > 0:
            netfriend.C2SOpenApplyFriendDlg()
        else:
            dlgsearchfriendmain.SwichOpenPage(searchfrienddefine.PAGE_RECOMMAND_FRIEND)

    
    def OnBtnTeamClick(self):
        import dailyteamdefines
        import usermacro
        if misc.IsInKuafuServer():
            usermacro.PROMPT_MSG('\xbd\xd0\xa6^\xa8\xec\xad\xec\xaaA\xa8\xcf\xa5\xce\xa6\xb9\xa5\\\xaf\xe0')
            return None
        
        oModel = mddailyteam.GetWarTeamInfoModel()
        if oModel.GetTeamApple():
            dlgdailyteammain.ShowWarTeamDlg(dailyteamdefines.PAGE_RECKLPM)
        else:
            dlgdailyteammain.ShowWarTeamDlg()
        self.GetView().SetWarTeamRedPoint(False)

    
    def OnBtnShituClick(self):
        import dlgnewshitumain
        dlgnewshitumain.OpenNewShituDlg()

    
    def OnBtnAudioCardClick(self):
        import netvoicecard
        import hero
        import usermacro
        if misc.IsInKuafuServer():
            usermacro.PROMPT_MSG('\xbd\xd0\xa6^\xa8\xec\xad\xec\xaaA\xa8\xcf\xa5\xce\xb8\xd3\xa5\\\xaf\xe0')
        else:
            netvoicecard.C2GSOpenUI(hero.GetHeroID())

    
    def OnDailyTeamLeaderUpdate(self):
        bInWarTeam = mddailyteam.IsInWarTeam()
        self.GetView().SetWarTeamShow(bInWarTeam)
        iNewTeamLeader = mddailyteam.GetWarTeamInfoModel().GetWarTeamNewLeader()
        self.GetView().SetWarTeamRedPoint(iNewTeamLeader > 0)

    
    def OnUpdateDailyTeamApply(self):
        oModel = mddailyteam.GetWarTeamInfoModel()
        self.GetView().SetWarTeamRedPoint(oModel.GetTeamApple())

    
    def onRefreshSysMailState(self):
        self.OnHasSysMailStateChange(self.m_oModel.GetHasSysMail())

    
    def OnHasSysMailStateChange(self, bHas):
        self.GetView().NotifySysRed(bHas)



class CComBtnMenuDelegate(delegatebase.CDelegateBase):
    '''
\t\xa5D\xac\xc9\xad\xb1\xa5k\xa4U\xa8\xa4\xaa\xba\xa6n\xa4\xcd\xab\xf6\xb6s\xac\xdb\xc3\xf6\xb1\xb1\xa8\xee\xc5\xde\xbf\xe8
\t'''
    
    def Init(self):
        self.m_oModel = GetModel()
        self.m_oModel.ssConnect(maildefines.SS_MD_HasSysMailStateChange, self.OnHasSysMailStateChange)
        self.GetView().ssConnect(maildefines.SS_Combtnmenu_RefreshSysMailState, self.onRefreshSysMailState)

    
    def OnHasSysMailStateChange(self, bHas):
        self.GetView().NotifyFriendRedDot(str(id(self)), bHas)

    
    def onRefreshSysMailState(self):
        self.GetView().NotifyFriendRedDot(str(id(self)), self.m_oModel.GetHasSysMail())



def GetModel():
    import mdmailcenter
    return mdmailcenter.GetModel()
