# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\slot_v2.py
from C_slot import CUnbound
from C_slot import CSignal
SIGOBJ = CSignal
SIGNAL = CUnbound
CSignal = CUnbound

class c2wlist(object):

    def __init__(self):
        super(c2wlist, self).__init__()
        self.__refcount = 0
        self.__list = []
        self.__writelock = False

    def _c2w_rd_finish(self, o_list):
        if self.__refcount > 0 and id(o_list) == id(self.__list):
            self.__refcount -= 1

    def _c2w_rd_list(self):
        self.__refcount += 1
        return self.__list

    def _c2w_wt_list(self):
        if self.__refcount != 0:
            n_list = list(self.__list)
            self.__list = n_list
        self.__writelock = True
        self.__refcount = 0
        return self.__list

    def _c2w_wt_finish(self, n_list):
        self.__writelock = False


class ISignal(object):
    pass


class ISignalSubject(object):

    def ssInit(self):
        if not hasattr(self, 'm_ssSignals'):
            self.m_ssSignals = {}

    def ssCreate(self, signature):
        signal = SIGOBJ()
        self.m_ssSignals[signature] = signal
        return signal

    def ssConnect(self, signature, func):
        signal = self.ssGetCreateSignal(signature)
        return signal.connect(func)

    def ssDisconnect(self, signature, func=None):
        signal = self.ssGetSignal(signature)
        if signal:
            signal.disconnect(func)

    def ssEmit(self, signature, *args, **argss):
        signal = self.ssGetSignal(signature)
        if signal:
            signal.emit(*args, **argss)

    def ssGetSignal(self, signature):
        return self.m_ssSignals.get(signature, None)

    def ssGetCreateSignal(self, signature):
        signal = self.ssGetSignal(signature)
        if signal is None:
            signal = SIGOBJ()
            self.m_ssSignals[signature] = signal
        return signal

    def ssCheckReleaseSignal(self, signature):
        raise self.ssCheckReleaseSignal

    def ssLoadSignalsFrom(self, signalSub):
        raise self.ssLoadSignalsFrom

    def ssReleaseSignal(self, signature):
        if signature in self.m_ssSignals:
            signal = self.m_ssSignals[signature]
            if signal:
                del self.m_ssSignals[signature]
