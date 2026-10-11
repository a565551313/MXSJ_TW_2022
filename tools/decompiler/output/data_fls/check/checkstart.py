# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\check\checkstart.py
g_Inited = False

def Start():
    global g_Inited
    if not g_Inited:
        g_Inited = True
        import statecheck
        statecheck.Start()
        import cpucheck
        cpucheck.Start()
        import gpucheck
        gpucheck.Start()
