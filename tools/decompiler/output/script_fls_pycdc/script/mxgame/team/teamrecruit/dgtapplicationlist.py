# pycdc 交叉复核产物 · script.fls entry 2009
# co_filename(原始)='script/mxgame/team/teamrecruit/dgtapplicationlist.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2009.pyc (Python 2.5)

import delegatebase
import mdteamrecruit
import \xe3isc
import netdailyteam
import mddailyteam
import usermacro

class CApplicationListDelegate(delegatebase.CDelegateBase):
    
    def Init(self):
        self.InitSignal()
        self.InitView()

    
    def InitView(self):
        import netreddot
        self.RefreshView()
        self.GetView().SetIntroTextShow(not mddailyteam.IsTempWarTeam())
        netreddot.C2SRemoveRedDot(netreddot.TEAMAPPLY)

    
    def InitSignal(self):
        oView = self.GetView()
        oModel = self.GetModel()
        oView.ssConnect(oView.SS_AcceptApplication, self.OnClickAcceptApplication)
        oView.ssConnect(oView.SS_DeleteApplication, self.OnClickDeleteApplication)
        oView.ssConnect(oView.SS_RightUpApplication, self.OnRightUpApplication)
        oModel.ssConnect(oModel.SS_DeleteApplication, self.OnApplicationDelete)

    
    def RefreshView(self):
        dDataList = self.GetModel().GetApplicationList()
        dTableDataList = \xe3isc.DeepCopy(dDataList)
        iLen = 5 - len(dTableDataList)
        dTableDataList.extend([
            None] * iLen)
        self.GetView().RefreshTbView(dTableDataList)

    
    def OnClickDeleteApplication(self, iPlayerID):
        if mddailyteam.IsWarTeamLeader():
            netdailyteam.C2GSDelApplyInfo(iPlayerID)
            self.GetModel().DeleteApplication(iPlayerID)
        else:
            usermacro.PROMPT_MSG('\xb5L\xbe\xde\xa7@\xc5v\xad\xad')

    
    def OnClickAcceptApplication(self, iPlayerID):
        if mddailyteam.IsWarTeamLeader():
            netdailyteam.C2GSInviteFriend(iPlayerID)
        else:
            usermacro.PROMPT_MSG('\xb5L\xbe\xde\xa7@\xc5v\xad\xad')

    
    def OnRightUpApplication(self, iPlayerID):
        import dlgrecruitdetailmember
        dApplication = self.GetModel().GetApplicationByPlayerID(iPlayerID)
        if dApplication:
            dData = {
                'id': dApplication['iPlayerID'],
                'avatar': dApplication['tAvatar'],
                'level': dApplication['iLevel'],
                'name': dApplication['sName'],
                'class': dApplication['iClass'],
                'time': dApplication['iTime'],
                'targetlist': dApplication['lTarget'],
                'intro': dApplication['sIntro'] }
            dlgrecruitdetailmember.ShowDlg(iPlayerID, dData)
        

    
    def OnApplicationDelete(self):
        self.RefreshView()

    
    def GetModel(self):
        return mdteamrecruit.GetTeamRecruitMgr()
