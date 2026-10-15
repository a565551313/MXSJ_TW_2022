# pycdc 交叉复核产物 · script.fls entry 132
# co_filename(原始)='script/blacklist/multiclientcheck.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_132.pyc (Python 2.5)

VALID_CLIENT_NUM = 3
g_MultiCheck = None

def ModuleReset():
    global g_MultiCheck
    if g_MultiCheck:
        g_MultiCheck.StopCheck()
    
    g_MultiCheck = None


def StartCheck(iTimes = 1, iInterval = None):
    oCheck = GetCheckObj()
    if iInterval is not None:
        oCheck.CheckInterval(iTimes, iInterval)
    elif iTimes > 0:
        oCheck.CheckOnce()
    


class CMultiClientCheck(object):
    DIFFRENT_ERROR = 0
    MAXNUM_ERROR = 1
    
    def __init__(self):
        self.m_Config = {
            'Method': [
                CSharememMethod(),
                CProcessMethod(),
                CWindowNameMethod()],
            'IgnoreError': [
                self.MAXNUM_ERROR] }
        self.m_CheckTimer = None

    
    def CheckInterval(self, iTimes, iInterval):
        import timer
        if self.m_CheckTimer:
            self.m_CheckTimer.Release()
        
        self.m_CheckTimer = timer.Timer(iInterval, self.CheckOnce, iTimes)

    
    def CheckOnce(self):
        lCheckResult = []
        for oMethod in self.m_Config['Method']:
            dResult = {
                'name': oMethod.GetMethodName(),
                'count': oMethod.GetClientCount() }
            lCheckResult.append(dResult)
        
        self.DealResult(lCheckResult)

    
    def StopCheck(self):
        if self.m_CheckTimer:
            self.m_CheckTimer.Release()
        
        self.m_CheckTimer = None

    
    def DealResult(self, lCheckResult):
        lError = []
        iCount = -1
        for dResult in lCheckResult:
            if iCount != -1 and dResult['count'] != iCount:
                lError.append(self.DIFFRENT_ERROR)
                break
                continue
            iCount = dResult['count']
        
        for dResult in lCheckResult:
            raise None, dResult
            if None[None] > VALID_CLIENT_NUM:
                lError.append(self.MAXNUM_ERROR)
                break
                continue
        
        self.DoPunish(lCheckResult, lError)

    
    def DoPunish(self, lCheckResult, lError):
        for iError in lError:
            if iError not in self.m_Config['IgnoreError']:
                break
                continue
        else:
            return None
        sMsg = ''
        for dResult in lCheckResult:
            sMsg += '%s\xb5\xb2\xaaG\xac\xb0: %s;' % (dResult['name'], dResult['count'])
        
        import blacklist
        blacklist.C2SResult(38, sMsg)



def GetCheckObj():
    global g_MultiCheck
    if not g_MultiCheck:
        g_MultiCheck = CMultiClientCheck()
    
    return g_MultiCheck


class CCheckMethod(object):
    METHODNAME = '<\xa5\xbc\xaa\xbe>'
    
    def GetMethodName(self):
        return self.METHODNAME

    
    def GetClientCount(self):
        raise NotImplementedError('\xbb\xdd\xadn\xb9\xea\xb2{GetClientCount\xa4\xe8\xaak')



class CSharememMethod(CCheckMethod):
    METHODNAME = '\xa6@\xa8\xc9\xa4\xba\xa6s\xc0\xcb\xb4\xfa'
    
    def GetClientCount(self):
        import sharemem
        return sharemem.GetMemAmount()



class CProcessMethod(CCheckMethod):
    METHODNAME = '\xb6i\xb5{\xbc\xc6\xb6q\xc0\xcb\xb4\xfa'
    
    def GetClientCount(self):
        import device
        return device.GetProcessCount()



class CWindowNameMethod(CCheckMethod):
    METHODNAME = '\xb5\xa1\xa4f\xbc\xd0\xc3D\xc0\xcb\xb4\xfa'
    
    def GetClientCount(self):
        import blacklist
        return blacklist.CCheckWindowsName.GetWindowCount() + 1
