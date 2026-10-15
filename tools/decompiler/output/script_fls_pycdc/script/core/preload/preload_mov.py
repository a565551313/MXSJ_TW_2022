# pycdc 交叉复核产物 · script.fls entry 2371
# co_filename(原始)='script/core/preload/preload_mov.py'
# uncompyle6 状态=recovered  转译阶段=baseline
# 生成时间=2026-10-14T23:56:17Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2371.pyc (Python 2.5)

'''
================================================================================
\xd7\xf7\xd5\xdf: hufenlin
\xc3\xe8\xca\xf6: \xd4\xa4\xbc\xd3\xd4\xd8 \xb7\xa8\xca\xf5\xd7\xca\xd4\xb4xxx.mgc
a. xxx.mgc
[info]\ta.\xb0\xb5\xc6\xc1\xb6\xaf\xbb\xad + \xca\xdc\xbb\xf7+hurt \xb5\xe3
Red=0
Green=0
Blue=0
Alpha=0
HitFrame=37 37
HurtFrame=37
VictimAction=move/10008a.mov  \xd0\xe8\xd2\xaa\xd4\xa4\xbc\xd3\xd4\xd8

AttackHurtAction=hurtxxx \xd3\xc5\xcf\xc8xxx.mov \xb1\xed\xcf\xd6
[des] \t\xca\xc7\xd7\xf6\xcc\xd8\xd0\xa7\xb9\xec\xbc\xa3 \xb6\xaf\xbb\xad\xa3\xba
3\t\xd7\xca\xd4\xb4\xca\xfd\xc1\xbf
res\x0cr2cx_0.igs 600 500\xd4\xb4\xc2\xb7\xbe\xb6 +Z+Speed \xd0\xe8\xd2\xaa\xd4\xa4\xbc\xd3\xd4\xd8

b. xxx.mov


================================================================================
'''
import preload_base
import C_sys
import misc
g_MovConfigMgr = None

def GetConfigMgr():
    global g_MovConfigMgr
    if not g_MovConfigMgr:
        g_MovConfigMgr = CMovConfigMgr()
    
    return g_MovConfigMgr


def ModuleReset():
    global None, g_MovConfigMgr
    None = None
    g_MovConfigMgr = None


class CMovConfigMgr(object):
    
    def __init__(self):
        self.m_dMovConfig = { }

    
    def GetMovConfig(self, fileName):
        dData = self.m_dMovConfig.get(fileName)
        if not dData:
            self.preloadMovConfig(fileName)
            dData = self.m_dMovConfig.get(fileName)
        
        return dData

    
    def preloadMovConfig(self, fileName):
        data = C_sys.LoadFile(fileName, 'magic')
        if data:
            data = data.splitlines()
        
        lCmd = []
        self.m_dMovConfig[fileName] = lCmd
        for line in data:
            array = line.split(' ')
            if not array:
                continue
            
            sFuncName = array[0]
            tValue = array[1:]
            lCmd.append((sFuncName, tValue))
        



class CPreloadMov(preload_base.CPreloadBase):
    
    def __init__(self, nMagicID, pMgr):
        super(CPreloadMov, self).__init__(nMagicID, pMgr)
        self.m_sMovID = nMagicID
        self.m_dPreloadFunc = {
            'PlayAni': 'preloadCmd_PlayAni',
            'PlayTraceAni': 'preloadCmd_PlayTraceAni' }

    
    def VLoadMagic(self):
        pass

    
    def VStartParser(self):
        pass

    
    def VPreloadMagic(self, pMagic):
        pMgr = GetConfigMgr()
        lCmd = pMgr.GetMovConfig(self.m_sMovID)
        for sEventName, tData in lCmd:
            sFunc = self.m_dPreloadFunc.get(sEventName)
            if not sFunc:
                continue
            
            pFunc = getattr(self, sFunc)
            if not pFunc:
                continue
            
            pFunc(tData, pMagic)
        

    
    def preloadCmd_PlayAni(self, lData, pMagic):
        sPath = lData[0]
        sDir = lData[1]
        pMgr = self.GetMgr()
        pMgr.PreloadResObj(sPath, sDir, pMagic)

    
    def preloadCmd_PlayTraceAni(self, lData, pMagic):
        nNum = lData[5]
        sPath = lData[6]
        sDir = lData[7]
        pMgr = self.GetMgr()
        pMgr.PreloadResObj(sPath, sDir, pMagic)
