# pycdc 交叉复核产物 · script.fls entry 293
# co_filename(原始)='script/data/equipicondata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_293.pyc (Python 2.5)


def GetIcon(iType, iLevel):
    if iType in DATA:
        if iLevel in DATA[iType]:
            return DATA[iType][iLevel]['iCoin']
        
    
    return 0

# WARNING: Decompyle incomplete
