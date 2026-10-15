# pycdc 交叉复核产物 · script.fls entry 3543
# co_filename(原始)='script/capturemgr.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3543.pyc (Python 2.5)

import permission
g_CaptureMgr = None
IGNORE = 0
CLEAR_SELF = 1
CLEAR_ALL = 2

def Capture(obj, cap, mouse = 0, iPolicy = CLEAR_ALL):
    if cap:
        GetCaptureMgr().Register(id(obj), obj, mouse, iPolicy)
    else:
        GetCaptureMgr().UnRegister(id(obj), obj)


def CaptureCover(pObj):
    GetCaptureMgr().CaptureCover(pObj)


def PrintStack():
    GetCaptureMgr().PrintCaptureStack()


class CCaptureMgr(object):
    
    def __init__(self):
        self.m_Stack = CCaptureStack()
        self.m_oTimer = None
        self.RefreshUpdateTimer()

    
    def Register(self, iKey, pObj, \xb9\x9d\xbf\xa5\xa3e, iConflictPolicy = CLEAR_ALL):
        '''
\t\t\xb5\xf9\xa5U\xa4@\xad\xd3\xb1\xb1\xa5\xf3\xaa\xbaCapture
\t\tArgs:
\t\t\tiKey: \xb5\xf9\xa5U\xaa\xbakey\xa1A\xa8C\xad\xd3\xadn\xb5\xf9\xa5U\xaa\xba\xb1\xb1\xa5\xf3\xb6\xc7\xa4J\xaa\xbakey\xc0\xb3\xb7\xed\xacO\xb0\xdf\xa4@\xaa\xba\xa1A\xb3q\xb1`\xa5\xceid(pObj)
\t\t\tpObj: \xadn\xb6i\xa6\xe6\xb3B\xb2z\xaa\xba\xb9\xef\xb6H
\t\t\tiMouse: Capture\xa6\xed\xab\xe1\xacO\xa7_\xadn\xb1\xb5\xa6\xac\xa8\xe4\xa5L\xa6a\xa4\xe8\xaa\xba\xc2I\xc0\xbb\xa8\xc6\xa5\xf3
\t\t\tiConfictPolicy: \xc0\xa3\xa4J\xb4\xcc\xae\xc9\xa1A\xa6p\xaaG\xa6\xb9\xae\xc9\xa6\xb3\xa8\xe4\xa5L\xaaF\xa6\xe8\xa5\xbf\xa6bcapture\xa1A\xabh\xb7|\xb5o\xa5\xcd\xbd\xc4\xac\xf0\xa1C\xb3o\xad\xd3\xb0\xd1\xbc\xc6\xb4N\xacO\xbd\xc4\xac\xf0\xae\xc9\xbf\xef\xa8\xfa\xaa\xba\xb5\xa6\xb2\xa4\xa1A\xa6\xb33\xba\xd8\xbf\xef\xbe\xdc
\t\t\t\t1.IGNORE \xa4\xa3\xb3B\xb2z
\t\t\t\t2.CLEAR_SELF \xa5\xfd\xa7\xe2\xb4\xcc\xa4\xba\xa6Pkey\xaa\xba\xb5\xb9\xb2M\xb2z\xa4F
\t\t\t\t3.CLEAR_ALL \xa7\xe2\xb4\xcc\xa4\xba\xb0\xa3\xa4FIGNORE\xaa\xba\xb6\xb5\xa5\xfe\xb2M\xb2z\xa4F
\t\tReturns:

\t\t'''
        import interface
        self.CheckValid()
        self.CheckConflict(iKey, iConflictPolicy)
        self.CheckPanelZAndPush(iKey, {
            'WeakRef': interface.CShadowObject(pObj),
            'IsAcceptOuterMsg': \xb9\x9d\xbf\xa5\xa3e,
            'Policy': iConflictPolicy })
        self.CaptureStackTop()
        if callable(getattr(pObj, 'Topmost', None)):
            pObj.Topmost()
        

    
    def UnRegister(self, iKey, pObj):
        '''
\t\t\xb2M\xb0\xa3\xa4@\xad\xd3\xb1\xb1\xa5\xf3\xaa\xbaCapture
\t\tArgs:
\t\t\tiKey: \xadn\xa8\xfa\xae\xf8\xb5\xf9\xa5U\xaa\xbakey

\t\tReturns:

\t\t'''
        self.CheckValid()
        (iTopKey, dInfo) = self.m_Stack.Top()
        if iTopKey == iKey:
            pObj = dInfo['WeakRef'].Get()
            self.m_Stack.Pop()
            if pObj:
                pObj._RealCapture(0)
            
        
        self.CaptureStackTop()

    
    def CaptureCover(self, pObj):
        if not pObj:
            return None
        
        (iKey, dInfo) = self.m_Stack.Top()
        if not iKey:
            return None
        
        oWr = dInfo['WeakRef']
        if not oWr and oWr.Get():
            return None
        
        oItem = oWr.Get()
        if oItem == pObj:
            return None
        
        oPar = oItem.GetParent()
        pPar = pObj.GetParent()
        if not pPar and oPar:
            return None
        
        if (oPar != pPar or oPar.GetZ() <= pPar.GetZ() or oPar == pPar) and oItem.GetZ() <= pObj.GetZ():
            if callable(getattr(oItem, 'OnCaptureCover', None)):
                oItem.OnCaptureCover(pObj)
            else:
                self.UnRegister(iKey, oItem)
                self.CaptureCover(pObj)
        

    
    def RefreshUpdateTimer(self):
        import timer
        if self.m_oTimer:
            self.m_oTimer.Release()
        
        if permission.GetSpecialVersion():
            self.m_oTimer = timer.Timer(0, self.CheckStackTopIsShowOrNeedClear)
        

    
    def GetTop(self):
        return self.m_Stack.Top()

    
    def PrintCaptureStack(self):
        '''
\t\t\xa5\xb4\xa6L\xb0\xef\xb4\xcc\xb1\xa1\xaap
\t\t'''
        tSaveList = []
        (iKey, dInfo) = self.m_Stack.Pop()
        while iKey:
            tSaveList.append((iKey, dInfo))
            (iKey, dInfo) = self.m_Stack.Pop()
        for tRecord in tSaveList[::-1]:
            self.m_Stack.Push(*tRecord)
        
        LOG_DEBUG('----stack begin----')
        for iKey, dInfo in tSaveList:
            if self.IsItemValid(dInfo):
                sExt = ''
            else:
                sExt = '\xbb\xdd\xadn\xb2M\xb2z'
            LOG_DEBUG('|', iKey, type(dInfo['WeakRef'].Get()), dInfo['Policy'], sExt)
        
        LOG_DEBUG('-----stack end-----')

    
    def CheckValid(self):
        '''
\t\t\xc0\xcb\xacd\xc1\xd9\xaf\xe0\xa5\xcd\xae\xc4\xaa\xbaCapture
\t\t'''
        tValidList = []
        (iKey, dInfo) = self.m_Stack.Pop()
        while iKey:
            if self.IsItemValid(dInfo):
                tValidList.append((iKey, dInfo))
            
            (iKey, dInfo) = self.m_Stack.Pop()
        for tRecord in tValidList[::-1]:
            self.m_Stack.Push(*tRecord)
        

    
    def CheckConflict(self, iKey, iPolicy):
        '''
\t\t\xb8\xd1\xa8M\xbd\xc4\xac\xf0
\t\tArgs:
\t\t\tiKey: \xb7s\xb4\xa1\xa4J\xaa\xbakey
\t\t\tiPolicy: \xbd\xc4\xac\xf0\xb8\xd1\xa8M\xaa\xba\xb5\xa6\xb2\xa4\xa1A\xadn\xa8\xcf\xa5\xce\xa7\xbb\xa9w\xb8q

\t\tReturns:

\t\t'''
        if iPolicy == IGNORE:
            return None
        elif iPolicy == CLEAR_ALL:
            tIgnoreList = []
            (iKey, dInfo) = self.m_Stack.Pop()
            while iKey:
                if not dInfo or dInfo['Policy'] == IGNORE:
                    tIgnoreList.append((iKey, dInfo))
                
                (iKey, dInfo) = self.m_Stack.Pop()
            for tRecord in tIgnoreList[::-1]:
                self.m_Stack.Push(*tRecord)
            
        elif iPolicy == CLEAR_SELF:
            self.m_Stack.Clear(iKey)
        

    
    def CheckPanelZAndPush(self, iKey, dInfo):
        '''
\t\t\xc0\xcb\xacdpanel\xaa\xba\xbch\xaf\xc5\xb5M\xab\xe1\xc0\xa3\xb4\xcc\xa1]\xa6\xb3\xa5i\xaf\xe0\xa5X\xb2{\xb4\xa1\xb6\xa4\xa1^
\t\t:param iKey: \xadn\xc0\xa3\xb4\xcc\xaa\xba\xc1\xe4\xad\xc8
\t\t:param dInfo: \xadn\xc0\xa3\xb4\xcc\xaa\xba\xa8\xe3\xc5\xe9\xabH\xae\xa7
\t\t:return:
\t\t'''
        tPreList = []
        iPushZ = GetDialogPanelZ(dInfo['WeakRef'].Get())
        iItemKey = True
        dItemInfo = None
        while iItemKey:
            if dItemInfo:
                iItemZ = GetDialogPanelZ(dItemInfo['WeakRef'].Get())
                if iItemZ > iPushZ:
                    tPreList.append(self.m_Stack.Pop())
                else:
                    break
            
            (iItemKey, dItemInfo) = self.m_Stack.Top()
        self.m_Stack.Push(iKey, dInfo)
        for tRecord in tPreList[::-1]:
            self.m_Stack.Push(*tRecord)
        

    
    def CaptureStackTop(self):
        '''
\t\tCapture\xa6\xed\xb4\xcc\xb3\xbb\xa1A\xaa\xc5\xb4\xcc\xabh\xa4\xa3\xa6ACapture
\t\t:return: N^ne
\t\t'''
        (iKey, dInfo) = self.m_Stack.Top()
        if iKey:
            oRealObj = dInfo['WeakRef'].Get()
            if oRealObj:
                oRealObj._RealCapture(1, dInfo['IsAcceptOuterMsg'])
            else:
                LOG_ERR('realobj\xa4\xa3\xc0\xb3\xb8\xd3\xac\xb0None-hzq, %s %s' % self.m_Stack.Top())
                self.CheckValid()
                self.CaptureStackTop()
        

    
    def IsItemValid(self, dInfo):
        '''
\t\t\xc0\xcb\xacd\xa4@\xad\xd3\xa4\xb8\xaf\xc0\xacO\xa7_\xa6\xb3\xae\xc4\xa1A\xb2{\xa6b\xacO3\xad\xd3\xb1\xf8\xa5\xf3\xa7P\xa9w\xa6\xb3\xae\xc4
\t\t1.\xaez\xa4\xde\xa5\xce\xa4\xa3\xac\xb0None
\t\t2.\xa4\xb8\xaf\xc0\xa5\xbb\xa8\xad\xa4\xa3\xac\xb0None
\t\t3.\xa4\xb8\xaf\xc0\xc5\xe3\xa5\xdc\xa4\xa4
\t\t'''
        oWr = dInfo['WeakRef']
        if oWr and oWr.Get() and oWr.Get().GetShow():
            return True
        
        return False

    
    def ClearAll(self):
        '''
\t\t\xa8\xfa\xae\xf8\xb1\xbc\xa9\xd2\xa6\xb3Capture\xb6\xb5
\t\tReturns:
\t\t'''
        pass

    
    def CheckStackTopIsShowOrNeedClear(self):
        '''
\t\t\xc0\xcb\xacd\xb7\xed\xabe\xb4\xcc\xb3\xbb\xa4\xb8\xaf\xc0\xacO\xa7_\xa6s\xa6b\xa4\xa3\xa6X\xb2z\xa4\xa7\xb3B\xa1A\xa5]\xacA
\t\t1.\xb4\xcc\xb3\xbb\xa4w\xb8g\xa4\xa3\xa6b\xa4F\xa1A\xa6\xfd\xacO\xa5\xa6\xa8S\xa6\xb3\xbd\xd5\xa5\xceCapture(0)\xa1A\xbe\xc9\xadPcapturemgr\xb3o\xc3\xe4\xa8S\xa6\xb3cap\xa6\xed\xa4U\xa4@\xad\xd3
\t\t2.\xb4\xcc\xb3\xbb\xc1\xd9\xa6b\xa1A\xa6\xfd\xacO\xa5\xa6\xaa\xba\xa4\xf7\xb8`\xc2I\xbe\xf0\xa4w\xb8g\xa4\xa3\xc5\xe3\xa5\xdc\xa4F
\t\t'''
        (iKey, dInfo) = self.m_Stack.Top()
        if not iKey:
            return None
        
        if not dInfo['WeakRef'] and dInfo['WeakRef'].Get():
            self.CheckValid()
            self.CaptureStackTop()
        else:
            oItem = dInfo['WeakRef'].Get()
            while oItem:
                if not oItem.GetShow():
                    self.UnRegister(iKey, oItem)
                    return None
                
                oItem = oItem.GetParent()

    
    def GetStackSize(self):
        self.CheckValid()
        return self.m_Stack.GetSize()



class CCaptureStack(object):
    
    def __init__(self):
        self.m_CaptureStack = []
        self.m_Config = { }

    
    def Top(self):
        '''
\t\t\xa8\xfa\xa5X\xb4\xcc\xb3\xbb\xabH\xae\xa7\xa1A\xa4\xa3\xbcu\xa5X\xb4\xcc\xb3\xbb
\t\t'''
        if not self.m_CaptureStack:
            return (None, None)
        
        iKey = self.m_CaptureStack[-1]
        dInfo = self.m_Config[iKey][-1]
        return (iKey, dInfo)

    
    def Pop(self):
        '''
\t\t\xbcu\xa5X\xb4\xcc\xb3\xbb
\t\t'''
        if not self.m_CaptureStack:
            return (None, None)
        
        iKey = self.m_CaptureStack.pop()
        dInfo = self.m_Config[iKey].pop()
        return (iKey, dInfo)

    
    def Push(self, iKey, dInfo):
        '''
\t\t\xc0\xa3\xa4J\xa4\xb8\xaf\xc0
\t\t'''
        self.m_CaptureStack.append(iKey)
        if iKey not in self.m_Config:
            self.m_Config[iKey] = []
        
        self.m_Config[iKey].append(dInfo)

    
    def Clear(self, iKey):
        '''
\t\t\xb2M\xb2z\xacY\xa4@\xad\xd3Key
\t\t'''
        while iKey in self.m_CaptureStack:
            self.m_CaptureStack.remove(iKey)
        self.m_Config[iKey] = []

    
    def GetSize(self):
        return len(self.m_CaptureStack)



def GetCaptureMgr():
    global g_CaptureMgr
    if not g_CaptureMgr:
        g_CaptureMgr = CCaptureMgr()
    
    return g_CaptureMgr


def GetDialogPanelZ(oDialog):
    import interface
    oParent = oDialog
    preParent = oDialog
    while oParent:
        if isinstance(oParent, interface.CPanel) and oParent.GetParent() is None:
            return oParent.GetZ()
            continue
        preParent = oParent
        oParent = oParent.GetParent()
    if preParent:
        return preParent.GetZ()
    
    return -1
