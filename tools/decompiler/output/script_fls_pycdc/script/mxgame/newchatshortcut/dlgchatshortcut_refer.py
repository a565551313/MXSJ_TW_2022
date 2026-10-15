# pycdc 交叉复核产物 · script.fls entry 4618
# co_filename(原始)='script/mxgame/newchatshortcut/dlgchatshortcut_refer.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4618.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/4/14 20:24
\xd7\xf7\xd5\xdf: sanli
\xce\xc4\xbc\xfe: dlgchatshortcut_refer
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import dlgtalk
import interface
import mainmenu
import newmyqbase
import slot

def OpenReferDlg(oParent, sText):
    oDlg = CChatShortCutReferDlg.OpenUI(oParent = oParent)
    oDlg.SetYinYongText(sText)


def OpenReferFromFriendDlg(oParent, sText):
    oDlg = CChatShortCutReferFromFriendDlg.OpenUI(oParent = oParent)
    oDlg.SetYinYongText(sText)


class CChatShortCutReferDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    sUIName = 'dialog4/mainmenu/chat_yinyong.dlg'
    dOpenUIConfig = {
        'KEY_ALIGN': -1 }
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.ssInit()
        self.Init()
        self.m_DelegateList = []
        self.InitDelegate()

    
    def InitDelegate(self):
        self.m_DelegateList = []

    
    def Init(self):
        global GetParent
        if isinstance(self.GetParent(), dlgtalk.CMultiTalkDialog):
            (iX, iY, iW, iH) = self.GetParent().GetLocData('noname4')
            (_, iOffh) = self.GetSize()
            self.SetPos(iX, iY + iH - iOffh)
            self.SetZ(self.GetParent().GetZ() + 1)
        else:
            oChatInput = mainmenu.GetChatInputPanel()
            GetParent = 'noname0'
            (iX, iY) = oChatInput.GetObject.GetPos()
            (_, iOffh) = self.GetSize()
            self.SetPos(iX, iY - iOffh)

    
    def SetYinYongText(self, sText):
        (iWidth, _) = self.GetObject('text_yinyong').GetSize()
        iFont = self.GetObject('text_yinyong').GetFont()
        iShowPos = newmyqbase.GetExtandTxtPos(iWidth - 10, iFont, sText, 1)
        if iShowPos:
            sText = sText[:iShowPos] + '...'
        
        self.GetObject('text_yinyong').SetText(sText)

    
    def CloseDlg(self):
        import mdchatshortcut
        mdchatshortcut.GetChatShortCutMgr().SetReferText('')
        self.CloseUI()

    
    def OnEditMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseDlg()
        

    
    def OnMessage(self, iMsgID):
        self.OnEditMessage(iMsgID)



class CChatShortCutReferFromFriendDlg(CChatShortCutReferDlg):
    
    def CloseDlg(self):
        import mdchatshortcut
        mdchatshortcut.GetChatShortCutMgr().SetReferFromFriendText('')
        self.CloseUI()
