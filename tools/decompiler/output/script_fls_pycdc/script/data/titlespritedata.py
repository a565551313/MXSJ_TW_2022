# pycdc 交叉复核产物 · script.fls entry 1665
# co_filename(原始)='script/data/titlespritedata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1665.pyc (Python 2.5)

TITLE2REAL = {
    1021: 960,
    1022: 961,
    1023: 962 }

def GetTitleIDData(titleID):
    titleID = TITLE2REAL.get(titleID, titleID)
    return TITLESPRITE_DATA.get(titleID)

# WARNING: Decompyle incomplete
