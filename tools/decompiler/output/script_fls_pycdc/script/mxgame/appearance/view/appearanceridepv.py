# pycdc 交叉复核产物 · script.fls entry 4251
# co_filename(原始)='script/mxgame/appearance/view/appearanceridepv.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4251.pyc (Python 2.5)

import random
import chardefine
import charpath
import combdialog
import descinterface
import dlgchpeditor
import misc
import oldwalkerprocess
import popupmgr
import ridedefine
import timer
import walker
DESC_1 = {
    'color': [
        0,
        0,
        0],
    'weapon': [
        1,
        5,
        4],
    'wing': [
        21],
    'titleFlash': 0,
    'fairy': [
        [
            0,
            0,
            0,
            0],
        [
            0,
            0,
            0,
            0]],
    'horse': [
        29,
        1,
        2] }
CHAR_ID_1 = 111
DESC_2 = {
    'color': [
        0,
        0,
        0],
    'weapon': [
        6,
        3,
        0],
    'wing': [
        19],
    'titleFlash': 0,
    'fairy': [
        [
            0,
            0,
            0,
            0],
        [
            0,
            0,
            0,
            0]] }
CHAR_ID_2 = 222
DESC_3 = {
    'color': [
        0,
        0,
        0],
    'weapon': [
        5,
        5,
        1],
    'wing': [
        21],
    'titleFlash': 0,
    'fairy': [
        [
            0,
            0,
            0,
            0],
        [
            0,
            0,
            0,
            0]] }
CHAR_ID_3 = 212
PV_CONFIG = {
    29: {
        'dPos1Info': {
            'dDesc': {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    1,
                    5,
                    1],
                'wing': [
                    21],
                'titleFlash': 0,
                'fairy': [
                    [
                        0,
                        0,
                        0,
                        0],
                    [
                        0,
                        0,
                        0,
                        0]],
                'horse': [
                    29,
                    1,
                    2] },
            'iCharID': 111 },
        'dPos2Info': {
            'dDesc': {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    6,
                    5,
                    6],
                'wing': [
                    1],
                'titleFlash': 0,
                'fairy': [
                    [
                        0,
                        0,
                        0,
                        0],
                    [
                        0,
                        0,
                        0,
                        0]] },
            'iCharID': 121 },
        'dPos3Info': {
            'dDesc': {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    2,
                    5,
                    2],
                'wing': [
                    1],
                'titleFlash': 0,
                'fairy': [
                    [
                        0,
                        0,
                        0,
                        0],
                    [
                        0,
                        0,
                        0,
                        0]] },
            'iCharID': 131 },
        'dPos4Info': {
            'dDesc': {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    3,
                    5,
                    3],
                'wing': [
                    1],
                'titleFlash': 0,
                'fairy': [
                    [
                        0,
                        0,
                        0,
                        0],
                    [
                        0,
                        0,
                        0,
                        0]] },
            'iCharID': 212 },
        'dPos5Info': {
            'dDesc': {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    4,
                    5,
                    4],
                'wing': [
                    1],
                'titleFlash': 0,
                'fairy': [
                    [
                        0,
                        0,
                        0,
                        0],
                    [
                        0,
                        0,
                        0,
                        0]] },
            'iCharID': 222 } } }

def ModuleReset():
    pass


def OpenPvDlg():
    popupmgr.GetPopupMgr().OpenUI(CRidePreviewDlg)


def OpenPvDlgEx(iHorseID, iStyle = None):
    iHorseID = 29
    popupmgr.GetPopupMgr().OpenUI(CRidePreviewExDlg, lstParam = [
        iHorseID])


def OpenAutoSelectRidePreviewExDlg(iShape, iDesc, iStyle = None):
    popupmgr.GetPopupMgr().OpenUI(CAutoSelectRidePreviewExDlg, lstParam = [
        iShape,
        iDesc,
        iStyle])


class CRidePreviewDlg(combdialog.CCombDialog):
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/new_player_present/battlepass/preview/ride_view.dlg')
        self.m_oRideAni = None
        self.m_iDir = 0
        self.Init()

    
    def Init(self):
        import dlgchpeditor
        del None.CChpFakeRole
        self.m_oRideAni = None.CChpFakeRole(self, CHAR_ID_1, DESC_1, charpath.IsUseNewRes())
        self.m_oRideAni.CreateTeamPlayer([
            (CHAR_ID_2, DESC_2),
            (CHAR_ID_3, DESC_3)])
        self.m_oRideAni.SetDirection(self.m_iDir)
        (x, y, w, h) = self.GetLocData('img_ride')
        self.m_oRideAni.SetPos(x + w / 2, y + h)

    
    def SetState(self, sState):
        if self.m_oRideAni:
            pass
        self.m_oRideAni.SetState(sState)

    
    def ChangeDir(self, iLeft):
        self.m_iDir = None if iLeft == 0 else (self.m_iDir - 4) % 32
        self.m_oRideAni.SetDirection(self.m_iDir)

    
    def CloseWindow(self):
        popupmgr.GetPopupMgr().CloseUI(CRidePreviewDlg)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 2:
            self.SetState('stand')
        elif iMsgID == 3:
            self.SetState('walk')
        elif iMsgID == 4:
            self.ChangeDir(1)
        elif iMsgID == 5:
            self.ChangeDir(0)
        



class CRidePreviewExDlg(combdialog.CCombDialog):
    
    def __init__(self, oParent, iPvHorseID):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/new_player_present/battlepass/preview/ride_view.dlg')
        self.m_oRideAni = None
        self.m_iDir = 0
        self.m_iPvHorseID = iPvHorseID
        self.Init()

    
    def Init(self):
        if self.m_iPvHorseID not in PV_CONFIG:
            return None
        
        dPvInfo = PV_CONFIG[self.m_iPvHorseID]
        (iCharID, dDesc) = charpath.GetHeroShow()
        dDesc['horse'] = [
            self.m_iPvHorseID,
            1,
            2]
        self.m_oRideAni = dlgchpeditor.CChpFakeRole(self, iCharID, dDesc, charpath.IsUseNewRes())
        tMulitInfoList = []
        for iIdx in range(2, 6):
            sKey = 'dPos%dInfo' % iIdx
            if sKey in dPvInfo:
                tMulitInfoList.append((dPvInfo[sKey]['iCharID'], dPvInfo[sKey]['dDesc']))
                continue
        
        if tMulitInfoList:
            self.m_oRideAni.CreateTeamPlayer(tMulitInfoList)
        
        self.m_oRideAni.SetDirection(self.m_iDir)
        (x, y, w, h) = self.GetLocData('img_ride')
        self.m_oRideAni.SetPos(x + w / 2, y + h)

    
    def SetState(self, sState):
        if self.m_oRideAni:
            self.m_oRideAni.SetState(sState)
            if self.m_oRideAni.m_HorseID in chardefine.FIVE_HORSE:
                for oRider in self.m_oRideAni.m_MultiHorsePlayerList:
                    if oRider.IsMultiHorsePlayer():
                        oRider.SetState(sState)
                        continue
                
            
        

    
    def ChangeDir(self, iLeft):
        self.m_iDir = None if iLeft == 0 else (self.m_iDir - 4) % 32
        LOG('iDir>>>', self.m_iDir)
        self.m_oRideAni.SetDirection(self.m_iDir)

    
    def CloseWindow(self):
        popupmgr.GetPopupMgr().CloseUI(CRidePreviewExDlg)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 2:
            self.SetState('stand')
        elif iMsgID == 3:
            self.SetState('walk')
        elif iMsgID == 4:
            self.ChangeDir(1)
        elif iMsgID == 5:
            self.ChangeDir(0)
        



class CChpFakeRole(dlgchpeditor.CChpFakeRole):
    
    def IsHideSamllHorse(self):
        return self.GetParent().IsHideSamllHorse()



class CAutoSelectRidePreviewExDlg(combdialog.CCombDialog):
    
    def __init__(self, oParent, iShape, dDesc, iStyle = None):
        if iStyle is None:
            iStyle = ''
        
        combdialog.CCombDialog.__init__(self, oParent, 'dialog%s/mulhorse/mulhorseteam_info.dlg' % iStyle)
        self.m_oRideAni = None
        self.m_bShowMulType = True
        self.m_iShowFirstType = 1
        self.m_iShowSecondType = 2
        self.m_iShapeID = iShape
        self.m_dOldPvInfo = None
        self.m_sState = chardefine.STATE_STAND
        self.m_dDesc = misc.DeepCopy(dDesc)
        self.m_iPvHorseID = descinterface.GetHorseID(dDesc)
        self.m_oRideTime = timer.Timer(10, self.OnStateTime, -1, self)
        self.m_iDir = None if self.m_iPvHorseID in chardefine.FIVE_HORSE else 0
        self.SetBtnSelect()
        self.ShowRole(True)

    
    def SetBtnSelect(self):
        for sLoc, bShow in (('btn_Sel1', self.m_iShowFirstType == 1), ('btn_Sel2', self.m_iShowSecondType == 2), ('btn_Sel3', self.m_bShowMulType)):
            self.GetObject(sLoc).SetSelect(bShow)
        

    
    def OnStateTime(self):
        if self.m_sState == chardefine.STATE_STAND:
            self.SetState(chardefine.STATE_WALK)
        else:
            self.SetState(chardefine.STATE_STAND)

    
    def ReleaseTimer(self):
        if self.m_oRideTime:
            self.m_oRideTime.Release()
        
        self.m_oRideTime = None

    
    def ShowRole(self, bReCreateRole):
        (iMaxPos, dPvInfo) = self.GetShowData(bReCreateRole)
        dDesc = misc.DeepCopy(self.m_dDesc)
        iHorseInfo = descinterface.GetHorseInfo(dDesc)
        iHorseInfo[1] = self.m_iShowFirstType
        iHorseInfo[2] = self.m_iShowSecondType
        if self.m_iPvHorseID in chardefine.DOUBLE_HORSE:
            import multihorsemgr
            dDesc = multihorsemgr.TransformSpeHorse(dDesc, 0)
            if self.m_bShowMulType and self.m_iPvHorseID in chardefine.DOUBLE_HORSE_TOG:
                dDesc = descinterface.ClearWing(dDesc)
                dDesc = descinterface.ClearBackDecorate(dDesc)
            
        
        self.m_oRideAni = CChpFakeRole(self, self.m_iShapeID, dDesc, charpath.IsUseNewRes())
        tMulitInfoList = []
        for iIdx in range(2, iMaxPos + 1):
            sKey = 'dPos%dInfo' % iIdx
            if sKey in dPvInfo:
                tMulitInfoList.append((dPvInfo[sKey]['iCharID'], dPvInfo[sKey]['dDesc']))
                continue
        
        if tMulitInfoList:
            self.m_oRideAni.CreateTeamPlayer(tMulitInfoList)
        
        self.m_oRideAni.SetDirection(self.m_iDir)
        (x, y, w, h) = self.GetLocData('loc_horse')
        if self.m_iPvHorseID in chardefine.DOUBLE_HORSE_SPE and self.m_bShowMulType:
            x -= 40
        
        self.m_oRideAni.SetPos(x, y)
        self.m_oRideAni.SetZ(self.GetObject('loc_horse').GetZ())

    
    def IsHideSamllHorse(self):
        return not (self.m_bShowMulType)

    
    def GetShowData(self, bReCreateRole = False):
        dPvInfo = { }
        if not self.m_bShowMulType:
            return (1, { })
        
        dDesc = misc.DeepCopy(self.m_dDesc)
        iHorseInfo = descinterface.GetHorseInfo(dDesc)
        iHorseInfo[1] = self.m_iShowFirstType
        iHorseInfo[2] = self.m_iShowSecondType
        bIsShowWing = descinterface.GetWingID(dDesc)
        if self.m_iPvHorseID in chardefine.FIVE_HORSE:
            iMaxPos = 5
            for iIdx in range(2, iMaxPos + 1):
                sKey = 'dPos%dInfo' % iIdx
                if not bReCreateRole and self.m_dOldPvInfo:
                    iCharID = self.m_dOldPvInfo[sKey]['iCharID']
                else:
                    iCharID = random.choice(chardefine.HERO_SHAPE_LIST)
                if not bReCreateRole and self.m_dOldPvInfo:
                    iWeaponList = descinterface.GetWeaponInfo(self.m_dOldPvInfo[sKey]['dDesc'])
                else:
                    iWeaponList = [
                        random.choice(chardefine.WEAPON_TYPE_LIST),
                        descinterface.GetWeaponLevel(dDesc),
                        0]
                dPvInfoDesc = {
                    'color': [
                        0,
                        0,
                        0],
                    'weapon': iWeaponList,
                    'wing': [
                         if bIsShowWing else 0,
                        0],
                    'titleFlash': 0,
                    'fairy': [
                        [
                            0,
                            0,
                            0,
                            0],
                        [
                            0,
                            0,
                            0,
                            0]],
                    'horse': iHorseInfo }
                dPvInfoDesciCharID = oldwalkerprocess.SpecialShape(0, iCharID, dPvInfoDesc)
                dPvInfo[sKey] = {
                    'dDesc': dPvInfoDesc,
                    'iCharID': dPvInfoDesciCharID }
            
        elif self.m_iPvHorseID in chardefine.DOUBLE_HORSE:
            iMaxPos = 2
            sKey = 'dPos2Info'
            dPvInfoDesc = {
                'color': [
                    0,
                    0,
                    0],
                'weapon': [
                    0,
                    0,
                    0],
                'wing': [
                     if bIsShowWing else 0,
                    0],
                'titleFlash': 0,
                'fairy': [
                    [
                        0,
                        0,
                        0,
                        0],
                    [
                        0,
                        0,
                        0,
                        0]],
                'horse': iHorseInfo }
            dPvInfoDesciCharID = oldwalkerprocess.SpecialShape(0, iCharID, dPvInfoDesc)
            dPvInfo[sKey] = {
                'dDesc': dPvInfoDesc,
                'iCharID': dPvInfoDesciCharID }
        else:
            return (1, { })
        self.m_dOldPvInfo = dPvInfo
        return (iMaxPos, dPvInfo)

    
    def SetState(self, sState):
        if self.m_iPvHorseID in (ridedefine.HORSE_9, ridedefine.HORSE_10):
            sState = chardefine.STATE_STAND
        
        self.m_sState = sState
        if self.m_oRideAni:
            self.m_oRideAni.SetState(sState)
            for oRider in self.m_oRideAni.m_MultiHorsePlayerList:
                if oRider.IsMultiHorsePlayer():
                    oRider.SetState(sState)
                    continue
            
        

    
    def ChangeDir(self, iLeft):
        self.m_iDir = None if iLeft == 0 else (self.m_iDir - 4) % 32
        self.m_oRideAni.SetDirection(self.m_iDir)

    
    def CloseWindow(self):
        popupmgr.GetPopupMgr().CloseUI(CAutoSelectRidePreviewExDlg)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID in (2, 9):
            self.m_iShowFirstType = 1 - self.m_iShowFirstType
            self.ShowRole(False)
            self.SetBtnSelect()
        elif iMsgID in (3, 10):
            self.m_iShowSecondType = 2 - self.m_iShowSecondType
            self.ShowRole(False)
            self.SetBtnSelect()
        elif iMsgID in (4, 11):
            self.m_bShowMulType = not (self.m_bShowMulType)
            self.ShowRole(True)
            self.SetBtnSelect()
        elif iMsgID == 5:
            self.SetState(chardefine.STATE_STAND)
            self.ReleaseTimer()
        elif iMsgID == 6:
            self.SetState(chardefine.STATE_WALK)
            self.ReleaseTimer()
        elif iMsgID == 7:
            self.ChangeDir(0)
        elif iMsgID == 8:
            self.ChangeDir(1)
