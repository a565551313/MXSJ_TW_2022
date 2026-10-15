# pycdc 交叉复核产物 · script.fls entry 1188
# co_filename(原始)='script/data/daobiaodata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1188.pyc (Python 2.5)


def GetDaoBiaoData(searchTxt):
    resultLst = []
    for name, exelNameLst in DATA.items():
        if searchTxt in name:
            resultLst += exelNameLst
            continue
    
    exec None

DATA = { }
