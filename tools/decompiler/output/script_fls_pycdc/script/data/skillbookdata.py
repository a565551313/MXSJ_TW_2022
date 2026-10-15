# pycdc 交叉复核产物 · script.fls entry 3075
# co_filename(原始)='script/data/skillbookdata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3075.pyc (Python 2.5)


def GetData(grade):
    return DATA.get(grade, None)


def GetSkillByID(iID):
    for _, dPage in DATA.items():
        for iIdx, dDesc in dPage.items():
            if dDesc['skillid'] == iID:
                return iID
                continue
        
    

# WARNING: Decompyle incomplete
