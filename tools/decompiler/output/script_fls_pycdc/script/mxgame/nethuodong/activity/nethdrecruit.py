# pycdc 交叉复核产物 · script.fls entry 3863
# co_filename(原始)='script/mxgame/nethuodong/activity/nethdrecruit.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3863.pyc (Python 2.5)

import huodongdefine
import net
import avatar

def GetRecruitNetObj():
    netobj = net.PacketPrepare(net.C2GS_HUODONG)
    netobj.PacketAddPS(huodongdefine.RECRUIT)
    return netobj


def AddRecruitList(netobj):
    dInfo = { }
    dInfo['canReCall'] = netobj.UnpackInt(1)
    dInfo['ID'] = netobj.UnpackInt(4)
    dInfo['grade'] = netobj.UnpackInt(2)
    dInfo['class'] = netobj.UnpackInt(1)
    dInfo['sex'] = netobj.UnpackInt(1)
    dInfo['photo'] = avatar.UnpackPhotoInt4(netobj)
    avatar.UnpackAvatarData(netobj, dInfo['ID'])
    dInfo['name'] = netobj.UnpackString(16)
    import dlgrecruit
    dlgrecruit.AddRecruit(dInfo)


def ShowRecruitDlg(netobj):
    iRecruited = netobj.UnpackInt(1)
    iReward = netobj.UnpackInt(1)
    import dlgrecruit
    dlgrecruit.ShowRecruitDlg(iRecruited, iReward)


def ShowRecruitRewardDlg(netobj):
    import dlgrecruit
    iSub = netobj.UnpackInt(1)
    LOG('\xa9\xdb\xb6\xd2\xbc\xfa\xc0y\xac\xc9\xad\xb1 %d' % iSub)
    if iSub == 1:
        iLen = netobj.UnpackInt(2)
        recruitList = []
        for i in xrange(iLen):
            dInfo = { }
            dInfo['ID'] = netobj.UnpackInt(4)
            dInfo['grade'] = netobj.UnpackInt(2)
            dInfo['name'] = netobj.UnpackString(16)
            dInfo['class'] = netobj.UnpackInt(1)
            dInfo['time'] = netobj.UnpackInt(4)
            dInfo['active'] = netobj.UnpackInt(2)
            dInfo['photo'] = avatar.UnpackPhotoInt4(netobj)
            avatar.UnpackAvatarData(netobj, dInfo['ID'])
            dInfo['sex'] = netobj.UnpackInt(1)
            dInfo['rewardmask'] = netobj.UnpackInt(1)
            recruitList.append(dInfo)
        
        dlgrecruit.ShowRecruitRewardDlg(recruitList)
    elif iSub == 2:
        dlgrecruit.CloseRecruitRewardDlg()
    


def ShowBackRewardDlg(netobj):
    import dlgrecruit
    iSub = netobj.UnpackInt(1)
    if iSub == 1:
        dMainInfo = { }
        recruitList = []
        dMainInfo['regressgrade'] = netobj.UnpackInt(1)
        dMainInfo['time'] = netobj.UnpackInt(4)
        dMainInfo['active'] = netobj.UnpackInt(2)
        dMainInfo['wardmask'] = netobj.UnpackInt(1)
        dMainInfo['haswardmask'] = netobj.UnpackInt(1)
        dMainInfo['showflag'] = netobj.UnpackInt(1)
        dMainInfo['isCanGetVip'] = netobj.UnpackInt(1)
        dMainInfo['hadGetVip'] = netobj.UnpackInt(1)
        dMainInfo['xiulian'] = netobj.UnpackInt(1)
        iType = netobj.UnpackInt(1)
        if iType == 0:
            iLen = netobj.UnpackInt(1)
            for i in xrange(iLen):
                ID = netobj.UnpackInt(4)
                name = netobj.UnpackString(16)
                recruitList.append({
                    'ID': ID,
                    'name': name })
            
        elif iType == 1:
            ID = netobj.UnpackInt(4)
            name = netobj.UnpackString(16)
            dMainInfo['\xa9\xdb\xb6\xd2\xa4H'] = (ID, name)
        
        exp = netobj.UnpackInt(4)
        fightCash = netobj.UnpackInt(4)
        xiulian = netobj.UnpackInt(4)
        petExp = netobj.UnpackInt(4)
        reserveLst = [
            exp,
            fightCash,
            xiulian,
            petExp]
        dlgrecruit.ShowBackRewardDlg(dMainInfo, recruitList, reserveLst)
    elif iSub == 2:
        dlgrecruit.CloseBackRewardDlg()
    


def ShowBackRewardDlg2(netobj):
    import dlgrecruit
    iSub = netobj.UnpackInt(1)
    if iSub == 1:
        dMainInfo = { }
        recruitList = []
        dMainInfo['time'] = netobj.UnpackInt(4)
        dMainInfo['active'] = netobj.UnpackInt(2)
        dMainInfo['wardmask'] = netobj.UnpackInt(1)
        iType = netobj.UnpackInt(1)
        if iType == 0:
            iLen = netobj.UnpackInt(1)
            for i in xrange(iLen):
                ID = netobj.UnpackInt(4)
                name = netobj.UnpackString(16)
                recruitList.append({
                    'ID': ID,
                    'name': name })
            
        elif iType == 1:
            ID = netobj.UnpackInt(4)
            name = netobj.UnpackString(16)
            dMainInfo['\xa9\xdb\xb6\xd2\xa4H'] = (ID, name)
        
        itemDct = { }
        shape1 = netobj.UnpackInt(4)
        num1 = netobj.UnpackInt(1)
        shape2 = netobj.UnpackInt(4)
        num2 = netobj.UnpackInt(1)
        itemDct[0] = [
            (shape1, num1),
            (shape2, num2)]
        manExp = netobj.UnpackInt(4)
        sumExp = netobj.UnpackInt(4)
        iCash = netobj.UnpackInt(4)
        XLExp = netobj.UnpackInt(4)
        dlgrecruit.ShowBackRewardDlg2(dMainInfo, recruitList, itemDct)
        dlgrecruit.CreateTextInfo(manExp, sumExp, iCash, XLExp)
    elif iSub == 2:
        dlgrecruit.CloseBackRewardDlg2()
    


def S2CSetFlash(netobj):
    flash = netobj.UnpackInt(1)
    import netstate
    netstate.CState452.SetFlashValue(flash)


def C2SOpenRecruitDlg():
    netobj = GetRecruitNetObj()
    netobj.PacketAddI(1, 1)
    netobj.PacketSend()


def C2SSendMessage(pid, idx):
    netobj = GetRecruitNetObj()
    netobj.PacketAddI(2, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketAddI(idx, 1)
    netobj.PacketSend()


def C2SOpenRecruitReward():
    netobj = GetRecruitNetObj()
    netobj.PacketAddI(3, 1)
    netobj.PacketSend()


def C2SGetRecruitReward(pid, idx):
    netobj = GetRecruitNetObj()
    netobj.PacketAddI(4, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketAddI(idx, 1)
    netobj.PacketSend()


def C2SSelectRecruit(pid):
    netobj = GetRecruitNetObj()
    netobj.PacketAddI(5, 1)
    netobj.PacketAddI(pid, 4)
    
    try:
        netobj()
        return None



def C2SGetBackReward(idx):
    netobj = GetRecruitNetObj()
    netobj.PacketAddI(6, 1)
    netobj.PacketAddI(idx, 1)
    netobj.PacketSend()

S2CFunc = { }

def S2CRecruitProcess(netobj):
    iSub = netobj.UnpackInt(1)
    if iSub not in S2CFunc:
        LOG('S2CRecruit-%d \xaf\xca\xa4\xd6\xa9w\xb8q\xa1I' % iSub)
        return None
    
    import protocolprint
    oFunc = S2CFunc[iSub]
    protocolprint.AppendS2CSubInfo('Recruit', oFunc.__name__)
    oFunc(netobj)
