# pycdc 交叉复核产物 · script.fls entry 1086
# co_filename(原始)='script/mxgame/sibling/delegate/dgtsiblingchat.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1086.pyc (Python 2.5)

from siblingdefine import *
import delegatebase
import mdsiblingchat
import mdsiblingallplayer

class CChatDelegate(delegatebase.CDelegateBase):
    
    def \xef\xc8\xcf\xd2(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_OpenEmote, self.OnOpenEmote)
        oView.ssConnect(oView.SS_SendChat, self.OnSendChat)
        oModel = mdsiblingchat.GetChatModel()
        oModel.ssConnect(oModel.SS_ChatChange, self.OnChatChange)
        self.InitDlg()

    
    def InitDlg(self):
        oModel = mdsiblingchat.GetChatModel()
        dChatList = oModel.GetChat()
        sResultList = []
        for dChat in dChatList:
            iPlayerID = dChat[KEY_PLAYER_ID]
            sChat = dChat[KEY_CHAT]
            sTxt = self.GetShowChat(iPlayerID, sChat)
            sResultList.append(sTxt)
        
        self.GetView().ResetChat(sResultList)

    
    def OnOpenEmote(self):
        LOG_DEBUG('\xa5\xb4\xb6}\xaa\xed\xb1\xa1\xac\xc9\xad\xb1')
        import dlgbaozi
        dlgbaozi.ShowBaoziAndBubble()
        self.GetView().ReleaseLastEmoteDlg()

    
    def OnSendChat(self, sChat):
        LOG_DEBUG('\xb5o\xb0e\xabH\xae\xa7', sChat)
        import dlgbaozi
        import wrapui
        iEmoteIDList = wrapui.GetBaoziList(sChat)
        if iEmoteIDList:
            pass
        dlgbaozi.AddHistory(iEmoteIDList)
        import netsibling
        netsibling.C2SSendChat(sChat)

    
    def OnChatChange(self, iPlayerID, sChat):
        LOG_DEBUG('\xb2\xe1\xa4\xd1\xae\xf8\xae\xa7', iPlayerID, sChat)
        oView = self.GetView()
        sTxt = self.GetShowChat(iPlayerID, sChat)
        oView.AddChat(sTxt)
        import dlgmention
        import misc
        if dlgmention.IsMentionedIgnoreCh(sTxt):
            misc.FlashWindow(misc.FLASH_MENTION)
        

    
    def Refresh(self):
        LOG_DEBUG('\xa8\xea\xb7s\xabH\xae\xa7\xa6C\xaa\xed')

    
    def GetShowChat(self, iPlayerID, sChat):
        dPlayerInfo = mdsiblingallplayer.GetSiblingMgr().GetPlayerInfo(iPlayerID)
        sName = dPlayerInfo[KEY_NAME]
        sTxt = '#s(2,%d,%s)%s' % (iPlayerID, sName, sChat)
        return sTxt
