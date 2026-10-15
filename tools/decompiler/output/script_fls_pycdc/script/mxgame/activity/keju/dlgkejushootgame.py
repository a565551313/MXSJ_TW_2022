# pycdc 交叉复核产物 · script.fls entry 2970
# co_filename(原始)='script/mxgame/activity/keju/dlgkejushootgame.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2970.pyc (Python 2.5)

import combdialog
import interface
import misc
import slot
import timer
import ui
import dlgpet
import mxnumbers
DEBUG_SHOW_BOX = False
g_ShootGameDlg = None
g_oWaiguShootGameDlg = None

def ModuleReset():
    global g_ShootGameDlg, g_oWaiguShootGameDlg
    g_ShootGameDlg = None
    g_oWaiguShootGameDlg = None


def Show():
    global g_ShootGameDlg
    g_ShootGameDlg = CShootGameDlg()


def ShowForWaiGua():
    global g_oWaiguShootGameDlg
    g_oWaiguShootGameDlg = CShootGameDlg(True)


class CShootGameDlg(combdialog.CCombDialog, slot.ISignalSubject):
    SHAKE_WIN_POS = ((5, 5), (2, 3), (-4, -6), (-10, 3), (0, 0))
    SS_FireSword = 'SS_FireSword()'
    SS_CloseWindow = 'SS_CloseWindow()'
    SS_ClickGameStart = 'SS_ClickGameStart()'
    
    def __init__(self, bWaiguaCheck = False):
        if bWaiguaCheck:
            combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog4/wgcheck/feijian.dlg')
        else:
            combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/keju/feijian.dlg')
        interface.Center(self)
        self.ssInit()
        self.Capture(1, 0)
        self.m_iShakeTime = 0
        self.m_tCenterPos = self.GetPos()
        self.m_oMonsters = { }
        self.m_oDeadMonsters = { }
        self.m_oAniDict = { }
        self.m_dSwords = { }
        self.m_oStandBySword = None
        self.m_oViewport = None
        self.m_oShakeTimer = None
        self.m_oSwordFireAni = None
        self.m_oClearTimer = None
        self.m_bWaiguaCheck = bWaiguaCheck
        self.InitDlg()
        self.InitDelegate()

    
    def GetIsWaiguaCheck(self):
        return self.m_bWaiguaCheck

    
    def SetGameStart(self, bStart):
        self.GetObject('loc_gamearea').SetShow(bStart)
        self.GetObject('loc_preparearea').SetShow(not bStart)

    
    def CreateStandBySword(self, iX, iY):
        self.m_oStandBySword = CSword(self.m_oViewport)
        self.m_oStandBySword.SetPos(iX, iY)

    
    def MonsterChat(self, iMonsterIdx, sChat):
        oMonster = self.m_oMonsters[iMonsterIdx]
        oMonster.Chat(sChat)

    
    def CreateMonster(self, iMonsterIdx, oMonsterInfo):
        oMonster = CChatMonster(self.m_oViewport, 0, oMonsterInfo.GetData('iMonsterShape'), oMonsterInfo.GetData('dMonsterDesc'))
        oMonster.SetState('stand')
        oMonster.m_bMove2Right = oMonsterInfo.GetData('iMonsterStartX') < oMonsterInfo.GetData('iMonsterEndX')
        iX = oMonsterInfo.GetData('iMonsterStartX')
        iY = oMonsterInfo.GetData('iMonsterStartY')
        oMonster.SetPos(iX, iY)
        if DEBUG_SHOW_BOX:
            oMonster.CreateTestBox(oMonsterInfo)
        

    
    def CreateSword(self, iSwordIdx, iX, iY, dSwordInfo = None):
        oSword = CSword(self.m_oViewport)
        if self.m_oSwordFireAni:
            self.m_oSwordFireAni.Release()
        
        self.m_oSwordFireAni = None
        self.m_oSwordFireAni = interface.CSpriteObject(oSword, 'jian04.spr', 'goods')
        self.m_oSwordFireAni.CreateCommand(1, 'one_off_animation')
        self.m_dSwords[iSwordIdx] = oSword
        if DEBUG_SHOW_BOX:
            oSword.CreateTestBox(dSwordInfo)
        
        oSword.SetPos(iX, iY)

    
    def SetMonsterPos(self, iMonsterIdx, iX, iY):
        oMonster = self.m_oMonsters[iMonsterIdx]
        if not oMonster.IsWalk():
            oMonster.SetState('walk')
        
        (iCurX, iCurY) = oMonster.GetPos()
        if iCurX < iX:
            oMonster.SetDirection(32)
        else:
            oMonster.SetDirection(7)
        oMonster.SetPos(iX, iY)

    
    def CreateHurtNum(self, iMonsterIdx, iHp):
        if iMonsterIdx not in self.m_oMonsters:
            return None
        
        oMonster = self.m_oMonsters[iMonsterIdx]
        (iW, iH) = oMonster.GetSize()
        (iX, iY) = oMonster.GetPos()
        iY -= iH / 2
        oHitNum = mxnumbers.CNumber1(self, 'shit', iHp, (0, 0))
        oHitNum.SetPos(iX, iY)

    
    def CreateBoomAni(self, iMonsterIdxList):
        self.ShakeWindow()
        for iMonsterIdx in iMonsterIdxList:
            oMonster = self.m_oMonsters[iMonsterIdx]
            oMonster.SetState('hit', False)
            oAni = interface.CSpriteObject(oMonster, 'jian03.spr', 'goods')
            oAni.SetPos(0, -70)
            oAni.CreateCommand(1, 'one_off_animation')
            self.m_oAniDict[iMonsterIdx] = oAni
        
        if self.m_oClearTimer:
            self.m_oClearTimer.Release()
        
        self.m_oClearTimer = None
        self.m_oClearTimer = timer.Timer(0.5, self.ClearAni)

    
    def SetMonsterDead(self, iMonsterIdx):
        if iMonsterIdx not in self.m_oMonsters:
            return None
        
        oMonster = self.m_oMonsters[iMonsterIdx]
        oMonster.SetEmote(13)
        oMonster.m_oDeadTimer = timer.Timer(oMonster.FrameAmount(True) * 0.033, misc.Functor(self.OnDeadMonsterFinish, iMonsterIdx), 0)
        self.m_oDeadMonsters[iMonsterIdx] = oMonster
        del self.m_oMonsters[iMonsterIdx]

    
    def SetSwordPos(self, iSwordIdx, iX, iY):
        oSword = self.m_dSwords[iSwordIdx]
        oSword.SetPos(iX, iY)

    
    def ReleaseSword(self, iSwordIdx):
        if iSwordIdx in self.m_dSwords:
            del self.m_dSwords[iSwordIdx]
        

    
    def ReleaseMonster(self, iMonsterIdx):
        if iMonsterIdx in self.m_oMonsters:
            del self.m_oMonsters[iMonsterIdx]
        

    
    def SetScoreText(self, iScore):
        self.GetObject('text_score').ReplaceText({
            '$score': str(iScore) })

    
    def SetSwordText(self, iSword):
        self.GetObject('text_times').ReplaceText({
            '$num': str(iSword) })

    
    def RealCloseWindow(self):
        global g_oWaiguShootGameDlg, g_ShootGameDlg
        self.Capture(0)
        if self.m_bWaiguaCheck:
            g_oWaiguShootGameDlg = None
        else:
            g_ShootGameDlg = None

    
    def SetTimeTxt(self, iTime):
        self.GetObject('txt_time').ReplaceText({
            '$sec': str(iTime) })

    
    def InitDelegate(self):
        import dgtkejushootgame
        self.m_DelegateList = [
            dgtkejushootgame.CKejuShootGameDelegate(self)]

    
    def Hold(self):
        pass

    
    def GetSize(self):
        return self.GetObject('main_frame').GetSize()

    
    def InitDlg(self):
        oBtn = self.GetObject('btn_shoot')
        oBtn.SetPlaySound(False)
        oBtn.FlashItself(5)
        (iX, iY, iW, iH) = self.GetLocData('loc_viewport')
        self.m_oViewport = interface.CViewportObject(self, iW, iH + 200)
        self.m_oViewport.SetPos(iX, iY)

    
    def Shake(self):
        tShakeList = self.SHAKE_WIN_POS
        (x, y) = tShakeList[self.m_iShakeTime]
        self.SetPos(self.m_tCenterPos[0] + x, self.m_tCenterPos[1] + y)
        self.m_iShakeTime += 1

    
    def ShakeWindow(self):
        if self.m_oShakeTimer:
            self.m_oShakeTimer.Release()
        
        self.m_iShakeTime = 0
        tShakeList = self.SHAKE_WIN_POS
        self.m_oShakeTimer = timer.Timer(0.03, self.Shake, len(tShakeList) - 1)

    
    def ClearAni(self):
        for oAni in self.m_oAniDict.itervalues():
            if oAni:
                oAni.Release()
                continue
        
        self.m_oAniDict = { }

    
    def RightUp(self):
        self.CloseWindow()

    
    def CloseWindow(self):
        self.ssEmit(self.SS_CloseWindow)

    
    def OnDeadMonsterFinish(self, iDeadMonsterIdx):
        if iDeadMonsterIdx in self.m_oDeadMonsters:
            del self.m_oDeadMonsters[iDeadMonsterIdx]
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 2:
            self.ssEmit(self.SS_FireSword)
        elif iMsgID == 4:
            self.ssEmit(self.SS_ClickGameStart)
        



class CSword(ui.CImage):
    
    def __init__(self, oPar):
        ui.CImage.__init__(self, oPar, 'jian02.igs', 'goods')
        self.CreateCommand(4, 'animation')
        self.m_oSwordTimer = None
        self.m_oTestBox = None

    
    def CreateTestBox(self, dSword):
        if dSword:
            iSwordW = dSword['iW']
            iSwordH = dSword['iH']
            self.m_oTestBox = interface.CBoxObject(self, iSwordW, iSwordH, 65280, 256)
            self.m_oTestBox.SetPos(-iSwordW / 2, -iSwordH)
            self.m_oTestBox.SetZ(-10)
        

    
    def StartSwordMove(self, iTime, oCB):
        self.m_oSwordTimer = timer.Timer(iTime, oCB, 1000, self)

    
    def GetSwordIsFly(self):
        return self.m_oSwordTimer is not None



class CShowArea(interface.CBoxObject):
    
    def __init__(self, oParent, iColor, tP1, tP2, tP3, tP4):
        self.m_PointList = [
            tP1,
            tP2,
            tP3,
            tP4]
        interface.CBoxObject.__init__(self, oParent, self.GetMaxW(), self.GetMaxH(), iColor, 255)
        self.UPos()
        self.SetZ(100)
        self.m_Timer = timer.Timer(0, misc.Functor(self.OnEnd), 0)
        self.m_Timer2 = timer.Timer(0, misc.Functor(self.OnUnValid), 0)

    
    def OnEnd(self):
        self.SetShow(False)

    
    def OnUnValid(self):
        self.SetColor(16777215)

    
    def GetMaxH(self):
        (tP1, tP2, tP3, tP4) = self.m_PointList
        return max(tP1[1], tP2[1], tP3[1], tP4[1]) - min(tP1[1], tP2[1], tP3[1], tP4[1])

    
    def GetMaxW(self):
        (tP1, tP2, tP3, tP4) = self.m_PointList
        return max(tP1[0], tP2[0], tP3[0], tP4[0]) - min(tP1[0], tP2[0], tP3[0], tP4[0])

    
    def UPos(self):
        (tP1, tP2, tP3, tP4) = self.m_PointList
        iX = min(tP1[0], tP2[0], tP3[0], tP4[0])
        iY = min(tP1[1], tP2[1], tP3[1], tP4[1])
        self.SetPos(iX, iY)



class CChatMonster(dlgpet.CFakeRole):
    
    def __init__(self, parent, iObjID, iCharIdx, desc, realShape = None, iIsUseNewRes = None):
        dlgpet.CFakeRole.__init__(self, parent, iObjID, iCharIdx, desc, realShape, iIsUseNewRes)
        self.m_Float = []
        self.m_oTestBox = None

    
    def CreateTestBox(self, oMonsterInfo):
        iMonsterW = oMonsterInfo.GetData('iMonsterW')
        iMonsterH = oMonsterInfo.GetData('iMonsterH')
        iMonsterX = -iMonsterW / 2 + oMonsterInfo.GetData('iMonsterDeltX')
        iMonsterY = 0
        iDW = int(iMonsterW / 2)
        iDH = int(iMonsterH)
        self.m_oTestBox = interface.CBoxObject(self, iMonsterW, iMonsterH, 16711680, 256)
        self.m_oTestBox.SetPos(iMonsterX - iDW, iMonsterY - iDH)
        self.m_oTestBox.SetZ(-10)

    
    def Chat(self, sMsg):
        import chatoutput
        oFloat = chatoutput.CChatFloat(self, sMsg)
        self.m_Float.append(oFloat)

    
    def SetPos(self, iX, iY):
        (iOX, iOY) = self.GetPos()
        iDfX = iX - iOX
        for oFloat in self.m_Float:
            (iFX, iFY) = oFloat.GetPos()
            oFloat.SetPos(iFX + iDfX / 2, iFY)
        
        dlgpet.CFakeRole.SetPos(self, iX, iY)
