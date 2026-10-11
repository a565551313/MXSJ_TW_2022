# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\function.py
__version__ = '0.0.1'
import types, weakref

def CreateFunctorByName(oPyTarget, sFunName, *args, **kwargs):
    return CFunctorByName(oPyTarget, sFunName, *args, **kwargs)


def CreateFunctor(oFunction, *args, **kwargs):
    return CFunctor(oFunction, *args, **kwargs)


def CreateFuncWrapper(oFunc, oBeforeFunc=None, oAfterFunc=None):
    return CFuncWrapper(oFunc, oBeforeFunc, oAfterFunc)


FunctorByName = CreateFunctorByName
Functor = CreateFunctor
FuncWrapper = CreateFuncWrapper

class CFunctorByName(object):

    def __init__(self, _pyTarget, _fnName, *args, **kwargs):
        if not isinstance(_pyTarget, types.ObjectType):
            raise "type '_pyTarget' must be %s, given %s" % (
             types.ObjectType, type(_pyTarget))
        self.m_wrObj = weakref.ref(_pyTarget)
        self.m_FuncName = _fnName
        self.m_Args = args
        self.m_kwArgs = kwargs

    def IsActive(self):
        return self.m_wrObj() is not None

    def __call__(self, *args, **kwargs):
        realObj = self.m_wrObj()
        if realObj is None:
            return
        else:
            curKwArgs = dict(self.m_kwArgs)
            curKwArgs.update(kwargs)
            return getattr(realObj, self.m_FuncName)(*(self.m_Args + args), **curKwArgs)


class CFunctor(object):
    m_bIsEngineMethod = False

    def __init__(self, _fn, *args, **kwargs):
        if not callable(_fn):
            raise Exception("CFunctor first argument must be not 'None'")
        self.m_bIsMethodType = True
        if isinstance(_fn, types.MethodType):
            self.m_wrObj = weakref.ref(_fn.im_self)
            self.m_Func = _fn.im_func
        elif isinstance(_fn, types.BuiltinFunctionType) and _fn.__self__:
            self.m_bIsEngineMethod = True
            self.m_wrObj = weakref.ref(_fn.__self__)
            self.m_Func = _fn.__name__
        else:
            self.m_bIsMethodType = False
            self.m_wrObj = None
            self.m_Func = _fn
        self.m_Args = args
        self.m_kwArgs = kwargs
        self.m_bIsPriorityCallArg = False
        return

    def IsActive(self):
        if not self.m_bIsMethodType:
            return True
        else:
            return self.m_wrObj() is not None

    def SetIsPrioriyCallArg(self, _bIsPri):
        self.m_bIsPriorityCallArg = _bIsPri

    def __call__(self, *args, **kwargs):
        curKwArgs = dict(self.m_kwArgs)
        curKwArgs.update(kwargs)
        if not self.m_bIsMethodType:
            if self.m_bIsPriorityCallArg:
                return self.m_Func(*(args + self.m_Args), **curKwArgs)
            else:
                return self.m_Func(*(self.m_Args + args), **curKwArgs)

        realObj = self.m_wrObj()
        if realObj is None:
            return
        else:
            pFunc = self.m_Func
            tArgs = (realObj,)
            if self.m_bIsEngineMethod:
                pFunc = getattr(realObj, self.m_Func)
                tArgs = ()
            if self.m_bIsPriorityCallArg:
                return pFunc(*(tArgs + args + self.m_Args), **curKwArgs)
            return pFunc(*(tArgs + self.m_Args + args), **curKwArgs)
            return


class CFuncWrapper(object):

    def __init__(self, pFunc, pBefore=None, pAfter=None):
        self.m_pBefore = pBefore
        self.m_pAfter = pAfter
        self.InitType(pFunc)

    def InitType(self, pFunc):
        if isinstance(pFunc, types.MethodType):
            self.m_Type = 1
            self.m_wrObj = weakref.ref(pFunc.im_self)
            self.m_pFunc = pFunc.im_func
        else:
            self.m_Type = 2
            self.m_pFunc = pFunc

    def __call__(self, *args, **kwargs):
        if self.m_Type == 1:
            obj = self.m_wrObj()
            if self.m_wrObj():
                if self.m_pBefore:
                    self.m_pBefore()
                res = self.m_pFunc(obj, *args, **kwargs)
                if self.m_pAfter:
                    self.m_pAfter()
                return res
        elif self.m_pBefore:
            self.m_pBefore()
        res = self.m_pFunc(*args, **kwargs)
        if self.m_pAfter:
            self.m_pAfter()
        return res
