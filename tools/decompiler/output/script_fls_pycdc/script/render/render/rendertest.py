# pycdc 交叉复核产物 · script.fls entry 1545
# co_filename(原始)='script/render/render/rendertest.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1545.pyc (Python 2.5)

import slot
TEST_RES = [
    'avatar/140_200/2300/231309.png']
g_bIsRenderAble = False
g_oRenderTest = None

def IsRenderAble():
    return g_bIsRenderAble


def InitRenderTest():
    GetRenderTest().Run()


def ConnectChangeCB(oCB):
    GetRenderTest().ssConnect(GetRenderTest().SS_RenderChange, oCB)


class CRenderTest(slot.ISignalSubject):
    SS_RenderChange = 'OnChange()'
    
    def __init__(self):
        self.ssInit()
        self.m_iTestTimes = 0
        self.m_iHeartBeatTimer = None

    
    def Run(self):
        self.NextTest()

    
    def KeepHeartBeat(self):
        import \xc3\xde\xdaer
        import netrender
        self.StopKeepAlive()
        self.m_iHeartBeatTimer = \xc3\xde\xdaer.Timer(2, netrender.C2RHeartBeat, -1, self)

    
    def StopKeepAlive(self):
        if self.m_iHeartBeatTimer:
            self.m_iHeartBeatTimer.Release()
            self.m_iHeartBeatTimer = None
        

    
    def NextTest(self):
        import renderavatar
        import interface
        self.m_iTestTimes += 1
        self.m_oRenderImg = renderavatar.CreateRenderAvatar(None, TEST_RES, interface.UIPath, self.OnRenderCB)
        if self.m_oRenderImg:
            self.m_oRenderImg.SetShow(False)
        

    
    def OnRenderCB(self, bSuccess):
        global g_bIsRenderAble
        LOG('render test:', self.m_iTestTimes, bSuccess)
        if g_bIsRenderAble != bSuccess:
            g_bIsRenderAble = bSuccess
            self.ssEmit(self.SS_RenderChange)
        
        if not bSuccess:
            if self.m_iTestTimes < 3:
                self.NextTest()
            else:
                self.m_oRenderImg = None
                self.KeepHeartBeat()
        else:
            self.m_oRenderImg = None
            self.KeepHeartBeat()



def GetRenderTest():
    global g_oRenderTest
    if not g_oRenderTest:
        g_oRenderTest = CRenderTest()
    
    return g_oRenderTest
