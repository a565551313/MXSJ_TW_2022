# pycdc 交叉复核产物 · script.fls entry 3435
# co_filename(原始)='script/mxui/cefwidget.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3435.pyc (Python 2.5)

import interface

class CCefVedioObj(interface.CClickBox):
    
    def __init__(self, w, h, sUrl, oCloseCB, loadStateCallback = None, jsCallback = None, jsFuncName = '', enable = 1, bCloseCapture = True, iBtnPosType = 0, sBtnPath = ''):
        import world
        interface.CClickBox.__init__(self, interface.TopmostPanel, world.WINDOW_WIDTH, world.WINDOW_HEIGHT, 0, 100, 0)
        self.m_oCefObj = interface.CCefObject(0, 0, w, h, sUrl, loadStateCallback = loadStateCallback, jsCallback = jsCallback, jsFuncName = jsFuncName, enable = enable)
        LOG_DEBUG(self.m_oCefObj.GetSize())
        self.m_oCloseBtn = None
        self.m_oCloseCB = oCloseCB
        self.m_Timer = None
        self.m_FindCaptureDlg = False
        self.m_sBtnPath = sBtnPath
        self.m_iBtnPosType = iBtnPosType
        self.Init()
        if bCloseCapture:
            self.InitCaptureTimer()
        

    
    def SetShow(self, iShow):
        self.SetShowCef(iShow)
        interface.CClickBox.SetShow(self, iShow)

    
    def Enable(self, bEnable):
        interface.CClickBox.Enable(self, bEnable)
        self.m_oCefObj.Enable(bEnable)

    
    def LoadUrl(self, sUrl):
        self.m_oCefObj.LoadUrl(sUrl)

    
    def GetEndCode(self):
        return self.m_oCefObj.LOADSTATE_END

    
    def GetErrCode(self):
        return self.m_oCefObj.LOADSTATE_ERROR

    
    def GetStartCode(self):
        return self.m_oCefObj.LOADSTATE_START

    
    def Init(self):
        self.SetShowCef(True)
        self.RefreshCloseBtn()

    
    def RefreshCloseBtn(self):
        if self.m_oCloseCB and None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, callable, self.m_oCloseCB):
            sPath = self.GetBtnPath()
            self.m_oCloseBtn = interface.CButton(self, sPath, 0, 0, msgid = 1)
            (iW, iH) = self.GetSize()
            (iCefW, iCefH) = self.m_oCefObj.GetSize()
            iCefX = (iW - iCefW) / 2
            iCefY = (iH - iCefH) / 2
            if self.m_iBtnPosType == 1:
                iBtnX = iCefX + iCefW
                iBtnY = iCefY
            else:
                (iBtnW, iBtnH) = self.m_oCloseBtn.GetSize()
                iBtnX = iCefX + iCefW
                iBtnY = iCefY - iBtnH
            self.m_oCloseBtn.SetPos(iBtnX, iBtnY)
        

    
    def GetBtnPath(self):
        import style
        sPath = None if self.m_sBtnPath else 'combdialog/\xb0\xb4\xc5\xa5/\xb9\xd8\xb1\xd5.igs'
        return style.GetPath(sPath, interface.GetStyle())

    
    def SetShowCef(self, bShow):
        (w, h) = self.GetSize()
        (iCefW, iCefH) = self.m_oCefObj.GetSize()
        if bShow:
            iCefX = (w - iCefW) / 2
            iCefY = (h - iCefH) / 2
            self.m_oCefObj.SetPos(iCefX, iCefY)
        else:
            self.m_oCefObj.SetPos(-iCefW, -iCefH)

    
    def InitCaptureTimer(self):
        import timer
        import misc
        if self.m_Timer:
            self.m_Timer.Release()
        
        self.m_Timer = timer.Timer(2, misc.Functor(self.CloseCaptureDlg), -1, self)

    
    def CloseCaptureDlg(self):
        import capturemgr
        (iKey, dInfo) = capturemgr.GetCaptureMgr().GetTop()
        if not dInfo:
            return None
        
        oWr = dInfo['WeakRef']
        if not oWr and oWr.Get():
            return None
        
        if not self.m_FindCaptureDlg:
            self.m_FindCaptureDlg = True
            return None
        
        oItem = oWr.Get()
        if oItem and hasattr(oItem, 'CloseWindow'):
            oItem.CloseWindow()
        
        self.m_FindCaptureDlg = False

    
    def RightUp(self):
        interface.CClickBox.RightUp(self)
        self.DoClose()

    
    def DoClose(self):
        if self.m_oCloseCB:
            pass
        self.m_oCloseCB()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.DoClose()
        


g_Test = None

def Close():
    global g_Test
    g_Test = None


def Test():
    global g_Test
    import misc
    sUrl = 'https://testid.duoyi.com/zm/html/reg-zm.html?gateSrc=mx'
    g_Test = CCefVedioObj(600, 500, sUrl, misc.Functor(Close))


def Test2():
    global g_Test
    import misc
    sUrl = 'https://testid.duoyi.com/zm/html/find-password-zm.html?gateSrc=mf/sw/mx'
    g_Test = CCefVedioObj(600, 500, sUrl, misc.Functor(Close))
