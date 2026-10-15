# pycdc 交叉复核产物 · script.fls entry 1324
# co_filename(原始)='script/mxgame/activity/guildcavern/view/dlgguildcavernroll.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1324.pyc (Python 2.5)

import combdialog
import interface
import slot
import dgtguildcavernroll
import ui
import item
import style
import misc
import netguildcavern
import guildcaverndefine as define
import timer
g_RollDlg = None

def ModuleReset():
    global g_RollDlg
    g_RollDlg = None


def ShowRollDlg():
    global g_RollDlg
    if not g_RollDlg:
        g_RollDlg = CRollDlg()
    


def CloseRollDlg():
    if g_RollDlg:
        g_RollDlg.CloseWindow()
    


def OnStartRoll():
    if g_RollDlg:
        g_RollDlg.StarRoll()
    


def OnRollRewardResult(iIdx):
    if g_RollDlg:
        g_RollDlg.StopDelay(iIdx)
    


class CRollDlg(combdialog.CCombDialog, slot.ISignalSubject):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/group_monster/rollreward.dlg')
        self.ssInit()
        self.InitDlg()
        self.InitSignal()
        self.InitDelegate()
        interface.Center(self)

    
    def InitDlg(self):
        self.m_oItems = []
        self.m_RollRewardTimer = None
        self.m_PerTimer = None
        self.m_bIsRolling = False
        self.GetObject('btn_roll').Enable(False)

    
    def RefreshRollBtn(self, iState):
        oBtn = self.GetObject('btn_roll')
        if iState == define.ROLL_STATE_RESET:
            oBtn.SetText('\xb6}\xa9l\xa9\xe2\xbc\xfa')
            oBtn.Enable(True)
        elif iState == define.ROLL_STATE_START:
            oBtn.SetText('\xbdT\xa9w')
            oBtn.Enable(True)
        

    
    def InitDelegate(self):
        self.m_DelegateList = [
            dgtguildcavernroll.CBossRollDgt(self)]

    
    def InitSignal(self):
        import commoncb
        commoncb.RegistCB(commoncb.SCENE_CHANGE, self, 'OnMapChange')

    
    def RemoveSignal(self):
        import commoncb
        commoncb.RemoveCB(commoncb.SCENE_CHANGE, self, 'OnMapChange')

    
    def OnMapChange(self, iSceneID, iMapID, iMiniMapID):
        CloseRollDlg()

    
    def RefreshReward(self, lReward):
        self.m_oItems = []
        oIconLst = self.GetObject('loc_icon_pos')
        for idx, tmpData in enumerate(lReward):
            iType = None if idx < 5 else 1
            oItem = CItemBox(self, iType = iType)
            if idx < 5:
                oItem.SetSpecial()
            
            oItem.RefreshItem(tmpData)
            (iX, iY) = oIconLst.GetArryPosByIdx(idx)
            oItem.SetPos(iX, iY)
            self.m_oItems.append(oItem)
        
        self.RefreshRollBtn(define.ROLL_STATE_RESET)

    
    def RefreshRollTimes(self, iTimes):
        self.GetObject('text_rolltimes').SetText(str(iTimes))

    
    def RefreshRollNum(self, iNum, iMax):
        self.GetObject('text_tips').ReplaceText({
            '$num': str(iNum),
            '$max': str(iMax) })

    
    def StarRoll(self):
        self.m_iSelect = 0
        self.m_iTick = 0
        self.m_bIsRolling = True
        self.m_RollRewardTimer = self.CreatePyCommand(3, misc.Functor(self.Flush))
        self.RefreshRollBtn(define.ROLL_STATE_START)
        self.RefreshTime(11)

    
    def Flush(self, *args):
        self.m_iTick += 1
        iPrev = 0
        if hasattr(self, 'm_iSelect'):
            iPrev = self.m_iSelect
            self.m_oItems[iPrev].Select(False)
        
        self.m_iSelect = (iPrev + 1) % len(self.m_oItems)
        self.m_oItems[self.m_iSelect].Select(True)
        return ()

    
    def StopDelay(self, iIdx):
        self.m_bIsRolling = True
        timer.Timer(1, misc.Functor(self.Stop, iIdx), 0)
        self.GetObject('btn_roll').Enable(False)

    
    def Stop(self, iIdx):
        global m_RollRewardTimer
        if self.m_RollRewardTimer:
            self.m_RollRewardTimer.Release()
        
        import misc
        lstArg = self.Initgamearg(iIdx)
        del m_RollRewardTimer
        (_, iDelay) = lstArg.pop
        self.m_iStep = misc.RandInt(2, 3)
        self.m_RollRewardTimer = self.CreatePyCommand(2, misc.Functor(self.OnChoice), lstArg, iDelay)

    
    def SetShape(self, iShape):
        self.m_iShape = iShape

    
    def Initgamearg(self, iIdx, iSpeed = 6):
        self.m_iResult = iIdx
        iSize = len(self.m_oItems)
        iSelectNum = getattr(self, 'm_iSelect', 0)
        lstArg = [ (iSelectNum + i) % iSize for i in range(0, ((self.m_iResult - iSelectNum) + iSize) % iSize) ]
        lstArg.append(self.m_iResult)
        lstArg.reverse()
        iSize = len(lstArg)
        lstArg = [ (lstArg[i], iSpeed - i * (iSpeed - 1) / iSize) for i in range(0, iSize) ]
        return lstArg

    
    def OnChoice(self, oObj, lstArg, iDelay):
        if lstArg:
            if iDelay:
                return (lstArg, iDelay - 1)
            
            iPrebox = oObj.m_iSelect
            (oObj.m_iSelect, iDelay) = lstArg.pop()
            oObj.SetSelect(iPrebox)
            return (lstArg, iDelay)
        elif iDelay:
            return (lstArg, iDelay - 1)
        
        oObj.SetSelect(oObj.m_iSelect - 1, False)
        oObj.OnOver()
        return None

    
    def SetSelect(self, iIdx, bPlay = True):
        self.m_oItems[iIdx].Select(False, bPlay)
        self.m_oItems[self.m_iSelect].Select(True, bPlay)

    
    def OnSelect(self, iIdx):
        self.m_oItems[iIdx].Select(True)

    
    def OnOver(self):
        import sound
        import sounddefine
        sound.Play(sounddefine.PATH_STOPBOX_SOUND)
        self.m_bIsRolling = False
        netguildcavern.C2SRollEnd()

    
    def ReleaseTimeTick(self):
        if self.m_PerTimer:
            self.m_PerTimer.Release()
            self.m_PerTimer = None
        

    
    def RefreshTime(self, iRollTime):
        self.ReleaseTimeTick()
        if iRollTime == 0:
            return None
        
        self.m_PerTimer = timer.Timer(iRollTime, self.ChangeRollingState)

    
    def ChangeRollingState(self):
        self.m_bIsRolling = False
        self.ReleaseTimeTick()

    
    def CloseWindow(self):
        global g_RollDlg
        if self.m_bIsRolling:
            return None
        
        self.RemoveSignal()
        g_RollDlg = None

    
    def OnStopClick(self):
        self.GetObject('btn_roll').Enable(False)
        netguildcavern.C2SLotteryReward()

    
    def OnBtnClick(self):
        if not self.m_bIsRolling:
            netguildcavern.C2SStartRoll()
        else:
            self.OnStopClick()

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            self.OnBtnClick()
        



class CItemBox(combdialog.CCombSubWnd):
    s_SpaceH = 10
    
    def __init__(self, parent, iType = 0):
        sPath = None if iType == 0 else 'dialog/group_monster/item2.dlg'
        combdialog.CCombSubWnd.__init__(self, parent, sPath)
        self.SetIgnoreEsc(True)
        self.MessageProcess()
        self.m_bHaveRoll = False
        self.m_oFlashAni = None
        self.m_oSpecialIcon = None

    
    def RefreshItem(self, dItemData):
        self.m_iShape = dItemData['iShape']
        self.m_oImage = item.CreateItem44Image(self, self.m_iShape)
        (iX, iY) = self.GetObject('loc_icon').GetPos()
        self.m_oImage.SetZ(10)
        self.m_oImage.SetPos(iX, iY)
        self.m_oSelBox = ui.CImage(self, style.GetPath('common/select.igs'), interface.UIPath)
        self.m_oSelBox.SetShow(False)
        self.m_oSelBox.SetPos(iX - 2, iY)
        self.GetObject('img_have').SetZ(11)
        self.SetNum(dItemData['iNum'])
        self.SetText(dItemData['sName'])
        self.RefreshState(dItemData['sBelong'])

    
    def RefreshState(self, sBelong):
        self.m_bHaveRoll = sBelong != ''
        self.GetObject('img_have').SetShow(self.m_bHaveRoll)
        self.GetObject('text_username').SetText(sBelong)
        if self.m_oSpecialIcon and self.m_bHaveRoll:
            self.m_oSpecialIcon = None
        

    
    def SetText(self, sName):
        self.GetObject('text_itemname').SetText(sName)

    
    def SetNum(self, iNum):
        self.m_iNum = iNum
        self.GetObject('text_itemnum').SetText('')
        self.GetObject('text_itemnum').SetZ(11)
        if iNum > 1:
            self.GetObject('text_itemnum').SetText(str(iNum))
        

    
    def Enter(self):
        import dlggetinfo
        self.m_oItemTips = dlggetinfo.NewItemInfo(self.m_iShape, self.m_iShape, None, None)

    
    def Leave(self):
        self.m_oItemTips = None

    
    def Select(self, sel, bPlay = True):
        if self.m_bHaveRoll:
            return None
        
        if sel and bPlay:
            import sound
            import sounddefine
            sound.Play(sounddefine.PATH_TICKBOX_SOUND)
        
        self.m_oSelBox.SetShow(sel)

    
    def SetSpecial(self):
        self.AddFlash()
        self.ShowSpecialIcon()

    
    def AddFlash(self):
        if self.m_bHaveRoll:
            self.m_oFlashAni = None
            return None
        
        flashObj = interface.CSpriteObject(self.GetObject('loc_icon'), 'avatar/particle_man.spr', 'interface')
        flashObj.SetPos(-2, 0)
        flashObj.SetZ(10)
        flashObj.CreateCommand(2, 'animation')
        self.m_oFlashAni = flashObj

    
    def ShowSpecialIcon(self):
        (iX, iY) = self.GetObject('loc_icon').GetPos()
        self.m_oSpecialIcon = ui.CStretchImage(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/\xcc\xd8\xca\xe2.png', interface.UIPath)
        self.m_oSpecialIcon.SetScale(0.8)
        self.m_oSpecialIcon.SetPos(iX - 2, iY)
        self.m_oSpecialIcon.SetZ(11)
