# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\timer.py
import misc, pubclass, traceback, slot, function, types, weakref, publog
g_Logger = publog.GetPubLogger(__name__)
g_AllTimer = slot.c2wlist()
g_AllSched = {}
g_fCurTime = misc.GetLastPubLoopStartTime()

def OnRestartClear():
    global g_AllSched
    global g_AllTimer
    global g_fCurTime
    g_AllTimer = slot.c2wlist()
    g_AllSched = {}
    g_fCurTime = misc.GetLastPubLoopStartTime()
    CTimerMgr.Get().Clear()


def Loop(_fCurTime):
    global g_fCurTime
    fCurTime = misc.GetLastPubLoopStartTime()
    CTimerMgr.Get().RefreshTimerPerFrame(fCurTime - g_fCurTime)
    g_fCurTime = fCurTime
    rlist = g_AllTimer._c2w_rd_list()
    for each in rlist:
        each.Check()

    g_AllTimer._c2w_rd_finish(rlist)
    for each in g_AllSched.values():
        each.Check()


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


def Sched(_fIntervalTime, _sName, _pCallFunc):
    if _sName in g_AllSched:
        g_Logger.debug('Warning: timer.Sched 新增的对象名字与容器里的重复, 执行覆盖')
        del g_AllSched[_sName]
    g_AllSched[_sName] = CSched(_fIntervalTime, _pCallFunc)


def Unsched(_sName):
    if _sName not in g_AllSched:
        return
    del g_AllSched[_sName]


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
                self.m_fCallTime = self.m_nInterval + self.m_fCallTime
                if self.m_nRepeat > 0:
                    self.m_nRepeat -= 1
            return

    def Release(self):
        self.m_pCallFunc = None
        RmTimer(self)
        return


class CSched(CTimer):

    def __init__(self, _fIntervalTime, _pCallFunc):
        super(CSched, self).__init__(_fIntervalTime, _pCallFunc)
        self.m_fIntervalTime = _fIntervalTime

    def Check(self):
        if g_fCurTime >= self.m_fCallTime:
            try:
                self.m_pCallFunc()
            except:
                traceback.print_exc()

            self.m_fCallTime += self.m_fIntervalTime
        return False

    def Clear(self):
        self.m_pCallFunc = None
        return

    def Release(self):
        self.m_pCallFunc = None
        return


def RegisterRefreshPerFrame(_pCallFunc):
    timerMgr = CTimerMgr.Get()
    timerMgr.ssConnect(timerMgr.SignalKey_TimerPerFrame, _pCallFunc)


def ReleaseRefreshPerFrame(_pCallFunc):
    timerMgr = CTimerMgr.Get()
    timerMgr.ssDisconnect(timerMgr.SignalKey_TimerPerFrame, _pCallFunc)


def RegisterRefreshPerSecond(_pCallFunc):
    CTimerMgr.Get().RegisterRefreshPerSecond(_pCallFunc)


def ReleaseRefreshPerSecond(_pCallFunc):
    CTimerMgr.Get().ReleaseRefreshPerSecond(_pCallFunc)


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
        self.m_dSecondCB = {}
        self.ssConnect(self.SignalKey_TimerPerSecond, self.OnRefreshSecond)

    def Clear(self):
        self.m_dSecondCB = {}

    def RefreshTimerPerFrame(self, _fDeltaTime):
        if len(self.m_ssSignals) <= 1 and not self.m_dSecondCB:
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
            self.m_fSecondTime -= 1.0
        if self.m_fMinuteTime >= 60.0:
            self.ssEmit(self.SignalKey_TimerPerMinute, _fDeltaTime)
            self.m_fMinuteTime -= 60.0
        if self.m_fHourTime >= 3600.0:
            self.ssEmit(self.SignalKey_TimerPerHour, _fDeltaTime)
            self.m_fHourTime -= 3600.0
        self.m_fLastTime = fCurTime

    def OnRefreshSecond(self, fDeltaTime):
        fCurTime = misc.GetLastPubLoopStartTime()
        for dCB in self.m_dSecondCB.values():
            cbFunc = dCB.get('cb')
            fStartTime = dCB.get('starttime')
            if fCurTime - fStartTime < 0.33:
                continue
            if cbFunc:
                fDeltaTime = fCurTime - self.m_fLastTime
                cbFunc(fDeltaTime)

    def RegisterRefreshPerSecond(self, _pCallFunc):
        fTime = misc.GetLastPubLoopStartTime()
        tFuncKey = self.GetFuncKey(_pCallFunc)
        self.m_dSecondCB[tFuncKey] = {'cb': (function.Functor(_pCallFunc)), 'starttime': fTime}

    def ReleaseRefreshPerSecond(self, _pCallFunc):
        tFuncKey = self.GetFuncKey(_pCallFunc)
        if tFuncKey in self.m_dSecondCB:
            del self.m_dSecondCB[tFuncKey]

    def GetFuncKey(self, _pCallFunc):
        if _pCallFunc is None:
            return 0
        else:
            if type(_pCallFunc) is not type(self.OnRefreshSecond):
                return str(id(_pCallFunc))
            return str(id(_pCallFunc.im_self)) + str(id(_pCallFunc.im_func))
