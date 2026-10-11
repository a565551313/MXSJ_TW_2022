# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\mxgame\gameloginqueue\dlgloginqueue.py
import combdialog, interface, timer
g_Dialog = None

def ModuleReset():
    global g_Dialog
    g_Dialog = None
    return


def ShowLoginQueueDialog(iPos, iQueueTime, iServer):
    global g_Dialog
    if not g_Dialog:
        g_Dialog = CLoginQueueDialog()
    g_Dialog.InitDialog(iPos, iQueueTime, iServer)
    return


def CloseLoginQueueDialog():
    global g_Dialog
    import C_sys
    if g_Dialog:
        g_Dialog.Capture(0)
    g_Dialog = None
    C_sys.HotKeyEnable(1)
    return


def ChooseOtherServer(iServer):
    import serverdata
    dInfo = serverdata.GetServerInfoByID(iServer)
    if dInfo:
        import selectserver
        selectserver.TransferServer(dInfo)
    return


class CLoginQueueDialog(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.TopmostPanel, 'login_new/loginwaiting.dlg')
        interface.Center(self)
        self.m_PointNum = 1
        timer.Timer(0.6, self.ChangeCirculationPoint, iRepeat=-1, oRelayObj=self)
        self.Capture(1, 1)
        return

    def InitDialog(self, iPos, iQueueTime, iServer):
        self.GetObject('txt_people').SetText(str(iPos))
        iMinute = iQueueTime / 60
        if iMinute == 0:
            sTime = '<1分鐘'
        elif iMinute > 60:
            sTime = '>1小時'
        else:
            sTime = '%d分鐘' % iMinute
        self.GetObject('txt_people').SetText(str(iPos))
        self.GetObject('txt_time').SetText(sTime)
        self.GetObject('txt_servername').SetShow(False)
        self.CheckServer(iServer)
        import commondialog, C_sys
        C_sys.HotKeyEnable(0)
        dlg = commondialog.g_MessageBox
        if getattr(dlg, 'm_RealMessageString', '') == '登錄中...':
            commondialog.HideMessageBox()
        return

    def CheckServer(self, iServer):
        import serverdata
        sServer = serverdata.GetServerNameByID(iServer)
        if sServer:
            self.GetObject('txt_ext').SetShow(True)
            oText = self.GetObject('txt_servername')
            font = oText.GetFont()
            color = oText.GetColor()
            (x, y, w, h) = self.GetLocData('txt_servername')
            self.m_ClickText = interface.CClickRichText(self, x, y, w + 100, '#u%s#n' % sServer, color, 16772707, font, msgid=2)
            self.m_ServerID = iServer
        else:
            self.GetObject('txt_ext').SetShow(False)
            self.m_ClickText = None
            self.m_ServerID = 0
        return

    def ChangeCirculationPoint(self):
        oText = self.GetObject('txt_circulation')
        oText.SetText('.' * self.m_PointNum)
        self.m_PointNum = (self.m_PointNum + 1) % 6
        return

    def DoQuit(self):

        def _OK(dlg):
            import netloginqueue
            netloginqueue.C2SQuitQueue()
            CloseLoginQueueDialog()
            return

        import commondialog
        commondialog.ShowNewMessageBox('退出後將放棄本次排隊，確定退出嗎？', ('確定',
                                                                                                                                                          '取消'), (_OK, None))
        return

    def DoChangeServer(self):

        def _OK(dlg):
            import netloginqueue
            netloginqueue.C2SQuitQueue()
            CloseLoginQueueDialog()
            ChooseOtherServer(self.m_ServerID)
            return

        import commondialog
        commondialog.ShowNewMessageBox('選擇該服務器將放棄本次排隊，確定退出嗎？', ('確定',
                                                                                                                                                                                     '取消'), (_OK, None))
        return

    def CloseWindow(self):
        return

    def OnMessage(self, iMsgid):
        if iMsgid == 1:
            self.DoQuit()
        elif iMsgid == 2:
            self.DoChangeServer()
        return


return
