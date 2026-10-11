# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\check\gpucheck.py
__all__ = [
 'Start',
 'GetSelfGPU',
 'GetTotalGPU']
CHECK_FRAME = 450
g_SelfGpu = 0
g_SelfGpuMemory = 0
g_TotalGpu = 0
g_TotalGpuMemory = 0

def ModuleReset():
    global g_SelfGpu
    global g_SelfGpuMemory
    global g_TotalGpu
    global g_TotalGpuMemory
    g_SelfGpu = 0
    g_SelfGpuMemory = 0
    g_TotalGpu = 0
    g_TotalGpuMemory = 0


def Start():
    import C_object
    C_object.SetGpuInfoCallback(GPUPercentCallBack, CHECK_FRAME)


def GetSelfGPU():
    return (
     g_SelfGpu, g_SelfGpuMemory)


def GetTotalGPU():
    return (
     g_TotalGpu, g_TotalGpuMemory)


def GPUPercentCallBack(self_gpu, self_gpuMemory, total_gpu, total_gpuMemory):
    global g_SelfGpu
    global g_SelfGpuMemory
    global g_TotalGpu
    global g_TotalGpuMemory
    g_SelfGpu = int(self_gpu)
    g_SelfGpuMemory = int(self_gpuMemory / 1024.0)
    g_TotalGpu = int(total_gpu)
    g_TotalGpuMemory = int(total_gpuMemory / 1024.0)
