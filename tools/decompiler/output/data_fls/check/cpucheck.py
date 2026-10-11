# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\check\cpucheck.py
__all__ = [
 'Start',
 'GetCPUPercent',
 'GetAverageCPUPercent']
CHECK_FRAME = 300
g_SelfCpu = 0
g_TotalCpu = 0
g_SelfCpus = []
g_TotalCpus = []

def ModuleReset():
    global g_SelfCpu
    global g_SelfCpus
    global g_TotalCpu
    global g_TotalCpus
    g_SelfCpu = 0
    g_TotalCpu = 0
    g_SelfCpus = []
    g_TotalCpus = []


def Start():
    import C_object
    C_object.SetProcessInfoCallback(CPUPercentCallBack, CHECK_FRAME)


def GetCPUPercent():
    return (
     g_SelfCpu, g_TotalCpu)


def GetAverageCPUPercent():

    def Average(lst):
        length = len(lst)
        if length == 0:
            return 0
        return sum(lst) / length

    return (Average(g_SelfCpus), Average(g_TotalCpus))


def CPUPercentCallBack(percent, total_percent):
    global g_SelfCpu
    global g_TotalCpu
    g_SelfCpu = percent
    g_TotalCpu = total_percent
    g_SelfCpus.append(percent)
    if len(g_SelfCpus) > 30:
        g_SelfCpus.pop(0)
    g_TotalCpus.append(total_percent)
    if len(g_TotalCpus) > 30:
        g_TotalCpus.pop(0)
