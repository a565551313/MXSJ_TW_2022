# pycdc 交叉复核产物 · script.fls entry 2717
# co_filename(原始)='script/mxgame/map/maptools.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2717.pyc (Python 2.5)


def ReadBlk(sPath):
    
    try:
        f = open(sPath, 'rb')
    except:
        return (0, 0, { })

    sData = f.read()
    f.close()
    (w1, w2, h1, h2) = sData[:4]
    (w1, w2, h1, h2) = (ord(w1), ord(w2), ord(h1), ord(h2))
    iW = w1 + w2 * 256
    iH = h1 + h2 * 256
    i = 0
    j = 0
    dBlk = { }
# WARNING: Decompyle incomplete
