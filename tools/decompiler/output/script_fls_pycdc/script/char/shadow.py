# pycdc 交叉复核产物 · script.fls entry 3927
# co_filename(原始)='script/char/shadow.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3927.pyc (Python 2.5)

import chardefine
import charpartdata
import interface
import misc

class CMapImageBox(interface.CMapImagesObject, interface.CBase):
    
    def __init__(self, parent, fname, path):
        interface.CMapImagesObject.__init__(self, parent, fname, path)
        interface.CBase.__init__(self)

    
    def IsCanMessage(self):
        import delayctrl
        oParent = self.GetParent()
        if delayctrl.GetDelayDlgCtrl().IsWalkerInDelay(oParent):
            return True
        

    
    def Enter(self):
        oParent = self.GetParent()
        if oParent and self.IsCanMessage():
            self.GetParent().Enter()
        

    
    def Leave(self):
        oParent = self.GetParent()
        if oParent and self.IsCanMessage():
            self.GetParent().Leave()
        

    
    def LeftDown(self):
        oParent = self.GetParent()
        if oParent and self.IsCanMessage():
            self.GetParent().LeftDown()
        

    
    def LeftUp(self):
        oParent = self.GetParent()
        if oParent and self.IsCanMessage():
            self.GetParent().LeftUp()
        

    
    def RightDown(self):
        oParent = self.GetParent()
        if oParent and self.IsCanMessage():
            self.GetParent().RightDown()
        

    
    def RightUp(self):
        oParent = self.GetParent()
        if oParent and self.IsCanMessage():
            self.GetParent().RightUp()
        



class CMapWalkerBox(interface.CMapWalkerObject, interface.CBase):
    
    def __init__(self, parent):
        interface.CMapWalkerObject.__init__(self, parent)
        interface.CBase.__init__(self)

    
    def IsCanMessage(self):
        import delayctrl
        oParent = self.GetParent()
        if delayctrl.GetDelayDlgCtrl().IsWalkerInDelay(oParent):
            return True
        

    
    def Enter(self):
        oParent = self.GetParent()
        if oParent and self.IsCanMessage():
            self.GetParent().Enter()
        

    
    def Leave(self):
        oParent = self.GetParent()
        if oParent and self.IsCanMessage():
            self.GetParent().Leave()
        

    
    def LeftDown(self):
        oParent = self.GetParent()
        if oParent and self.IsCanMessage():
            self.GetParent().LeftDown()
        

    
    def LeftUp(self):
        oParent = self.GetParent()
        if oParent and self.IsCanMessage():
            self.GetParent().LeftUp()
        

    
    def RightDown(self):
        oParent = self.GetParent()
        if oParent and self.IsCanMessage():
            self.GetParent().RightDown()
        

    
    def RightUp(self):
        oParent = self.GetParent()
        if oParent and self.IsCanMessage():
            self.GetParent().RightUp()
        

    
    def CSetDirection(self, d):
        pass

    
    def Stop(self):
        pass



class CShadow(object):
    
    def __init__(self, oParent):
        self.m_Ani = None
        self.m_Shadow = None
        self.GetShadow(oParent)
        self.Create(oParent)

    
    def GetShadow(self, oParent):
        if isinstance(oParent, (interface.CMapWalkerObject, interface.CMapHeroObject)):
            cls = CMapWalkerBox
        else:
            cls = interface.CWalkerObject
        if isinstance(self.m_Shadow, cls):
            return None
        
        self.m_Shadow = cls(oParent)
        import delayctrl
        if delayctrl.GetDelayDlgCtrl().IsWalkerInDelay(oParent) and hasattr(self.m_Shadow, 'MessageProcess'):
            self.m_Shadow.MessageProcess()
        
        self.m_Shadow.CSetDirection = misc.Functor(self.NotUse)
        self.m_Shadow.Stop = misc.Functor(self.NotUse)

    
    def NotUse(self, *args):
        pass

    
    def Create(self, oWalker):
        if oWalker.m_HorseID and charpartdata.GetHorseShadow(oWalker.m_HorseID):
            if self.CreateHorseSpeShadow(oWalker, oWalker.m_HorseID, oWalker.m_State):
                return None
            
        
        iShadow = charpartdata.GetNpcShadow(oWalker.m_CharIdx)
        if oWalker.m_CharIdx > 1000 and oWalker.m_State in ('stand', 'walk', 'spestand') and iShadow:
            if self.CreateNpcSpeShadow(oWalker, oWalker.m_CharIdx, oWalker.m_State):
                return None
            
        
        if oWalker.m_CharIdx != oWalker.BOSS_SHAPE:
            if self.CreateNorShadow(oWalker, oWalker.m_HorseID):
                if iShadow == 2:
                    None(None, None, None, None, None, None, None, self.m_Shadow.SetShow, False)
                
                return None
            
        
        self.m_Shadow = None

    
    def CreateHorseSpeShadow(self, oWalker, iHorseID, sState):
        self.GetShadow(oWalker)
        if sState not in (chardefine.STATE_STAND, chardefine.STATE_WALK):
            sState = chardefine.STATE_STAND
        
        sFileName = 'horse/%.3d/%s.spr' % (iHorseID, sState)
        
        try:
            self.m_Shadow.Load(sFileName, chardefine.PCK_HERO)
            sFileName = 'horse/%.3d/shadow/%s.igs' % (iHorseID, sState)
            self.m_Shadow.SetZ(-2)
            self.m_Shadow.SetAlpha(chardefine.SHADOW_AL)
            if not self.m_Shadow.LoadImages(sFileName):
                if self.m_Ani:
                    self.m_Ani.Release()
                
                self.m_Ani = self.m_Shadow.CreateCommand(0, 'animation')
                return True
        except:
            LOG_ERR('CreateHorseSpeShadow Failed', sFileName, chardefine.PCK_HERO)

        return False

    
    def CreateNpcSpeShadow(self, oWalker, iShape, sState):
        self.GetShadow(oWalker)
        if sState not in (chardefine.STATE_STAND, chardefine.STATE_WALK):
            sState = chardefine.STATE_STAND
        
        sFileName = '%.4d/%s.spr' % (iShape, sState)
        
        try:
            self.m_Shadow.Load(sFileName, chardefine.PCK_NEW_CHAR)
            sFileName = '%.4d/shadow/%s.igs' % (iShape, sState)
            self.m_Shadow.SetZ(-1)
            self.m_Shadow.SetAlpha(chardefine.SHADOW_AL)
            if not self.m_Shadow.LoadImages(sFileName):
                if self.m_Ani:
                    self.m_Ani.Release()
                
                self.m_Ani = self.m_Shadow.CreateCommand(0, 'animation')
                return True
        except:
            LOG_ERR('CreateNpcSpeShadow Failed', sFileName, chardefine.PCK_NEW_CHAR)

        return False

    
    def CreateNorShadow(self, oWalker, iHorseID):
        if isinstance(oWalker, (interface.CMapWalkerObject, interface.CMapHeroObject)):
            cls = CMapImageBox
        else:
            cls = interface.CImagesObject
        if iHorseID in (9, 10):
            sFileName = 'bigshadow.igs'
        else:
            sFileName = 'shadow.igs'
        
        try:
            self.m_Shadow = cls(oWalker, sFileName, chardefine.PCK_NEW_CHAR)
            import delayctrl
            if delayctrl.GetDelayDlgCtrl().IsWalkerInDelay(oWalker) and hasattr(self.m_Shadow, 'MessageProcess'):
                self.m_Shadow.MessageProcess()
            
            self.m_Shadow.SetZ(-1)
            return True
        except:
            LOG_ERR('CreateNorShadow Failed', sFileName, chardefine.PCK_NEW_CHAR)

        return False

    
    def SetZ(self, iZ):
        if self.m_Shadow:
            self.m_Shadow.SetZ(iZ)
        

    
    def SetDirection(self, iDir):
        if self.m_Shadow:
            self.m_Shadow.SetDirection(iDir)
        

    
    def CreateCommand(self, *args):
        if self.m_Shadow:
            self.m_Shadow.CreateCommand(*args)
