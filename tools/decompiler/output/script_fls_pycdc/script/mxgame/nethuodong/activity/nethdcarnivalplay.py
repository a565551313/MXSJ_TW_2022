# pycdc 交叉复核产物 · script.fls entry 1648
# co_filename(原始)='script/mxgame/nethuodong/activity/nethdcarnivalplay.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1648.pyc (Python 2.5)

import huodongdefine
import net

def GetCarnivalplayNetObj():
    netobj = net.PacketPrepare(net.C2GS_HUODONG)
    netobj.PacketAddPS(huodongdefine.CARNIVALPLAY)
    return netobj


def S2CMatchFlag(netobj):
    isMatch = netobj.UnpackInt(1)
    isLeader = netobj.UnpackInt(1)
    import dlgminipanel
    dlgminipanel.CreateCarnivalPlayPanel(1, isMatch, isLeader)


def S2COpen(netobj):
    import dlghuashanduel
    dlghuashanduel.ShowCarnivalPlayDlg()


def S2CChat(netobj):
    msg = netobj.UnpackString(0)
    import dlgnpc
    dlg = dlgnpc.ShowCloseResponseDlg(msg, '')
    dlg.SetCloseID(99)


def S2CCloseChat(netobj):
    import dlgnpc
    dlgnpc.CloseNpcDlg()


def C2SCheckMatch(isMacth):
    netobj = GetCarnivalplayNetObj()
    netobj.PacketAddI(1, 1)
    netobj.PacketAddI(isMacth, 1)
    netobj.PacketSend()


def C2SChangeLiuPai(iMain, iCls):
    netobj = GetCarnivalplayNetObj()
    netobj.PacketAddI(2, 1)
    netobj.PacketAddI(iMain, 2)
    netobj.PacketAddI(iCls, 1)
    netobj.PacketSend()


def C2SChangeColor(\xcbhape, color, wing, wingcolor):
    netobj = GetCarnivalplayNetObj()
    netobj.PacketAddI(3, 1)
    netobj.PacketAddI(\xcbhape, 2)
    for idx in range(3):
        netobj.PacketAddI(color[idx], 1)
    
    netobj.PacketAddI(wing, 1)
    netobj.PacketAddI(wingcolor, 1)
    netobj.PacketSend()


def C2SCheckLiuPai(iMain, iCls):
    netobj = GetCarnivalplayNetObj()
    netobj.PacketAddI(4, 1)
    netobj.PacketAddI(iMain, 2)
    netobj.PacketAddI(iCls, 1)
    netobj.PacketSend()

S2CFunc = {
    1: S2CMatchFlag,
    2: S2COpen,
    3: S2CChat,
    4: S2CCloseChat }

def S2CCarnivalplayProcess(netobj):
    iSub = netobj.UnpackInt(1)
    if iSub not in S2CFunc:
        LOG('S2CCarnivalplay-%d \xaf\xca\xa4\xd6\xa9w\xb8q\xa1I' % iSub)
        return None
    
    import protocolprint
    oFunc = S2CFunc[iSub]
    protocolprint.AppendS2CSubInfo('Carnivalplay', oFunc.__name__)
    oFunc(netobj)
