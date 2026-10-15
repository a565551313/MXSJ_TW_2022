# pycdc 交叉复核产物 · script.fls entry 294
# co_filename(原始)='script/mxgame/imtools/dlgimnewgame.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_294.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/8/12 17:03
\xd7\xf7\xd5\xdf: jiangweichao
\xce\xc4\xbc\xfe: dlgimnewgame
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import interface
g_oIMNewGameDialog = None

def ModuleReset():
    global g_oIMNewGameDialog
    g_oIMNewGameDialog = None


def OpenIMNewGameDialog(dData):
    global g_oIMNewGameDialog
    g_oIMNewGameDialog = CIMNewGameDialog()
    g_oIMNewGameDialog.InitData(dData)


def OpenNPCDialog(dData):
    import dlgnpc
    import misc
    sText = '\xae\xa5\xb3\xdf\xb1z\xa4w\xb8g\xbfE\xac\xa1#Y%s#n\xa1A\xa5i\xb3q\xb9L\xbe\xd4\xb7\xf9\xa5\xb4\xb6}\xb9C\xc0\xb8\nL\xa5\xdf\xa7Y\xabe\xa9\xb9\xb9C\xc0\xb8\nR\xb5y\xab\xe1\xa6A\xaa\xb1' % dData['sGameName']
    dlgnpc.ShowClientDlg(sText, '', misc.Functor(OnNPCDialogMessage, dData['iGameID'], dData['sGameName'], dData['sGameUrl']))


def OnNPCDialogMessage(iGameID, sGameName, sGameUrl, iMsgID):
    import imnewgamemgr
    if iMsgID == 1:
        imnewgamemgr.ShowNewGame_Public(iGameID, sGameName, sGameUrl)
    


class CIMNewGameDialog(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog4/itembill/cdkey_tips.dlg')
        interface.Center(self)
        self.m_dData = { }

    
    def InitData(self, dData):
        self.m_dData = dData
        self.RefreshText()

    
    def RefreshText(self):
        bHaveCD = self.m_dData['sCDKey']
        if not bHaveCD:
            self.SetShowObject('txt_cdkey', False)
            self.SetShowObject('btn_copy', False)
            self.GetObject('txt_tips').SetText('\xae\xa5\xb3\xdf\xb1z\xc0\xf2\xb1o\xa4F\xa1m$game\xa1n\xbfE\xac\xa1\xb8\xea\xae\xe6')
            self.GetObject('btn_jihuo').\xf9\xcf\xde\xfaos(111, 91)
        
        self.GetObject('txt_tips').ReplaceText({
            '$game': self.m_dData['sGameName'] })
        self.GetObject('txt_cdkey').SetText(self.m_dData['sCDKey'])

    
    def OnActivateGame(self):
        import netcommon
        netcommon.C2SActivateNewGame(self.m_dData['iItemID'], self.m_dData['iGameID'], self.m_dData['sCDKey'])

    
    def OnCopyCDKey(self):
        import C_sys
        import usermacro
        sCDKey = self.m_dData['sCDKey']
        C_sys.SetClipboardData(sCDKey)
        usermacro.PROMPT_MSG('\xbfE\xac\xa1\xbdX\xa4w\xbd\xc6\xbbs\xa8\xec\xb0\xc5\xb6K\xaaO\xa1A#YCtrl+V#n\xa5i\xd6\xdf\xb6K\xa8\xcf\xa5\xce')

    
    def CloseWindow(self):
        global g_oIMNewGameDialog
        g_oIMNewGameDialog = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 2:
            self.OnActivateGame()
            self.CloseWindow()
        elif iMsgID == 3:
            self.OnCopyCDKey()
            self.CloseWindow()
