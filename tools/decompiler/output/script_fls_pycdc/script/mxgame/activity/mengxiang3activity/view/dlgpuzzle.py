# pycdc 交叉复核产物 · script.fls entry 4988
# co_filename(原始)='script/mxgame/activity/mengxiang3activity/view/dlgpuzzle.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4988.pyc (Python 2.5)

import combdialog
import interface
import slot
import misc
import wrapinterface
import ui
PINTU_REWARD_NUM = [
    [
        26801,
        1],
    [
        73776,
        3],
    [
        10009,
        1]]
SHAPE_SHENGONGFU = 10009
PINTU_IMG_NUM = 15
REWARD_LOCK = 0
REWRAD_SHOW = 1
REWRAD_FINISH = 2
TEXT_SHENGONGFU = '\xa5\xb4\xb3y\xa9\xce\xad\xab\xb3y\xb1M\xa6\xb3\xb8\xcb\xb3\xc6\xae\xc9\xa1A\xa5i\xa8\xcf\xb8\xcb\xb3\xc6\xc0\xf2\xb1o\xa4@\xad\xd3\xb8\xcb\xb3\xc6\xafS\xa7\xde\xa9\xce\xafS\xae\xc4\xa1A\xb8\xcb\xb3\xc6\xa6\xdb\xb0\xca\xc5\xb3\xa9w\xa5B\xb5L\xbb\xdd\xae\xf8\xaf\xd3\xc5\xb3\xa9w\xb2\xc5#r\xa1i\xb3\xc6\xb5\xf9\xa1j\xbb\xe2\xa8\xfa\xae\xc9\xa5i\xc0\xf2\xb1o\xb7\xed\xabe\xa8\xa4\xa6\xe2\xb5\xa5\xaf\xc5+10\xaf\xc5\xaa\xba\xaf\xab\xa4u\xb2\xc5\xa1A\xb3\xcc\xa7C\xa5i\xbb\xe2\xa8\xfa80\xaf\xc5\xaf\xab\xa4u\xb2\xc5'

def BuildSubWnd(oParent):
    return CPuzzleDlialog(oParent)


class CPuzzleDlialog(combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_ClickRewardImg = 'SS_ClickRewardImg(iPos)'
    SS_ClickBgImg = 'SS_ClickBgImg(iMsgID)'
    SS_OpenDlg = 'SS_OpenDlg(iPage)'
    sUIName = 'dialog/new_player_present/page_pintu.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, self.sUIName)
        self.ssInit()
        self.m_oRewradList = []
        self.m_oBgItemDict = { }
        self.m_oDelegateList = []
        self.m_oShowImgDict = { }
        self.m_iClickPuzzleIdex = 0
        self.SetIgnoreEsc(True)
        self.InitDelegate()
        self.Init()
        interface.Center(self)

    
    def InitDelegate(self):
        import dgtpuzzle
        self.m_oDelegateList = [
            dgtpuzzle.CPuzzleDelegate(self)]

    
    def Init(self):
        self.InitRewardImg()
        self.InitBgItem()
        self.SetBg(False, False)
        self.GetObject('text_shuzi').SetText('')

    
    def ResetImg(self):
        self.m_oBgItemDict = { }
        self.m_oShowImgDict = { }

    
    def InitRewardImg(self):
        iIdex = 0
        for iShape, iQuantity in PINTU_REWARD_NUM:
            iIdex += 1
            oRewardLoc = self.GetObject('loc_reward%s' % iIdex)
            oReward = CRewardItemStretch(oRewardLoc, 0, 0, iIdex, misc.Functor(self.OnClickReward, iIdex))
            if SHAPE_SHENGONGFU == iShape:
                oReward.ShowShape(iShape, '\xaf\xab\xa4u\xb2\xc5', TEXT_SHENGONGFU)
            else:
                oReward.ResetShape(iShape)
            oReward.SetQuantity(iQuantity)
            None(None, None, self.m_oRewradList.append, oReward)
        

    
    def InitBgItem(self):
        self.m_oBgItemDict = { }
        for iIdex in range(PINTU_IMG_NUM):
            iIdex += 1
            oLoc = self.GetObject('loc_pintu%s' % iIdex)
            oBgItem = CSingePuzzle(self, iIdex + 100)
            oBgItem.SetPos(*oLoc.GetPos())
            self.m_oBgItemDict[iIdex] = oBgItem
        

    
    def OnShowSinglePuzzle(self, iIdex):
        iIdex += 1
        if iIdex not in self.m_oShowImgDict.keys():
            oItem = self.m_oBgItemDict[iIdex]
            if self.m_iClickPuzzleIdex != iIdex:
                self.m_oBgItemDict.pop(iIdex)
            else:
                self.PingTuFadeIn(oItem.GetItem())
        

    
    def SetBg(self, bShow1, bShow2):
        self.SetShowObject('frame_ditu1', bShow1)
        self.SetShowObject('frame_ditu2', bShow2)

    
    def PingTuFadeIn(self, oImg):
        import action
        oActionFade = action.CAlphaChange(50, 255, 0, misc.Functor(self.ClearPuzzle, oImg))
        action.AddAction(oImg, oActionFade)
        self.m_iClickPuzzleIdex = 0

    
    def ClearPuzzle(self, oImg, oCBAction):
        if hasattr(oImg, 'SetShow'):
            oImg.SetShow(False)
        

    
    def SetPageState(self, iPage):
        if iPage == 1:
            self.SetGreyState('btn_right')
            self.SetLightState('btn_left')
            self.SetBg(True, False)
        else:
            self.SetGreyState('btn_left')
            self.SetLightState('btn_right')
            self.SetBg(False, True)

    
    def SetGreyState(self, sName):
        self.GetObject(sName).Enable(True)
        self.GetObject(sName).SetLight(8)

    
    def SetLightState(self, sName):
        self.GetObject(sName).Enable(False)
        self.GetObject(sName).SetGrey()

    
    def SetActive(self, bActive):
        self.SetShow(bActive)

    
    def SetClickPuzzleIdex(self, iIdex):
        self.m_iClickPuzzleIdex = iIdex

    
    def RefRewardImg(self, iPos, iState):
        self.m_oRewradList[iPos - 1].RefCornerState(iState)

    
    def GetRewradItem(self, iPos):
        return self.m_oRewradList[iPos]

    
    def SetPuzzleNum(self, iNum):
        self.GetObject('text_shuzi').SetText(str(iNum))

    
    def OnClickReward(self, iPos):
        self.ssEmit(self.SS_ClickRewardImg, iPos)

    
    def OnClickPuzzle(self, iPos):
        self.ssEmit(self.SS_ClickBgImg, iPos)
        self.SetClickPuzzleIdex(iPos)

    
    def OnClickPage(self, iPage):
        self.SetClickPuzzleIdex(0)
        self.ssEmit(self.SS_OpenDlg, iPage)

    
    def OnMessage(self, iMsgID):
        if iMsgID in (1, 2):
            self.OnClickPage(iMsgID)
        elif iMsgID < iMsgID:
            pass
        elif iMsgID < 150:
            self.OnClickPuzzle(iMsgID - 100)
        



class CRewardItemStretch(wrapinterface.CItemIcon):
    
    def __init__(self, oParent, iShape, iQuantity, iMsgID, oClickCB):
        wrapinterface.CItemIcon.__init__(self, oParent, iShape, iQuantity, iMsgID)
        self.m_oClickCB = oClickCB
        self.m_iState = 0

    
    def ResetShape(self, iShape):
        import item
        import itemdata
        self.m_Image = item.CreateItem44StretchImage(self, iShape)
        (sName, sExplain) = itemdata.GetData(iShape)
        self.UpdateArgs(iShape, sName, sExplain, None, interface.ITEM_PATH)

    
    def ShowShape(self, iShape, sName, sExplain):
        import item
        self.m_Image = item.CreateItem44StretchImage(self, iShape)
        self.UpdateArgs(iShape, sName, sExplain, None, interface.ITEM_PATH)

    
    def UpdateArgs(self, iShape, sName, sExplain, sExt, sPath):
        self.m_Shape = iShape
        self.m_Name = sName
        self.m_Info = sExplain
        self.m_InfoExt = sExt
        self.m_Path = sPath

    
    def RefCornerState(self, iState):
        self.m_iState = iState
        if iState == REWRAD_SHOW:
            self.SetFlash(True)
            self.SetLock(False)
        elif iState == REWARD_LOCK:
            sPath = 'combdialog4/\xbd\xb1\xc0\xf8\xd6\xd0\xd0\xc4/\xbd\xad\xba\xfe\xc3\xd8\xb1\xa6\xc2\xbc/\xcb\xf80.png'
        else:
            sPath = 'combdialog3/\xd4\xd3\xcd\xbc/\xc6\xdf\xc8\xd5\xb5\xc7\xc2\xbc/\xd2\xd1\xc1\xec\xc8\xa1.png'
        self.SetLock(True, sPath)
        self.SetFlash(False)

    
    def GetState(self):
        return self.m_iState

    
    def SetFlash(self, bFlash):
        if bFlash and self.m_Image:
            (w, h) = self.GetSize()
            z = self.GetZ()
            flashObj = interface.CSpriteObject(self, '\xd4\xd3\xcd\xbc/\xce\xef\xc6\xb7\xb1\xdf\xbf\xf2\xc1\xf7\xb9\xe2.spr', 'interface')
            flashObj.SetPos(w / 2 - 1, h / 2 - 1)
            flashObj.SetZ(z + 1)
            flashObj.CreateCommand(1, 'animation')
        else:
            flashObj = None
        self.m_FlashObj = flashObj

    
    def SetLock(self, bLock, sPath = None):
        if bLock and self.m_Image and sPath:
            z = self.GetZ()
            lockObj = ui.CImage(self, sPath, interface.UIPath)
            lockObj.SetZ(z + 1)
        else:
            lockObj = None
        self.m_LockObj = lockObj

    
    def Enter(self):
        self.ShowTips()

    
    def Leave(self):
        self.HideTips()

    
    def LeftUp(self):
        if self.m_oClickCB:
            pass
        self.m_oClickCB()



class CSingePuzzle(interface.CContainerObject, interface.CClickObject):
    
    def __init__(self, oParent, iMsgID):
        interface.CContainerObject.__init__(self, oParent)
        interface.CClickObject.__init__(self, iMsgID)
        self.m_oBgImg = None
        self.InitBgImg(iMsgID)

    
    def InitBgImg(self, iMsgID):
        self.m_oBgImg = ui.CImage(self, 'combdialog4\\\xc3\xce\xcf\xeb3\xbb\xee\xb6\xaf\\\xc6\xb4\xcd\xbc\xbd\xd2\xc3\xd8\\huawenbeijing%s.igs' % (iMsgID - 100), interface.UIPath)

    
    def GetItem(self):
        return self.m_oBgImg
