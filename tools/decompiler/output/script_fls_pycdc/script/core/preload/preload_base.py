# pycdc 交叉复核产物 · script.fls entry 4756
# co_filename(原始)='script/core/preload/preload_base.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4756.pyc (Python 2.5)

'''
================================================================================
\xd7\xf7\xd5\xdf: hufenlin
\xc3\xe8\xca\xf6: \xd4\xa4\xbc\xd3\xd4\xd8 \xb7\xa8\xca\xf5\xd7\xca\xd4\xb4\xc0\xe0\xd0\xcdpreload_base.py
\t\xcc\xe1\xb9\xa9\xb3\xe9\xcf\xf3\xbd\xd3\xbf\xda
\tInit \xb3\xf5\xca\xbc\xbb\xaf \xb5\xf7\xd3\xc3VLoadMagic/VStartParser
\tVLoadMagic \xbc\xd3\xd4\xd8\xd7\xca\xd4\xb4xxx.mgc/skill/pfm
\tVStartParser \xbd\xe2\xce\xf6\xb7\xa8\xca\xf5\xce\xc4\xbc\xfe \xc5\xb5\xc1\xd0\xb3\xf6\xd0\xe8\xd2\xaa\xd4\xa4\xbc\xd3\xd4\xd8\xb5\xc4\xd7\xca\xd4\xb4
\tVPreloadMagic \xbf\xaa\xca\xbc\xd4\xa4\xbc\xd3\xd4\xd8\xd7\xca\xd4\xb4

================================================================================
'''
import weakref

class CPreloadBase(object):
    
    def __init__(self = None, nMagicID = None, pMgr = None):
        self.m_nMagicID = nMagicID
        self.m_wrMgr = weakref.ref(pMgr)
        self.m_dResult = { }
        self.m_dPath2Num = { }

    
    def Init(self):
        self.VLoadMagic()
        self.VStartParser()

    
    def GetMgr(self):
        return self.m_wrMgr()

    
    def Clear(self):
        pMgr = self.GetMgr()
        for tPath, nNum in self.m_dPath2Num.items():
            pMgr.ClearRes(tPath, nNum)
        
        self.m_dPath2Num = { }

    
    def VLoadMagic(self):
        pass

    
    def VStartParser(self):
        pass

    
    def VPreloadMagic(self, pCmd):
        pass
