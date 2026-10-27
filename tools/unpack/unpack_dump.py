#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DuoyiProtect 脱壳转储器（32 位 Python + ctypes 原生 Win32 调试）。

策略：
  1) 以 DEBUG_ONLY_THIS_PROCESS 拉起 mx.exe；
  2) 基础 anti-anti-debug：清 PEB.BeingDebugged、伪装调试端口；
  3) 在主线程上下文里下硬件执行断点 DR0 = OEP(0xcba0ae)，DR7 使能；
     —— 硬件断点能扛住壳对代码段的解密/覆盖，软件 0xCC 会被覆盖掉；
  4) 全程把异常当 HANDLED 放行，让壳自己的 SEH/VEH 正常跑；
  5) 当主线程在 OEP 处触发 EXCEPTION_SINGLE_STEP(0x80000004) 时，
     用 VirtualQueryEx 枚举镜像区间并 ReadProcessMemory 平铺转储到 mx_unpacked.bin；
  6) 强杀进程，收工。

注意：硬件断点只在主线程生效；若壳把真实 OEP 放到别的线程/地址，需另想办法。
用法: D:\Python315-32\python.exe unpack_dump.py <exe> [timeout_sec]
"""
import sys, ctypes, ctypes.wintypes, time, os

kernel32 = ctypes.windll.kernel32
ntdll = ctypes.windll.ntdll

# constants
DEBUG_ONLY_THIS_PROCESS = 0x00000002
CREATE_NEW_CONSOLE      = 0x00000010
CONTEXT_FULL            = 0x10007
CONTEXT_DEBUG_REGISTERS = 0x100010
PROCESS_ALL_ACCESS      = 0x1F0FFF

EXCEPTION_BREAKPOINT    = 0x80000003
EXCEPTION_SINGLE_STEP   = 0x80000004

IMAGE_BASE = 0x00400000
OEP_RVA    = 0x008ba0ae
OEP_VA     = IMAGE_BASE + OEP_RVA   # 0xcba0ae

# ---- structures ----
class STARTUPINFO(ctypes.Structure):
    _fields_ = [("cb", ctypes.c_ulong),("lpReserved", ctypes.c_void_p),
        ("lpDesktop", ctypes.c_void_p),("lpTitle", ctypes.c_void_p),
        ("dwX", ctypes.c_ulong),("dwY", ctypes.c_ulong),("dwXSize", ctypes.c_ulong),
        ("dwYSize", ctypes.c_ulong),("dwXCountChars", ctypes.c_ulong),
        ("dwYCountChars", ctypes.c_ulong),("dwFillAttribute", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),("wShowWindow", ctypes.c_ushort),
        ("cbReserved2", ctypes.c_ushort),("lpReserved2", ctypes.c_void_p),
        ("hStdInput", ctypes.c_void_p),("hStdOutput", ctypes.c_void_p),
        ("hStdError", ctypes.c_void_p)]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [("hProcess", ctypes.c_void_p),("hThread", ctypes.c_void_p),
        ("dwProcessId", ctypes.c_ulong),("dwThreadId", ctypes.c_ulong)]

class CONTEXT(ctypes.Structure):
    _fields_ = [("ContextFlags", ctypes.c_ulong),
        ("Dr0", ctypes.c_ulong),("Dr1", ctypes.c_ulong),("Dr2", ctypes.c_ulong),
        ("Dr3", ctypes.c_ulong),("Dr6", ctypes.c_ulong),("Dr7", ctypes.c_ulong),
        ("FloatSave", ctypes.c_byte*112),
        ("SegGs", ctypes.c_ulong),("SegFs", ctypes.c_ulong),("SegEs", ctypes.c_ulong),
        ("SegDs", ctypes.c_ulong),("Edi", ctypes.c_ulong),("Esi", ctypes.c_ulong),
        ("Ebx", ctypes.c_ulong),("Edx", ctypes.c_ulong),("Ecx", ctypes.c_ulong),
        ("Eax", ctypes.c_ulong),("Ebp", ctypes.c_ulong),("Eip", ctypes.c_ulong),
        ("SegCs", ctypes.c_ulong),("EFlags", ctypes.c_ulong),("Esp", ctypes.c_ulong),
        ("SegSs", ctypes.c_ulong),("ExtendedRegisters", ctypes.c_byte*512)]

class DEBUG_EVENT(ctypes.Structure):
    _fields_ = [("dwDebugEventCode", ctypes.c_ulong),("dwProcessId", ctypes.c_ulong),
        ("dwThreadId", ctypes.c_ulong),("_pad", ctypes.c_byte*200)]
    EV_EXC_CODE = 12; EV_EXC_ADDR = 24; EV_EXC_FLAGS = 16
    CP_BASE = 24; CP_START = 40; CP_HTHREAD = 20
    EP_EXITCODE = 12

class PROCESS_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [("ExitStatus", ctypes.c_long),("PebBaseAddress", ctypes.c_void_p),
        ("AffinityMask", ctypes.c_void_p),("BasePriority", ctypes.c_long),
        ("UniqueProcessId", ctypes.c_void_p),("InheritedFrom", ctypes.c_void_p)]

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p),("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_ulong),("RegionSize", ctypes.c_ulong),
        ("State", ctypes.c_ulong),("Protect", ctypes.c_ulong),("Type", ctypes.c_ulong)]

def SetBP(hthread):
    ctx = CONTEXT(); ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS
    if not kernel32.GetThreadContext(hthread, ctypes.byref(ctx)):
        raise RuntimeError("GetThreadContext failed %d" % kernel32.GetLastError())
    ctx.Dr0 = OEP_VA
    ctx.Dr7 = 0x1   # L0=1 (local exec bp on DR0)
    ctx.Dr6 = 0
    if not kernel32.SetThreadContext(hthread, ctypes.byref(ctx)):
        raise RuntimeError("SetThreadContext failed %d" % kernel32.GetLastError())
    print("[*] hardware BP set on OEP 0x%08x" % OEP_VA)

def HideDebugger(hproc):
    pbi = PROCESS_BASIC_INFORMATION()
    ret = ctypes.c_ulong()
    r = ntdll.NtQueryInformationProcess(hproc, 0, ctypes.byref(pbi),
            ctypes.sizeof(pbi), ctypes.byref(ret))
    if r == 0 and pbi.PebBaseAddress:
        zero = ctypes.c_char(b'\x00')
        written = ctypes.c_ulong()
        # PEB.BeingDebugged at offset 2
        kernel32.WriteProcessMemory(hproc, ctypes.c_void_p(pbi.PebBaseAddress+2),
                ctypes.byref(zero), 1, ctypes.byref(written))
        print("[*] cleared PEB.BeingDebugged")
    # 伪装调试端口
    val = ctypes.c_ulong(0)
    ntdll.NtSetInformationProcess(hproc, 7, ctypes.byref(val), 4)  # 7=ProcessDebugPort
    val2 = ctypes.c_ulong(1)
    ntdll.NtSetInformationProcess(hproc, 0x1f, ctypes.byref(val2), 4)  # 31=ProcessDebugFlags
    print("[*] masked debug port / debug flags")

def DumpImage(hproc, outpath, imagesize):
    # 平铺转储 IMAGE_BASE..IMAGE_BASE+imagesize，只取已提交内存
    dump = bytearray(imagesize)
    addr = IMAGE_BASE
    end = IMAGE_BASE + imagesize
    regions = 0
    while addr < end:
        mbi = MEMORY_BASIC_INFORMATION()
        if not kernel32.VirtualQueryEx(hproc, ctypes.c_void_p(addr),
                ctypes.byref(mbi), ctypes.sizeof(mbi)):
            break
        if mbi.State == 0x1000 and (mbi.Protect & 0xFF) not in (0, 0x01):  # MEM_COMMIT & 有访问权限
            size = mbi.RegionSize
            buf = ctypes.create_string_buffer(size)
            read = ctypes.c_ulong()
            if kernel32.ReadProcessMemory(hproc, ctypes.c_void_p(addr),
                    buf, size, ctypes.byref(read)):
                off = addr - IMAGE_BASE
                dump[off:off+read.value] = buf[:read.value]
                regions += 1
            addr += size
        else:
            addr += mbi.RegionSize
    with open(outpath, "wb") as f:
        f.write(dump)
    print("[*] dumped %d committed regions, %d bytes -> %s" % (regions, len(dump), outpath))

def main():
    exe = sys.argv[1]
    timeout = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0
    outpath = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "mx_unpacked.bin")
    imagesize = int(sys.argv[4]) if len(sys.argv) > 4 else 0xA60000
    si = STARTUPINFO(); si.cb = ctypes.sizeof(STARTUPINFO)
    pi = PROCESS_INFORMATION()
    ok = kernel32.CreateProcessW(ctypes.c_wchar_p(exe), None, None, None, False,
            DEBUG_ONLY_THIS_PROCESS | CREATE_NEW_CONSOLE, None, None,
            ctypes.byref(si), ctypes.byref(pi))
    if not ok:
        raise RuntimeError("CreateProcessW failed %d" % kernel32.GetLastError())
    print("[*] started pid=%d" % pi.dwProcessId)
    HideDebugger(pi.hProcess)

    ev = DEBUG_EVENT()
    start = time.time()
    bp_set = False
    dumped = False
    while True:
        if time.time() - start > timeout:
            print("[!] timeout without reaching OEP")
            break
        if not kernel32.WaitForDebugEvent(ctypes.byref(ev), 1000):
            continue
        code = ev.dwDebugEventCode
        if code == 3:  # CREATE_PROCESS
            if not bp_set:
                hthr = ctypes.cast(ctypes.addressof(ev)+ev.CP_HTHREAD, ctypes.POINTER(ctypes.c_void_p)).contents.value
                try:
                    SetBP(hthr); bp_set = True
                except Exception as e:
                    print("[!] SetBP failed:", e)
            kernel32.ContinueDebugEvent(ev.dwProcessId, ev.dwThreadId, 0x10002)
        elif code == 1:  # EXCEPTION
            exc_code = ctypes.cast(ctypes.addressof(ev)+ev.EV_EXC_CODE, ctypes.POINTER(ctypes.c_ulong)).contents.value
            exc_addr = ctypes.cast(ctypes.addressof(ev)+ev.EV_EXC_ADDR, ctypes.POINTER(ctypes.c_ulong)).contents.value
            if exc_code == EXCEPTION_SINGLE_STEP and exc_addr == OEP_VA:
                print("[*] >>> OEP hit at 0x%08x, dumping image" % exc_addr)
                DumpImage(pi.hProcess, outpath, imagesize)
                dumped = True
                kernel32.ContinueDebugEvent(ev.dwProcessId, ev.dwThreadId, 0x10002)
                break
            # 放行所有异常给程序的 SEH 处理
            kernel32.ContinueDebugEvent(ev.dwProcessId, ev.dwThreadId, 0x10002)
        elif code == 5:  # EXIT_PROCESS
            ec = ctypes.cast(ctypes.addressof(ev)+ev.EP_EXITCODE, ctypes.POINTER(ctypes.c_ulong)).contents.value
            print("[!] process exited before OEP, code=0x%08x" % ec)
            break
        else:
            kernel32.ContinueDebugEvent(ev.dwProcessId, ev.dwThreadId, 0x10002)
    kernel32.TerminateProcess(pi.hProcess, 0)
    kernel32.CloseHandle(pi.hProcess); kernel32.CloseHandle(pi.hThread)
    print("[*] done, dumped=%s" % dumped)

if __name__ == "__main__":
    main()
