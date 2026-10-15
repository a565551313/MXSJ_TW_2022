# pycdc 交叉复核产物 · script.fls entry 792
# co_filename(原始)='script/protocol/cs2021newserveractivity.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_792.pyc (Python 2.5)

import net
import protocolcount
import net2021newserveractivity
import huodongdefine

def GS2CO\x91\x84\x8f\xa5\x8d\x86(oNetObj):
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=1', 'GS2COpenDlg()')
    net2021newserveractivity.OnOpenDlg()

g_NetFunction = {
    1: GS2CO\x91\x84\x8f\xa5\x8d\x86 }

def OnCommand(oNetObj):
    iSub = oNetObj.UnpackInt(1)
    func = g_NetFunction.get(iSub)
    if not func:
        protocolcount.ErrorLog('net.GS2C_HUODONG_OP', '\xb5L\xaak\xb8\xd1\xaaR GS2C_HUODONG_OP=0xce \xaa\xba\xa4l\xa8\xf3\xc4\xb3\xa1G%s' % iSub)
        return None
    
    func(oNetObj)


def C2GSOpenDlg():
    oNetObj = GetHuoDongNetObj(1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=1', 'C2GSOpenDlg()')


def GetHuoDongNetObj(iSub):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_HUODONG)
    (None,).PacketAddI(len(huodongdefine.NEWSERVERACTIVITY), 1)
    oNetObj.PacketAddS(huodongdefine.NEWSERVERACTIVITY, len(huodongdefine.NEWSERVERACTIVITY))
    oNetObj.PacketAddI(iSub, 1)
    return oNetObj
