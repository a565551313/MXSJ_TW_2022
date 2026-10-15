# pycdc 交叉复核产物 · script.fls entry 1709
# co_filename(原始)='script/mxgame/ornament/netornament.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1709.pyc (Python 2.5)

'''
Author huyuhong01
Create Time 2018/12/13
\xbf\xec\xbd\xdd\xb9\xba\xc2\xf2\xca\xce\xc6\xb7\xcf\xe0\xb9\xd8\xcd\xf8\xc2\xe7\xd0\xad\xd2\xe9
'''
import c2spetuicom
import net
import mdornament
import misc
import permission
g_oPetAniRef = None

def CallPetCenterDlgRefreshPetAni(iID):
    global g_oPetAniRef
    import pet
    if g_oPetAniRef:
        oPetAni = g_oPetAniRef.Get()
        if not oPetAni:
            return None
        
        if oPetAni.m_PetID == iID:
            oPetAni.CreateOrnamentImg()
            g_oPetAniRef = None
        
    


def C2SGetSummonWepAmount(iPetId, oCallback):
    global g_oPetAniRef
    g_oPetAniRef = misc.WeakRef(oCallback)
    if permission.IsOpenUICom():
        netobj = c2spetuicom.GetPetUIComNetObj(2)
    else:
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_OPEN_UI)
        netobj.PacketAddI(19, 1)
    netobj.PacketAddI(1, 1)
    netobj.PacketAddI(1, 1)
    netobj.PacketAddI(iPetId, 4)
    netobj.PacketSend()


def C2SQuickBuySummonWep(iPetId, iOrnament):
    if permission.IsOpenUICom():
        netobj = c2spetuicom.GetPetUIComNetObj(2)
    else:
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_OPEN_UI)
        netobj.PacketAddI(19, 1)
    netobj.PacketAddI(2, 1)
    netobj.PacketAddI(iPetId, 4)
    netobj.PacketAddI(iOrnament, 1)
    netobj.PacketSend()


def C2SGmOpenSummon(iPlayerId, iPetid, iType):
    if permission.IsOpenUICom():
        netobj = c2spetuicom.GetPetUIComNetObj(2)
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_OPEN_UI)
    netobj.PacketAddI(19, 1)
    netobj.PacketAddI(3, 1)
    netobj.PacketAddI(iPetid, 4)
    netobj.PacketAddI(iPlayerId, 4)
    netobj.PacketAddI(iType, 1)
    netobj.PacketSend()


def S2CSummonMaxWea(netobj):
    iLstLen = netobj.UnpackInt(1)
    for i in range(iLstLen):
        iId = netobj.UnpackInt(4)
        iMax = netobj.UnpackInt(4)
        mdornament.AddOrnamentMax(iId, iMax)
        CallPetCenterDlgRefreshPetAni(iId)
