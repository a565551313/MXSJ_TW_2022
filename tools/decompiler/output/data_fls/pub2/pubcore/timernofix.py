# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\timernofix.py
import misc, pubclass, traceback, slot, function, types, weakref
g_AllTimer = slot.c2wlist()
g_fCurTime = misc.GetLastPubLoopStartTime()

def OnRestartClear():
    global g_AllTimer
    global g_fCurTime
    g_AllTimer = slot.c2wlist()
    g_fCurTime = misc.GetLastPubLoopStartTime()


def Loop():
    global g_fCurTime
    _fCurTime = misc.GetLastPubLoopStartTime()
    CTimerMgr.Get().RefreshTimerPerFrame(_fCurTime - g_fCurTime)
    g_fCurTime = _fCurTime
    rlist = g_AllTimer._c2w_rd_list()
    for each in rlist:
        each.Check()

    g_AllTimer._c2w_rd_finish(rlist)


def Timer(_fDelayTime, _pCallFunc, _nRepeat=0, pRelayObj=None):
    obj = CTimer(_fDelayTime, _pCallFunc, _nRepeat, pRelayObj)
    wlist = g_AllTimer._c2w_wt_list()
    wlist.append(obj)
    g_AllTimer._c2w_wt_finish(wlist)
    return obj


def RmTimer(_pTimer):
    rlist = g_AllTimer._c2w_rd_list()
    if _pTimer not in rlist:
        g_AllTimer._c2w_rd_finish(rlist)
        return
    g_AllTimer._c2w_rd_finish(rlist)
    wlist = g_AllTimer._c2w_wt_list()
    wlist.remove(_pTimer)
    g_AllTimer._c2w_wt_finish(wlist)


class CTimer(object):

    def __init__(self, _fTime, _pCallFunc, _nRepeat=0, pRelayObj=None):
        fRealCurTime = misc.GetLastPubLoopStartTime()
        self.m_fCallTime = fRealCurTime + _fTime
        self.m_nInterval = _fTime
        if type(_pCallFunc) is types.MethodType:
            _pCallFunc = function.Functor(_pCallFunc)
        self.m_pCallFunc = _pCallFunc
        self.m_nRepeat = _nRepeat
        if pRelayObj != None:
            pRelayObj = weakref.ref(pRelayObj)
        self.m_wrRelayObj = pRelayObj
        return

    def Check(self):
        if self.m_pCallFunc is None:
            return
        else:
            if isinstance(self.m_pCallFunc, function.CFunctor) and not self.m_pCallFunc.IsActive():
                self.Release()
                return
            if g_fCurTime >= self.m_fCallTime:
                bRelease = self.m_wrRelayObj != None and self.m_wrRelayObj() == None
                if not bRelease:
                    try:
                        self.m_pCallFunc()
                    except:
                        traceback.print_exc()

                if self.m_nRepeat == 0 or bRelease:
                    self.Release()
                    return
                self.m_fCallTime = self.m_nInterval + g_fCurTime
                if self.m_nRepeat > 0:
                    self.m_nRepeat -= 1
            return

    def Release(self):
        self.m_pCallFunc = None
        RmTimer(self)
        return


def RegisterRefreshPerFrame(_pCallFunc):
    timerMgr = CTimerMgr.Get()
    timerMgr.ssConnect(timerMgr.SignalKey_TimerPerFrame, _pCallFunc)


def ReleaseRefreshPerFrame(_pCallFunc):
    timerMgr = CTimerMgr.Get()
    timerMgr.ssDisconnect(timerMgr.SignalKey_TimerPerFrame, _pCallFunc)


def RegisterRefreshPerSecond(_pCallFunc):
    timerMgr = CTimerMgr.Get()
    timerMgr.ssConnect(timerMgr.SignalKey_TimerPerSecond, _pCallFunc)


def ReleaseRefreshPerSecond(_pCallFunc):
    timerMgr = CTimerMgr.Get()
    timerMgr.ssDisconnect(timerMgr.SignalKey_TimerPerSecond, _pCallFunc)


def RegisterRefreshPerMinute(_pCallFunc):
    timerMgr = CTimerMgr.Get()
    timerMgr.ssConnect(timerMgr.SignalKey_TimerPerMinute, _pCallFunc)


def ReleaseRefreshPerMinute(_pCallFunc):
    timerMgr = CTimerMgr.Get()
    timerMgr.ssDisconnect(timerMgr.SignalKey_TimerPerMinute, _pCallFunc)


def RegisterRefreshPerHour(_pCallFunc):
    timerMgr = CTimerMgr.Get()
    timerMgr.ssConnect(timerMgr.SignalKey_TimerPerHour, _pCallFunc)


def ReleaseRefreshPerHour(_pCallFunc):
    timerMgr = CTimerMgr.Get()
    timerMgr.ssDisconnect(timerMgr.SignalKey_TimerPerHour, _pCallFunc)


class CTimerMgr(pubclass.CSingleTon, slot.ISignalSubject):
    SignalKey_TimerPerSecond = 'sk_TimerPerSecond'
    SignalKey_TimerPerMinute = 'sk_TimerPerMinute'
    SignalKey_TimerPerHour = 'sk_TimerPerHour'
    SignalKey_TimerPerFrame = 'sk_TimerPerFrame'

    def __init__(self):
        super(CTimerMgr, self).__init__()
        slot.ISignalSubject.ssInit(self)
        self.m_fSecondTime = 0.0
        self.m_fMinuteTime = 0.0
        self.m_fHourTime = 0.0
        self.m_fLastTime = 0.0

    def RefreshTimerPerFrame(self, _fDeltaTime):
        if len(self.m_ssSignals) <= 0:
            self.m_fSecondTime = 0.0
            self.m_fMinuteTime = 0.0
            self.m_fHourTime = 0.0
            self.m_fLastTime = 0.0
            return
        fCurTime = misc.GetLastPubLoopStartTime()
        if self.m_fLastTime >= 0.001:
            fDeltaTime = fCurTime - self.m_fLastTime
        else:
            fDeltaTime = _fDeltaTime
        self.ssEmit(self.SignalKey_TimerPerFrame, _fDeltaTime)
        self.m_fSecondTime += fDeltaTime
        self.m_fMinuteTime += fDeltaTime
        self.m_fHourTime += fDeltaTime
        if self.m_fSecondTime >= 1.0:
            self.ssEmit(self.SignalKey_TimerPerSecond, _fDeltaTime)
            self.m_fSecondTime = 0.0
        if self.m_fMinuteTime >= 60.0:
            self.ssEmit(self.SignalKey_TimerPerMinute, _fDeltaTime)
            self.m_fMinuteTime = 0.0
        if self.m_fHourTime >= 3600.0:
            self.ssEmit(self.SignalKey_TimerPerHour, _fDeltaTime)
            self.m_fHourTime = 0.0
        self.m_fLastTime = fCurTime
