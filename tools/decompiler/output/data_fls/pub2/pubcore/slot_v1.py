# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\slot_v1.py
from types import MethodType
from weakref import ref
DEBUG = False

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


class CSignal(c2wlist):

    def __init__(self, *args):
        super(CSignal, self).__init__()
        self.__itercall = True
        self.__bound = None
        if DEBUG:
            self._name = 'unbound'
        return

    def copysignal(self, obj):
        signal = CSignal()
        signal.__bound = ref(obj)
        return signal

    def deepcopy(self, obj=None):
        signal = CSignal()
        signal.__itercall = self.__itercall
        if obj:
            signal.__bound = ref(obj)
        slots_copy = signal._c2w_wt_list()
        slots = self._c2w_rd_list()
        for i_slot in slots:
            cp_slot = i_slot.copyslot()
            cp_slot._signal = ref(signal)
            slots_copy.append(cp_slot)

        self._c2w_rd_finish(slots)
        signal._c2w_wt_finish(slots_copy)
        return signal

    def bound(self):
        if not self.__bound:
            return None
        else:
            return self.__bound()

    def setbound(self, obj):
        self.__bound = ref(obj)

    def itercall(self, _itercall=None):
        if _itercall is None:
            return self.__itercall
        else:
            self.__itercall = _itercall
            return

    def emit(self, *args, **kwargs):
        slots = self._c2w_rd_list()
        signal_itercall = self.__itercall
        for i_slot in slots:
            if not i_slot.isok():
                continue
            slot_notitercall = True
            if signal_itercall:
                slot_notitercall = not i_slot._runflag & _slot.FG_ITTERCB
            if slot_notitercall:
                i_slot._runflag &= ~_slot._FG_ENABLED
            if i_slot._self is None:
                i_slot._meth(*args, **kwargs)
            else:
                _self = i_slot._self()
                i_slot._meth(_self, *args, **kwargs)
            if slot_notitercall:
                i_slot._runflag |= _slot._FG_ENABLED

        self._c2w_rd_finish(slots)
        return

    def connect(self, func):
        slots = self._c2w_wt_list()
        key = self._funckey(func)
        self._clearslots(slots, key)
        slot = _slot(func, key)
        slot._signal = ref(self)
        slots.append(slot)
        self._c2w_wt_finish(slots)
        return slot

    def disconnect(self, func=None, iskey=False):
        slots = self._c2w_wt_list()
        k = 0
        if iskey:
            k = func
        else:
            k = self._funckey(func)
        self._clearslots(slots, k)
        self._c2w_wt_finish(slots)

    def candel(self):
        slots = self._c2w_rd_list()
        len_slots = len(slots)
        self._c2w_rd_finish(slots)
        return len_slots == 0

    def __call__(self, *args, **kwargs):
        self.emit(*args, **kwargs)

    def _clearslots(self, slots, key=0):
        rmlist = []
        for i_slot in slots:
            if i_slot.candel():
                rmlist.append(i_slot)
                continue
            if key == 0 or i_slot.key() == key:
                rmlist.append(i_slot)

        for i_slot in rmlist:
            i_slot.release()
            slots.remove(i_slot)

    def _funckey(self, func):
        if func is None:
            return 0
        else:
            if type(func) is not MethodType:
                return [id(func)]
            return [
             id(func.im_self), id(func.im_func)]


class _slot(object):
    FG_ENABLED = 1
    FG_ITTERCB = 2
    _FG_ENABLED = 256
    _FG_CHECKED = 512
    __slots__ = [
     '_signal', '_runflag', '_key', '_meth', '_self']

    def __init__(self, func, key=0):
        self._runflag = _slot.FG_ENABLED | _slot.FG_ITTERCB
        self._signal = None
        self._key = key
        self._meth = None
        self._self = None
        if type(func) is not MethodType:
            self._meth = func
        else:
            self._self = ref(func.im_self)
            self._meth = func.im_func
        if hasattr(func, 'IsActive'):
            self._runflag |= _slot._FG_CHECKED
        return

    def disconnect(self):
        if self._signal is None or self._signal() is None:
            return False
        self._signal().disconnect(self._key, True)
        return

    def itercall(self, _itercall=None):
        if _itercall == False:
            self._runflag &= ~_slot.FG_ITTERCB
        elif _itercall == True:
            self._runflag |= _slot.FG_ITTERCB
        return bool(self._runflag & _slot.FG_ITTERCB)

    def key(self):
        return self._key

    def isok(self):
        if not self._runflag & (_slot.FG_ENABLED | _slot._FG_ENABLED):
            return False
        else:
            if self._meth is None:
                return False
            if self._runflag & _slot._FG_CHECKED and not self._meth.IsActive():
                return False
            return self._self is None or self._self() is not None

    def candel(self):
        if self._meth is None:
            return True
        else:
            if self._runflag & _slot._FG_CHECKED and not self._meth.IsActive():
                return True
            return self._self is not None and self._self() is None

    def release(self):
        self._meth = None
        return

    def enable(self, _enable=None):
        if _enable == False:
            self._runflag &= ~_slot.FG_ENABLED
        elif _enable == True:
            self._runflag |= _slot.FG_ENABLED
        return bool(self._runflag & _slot.FG_ENABLED)

    def copyslot(self):
        slot = _slot(None)
        slot._runflag = self._runflag & ~_slot._FG_ENABLED
        slot._key = self._key
        slot._self = self._self
        slot._meth = self._meth
        return slot


class ISignal(object):
    _cls_unique_bound = False

    def __init__(self):
        if self._cls_unique_bound:
            return
        else:
            self._cls_unique_bound = True
            for k in dir(self):
                if k == '__dict__':
                    continue
                v = getattr(self, k)
                if not isinstance(v, CSignal):
                    continue
                if v.bound() is not None:
                    continue
                signal = v.copysignal(self)
                setattr(self, k, signal)
                if DEBUG:
                    signal._name = '[%s].[%s]' % (self, k)

            return


class ISignalSubject(object):

    def ssInit(self):
        if not hasattr(self, 'm_ssSignals'):
            self.m_ssSignals = {}

    def ssCreate(self, signature):
        signal = CSignal()
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
            signal = CSignal()
            self.m_ssSignals[signature] = signal
        return signal

    def ssCheckReleaseSignal(self, signature):
        if signature in self.m_ssSignals:
            signal = self.m_ssSignals[signature]
            if signal and signal.candel():
                del self.m_ssSignals[signature]

    def ssLoadSignalsFrom(self, signalSub):
        self.m_ssSignals = {}
        for signature, signal in signalSub.m_ssSignals.items():
            self.m_ssSignals[signature] = signal.deepcopy()

    def ssReleaseSignal(self, signature):
        if signature in self.m_ssSignals:
            signal = self.m_ssSignals[signature]
            if signal:
                del self.m_ssSignals[signature]
