# pycdc 交叉复核产物 · script.fls entry 124
# co_filename(原始)='script/data/areaphonecodedata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_124.pyc (Python 2.5)


def GetCountryData(shortname):
    for data in INFOLST:
        if data['sCountry'] == shortname:
            return data
            continue
    

# WARNING: Decompyle incomplete
