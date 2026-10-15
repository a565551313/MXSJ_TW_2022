# pycdc 交叉复核产物 · script.fls entry 1775
# co_filename(原始)='script/mxgame/serverbattle/serverbattleinterface.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1775.pyc (Python 2.5)


def GetNextGroup(iCurGroup):
    import serverbattledefine
    if iCurGroup in serverbattledefine.TX_GROUP_NAME:
        lstLoopGroup = serverbattledefine.LOOP165_CHANGE_LIST
    else:
        lstLoopGroup = serverbattledefine.LOOPNOR_CHANGE_LIST
# WARNING: Decompyle incomplete
