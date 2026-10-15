# pycdc 交叉复核产物 · script.fls entry 3699
# co_filename(原始)='script/core/preload/myprofie.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3699.pyc (Python 2.5)

'''
================================================================================
\xd7\xf7\xd5\xdf: hufenlin
\xc3\xe8\xca\xf6: \xb4\xf2\xd3\xa1\xca\xb1\xbc\xe4\xcf\xfb\xba\xc4

================================================================================
'''
import time
S_FPRINT_TIME = 0.1

class TimeRecord(object):
    
    def __init__(self, sKey):
        self.m_sKey = sKey
        self.m_bRecord = True
        self.m_fStartTime = time.clock()

    
    def Start(self):
        self.m_fStartTime = time.clock()

    
    def Record(self):
        fTime = time.clock()
        \xda\xec\xe8ime = fTime - self.m_fStartTime
        \xda\xec\xe8ime = \xda\xec\xe8ime * 1000
        self.m_bRecord = \xda\xec\xe8ime > S_FPRINT_TIME
        if self.m_bRecord:
            LOG('%s costtime:' % self.m_sKey, \xda\xec\xe8ime)
        
        self.m_fStartTime = time.clock()

    
    def IsRecord(self):
        return self.m_bRecord


g_TimeRecord = { }

def Start(sKey):
    pTime = g_TimeRecord.get(sKey, None)
    if not pTime:
        pTime = TimeRecord(sKey)
        g_TimeRecord[sKey] = pTime
    
    pTime.Start()


def Record(sKey):
    pTime = g_TimeRecord.get(sKey, None)
    if pTime:
        pTime.Record()
    


def Get(sKey):
    return g_TimeRecord.get(sKey, None)


def westartClear():
    g_TimeRecord.clear()
