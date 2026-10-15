# MXSJ 恢复产物 · script.fls entry 3794 (id=0xc1035c2f)
# co_filename(原始)='script/mxgame/a\x00tivity/yardmatch/yardmatchtools.py'
# 转译阶段=baseline  密钥修复=False
# keys=[5, 96, 3, 96, 195] bounds=[153, 278, 279, 362]
# 生成时间=2026-10-14T23:11:09Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72

# 注意：包内自报文件名已清洗（renamed）；原名见上文。# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\mxgame\activity\yardmatch\yardmatchtools.py


def GetTicketNumRoughlyDesc(iTicketNum):
    if iTicketNum < 10000:
        if iTicketNum < 500:
            sDesc = '<500'
        else:
            sDesc = '%d+' % (iTicketNum / 500 * 500)
    else:
        sDesc = '%.1f萬+' % (float(iTicketNum / 1000) / 10)
    return sDesc


return
