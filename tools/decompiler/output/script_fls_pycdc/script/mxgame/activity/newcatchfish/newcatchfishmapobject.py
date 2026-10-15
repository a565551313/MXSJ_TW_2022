# pycdc 交叉复核产物 · script.fls entry 3431
# co_filename(原始)='script/mxgame/activity/newcatchfish/newcatchfishmapobject.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3431.pyc (Python 2.5)

import interface
import timer
import ui
import world
import misc
import map
import newcatchfishdefine

class CFish(interface.CMapWalkerObject, world.CObject):
    
    def Stop(self):
        if self.m_oAniTimer:
            self.m_oAniTimer.Release()
        
        self.m_oAniTimer = self.CreateCommand(1, 'animation')
        if self.m_oNextCircleTimer:
            self.m_oNextCircleTimer.Release()
        
        self.m_oNextCircleTimer = self.CreatePyCommand(0, self.NextCircle)

    
    def NextCircle(self, oObj):
        (iX, iY) = self.GetPos()
        self.WalkTo([
            (iX, iY)] + misc.DeepCopy(self.m_tWalkPath))

    
    def CSetDirection(self, *args):
        pass

    
    def __init__(self, oParent, iObjID, iGroupID, iFishShape):
        '''
\t\t:param iGroupID: \xb3\xbd\xb8sid
\t\t'''
        interface.CMapWalkerObject.__init__(self, oParent)
        world.CObject.__init__(self, iObjID)
        self.m_iID = iObjID
        self.m_iShape = iFishShape
        self.m_bCatchAble = True
        (self.m_iOffX, self.m_iOffY) = (0, 0)
        self.m_iNormSpeed = 0
        self.m_iScareSpeed = 0
        self.m_TeamID = iGroupID
        self.m_iOwnerID = 0
        self.m_tWalkPath = []
        self.m_oSpeedUpTimer = None
        self.m_oAniTimer = None
        self.m_oFlashTimer = None
        self.m_oNextCircleTimer = None
        self.ShowAni()

    
    def ShowAni(self):
        self.Load('furniture/animal/%.3d/stand.spr' % self.m_iShape, 'mapobject')
        if self.m_oAniTimer:
            self.m_oAniTimer.Release()
        
        self.m_oAniTimer = self.CreateCommand(1, 'animation')

    
    def GetNowPath(self):
        tPathList = self.GetPath()
        tPathList = [ map.GetGameMapObject().ServerPixelPos2ClientPos(x, y) for x, y in tPathList ]
        if len(tPathList) > 1:
            (iNowX, iNowY) = tPathList[0]
            (iLastX, iLastY) = (0, 0)
            for iX, iY in enumerate(tPathList[1:]):
                if not iLastX:
                    iLastX = iX
                    iLastY = iY
                    continue
                
                if abs(iLastX - iNowX) + abs(iX - iNowX) == abs(iX - iLastX) and abs(iLastY - iNowY) + abs(iY - iNowY) == abs(iLastY - iY):
                    return [
                        (iNowX, iNowY)] + tPathList[iPos + 1:]
                
                iLastX = iX
                iLastY = iY
            
        
        return list(tPathList)

    
    def SetShadow(self, bSet):
        pass

    
    def CheckShow(self):
        pass

    
    def WalkTo(self, tPathList):
        if self.m_oAniTimer:
            self.m_oAniTimer.Release()
            self.m_oAniTimer = None
        
        self.m_tWalkPath = tPathList
        self.SetPath(tPathList, 0, self.m_iNormSpeed)

    
    def RightDown(self):
        import map
        map.GetGameMapObject().RightDown()

    
    def BeScare(self):
        if self.m_oSpeedUpTimer:
            self.m_oSpeedUpTimer.Release()
            self.m_oSpeedUpTimer = None
        
        tNowPath = self.GetNowPath()
        self.SetPath(tNowPath, 0, self.m_iScareSpeed)
        self.m_oSpeedUpTimer = timer.Timer(newcatchfishdefine.FISH_SCARE_MOVE_TIME, self.EndSpeedUp, 0, oRelayObj = self)

    
    def EndSpeedUp(self):
        if self.m_oSpeedUpTimer:
            self.m_oSpeedUpTimer.Release()
            self.m_oSpeedUpTimer = None
        
        tNowPath = self.GetNowPath()
        self.SetPath(tNowPath, 0, self.m_iNormSpeed)

    
    def BeCatch(self, oOverCB, *args):
        self.m_bCatchAble = False
        self.ClearPath()
        if self.m_oFlashTimer:
            self.m_oFlashTimer.Release()
        
        self.m_oFlashTimer = self.CreatePyCommand(2, misc.Functor(self.Flash), newcatchfishdefine.FISH_FLASH_TIME, misc.Functor(oOverCB), args)

    
    def Flash(self, oFishObj, iTick, oOverCB, args):
        oFishObj.SetShow(iTick % 2 == 0)
        if iTick > 0:
            return (iTick - 1, oOverCB, args)
        
        if callable(oOverCB):
            oOverCB(oFishObj, *args)
        

    
    def SetNormSpeed(self, iNormSpeed):
        self.m_iNormSpeed = iNormSpeed

    
    def SetScareSpeed(self, iScareSpeed):
        self.m_iScareSpeed = iScareSpeed

    
    def GetFishID(self):
        return self.m_iID

    
    def GetGroupID(self):
        return self.m_TeamID

    
    def IsCatchAble(self):
        return self.m_bCatchAble

    
    def SetOwnerID(self, iPlayerID):
        self.m_iOwnerID = iPlayerID

    
    def GetOwnerID(self):
        return self.m_iOwnerID

    
    def GetShape(self):
        return self.m_iShape

    
    def GetNormSpeed(self):
        return self.m_iNormSpeed

    
    def GetScareSpeed(self):
        return self.m_iScareSpeed



class CNumber(interface.CContainerObject):
    
    def __init__(self, oParent, iNum, bSuperHit = False):
        interface.CContainerObject.__init__(self, oParent)
        self.CreateNumImgs(iNum, bSuperHit)
        self.ResetPos(bSuperHit)

    
    def CreateNumImgs(self, iNum, bSuperHit):
        self.m_oNums = []
        while True:
            if bSuperHit:
                oIgs = ui.CImage(self, 'war/shit/%d.igs' % iNum % 10, 'interface')
                oIgs.CreateCommand(1, 'animation')
            else:
                oIgs = interface.CSpriteObject(self, 'sea/number/%d.spr' % iNum % 10, 'mapobject')
            self.m_oNums.append(oIgs)
            iNum = iNum / 10
            if None(None, None, *iNum, **0):
                break
                continue
        self.m_oNums.reverse()

    
    def ResetPos(self, bSuperHit):
        iLen = len(self.m_oNums)
        (iW, iH) = self.GetImgSize(self.m_oNums[0])
        iX = (-iH / 2) * iLen
        iNumZ = 1000
        if not bSuperHit:
            self.m_oMulti = interface.CSpriteObject(self, 'sea/number/multiply.spr', 'mapobject')
            self.m_oMulti.SetPos(iX, 0)
            (iMWidth, _) = self.GetImgSize(self.m_oMulti)
            iX += iMWidth
            iNumZ = 888
        
        for oNum in self.m_oNums:
            oNum.SetPos(iX, -iH / 2)
            (iW, _) = self.GetImgSize(oNum)
            iX += iW
        
        self.SetZ(iNumZ)

    
    def GetImgSize(self, oIgs):
        (iX, iY) = oIgs.GetSize()
        if iX == 0 or iY == 0:
            (iX, iY) = oIgs.GetResSize()
        
        return (iX, iY)
