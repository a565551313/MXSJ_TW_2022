# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\render\renderonlineupdate.py
import C_sys
g_CodeMd5Set = set()

def OnlineUpdate(sName, sCode):
    import md5
    key = md5.new(sCode).hexdigest()
    if key in g_CodeMd5Set:
        return
    g_CodeMd5Set.add(key)
    import marshal, zlib
    data = zlib.decompress(sCode, zlib.MAX_WBITS)
    data = marshal.loads(data)
    data = C_sys.GBK_to_UTF8(data)
    DebugLog('执行渲染端加密在线更新客户端代码: %s' % sName, type=1)
    exec data
