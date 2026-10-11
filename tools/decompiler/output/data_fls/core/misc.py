# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\core\misc.py
import C_sys

def GetMac():
    return GetLocalMAC()


def GetLocalMAC():
    try:
        ver = C_sys.GetWindowVersion()
        if type(ver) == tuple:
            ver = ver[0]
        if ver == 6:
            mac = C_sys.GetWin7MAC()
        else:
            mac = C_sys.GetMAC()
    except:
        import os
        if 0 and os.path.exists('iphlpapi.dll'):
            mac = 'FFFFFF'
        else:
            mac = '0'

    return mac
