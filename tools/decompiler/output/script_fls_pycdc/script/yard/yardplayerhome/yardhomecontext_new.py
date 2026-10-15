# pycdc 交叉复核产物 · script.fls entry 4852
# co_filename(原始)='script/yard/yardplayerhome/yardhomecontext_new.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4852.pyc (Python 2.5)

import yardhome_oneplayer
import yardmapdatamgr
import hero
g_oYardHomeContext = None

def ModuleReset():
    global g_oYardHomeContext
    g_oYardHomeContext = None


def GetHomeContext():
    global g_oYardHomeContext
    if not g_oYardHomeContext:
        g_oYardHomeContext = CYardHomeContext()
    
    return g_oYardHomeContext


class CYardHomeContext(object):
    
    def __init__(self):
        self.m_dPlayerYardHome = { }
        self.m_oYardMapMgr = None
        self.m_oMainDlg = None
        self.m_oVisitDataMgr = None

    
    def GetYardMapMgr(self):
        if not self.m_oYardMapMgr:
            self.m_oYardMapMgr = yardmapdatamgr.CYardMapDataMgr()
        
        return self.m_oYardMapMgr

    
    def GetVisitDataMgr(self):
        import yardhomevisitdatamgr
        if not self.m_oVisitDataMgr:
            self.m_oVisitDataMgr = yardhomevisitdatamgr.CYardVisitDataMgr()
        
        return self.m_oVisitDataMgr

    
    def IsHomeYard(self, iYardOwnerID):
        bHomeYard = iYardOwnerID in self.m_dPlayerYardHome
        if bHomeYard:
            return True
        else:
            for _, oPlayerHome in self.m_dPlayerYardHome.iteritems():
                if iYardOwnerID in oPlayerHome.GetCoupleID():
                    return True
                    continue
            
            return False

    
    def GetYardHomeDlg(self):
        return self.m_oMainDlg

    
    def IsEnableShowYard(self):
        if not self.m_dPlayerYardHome:
            return False
        else:
            return True

    
    def IsYardHomeDlgShow(self):
        if self.m_oMainDlg and self.m_oMainDlg.GetShow():
            return True
        else:
            return False

    
    def ShowYardHomeDlg(self, dExtend = None):
        import interface
        import dlgyardhome
        if not self.m_oMainDlg:
            self.m_oMainDlg = dlgyardhome.CYardHomeDlg(interface.DialogPanel)
        else:
            self.m_oMainDlg.Topmost()
        self.m_oMainDlg.VOpenPage(dExtend)
        interface.Center(self.m_oMainDlg)
        import netyardhome
        netyardhome.C2SYardHome_GetInfo()
        netyardhome.C2SYardHome_GetState()

    
    def HideYardHomeDlg(self):
        if not (self.m_oMainDlg) or not self.m_oMainDlg.GetShow():
            return None
        
        import netyardhome
        netyardhome.C2SYardHome_Close()
        import luckyfishdatamgr
        oHeroLuckyFish = luckyfishdatamgr.GetHeroLuckyFishDataMgr()
        oHeroLuckyFish.SetIsRedPoint(False)
        if self.m_oMainDlg:
            self.m_oMainDlg.SetShow(False)
        

    
    def GetYardHome(self, iPlayerID):
        if not iPlayerID:
            iPlayerID = hero.GetHeroID()
        
        if iPlayerID not in self.m_dPlayerYardHome:
            self.CreateYardHome(iPlayerID)
        
        return self.m_dPlayerYardHome[iPlayerID]

    
    def CreateYardHome(self, iPlayerID, iMarryID = 0):
        if not iMarryID:
            oVisitData = self.GetVisitDataMgr()
            del GetMarryID
            iMarryID = None(oVisitData.GetMarryID)
        
        oYardMapMgr = self.GetYardMapMgr()
        oOnePlayerHome = yardhome_oneplayer.CYardHome_OnePlayer(iPlayerID, iMarryID, oYardMapMgr)
        self.m_dPlayerYardHome[iPlayerID] = oOnePlayerHome
