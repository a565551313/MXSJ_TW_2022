# pycdc 交叉复核产物 · script.fls entry 2515
# co_filename(原始)='script/mxgame/activity/qixi/dgteternallove.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2515.pyc (Python 2.5)

import delegatebase
import mdeternallove
import permission
import qixidescribledata

class CDelegateEternallove(delegatebase.CDelegateBase):
    
    def __init__(self, oView):
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def GetModel(self):
        return mdeternallove.GetMdEternallove()

    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_OnClickForMe, self.OnClickForMe)
        oView.ssConnect(oView.SS_OnClickForYou, self.OnClickForYou)
        oView.ssConnect(oView.SS_OnClickSelectForMe, self.OnClickSelectForMe)
        oView.ssConnect(oView.SS_OnClickSelectForYou, self.OnClickSelectForYou)
        oView.ssConnect(oView.SS_OnClickSelectContext, self.OnClickSelectContext)
        oView.ssConnect(oView.SS_OnClickSelectFriends, self.OnClickSelectFriends)
        oView.ssConnect(oView.SS_OnClickSendContext, self.OnClickSendContext)
        oView.ssConnect(oView.SS_OnCloseWindow, self.OnCloseWindow)
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_UpdataDescForMe, self.UpdataDescForMe)
        oModel.ssConnect(oModel.SS_UpdataDescForYou, self.UpdataDescForYou)
        oModel.ssConnect(oModel.SS_UpdataContext, self.UpdataContext)
        oModel.ssConnect(oModel.SS_UpdataFriendName, self.UpdataFriendName)
        oModel.SetCurContextIdx(1)
        oModel.SetCurDescFormeIdx(1)
        oModel.SetCurDescForYouIdx(1)

    
    def OnClickForMe(self):
        oView = self.GetView()
        oModel = self.GetModel()
        bSelect = not oView.GetCheckForMe()
        oView.SetCheckForMe(bSelect)
        if bSelect:
            oModel.SetCurDescFormeIdx(1)
        else:
            oModel.SetCurDescFormeIdx(0)

    
    def OnClickForYou(self):
        oView = self.GetView()
        oModel = self.GetModel()
        bSelect = not oView.GetCheckForYou()
        oView.SetCheckForYou(bSelect)
        if bSelect:
            oModel.SetCurDescForYouIdx(1)
        else:
            oModel.SetCurDescForYouIdx(0)

    
    def OnClickSelectForMe(self, iMsgID):
        oView = self.GetView()
        if not oView.GetCheckForMe():
            return None
        
        oModel = self.GetModel()
        idx = oModel.GetCurDescForMeIdx()
        if iMsgID == 16:
            idx -= 1
        elif iMsgID == 19:
            idx += 1
        
        iMax = qixidescribledata.GetXRWordLen()
        if idx < 1:
            idx = iMax
        elif idx > iMax:
            idx = 1
        
        oModel.SetCurDescFormeIdx(idx)

    
    def OnClickSelectForYou(self, iMsgID):
        oView = self.GetView()
        if not oView.GetCheckForYou():
            return None
        
        oModel = self.GetModel()
        idx = oModel.GetCurDescForYouIdx()
        if iMsgID == 18:
            idx -= 1
        elif iMsgID == 20:
            idx += 1
        
        iMax = qixidescribledata.GetXRYouWordLen()
        if idx < 1:
            idx = iMax
        elif idx > iMax:
            idx = 1
        
        oModel.SetCurDescForYouIdx(idx)

    
    def OnClickSelectContext(self, iMsgID):
        oModel = self.GetModel()
        idx = oModel.GetCurContextIdx()
        if iMsgID == 17:
            idx -= 1
        elif iMsgID == 21:
            idx += 1
        
        iMax = qixidescribledata.GetDescWordLen()
        if idx < 1:
            idx = iMax
        elif idx > iMax:
            idx = 1
        
        oModel.SetCurContextIdx(idx)

    
    def OnClickSelectFriends(self):
        import dlgeternalovefriendlist
        dlgeternalovefriendlist.SetShow(True)

    
    def OnClickSendContext(self):
        import usermacro
        import netopenui
        import c2sitemuicom
        oView = self.GetView()
        oModel = self.GetModel()
        iItemID = oView.GetItemID()
        iPlayerID = oModel.GetFriendId()
        sPlayerName = oModel.GetFriendName()
        sDesc = oModel.GetTextDesc()
        sWorld = oModel.GetWorldDesc()
        if not iPlayerID or not sPlayerName:
            usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xbf\xef\xbe\xdc\xc3\xd8\xb0e\xb9\xef\xb9\xb3')
            return None
        
        netopenui.C2SSendQixidEternalLove(iItemID, iPlayerID, sDesc, sWorld)

    
    def OnCloseWindow(self):
        mdeternallove.ResetModel()

    
    def UpdataDescForMe(self, idx):
        oView = self.GetView()
        desc = qixidescribledata.GetXRDescByIdx(idx, 'desc')
        oView.SetDescribeForSelfText(desc)
        self.SetDesginEffect()

    
    def UpdataDescForYou(self, idx):
        oView = self.GetView()
        desc = qixidescribledata.GetXRYouDescByIdx(idx, 'desc')
        oView.SetDescribeForYouText(desc)
        self.SetDesginEffect()

    
    def UpdataContext(self, idx):
        oView = self.GetView()
        desc = qixidescribledata.GetDescByIdx(idx, 'desc')
        oView.SetContext(desc)
        self.SetDesginEffect()

    
    def UpdataFriendName(self, id, sName):
        oView = self.GetView()
        oView.SetFriendName(sName)
        self.SetDesginEffect()

    
    def SetDesginEffect(self):
        import hero
        oView = self.GetView()
        oModel = self.GetModel()
        iForMeIdx = oModel.GetCurDescForMeIdx()
        iForYouIdx = oModel.GetCurDescForYouIdx()
        iContextIdx = oModel.GetCurContextIdx()
        sDescForMe = qixidescribledata.GetXRDescByIdx(iForMeIdx, 'style')
        sMyName = hero.GetProp('m_Name')
        sDescForYou = qixidescribledata.GetXRDescByIdx(iForYouIdx, 'style')
        sFriendName = oModel.GetFriendName()
        sContext = None(None, None(None, qixidescribledata.GetDescByIdx, **iContextIdx))
        iSex = hero.GetProp('m_Sex', 1)
        if iSex == 1:
            sMyColor = '#c00ffff'
            sFriendColor = '#R'
        else:
            sMyColor = '#R'
            sFriendColor = '#c00ffff'
        if not sFriendName:
            sFriendName = 'Ta'
        
        desc = '%s%s%s#n\xb7Q\xb9\xef%s%s%s#n\xbb\xa1\xa1G%s' % (sDescForMe, sMyColor, sMyName, sDescForYou, sFriendColor, sFriendName, sContext)
        oView.UpdataDesginEffect(desc)
        oModel.SetTextDesc(desc)
        worldDesc = '\xb9\xef%s%s%s#n\xbb\xa1\xa1G%s' % (sDescForYou, sFriendColor, sFriendName, sContext)
        oModel.SetWorldDesc(worldDesc)
