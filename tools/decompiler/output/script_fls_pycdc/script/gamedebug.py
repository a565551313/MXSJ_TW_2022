# pycdc 交叉复核产物 · script.fls entry 3327
# co_filename(原始)='script/gamedebug.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3327.pyc (Python 2.5)

import sys

def systrace():
    print 'Traceback:', sys.exc_info()[0], 'Value:', sys.exc_info()[1]
    info = sys.exc_info()[2]
    import traceback
    traceback.print_tb(info)


def functrace(\xd8\xddmit = None):
    f = sys._getframe().f_back
    infos = []
    n = 0
    while f is not None:
        if \xd8\xddmit is None or n < \xd8\xddmit:
            co = f.f_code
            infos.append((co.co_filename, f.f_lineno, co.co_name))
            f = f.f_back
            n += 1
            continue
    :
        f = sys._getframe().f_back
        infos = []
        n = 0
        while f is not None:
            if \xd8\xddmit is None or n < \xd8\xddmit:
                co = f.f_code
                infos.append((co.co_filename, f.f_lineno, co.co_name))
                f = f.f_back
                n += 1
                continue
        
        infos.reverse()
    infos.reverse()


def GetSystrace():
    systrace()
    import traceback
    info = sys.exc_info()
    sExcept = str(info[0])
    sDetail = str(info[1])
    sTrace = sExcept + sDetail
    sTrace = sTrace.replace("'", '')
    sTrace = sTrace.replace('"', '')
    sTrace = sTrace.replace('%', '\xa2H')
    sStack = str(traceback.extract_tb(info[2]))
    sStack = sStack.replace("'", '')
    sStack = sStack.replace('"', '')
    sStack = sStack.replace('%', '\xa2H')
    i = len(sTrace) - 240
    sTrace += sStack[i:]
    return sTrace
