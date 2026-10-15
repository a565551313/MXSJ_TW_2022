# pycdc 交叉复核产物 · script.fls entry 4941
# co_filename(原始)='script/yard/netyard_others.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4941.pyc (Python 2.5)

'''
\xbb\xf1\xc8\xa1\xcd\xe6\xbc\xd2\xd6\xae\xbc\xd2\xcf\xe0\xb9\xd8\xd0\xad\xd2\xe9
S2C:
\t\xa5D\xa8\xf3\xc4\xb3\xa1G 0x50
\tsub\xa3\xba 107
\tsub1:\xc2\xd4

'''

def S2CYardOtherProcess(netobj):
    iSub = netobj.UnpackInt(1)
    oFunc = g_Sub2Func.get(iSub)
    if not oFunc:
        return None
    
    oFunc(netobj)


def S2CClosePrivat\x86\xb0torage(oNetObj):
    '''\xc3\xf6\xb1\xbc\xad\xd3\xa4H\xad\xdc\xaew'''
    import yardstoragedlg
    yardstoragedlg.CloseDlg()

g_Sub2Func = {
    1: S2CClosePrivat\x86\xb0torage }
