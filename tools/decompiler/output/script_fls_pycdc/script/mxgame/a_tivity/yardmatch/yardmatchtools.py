# pycdc 交叉复核产物 · script.fls entry 3794
# co_filename(原始)='script/mxgame/a\x00tivity/yardmatch/yardmatchtools.py'
# uncompyle6 状态=full  转译阶段=baseline
# 生成时间=2026-10-14T23:56:19Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3794.pyc (Python 2.5)


def GetTicketNumRoughlyDesc(iTicketNum):
    if iTicketNum < 10000:
        if iTicketNum < 500:
            sDesc = '<500'
        else:
            sDesc = '%d+' % (iTicketNum / 500) * 500
    else:
        sDesc = '%.1f\xb8U+' % float(iTicketNum / 1000) / 10
    return sDesc
