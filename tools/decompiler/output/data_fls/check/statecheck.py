# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\check\statecheck.py
g_StateChecker = None

def Start():
    global g_StateChecker
    if g_StateChecker is None:
        g_StateChecker = CStateCheck()
    return


def OnGLErr(sCode, sErr):
    if g_StateChecker:
        g_StateChecker.OnGLErr(sCode, sErr)


class CStateCheck(object):

    def __init__(self):
        self.m_IsFirstGLErr = True
        self.m_GLErrState = 0
        self.m_GLErrList = []
        import pubcore.timer
        pubcore.timer.Timer(1800, self.Loop, -1, self)

    def Loop(self):
        if self.m_GLErrState == 1:
            self.m_GLErrState = 2
        elif self.m_GLErrState == 2:
            self.m_GLErrState = 0
            self.SendGLErr()

    def OnGLErr(self, sCode, sErr):
        self.m_GLErrList.append('Code: %s, Detail:%s' % (sCode, sErr))
        if self.m_IsFirstGLErr:
            self.m_IsFirstGLErr = False
            self.SendGLErr()
        else:
            self.m_GLErrState = 1

    def SendGLErr(self):
        if not self.m_GLErrList:
            return
        sLog = ('\n').join(self.m_GLErrList)
        self.m_GLErrList = []
        self.SendLog(sLog)

    def SendLog(self, sLog):
        NormalLog(sLog)
