# pycdc 交叉复核产物 · script.fls entry 2749
# co_filename(原始)='script/protocol/openui/csyanzhiguan.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2749.pyc (Python 2.5)

import avatar
import protocolcount
import netyanzhiguan
import openuiutil

def GS2CColorUI(oNetObj):
    LstDesc = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iDesc = oNetObj.UnpackInt(4)
        LstDesc.append(iDesc)
    
    dTime = { }
    for _index in xrange(oNetObj.UnpackInt(1)):
        iType = oNetObj.UnpackInt(1)
        iTime = oNetObj.UnpackInt(4)
        dTime[iType] = iTime
    
    iColor1 = oNetObj.UnpackInt(1)
    iColor2 = oNetObj.UnpackInt(1)
    iColor3 = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=1', 'openui.csyanzhiguan-GS2CColorUI')
    netyanzhiguan.OnColorUI(LstDesc, dTime, iColor1, iColor2, iColor3)


def GS2CCloseColorUI(oNetObj):
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=2', 'openui.csyanzhiguan-GS2CCloseColorUI')
    netyanzhiguan.OnCloseColorUI()


def GS2CFreeColorUI(oNetObj):
    iNeedHuancai = oNetObj.UnpackInt(1)
    iFirst = oNetObj.UnpackInt(1)
    iCostOff = oNetObj.UnpackInt(1)
    dTmpColor = openuiutil.UnPackBinaryS(oNetObj)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=3', 'openui.csyanzhiguan-GS2CFreeColorUI')
    netyanzhiguan.OnFreeColorUI(iNeedHuancai, iFirst, iCostOff, dTmpColor)


def GS2CUpdateFreeColor(oNetObj):
    iTmpType = oNetObj.UnpackInt(1)
    dInfo = openuiutil.UnPackBinaryS(oNetObj, 1)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=4', 'openui.csyanzhiguan-GS2CUpdateFreeColor')
    netyanzhiguan.OnUpdateFreeColor(iTmpType, dInfo)


def GS2CReplaceFreeColor(oNetObj):
    iTmpType = oNetObj.UnpackInt(1)
    lstInfo = openuiutil.UnPackBinaryS(oNetObj, 1)
    dTmpColor = openuiutil.UnPackBinaryS(oNetObj)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=5', 'openui.csyanzhiguan-GS2CReplaceFreeColor')
    netyanzhiguan.OnReplaceFreeColor(iTmpType, lstInfo, dTmpColor)


def GS2CDelTmpFreeColor(oNetObj):
    iTmpType = oNetObj.UnpackInt(1)
    iPos = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=6', 'openui.csyanzhiguan-GS2CDelTmpFreeColor')
    netyanzhiguan.OnDelTmpFreeColor(iTmpType, iPos)


def GS2CColorUINew(oNetObj):
    lstDesc = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iInfo = oNetObj.UnpackInt(4)
        lstDesc.append(iInfo)
    
    dColorTime = { }
    for _index in xrange(oNetObj.UnpackInt(1)):
        iType = oNetObj.UnpackInt(1)
        iTime = oNetObj.UnpackInt(4)
        dColorTime[iType] = iTime
    
    iColor1 = oNetObj.UnpackInt(1)
    iColor2 = oNetObj.UnpackInt(1)
    iColor3 = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=7', 'openui.csyanzhiguan-GS2CColorUINew')
    netyanzhiguan.OnColorUINew(lstDesc, dColorTime, iColor1, iColor2, iColor3)


def GS2CFreeColorUINew(oNetObj):
    iNeedHuancai = oNetObj.UnpackInt(1)
    iFirst = oNetObj.UnpackInt(1)
    iCostOff = oNetObj.UnpackInt(1)
    dTmpColor = openuiutil.UnPackBinaryS(oNetObj)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=8', 'openui.csyanzhiguan-GS2CFreeColorUINew')
    netyanzhiguan.OnFreeColorUINew(iNeedHuancai, iFirst, iCostOff, dTmpColor)


def GS2CChangeShapeUINew1(oNetObj):
    tShape = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        \xf2\xc8\xf3ape = oNetObj.UnpackInt(2)
        tShape.append(\xf2\xc8\xf3ape)
    
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=9', 'openui.csyanzhiguan-GS2CChangeShapeUINew1')
    netyanzhiguan.OnChangeShapeUINew1(tShape)


def GS2CUpdateFreeColorNew(oNetObj):
    iTmpType = oNetObj.UnpackInt(1)
    dTmpColor = openuiutil.UnPackBinaryS(oNetObj)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=11', 'openui.csyanzhiguan-GS2CUpdateFreeColorNew')
    netyanzhiguan.OnUpdateFreeColorNew(iTmpType, dTmpColor)


def GS2CDelTmpFreeColorNew(oNetObj):
    iTmpType = oNetObj.UnpackInt(1)
    iPos = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=12', 'openui.csyanzhiguan-GS2CDelTmpFreeColorNew')
    netyanzhiguan.OnDelTmpFreeColorNew(iTmpType, iPos)


def GS2CWeaponItemColor(oNetObj):
    ItemID = oNetObj.UnpackInt(4)
    iColor = oNetObj.UnpackInt(1)
    iKaiQiao = oNetObj.UnpackInt(1)
    iKqTimeOut = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=13', 'openui.csyanzhiguan-GS2CWeaponItemColor')
    netyanzhiguan.OnWeaponItemColor(ItemID, iColor, iKaiQiao, iKqTimeOut)


def GS2CSpriteItemColor(oNetObj):
    iItemObjId = oNetObj.UnpackInt(4)
    iColor = oNetObj.UnpackInt(1)
    iAddon = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=14', 'openui.csyanzhiguan-GS2CSpriteItemColor')
    netyanzhiguan.OnSpriteItemColor(iItemObjId, iColor, iAddon)


def GS2CRideExchangeCnt(oNetObj):
    iCnt = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=15', 'openui.csyanzhiguan-GS2CRideExchangeCnt')
    netyanzhiguan.OnRideExchangeCnt(iCnt)


def GS2CPerfomColorCost(oNetObj):
    iSkillId = oNetObj.UnpackInt(2)
    iColorType = oNetObj.UnpackInt(1)
    iRyzyNum = oNetObj.UnpackInt(2)
    iChsNum = oNetObj.UnpackInt(1)
    iBanPal = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=16', 'openui.csyanzhiguan-GS2CPerfomColorCost')
    netyanzhiguan.OnPerfomColorCost(iSkillId, iColorType, iRyzyNum, iChsNum, iBanPal)


def GS2CRideColorList(oNetObj):
    iRideType = oNetObj.UnpackInt(4)
    iClass = oNetObj.UnpackInt(1)
    iPart = oNetObj.UnpackInt(1)
    lstColor = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iColor = oNetObj.UnpackInt(1)
        lstColor.append(iColor)
    
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=17', 'openui.csyanzhiguan-GS2CRideColorList')
    netyanzhiguan.OnRideColorList(iRideType, iClass, iPart, lstColor)


def GS2CWeaponColorList(oNetObj):
    iItemObjId = oNetObj.UnpackInt(4)
    lstColor = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iColor = oNetObj.UnpackInt(1)
        lstColor.append(iColor)
    
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=18', 'openui.csyanzhiguan-GS2CWeaponColorList')
    netyanzhiguan.OnWeaponColorList(iItemObjId, lstColor)


def GS2COpenYanZhiUI(oNetObj):
    iMainType = oNetObj.UnpackInt(1)
    iSubType = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=19', 'openui.csyanzhiguan-GS2COpenYanZhiUI')
    netyanzhiguan.OnOpenYanZhiUI(iMainType, iSubType)


def GS2COpenPerformRanseUI(oNetObj):
    iPerform = oNetObj.UnpackInt(2)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=20', 'openui.csyanzhiguan-GS2COpenPerformRanseUI')
    netyanzhiguan.OnOpenPerformRanseUI(iPerform)


def GS2COpenYanZhiUIAndSelect(oNetObj):
    iMainType = oNetObj.UnpackInt(1)
    dExtendData = openuiutil.UnPackBinaryS(oNetObj, 2)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=21', 'openui.csyanzhiguan-GS2COpenYanZhiUIAndSelect')
    netyanzhiguan.OnOpenYanZhiUIAndSelect(iMainType, dExtendData)


def GS2CFrdList(oNetObj):
    iType = oNetObj.UnpackInt(1)
    lstFrd = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iFrdID = oNetObj.UnpackInt(4)
        iIcon = oNetObj.UnpackInt(1)
        lstPhoto = avatar.UnpackPhotoInt4(oNetObj)
        sName = oNetObj.UnpackInt(1)
        iOnline = oNetObj.UnpackInt(1)
        lstFrd.append([
            iFrdID,
            iIcon,
            lstPhoto,
            sName,
            iOnline])
    
    iNeedSG = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C_OPEN_UI=0x59,iSub=7,iSub=22', 'openui.csyanzhiguan-GS2CFrdList')
    netyanzhiguan.OnFrdList(iType, lstFrd, iNeedSG)

g_NetFunction = {
    1: GS2CColorUI,
    2: GS2CCloseColorUI,
    3: GS2CFreeColorUI,
    4: GS2CUpdateFreeColor,
    5: GS2CReplaceFreeColor,
    6: GS2CDelTmpFreeColor,
    7: GS2CColorUINew,
    8: GS2CFreeColorUINew,
    9: GS2CChangeShapeUINew1,
    11: GS2CUpdateFreeColorNew,
    12: GS2CDelTmpFreeColorNew,
    13: GS2CWeaponItemColor,
    14: GS2CSpriteItemColor,
    15: GS2CRideExchangeCnt,
    16: GS2CPerfomColorCost,
    17: GS2CRideColorList,
    18: GS2CWeaponColorList,
    19: GS2COpenYanZhiUI,
    20: GS2COpenPerformRanseUI,
    21: GS2COpenYanZhiUIAndSelect,
    22: GS2CFrdList }

def OnCommand(oNetObj):
    iSub = oNetObj.UnpackInt(1)
    func = g_NetFunction.get(iSub)
    if not func:
        protocolcount.ErrorLog('net.GS2C_OPEN_UI', '\xb5L\xaak\xb8\xd1\xaaR GS2C_OPEN_UI=0x59 \xaa\xba\xa4l\xa8\xf3\xc4\xb3\xa1G%s' % iSub)
        return None
    
    func(oNetObj)


def C2GSAppearanceTGF():
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(1, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=1', 'openui.csyanzhiguan-C2GSAppearanceTGF')


def C2GSAppearancePTDye():
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(2, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=2', 'openui.csyanzhiguan-C2GSAppearancePTDye')


def C2GSAppearanceChgShape():
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(3, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=3', 'openui.csyanzhiguan-C2GSAppearanceChgShape')


def C2GSAppearanceConfirmPTDye(iResult, iType, iFriendID):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(4, 1)
    oNetObj.PacketAddI(iResult, 4)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketAddI(iFriendID, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=4', 'openui.csyanzhiguan-C2GSAppearanceConfirmPTDye')


def C2GSAppearanceFreeDye(lstHSV, iType, iID):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(5, 1)
    oNetObj.PacketAddI(len(lstHSV), 1)
    for iHue, iSat, iVal in lstHSV:
        oNetObj.PacketAddI(iHue, 2)
        oNetObj.PacketAddI(iSat, 1)
        oNetObj.PacketAddI(iVal, 1)
    
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketAddI(iID, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=5', 'openui.csyanzhiguan-C2GSAppearanceFreeDye')


def C2GSAppearanceSaveFreeDye(iType, iPos, \xf2\xc8\xf3ape, lstHSV):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(6, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketAddI(iPos, 1)
    oNetObj.PacketAddI(\xf2\xc8\xf3ape, 1)
    oNetObj.PacketAddI(len(lstHSV), 1)
    for iHue, iSat, iVal in lstHSV:
        oNetObj.PacketAddI(iHue, 2)
        oNetObj.PacketAddI(iSat, 1)
        oNetObj.PacketAddI(iVal, 1)
    
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=6', 'openui.csyanzhiguan-C2GSAppearanceSaveFreeDye')


def C2GSAppearanceDelFreeDye(iType, iPos):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(7, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketAddI(iPos, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=7', 'openui.csyanzhiguan-C2GSAppearanceDelFreeDye')


def C2GSAppearanceDelTmpDye():
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(8, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=8', 'openui.csyanzhiguan-C2GSAppearanceDelTmpDye')


def C2GSAppearanceChgShapeConfirm(\xf2\xc8\xf3ape, iPlayerMode):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(9, 1)
    oNetObj.PacketAddI(\xf2\xc8\xf3ape, 2)
    oNetObj.PacketAddI(iPlayerMode, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=9', 'openui.csyanzhiguan-C2GSAppearanceChgShapeConfirm')


def C2GSAppearanceHorseChangeCount():
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(10, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('F7BVZJU@KZPL85x58,iSub=162,iSub=10', 'openui.csyanzhiguan-C2GSAppearanceHorseChangeCount')


def C2GSAppearanceHorseColor(iType, iHorseShape):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(12, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketAddI(iHorseShape, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=12', 'openui.csyanzhiguan-C2GSAppearanceHorseColor')


def C2GSAppearanceCombineFairy(iItemID1, iItemID2):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(14, 1)
    oNetObj.PacketAddI(iItemID1, 4)
    oNetObj.PacketAddI(iItemID2, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=14', 'openui.csyanzhiguan-C2GSAppearanceCombineFairy')


def C2GSAppearanceGetOutFairy():
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(17, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=17', 'openui.csyanzhiguan-C2GSAppearanceGetOutFairy')


def C2GSAppearanceResetWeaponColor():
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(18, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=18', 'openui.csyanzhiguan-C2GSAppearanceResetWeaponColor')


def C2GSAppearanceResetHorseColor(iType, iHorseShape):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(19, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketAddI(iHorseShape, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=19', 'openui.csyanzhiguan-C2GSAppearanceResetHorseColor')


def C2GSAppearanceResetFairyColor(iFairyID):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(20, 1)
    oNetObj.PacketAddI(iFairyID, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=20', 'openui.csyanzhiguan-C2GSAppearanceResetFairyColor')


def C2GSMagicPalPrice(iSkillID, iCase):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(21, 1)
    oNetObj.PacketAddI(iSkillID, 4)
    oNetObj.PacketAddI(iCase, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=21', 'openui.csyanzhiguan-C2GSMagicPalPrice')


def C2GSCommitMagicPal(iSkillID, iCase):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(22, 1)
    oNetObj.PacketAddI(iSkillID, 4)
    oNetObj.PacketAddI(iCase, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=22', 'openui.csyanzhiguan-C2GSCommitMagicPal')


def C2GSRideAllColor(iRideShape, iRideType, iRidePart):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(23, 1)
    oNetObj.PacketAddI(iRideShape, 4)
    oNetObj.PacketAddI(iRideType, 1)
    oNetObj.PacketAddI(iRidePart, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=23', 'openui.csyanzhiguan-C2GSRideAllColor')


def C2GSWeaponAllColor(iWeaponID):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(24, 1)
    oNetObj.PacketAddI(iWeaponID, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=24', 'openui.csyanzhiguan-C2GSWeaponAllColor')


def C2GSUnluckHorseFairy():
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(25, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=25', 'openui.csyanzhiguan-C2GSUnluckHorseFairy')


def C2GSOpenAppearence():
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(26, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=26', 'openui.csyanzhiguan-C2GSOpenAppearence')


def C2GSOpenGiftDlg():
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(27, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=27', 'openui.csyanzhiguan-C2GSOpenGiftDlg')


def C2GSGiftFriend(iType, \xf2\xc8\xf3ape, iFriendID):
    oNetObj = openuiutil.GetOpenUINetObj(162)
    oNetObj.PacketAddI(28, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketAddI(\xf2\xc8\xf3ape, 4)
    oNetObj.PacketAddI(iFriendID, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=28', 'openui.csyanzhiguan-C2GSGiftFriend')


def C2GSAppearanceWeaponItemColor(iItemID):
    oNetObj = openuiutil.GetOpenUINetObj(162, 11)
    oNetObj.PacketAddI(1, 1)
    oNetObj.PacketAddI(iItemID, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=11,iSub=1', 'openui.csyanzhiguan-C2GSAppearanceWeaponItemColor')


def C2GSAppearanceHeroWeaponColor():
    oNetObj = openuiutil.GetOpenUINetObj(162, 11)
    oNetObj.PacketAddI(2, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=11,iSub=2', 'openui.csyanzhiguan-C2GSAppearanceHeroWeaponColor')


def C2GSAppearanceFairyItemColor(iItemID):
    oNetObj = openuiutil.GetOpenUINetObj(162, 13)
    oNetObj.PacketAddI(1, 1)
    oNetObj.PacketAddI(iItemID, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=13,iSub=1', 'openui.csyanzhiguan-C2GSAppearanceFairyItemColor')


def C2GSAppearanceHeroFairyColor():
    oNetObj = openuiutil.GetOpenUINetObj(162, 13)
    oNetObj.PacketAddI(2, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=13,iSub=2', 'openui.csyanzhiguan-C2GSAppearanceHeroFairyColor')


def C2GSAppearanceFairyItemAct(iItemID):
    oNetObj = openuiutil.GetOpenUINetObj(162, 15)
    oNetObj.PacketAddI(1, 1)
    oNetObj.PacketAddI(iItemID, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=15,iSub=1', 'openui.csyanzhiguan-C2GSAppearanceFairyItemAct')


def C2GSAppearanceHeroFairyAct():
    oNetObj = openuiutil.GetOpenUINetObj(162, 15)
    oNetObj.PacketAddI(2, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=15,iSub=2', 'openui.csyanzhiguan-C2GSAppearanceHeroFairyAct')


def C2GSAppearanceAskWeaponColor(iItemID):
    oNetObj = openuiutil.GetOpenUINetObj(162, 16)
    oNetObj.PacketAddI(1, 1)
    oNetObj.PacketAddI(iItemID, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=16,iSub=1', 'openui.csyanzhiguan-C2GSAppearanceAskWeaponColor')


def C2GSAppearanceAskFairyColor(iItemID):
    oNetObj = openuiutil.GetOpenUINetObj(162, 16)
    oNetObj.PacketAddI(2, 1)
    oNetObj.PacketAddI(iItemID, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_OPEN_UI=0x58,iSub=162,iSub=16,iSub=2', 'openui.csyanzhiguan-C2GSAppearanceAskFairyColor')
