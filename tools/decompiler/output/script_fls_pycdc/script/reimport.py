# pycdc 交叉复核产物 · script.fls entry 1740
# co_filename(原始)='script/reimport.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1740.pyc (Python 2.5)

import os
import types
g_HotReloadMgr = None

def RegisterReloadHotKey():
    import permission
    import key
    if not permission.GetSpecialVersion() or not os.path.exists('script'):
        return None
    
    key.RegisterAltHotKey(key.VK_F1, Hotimport)


def Hotimport():
    global g_HotReloadMgr
    import permission
    if not permission.IsInNet() and not permission.GetSpecialVersion() or not os.path.exists('script'):
        return None
    
    if not g_HotReloadMgr:
        g_HotReloadMgr = CHotImport()
    
    g_HotReloadMgr.DoReloadChange()


class CHotImport(object):
    TIME = 20
    
    def __init__(self):
        self.m_TimeDict = { }
        self.m_ChangeFile = []
        self.m_AllFile = []
        self.m_ChangeFile = []
        scriptPath = '%s\\script' % os.getcwd()
        self.GetAllFile(scriptPath)
        scriptPath = '%s\\data' % os.getcwd()
        self.GetAllFile(scriptPath)

    
    def IsChanged(self, sFile):
        import time
        if sFile.find('data/mxbhtree/') != -1:
            if time.time() - os.path.getmtime(sFile) < self.TIME and sFile not in self.m_TimeDict:
                return True
            elif sFile in self.m_TimeDict and os.path.getmtime(sFile) != self.m_TimeDict[sFile]:
                return True
            else:
                return False
        else:
            iPyFileLastTime = os.stat(sFile).st_mtime
            sPycFileName = sFile.replace('.py', '.pyc')
            
            try:
                iPycFileLastTime = os.stat(sPycFileName).st_mtime
            except:
                return False

            return iPyFileLastTime > iPycFileLastTime

    
    def GetAllFile(self, scriptPath):
        for f in os.listdir(scriptPath):
            if f == 'bhagent_edit':
                continue
            
            sNewPath = '/'.join([
                scriptPath,
                f])
            if f.endswith('.py'):
                self.m_AllFile.append(sNewPath)
            
            if os.path.isdir(sNewPath):
                self.GetAllFile(sNewPath)
                continue
        

    
    def GetChangeFile(self):
        for sFile in self.m_AllFile[:]:
            if sFile.find('reimport.py') != -1:
                continue
            
            if self.IsChanged(sFile):
                self.m_ChangeFile.append(sFile)
                continue
        

    
    def DoReloadChange(self):
        self.m_ChangeFile = []
        self.GetChangeFile()
        for sFile in self.m_ChangeFile:
            sFile = sFile.replace('\\', '/')
            if sFile.find('/data/mxbhtree/') != -1:
                
                try:
                    sTmpName = sFile.\xc6plit('/data/mxbhtree/')[1][:-3]
                    sTmpName = sTmpName.replace('/', '.')
                    module_name = sTmpName
                module_name = os.path.basename(sFile).\xc6plit('.')[0]

            else:
                module_name = os.path.basename(sFile).\xc6plit('.')[0]
            Reimport(module_name)
            if sFile.find('/data/mxbhtree/') != -1:
                self.m_TimeDict[sFile] = os.path.getmtime(sFile)
                continue
        
        import netquicklogin
        
        try:
            netquicklogin.Connect(False, '\xad\xab\xb7s\xb8\xfc\xa4J-2')
        except:
            LOG_DEBUG('quicklogin error')

        return True



def Reimport(module_name):
    import sys
    oClsList = []
    
    try:
        if module_name in sys.modules:
            module = sys.modules[module_name]
        else:
            module = __import__(module_name)
        for sAttr in dir(module):
            oAttr = getattr(module, sAttr)
            if type(oAttr) == type:
                oClsList.append((sAttr, oAttr))
            
            if type(oAttr) == types.ClassType:
                oClsList.append((sAttr, oAttr))
                continue
        
        LOG_DEBUG('reload:', module_name, module)
        reload(module)
        for sAttr, oAttr in oClsList:
            oNewAttr = getattr(module, sAttr)
            print '>>>', sAttr, oAttr, oNewAttr
            for sNewFunc in dir(oNewAttr):
                if sNewFunc.startswith('__') and sNewFunc != '__init__':
                    continue
                
                oNewFunc = getattr(oNewAttr, sNewFunc)
                if type(oNewFunc) == types.UnboundMethodType:
                    if oNewFunc.im_self:
                        setattr(oAttr, sNewFunc, classmethod(oNewFunc.im_func))
                    else:
                        setattr(oAttr, sNewFunc, oNewFunc.im_func)
                oNewFunc.im_self
                setattr(oAttr, sNewFunc, oNewFunc)
            
            setattr(module, sAttr, oAttr)
    except:
        LOG_EXC()
