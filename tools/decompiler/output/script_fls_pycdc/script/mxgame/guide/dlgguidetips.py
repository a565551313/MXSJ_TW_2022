# pycdc 交叉复核产物 · script.fls entry 2162
# co_filename(原始)='script/mxgame/guide/dlgguidetips.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2162.pyc (Python 2.5)

import combdialog
import interface
import misc
import timer
import wrapmath
import ui
TYPE_IN_WAR = 1
TYPE_OUT_WAR = 2
TYPE_ALL = 3
g_TipsMgr = None

def ModuleReset():
    global g_TipsMgr
    g_TipsMgr = None


def CreateTips(iType, oParent, sText, iDir, iX, iY, iParentW, iParentH, oRefObj = None):
    return GetTipsMgr().CreateTips(iType, oParent, sText, iDir, iX, iY, iParentW, iParentH, oRefObj)


def GetTips(iTipsID):
    return GetTipsMgr().GetTips(iTipsID)


def RemoveTips(iTipsID):
    GetTipsMgr().ReomveTips(iTipsID)


class CTipsMgr(object):
    
    def __init__(self):
        self.m_dTipsID2TipsObj = { }
        self.m_dType2TipsIDList = { }
        self.m_oTimer = timer.Timer(0, self.OnLoop, -1, self)
        self.InitCB()

    
    def CreateTips(self, iType, oParent, sText, iDir, iX, iY, iParentW, iParentH, oRefObj = None):
        '''\xb3\xd0\xab\xd8tips\xa1A\xaa\xf0\xa6^\xaa\xbatips\xa4\xa3\xadn\xa6s\xc0x'''
        oTips = CGuideTips(oParent, sText, iDir, iX, iY, iParentW, iParentH, oRefObj)
        iTipsID = id(oTips)
        if iType not in self.m_dType2TipsIDList:
            self.m_dType2TipsIDList[iType] = []
        
        self.m_dType2TipsIDList[iType].append(iTipsID)
        self.m_dTipsID2TipsObj[iTipsID] = misc.WeakRef(oTips)
        return (iTipsID, oTips)

    
    def GetTips(self, iTipsID):
        oTipsWr = self.m_dTipsID2TipsObj.get(iTipsID)
        if oTipsWr:
            return oTipsWr()
        
        return oTipsWr

    
    def ReomveTips(self, iTipsID):
        if iTipsID not in self.m_dTipsID2TipsObj:
            return None
        
        oTipsWr = self.m_dTipsID2TipsObj[iTipsID]
        if oTipsWr and oTipsWr():
            oTipsWr().SetDelete()
        
        del self.m_dTipsID2TipsObj[iTipsID]
        iTipsType = None
        for iType, iTipsIDList in self.m_dType2TipsIDList.iteritems():
            if iTipsID in iTipsIDList:
                iTipsType = iType
                break
                continue
        
        if iTipsType is not None:
            self.m_dType2TipsIDList[iTipsType].remove(iTipsID)
        

    
    def InitCB(self):
        import commoncb
        commoncb.RegistCB(commoncb.WAR_START, self, 'OnWarStart')
        commoncb.RegistCB(commoncb.WAR_END, self, 'OnWarEnd')

    
    def OnWarStart(self):
        for iTipsID in self.m_dType2TipsIDList.get(TYPE_OUT_WAR, []):
            oTips = self.GetTips(iTipsID)
            if oTips:
                pass
            oTips.SetShow(False)
        
        for iTipsID in self.m_dType2TipsIDList.get(TYPE_IN_WAR, []):
            oTips = self.GetTips(iTipsID)
            if oTips:
                pass
            oTips.SetShow(True)
        

    
    def OnWarEnd(self):
        for iTipsID in self.m_dType2TipsIDList.get(TYPE_OUT_WAR, []):
            oTips = self.GetTips(iTipsID)
            if oTips:
                pass
            oTips.SetShow(True)
        
        for iTipsID in self.m_dType2TipsIDList.get(TYPE_IN_WAR, []):
            oTips = self.GetTips(iTipsID)
            if oTips:
                pass
            oTips.SetShow(False)
        

    
    def OnLoop(self):
        for oTipsWr in self.m_dTipsID2TipsObj.itervalues():
            oTips = oTipsWr()
            if oTips:
                oTips.OnLoopChangePos()
                continue
        



class CGuideTips(combdialog.CCombDialog):
    
    def __init__(self, oParent, sText, iDir, iX, iY, iParentW, iParentH, oRefObj = None):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/dlgguidetips.dlg')
        interface.g_DialogList.pop()
        self.m_bDelete = False
        self.m_ClickCB = None
        if oRefObj:
            self.m_oRefObj = misc.WeakRef(oRefObj)
        else:
            self.m_oRefObj = None
        self.m_iDir = iDir
        self.m_oGuideAniList = []
        self.m_tPosInfo = (iX, iY, iParentW, iParentH)
        if interface.IsNewStyle():
            sText = sText.replace('#Y', '#cED8200')
        
        self.m_sText = sText
        self.m_dIconPath = {
            0: ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/center_middle_120X120.png', 0),
            1: ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/left_up_120X120.png', 0),
            2: ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/left_down_120X120.png', 0),
            3: ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/right_up_120X120.png', 0),
            4: ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/right_down_120X120.png', 3) }
        self.MessageProcess()
        self.Refresh()
        self.ResetPos(iX, iY, iParentW, iParentH)
        self.Topmost()

    
    def AddOtherPart(self, oAni):
        self.m_oGuideAniList.append(oAni)

    
    def SetDelete(self):
        self.m_bDelete = True
        self.SetShow(False)

    
    def SetShow(self, bShow):
        if bShow and self.m_bDelete:
            return None
        
        for oAni in self.m_oGuideAniList:
            oAni.SetShow(bShow)
        
        combdialog.CCombDialog.SetShow(self, bShow)

    
    def SetClickCB(self, oCB):
        self.m_ClickCB = oCB

    
    def GetRefObj(self):
        if self.m_oRefObj and self.m_oRefObj.Get():
            return self.m_oRefObj.Get()
        

    
    def Hold(self):
        pass

    
    def Topmost(self):
        self.DoTopmost()

    
    def RefreshText(self):
        oTextLeft = self.GetObject('text_left')
        oTextRight = self.GetObject('text_right')
        bShowLeft = self.m_iDir in (0, 1, 2)
        if not self.m_sText:
            oTextLeft.SetShow(False)
            oTextRight.SetShow(False)
        else:
            oTextLeft.SetShow(bShowLeft)
            oTextRight.SetShow(not bShowLeft)
            if bShowLeft:
                oTextLeft.SetText(self.m_sText)
            else:
                oTextRight.SetText(self.m_sText)

    
    def RefreshIcon(self):
        bShowLeft = self.m_iDir in (0, 1, 2)
        oFrameRight = self.GetObject('frame_right')
        oFrameLeft = self.GetObject('frame_left')
        oFrameLeft.SetShow(bShowLeft)
        oFrameRight.SetShow(not bShowLeft)
        oImgRight = self.GetObject('img_right')
        oImgLeft = self.GetObject('img_left')
        oImgLeft.SetShow(bShowLeft)
        oImgRight.SetShow(not bShowLeft)
        (sImgPath, iOffsetY) = self.m_dIconPath[self.m_iDir]
        if bShowLeft:
            oRefreshObj = oImgLeft
        else:
            oRefreshObj = oImgRight
        oRefreshObj.SetPath(sImgPath)
        (x, y) = oRefreshObj.GetPos()
        oRefreshObj.SetPos(x, y + iOffsetY)

    
    def Refresh(self):
        self.RefreshText()
        self.RefreshIcon()

    
    def ResetPos(self, iParentX, iParentY, iParentW, iParentH):
        oRefObj = self.GetRefObj()
        oParent = self.GetParent()
        if oRefObj:
            (iPosX, iPosY) = oRefObj.GetScreenPos()
            (iPPosX, iPPoxY) = oParent.GetScreenPos()
            iDPosX = iPosX - iPPosX
            iDPosY = iPosY - iPPoxY
        else:
            iDPosX = 0
            iDPosY = 0
        (iWidth, iHeight) = self.GetSize()
        (iImgRightX, _, iImgRightW, _) = self.GetLocData('img_right')
        (iImgLeftX, _, _, _) = self.GetLocData('img_left')
        (x, y) = (0, 0)
        if self.m_iDir in (0, 1, 2):
            x = iParentX + iParentW - iImgLeftX
            if self.m_iDir == 0:
                y = iParentY + (iParentH - iHeight) / 2
            elif self.m_iDir == 1:
                y = iParentY + iParentH
            elif self.m_iDir == 2:
                y = iParentY - iHeight
            
        else:
            x = iParentX - (iImgRightX + iImgRightW)
            if self.m_iDir == 3:
                y = iParentY + iParentH
            elif self.m_iDir == 4:
                y = iParentY - iHeight
            
        self.SetPos(iDPosX + x, iDPosY + y)

    
    def OnLoopChangePos(self):
        if self.GetRefObj():
            self.ResetPos(*self.m_tPosInfo)
        

    
    def LeftUp(self):
        self.SetShow(False)
        if self.m_ClickCB:
            pass
        self.m_ClickCB()
        RemoveTips(id(self))

    
    def SetAutoFindPathFlag(self):
        self.m_AutoFindPathFlag = True

    
    def GetTextContent(self):
        '''\xc0\xf2\xa8\xfa\xab\xfc\xa4\xde\xa4\xe5\xa6r'''
        return self.m_sText

    
    def SetMovieHide(self):
        import commoncb
        commoncb.RegistCB(commoncb.DLG_MOVIE_ON, self, 'OnRefreshMovieHide')
        commoncb.RegistCB(commoncb.DLG_MOVIE_ANI_OFF, self, 'OnRefreshMovieHide')
        self.OnRefreshMovieHide()

    
    def OnRefreshMovieHide(self):
        import dlgnpc
        bIsPlayingMovie = dlgnpc.IsInJuQing()
        self.SetShow(not bIsPlayingMovie)



class CUpgradeGuideTips(CGuideTips):
    
    def __init__(self, oParent, sText, iDir, iX, iY, iParentW, iParentH):
        self.m_oAniTimer = None
        self.m_oAniObj = None
        self.m_iAniFrame = 1
        self.m_dAniFramePathMap = {
            0: [
                ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/center_middle_120X120.png', 0),
                ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/center_middle_120X120.png', 0)],
            1: [
                ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/center_middle_120X120.png', 0),
                ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/left_up_120X120.png', 0)],
            2: [
                ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/center_middle_120X120.png', 0),
                ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/left_down_120X120.png', 0)],
            3: [
                ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/center_middle_120X120.png', 0),
                ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/right_up_120X120.png', 0)],
            4: [
                ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/center_middle_120X120.png', 0),
                ('common/\xd0\xa1\xea\xbf\xd6\xb8\xcf\xf2/right_down_120X120.png', 0)] }
        CGuideTips.__init__(self, oParent, sText, iDir, iX, iY, iParentW, iParentH)

    
    def RefreshIcon(self):
        bShowLeft = self.m_iDir in (0, 1, 2)
        oFrameRight = self.GetObject('frame_right')
        oFrameLeft = self.GetObject('frame_left')
        oFrameLeft.SetShow(bShowLeft)
        oFrameRight.SetShow(not bShowLeft)
        oImgRight = self.GetObject('img_right')
        oImgLeft = self.GetObject('img_left')
        oImgLeft.SetShow(bShowLeft)
        oImgRight.SetShow(not bShowLeft)
        if bShowLeft:
            self.m_oAniObj = oImgLeft
        else:
            self.m_oAniObj = oImgRight
        import timer
        self.NextAniFrame()
        self.m_oAniTimer = timer.Timer(0.5, self.NextAniFrame, -1)

    
    def NextAniFrame(self):
        self.m_iAniFrame = (self.m_iAniFrame + 1) % len(self.m_dAniFramePathMap[self.m_iDir])
        (sImgPath, iOffsetY) = self.m_dAniFramePathMap[self.m_iDir][self.m_iAniFrame]
        self.m_oAniObj.SetPath(sImgPath)
        (x, y) = self.m_oAniObj.GetPos()
        self.m_oAniObj.SetPos(x, y + iOffsetY)



def GetTipsMgr():
    global g_TipsMgr
    if not g_TipsMgr:
        g_TipsMgr = CTipsMgr()
    
    return g_TipsMgr


class CGuideMask(ui.CHotBox):
    
    def __init__(self, oParent, dExtData, w, h):
        ui.CHotBox.__init__(self, oParent, w, h, 0)
        self.m_oSize = wrapmath.CVector(oParent.GetSize()) * 1.2
        self.m_dExtData = dExtData
        self.m_oLeftUpCB = None
        self.m_oRightUpCB = None
        self.SetMaskSize(self.m_oSize)

    
    def SetMaskSize(self, oSize):
        self.SetSize(*oSize.data())

    
    def Topmost(self):
        iDepth = self.GetParent().GetZ()
        self.SetZ(iDepth + 1000)

    
    def SetLeftUpCB(self, oCB):
        self.m_oLeftUpCB = oCB

    
    def LeftUp(self):
        ui.CHotBox.LeftUp(self)
        if self.m_oLeftUpCB:
            self.m_oLeftUpCB(self.m_dExtData)
        

    
    def SetRightUpCB(self, oCB):
        self.m_oRightUpCB = oCB

    
    def RightUp(self):
        ui.CHotBox.RightUp(self)
        if self.m_oRightUpCB:
            self.m_oRightUpCB(self.m_dExtData)
