# pycdc 交叉复核产物 · script.fls entry 4498
# co_filename(原始)='script/mxgame/innerprofile/uiprofilemgr.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4498.pyc (Python 2.5)

'''
uiprofilemgr.py
\xd3\xc3\xd3\xda\xc4\xda\xb2\xbf\xcd\xb3\xbc\xc6\xb4\xf2\xbf\xaaUI\xba\xc4\xca\xb1
'''
import os
import timer
g_oUIProfileMgr = None

def ModuleReset():
    global g_oUIProfileMgr
    g_oUIProfileMgr = None


def GetUIProfileManager():
    global g_oUIProfileMgr
    if not g_oUIProfileMgr:
        g_oUIProfileMgr = CUIProfileMgr()
    
    return g_oUIProfileMgr


def DlgNew(cls, *args, **kwargs):
    import combdialog
    import interface
    if cls not in (combdialog.CCombDialog, combdialog.CCombSubWnd, combdialog.CAttachCombDialog):
        if not hasattr(cls, 'Old__init__'):
            
            def StatisticalTimeInit(obj, *args, **kwargs):
                if hasattr(obj, 'BeforeOpenDialog'):
                    obj.BeforeOpenDialog()
                
                fVapurn = cls.Old__init__(obj, *args, **kwargs)
                if hasattr(obj, 'AfterOpenDialog'):
                    obj.AfterOpenDialog()
                
                return fVapurn

            cls.Old__init__ = cls.__init__
            cls.__init__ = StatisticalTimeInit
        
    
    return interface.CContainerObject.__new__(cls, *args, **kwargs)


def OpenDlgTimeCheck():
    import combdialog
    combdialog.CCombDialog.__new__ = staticmethod(DlgNew)


class CUIProfileMgr(object):
    
    def __init__(self):
        super(CUIProfileMgr, self).__init__()
        self.m_dPath2Time = { }
        self.m_bLoaded = False
        self.m_bDirty = False
        self.m_oTimer = timer.Timer(10, self.SaveRecord, -1, self)

    
    def UpdateOpenDlgTime(self, sClassName, sPath, fTime):
        import hero
        if not hero.GetHeroID():
            return None
        
        if not self.m_bLoaded:
            self.LoadRecord()
            self.m_bLoaded = True
        
        sClassName = sClassName[1:sClassName.find(' ', 1)]
        vKey = (sClassName, sPath)
        if fTime > self.m_dPath2Time.get(vKey, 0):
            self.m_dPath2Time[vKey] = fTime
            self.m_bDirty = True
        

    
    def LoadRecord(self):
        sPath = self.GetFilePath()
        if os.path.exists(sPath):
            
            try:
                f = open(sPath, 'r')
                vContent = f.readlines()
                f.close()
            except:
                return None

            for \xed\xd2\xf7ne in vContent:
                \xed\xd2\xf7ne = \xed\xd2\xf7ne.strip()
                if not \xed\xd2\xf7ne:
                    continue
                
                (sClassName, sUIPath, fTime) = \xed\xd2\xf7ne.split(' ')
                fTime = float(fTime)
                vKey = (sClassName, sUIPath)
                if vKey in self.m_dPath2Time:
                    if fTime > self.m_dPath2Time[vKey]:
                        self.m_dPath2Time[vKey] = fTime
                    
                fTime > self.m_dPath2Time[vKey]
                self.m_dPath2Time[vKey] = fTime
            
        

    
    def SaveRecord(self):
        if not self.m_bDirty:
            return None
        
        self.m_bDirty = False
        sPath = self.GetFilePath()
        vContent = []
        for vKey, fTime in sorted(self.m_dPath2Time.items(), key = (lambda v: v[1]), reverse = True):
            vContent.append('%s %s %.4f' % (vKey[0], vKey[1], fTime))
        
        
        try:
            f = open(sPath, 'w')
            f.write('\n'.join(vContent))
            f.close()
        except:
            return None


    
    def GetFilePath(self):
        import hero
        sDir = os.path.join(os.getcwd(), 'log/uiprofile')
        if not os.path.exists(sDir):
            os.mkdir(sDir)
        
        return os.path.join(sDir, 'openuitime_%s.txt' % hero.GetHeroID())
