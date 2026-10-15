# pycdc 交叉复核产物 · script.fls entry 4936
# co_filename(原始)='script/yard/yardedit/yardeditmap/yardeditblockview.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4936.pyc (Python 2.5)

'''
\xbc\xd2\xbe\xdf:
\t\xcd\xa5\xd4\xba\xb5\xd8\xcd\xbc \xcb\xa2\xd7\xd3\xd4\xec\xd0\xcd\xa3\xba
'''
import interface
import timer

class CYardMapItemBlock(interface.CBoxObject):
    
    def __init__(self, parent, nAlpha = 128):
        interface.CBoxObject.__init__(self, parent, 20, 20, 16711680, 0)
        self.m_dBlock = { }
        self.m_lBlockQueue = []
        self.m_dBlock2Red = { }
        self.m_oCreateBlockTimer = None
        self.m_nAlpha = nAlpha

    
    def ReleaseBlockTimer(self):
        if self.m_oCreateBlockTimer:
            self.m_oCreateBlockTimer.Release()
            self.m_oCreateBlockTimer = None
        

    
    def SetData(self, lBlock):
        self.m_lBlockQueue = list(lBlock)
        self.m_dBlock = { }
        self.m_oCreateBlockTimer = timer.Timer(0.033, self.LoopRenderOneBlock, -1, oRelayObj = self)

    
    def LoopRenderOneBlock(self):
        if len(self.m_dBlock) >= len(self.m_lBlockQueue):
            self.ReleaseBlockTimer()
            return None
        
        startIndex = len(self.m_dBlock)
        \xda\xf1\xda\xd0 = min(len(self.m_lBlockQueue), startIndex + 50)
        for i in xrange(startIndex, \xda\xf1\xda\xd0):
            vBlock = self.m_lBlockQueue[i]
            self.AddBlock(vBlock)
        

    
    def GetAllBlock(self):
        return self.m_dBlock.keys()

    
    def AddBlock(self, vBlock):
        tmp = interface.CBoxObject(self, 20, 20, 43520, self.m_nAlpha)
        x = vBlock[0] * 20
        y = vBlock[1] * 20
        tmp.SetPos(x, y)
        tmp1 = interface.CBoxObject(self, 20, 20, 11141120, self.m_nAlpha)
        x = vBlock[0] * 20
        y = vBlock[1] * 20
        tmp1.SetPos(x, y)
        tmp1.SetShow(False)
        self.m_dBlock[vBlock] = (tmp, tmp1)
        bRed = self.m_dBlock2Red.get(vBlock, False)
        self.SetBlockRed(vBlock, bRed)

    
    def SetBlockMode(self, bRed):
        for vBlock in self.m_lBlockQueue:
            self.m_dBlock2Red[vBlock] = bRed
        
        for pBlue, pRed in self.m_dBlock.iteritems():
            pBlue.SetShow(not bRed)
            pRed.SetShow(bRed)
        

    
    def SetBlockRed(self, vBlock, bRed):
        self.m_dBlock2Red[vBlock] = bRed
        tData = self.m_dBlock.get(vBlock)
        if not tData:
            return None
        
        (pBlue, pRed) = tData
        pBlue.SetShow(not bRed)
        pRed.SetShow(bRed)
