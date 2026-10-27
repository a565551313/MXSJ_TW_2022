#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最小 Win32 调试器探针：用 32 位 Python + ctypes 把 mx.exe 拉到调试器下，
只抓初始 EIP 与前若干个调试事件（创建进程 / 异常 / 退出），用来判断：
  1) 入口是不是真在加密段、能否执行；
  2) 进程能否在无桌面环境跑起来；
  3) 是否有 anti-debug 导致提前退出。
不脱壳、不转储，纯侦察。超时后强杀。
用法: D:\\Python315-32\\python.exe unpack_probe.py <exe> [timeout_sec]
"""
import sys, ctypes, ctypes.wintypes, time

kernel32 = ctypes.windll.kernel32

# ---- constants ----
DEBUG_ONLY_THIS_PROCESS = 0x00000002
CREATE_NEW_CONSOLE      = 0x00000010
INFINITE                = 0xFFFFFFFF
CONTEXT_FULL            = 0x10007
THREAD_ALL_ACCESS       = 0x1F03FF
PROCESS_ALL_ACCESS      = 0x1F0FFF

EXCEPTION_BREAKPOINT    = 0x80000003
EXCEPTION_ACCESS_VIOLATION = 0xC0000005
EXCEPTION_ILLEGAL_INSTRUCTION = 0xC000001D
EXCEPTION_SINGLE_STEP   = 0x80000004

# ---- structures ----
class STARTUPINFO(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("lpReserved", ctypes.c_void_p),
        ("lpDesktop", ctypes.c_void_p),
        ("lpTitle", ctypes.c_void_p),
        ("dwX", ctypes.c_ulong), ("dwY", ctypes.c_ulong),
        ("dwXSize", ctypes.c_ulong), ("dwYSize", ctypes.c_ulong),
        ("dwXCountChars", ctypes.c_ulong), ("dwYCountChars", ctypes.c_ulong),
        ("dwFillAttribute", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("wShowWindow", ctypes.c_ushort),
        ("cbReserved2", ctypes.c_ushort),
        ("lpReserved2", ctypes.c_void_p),
        ("hStdInput", ctypes.c_void_p),
        ("hStdOutput", ctypes.c_void_p),
        ("hStdError", ctypes.c_void_p),
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", ctypes.c_void_p),
        ("hThread", ctypes.c_void_p),
        ("dwProcessId", ctypes.c_ulong),
        ("dwThreadId", ctypes.c_ulong),
    ]

class CONTEXT(ctypes.Structure):
    _fields_ = [
        ("ContextFlags", ctypes.c_ulong),
        ("Dr0", ctypes.c_ulong), ("Dr1", ctypes.c_ulong), ("Dr2", ctypes.c_ulong),
        ("Dr3", ctypes.c_ulong), ("Dr6", ctypes.c_ulong), ("Dr7", ctypes.c_ulong),
        ("FloatSave", ctypes.c_byte * 112),
        ("SegGs", ctypes.c_ulong), ("SegFs", ctypes.c_ulong),
        ("SegEs", ctypes.c_ulong), ("SegDs", ctypes.c_ulong),
        ("Edi", ctypes.c_ulong), ("Esi", ctypes.c_ulong), ("Ebx", ctypes.c_ulong),
        ("Edx", ctypes.c_ulong), ("Ecx", ctypes.c_ulong), ("Eax", ctypes.c_ulong),
        ("Ebp", ctypes.c_ulong), ("Eip", ctypes.c_ulong), ("SegCs", ctypes.c_ulong),
        ("EFlags", ctypes.c_ulong), ("Esp", ctypes.c_ulong), ("SegSs", ctypes.c_ulong),
        ("ExtendedRegisters", ctypes.c_byte * 512),
    ]

class DEBUG_EVENT(ctypes.Structure):
    _fields_ = [
        ("dwDebugEventCode", ctypes.c_ulong),
        ("dwProcessId", ctypes.c_ulong),
        ("dwThreadId", ctypes.c_ulong),
        ("_pad", ctypes.c_byte * (160 - 12)),  # oversize union
    ]
    # field offsets within union (32-bit)
    EV_EXC_CODE   = 12
    EV_EXC_ADDR   = 24
    CP_BASE       = 24
    CP_START      = 40
    CP_HTHREAD    = 20
    EP_EXITCODE   = 12

def err(name):
    code = kernel32.GetLastError()
    raise RuntimeError("%s failed, GetLastError=%d (0x%x)" % (name, code, code))

def get_context(hthread):
    ctx = CONTEXT()
    ctx.ContextFlags = CONTEXT_FULL
    if not kernel32.GetThreadContext(hthread, ctypes.byref(ctx)):
        return None
    return ctx

def main():
    exe = sys.argv[1]
    timeout = float(sys.argv[2]) if len(sys.argv) > 2 else 8.0
    si = STARTUPINFO()
    si.cb = ctypes.sizeof(STARTUPINFO)
    pi = PROCESS_INFORMATION()
    # lpDesktop=None 让它用默认桌面；无桌面时可能失败，但先试
    ok = kernel32.CreateProcessW(
        ctypes.c_wchar_p(exe), None, None, None, False,
        DEBUG_ONLY_THIS_PROCESS | CREATE_NEW_CONSOLE, None, None,
        ctypes.byref(si), ctypes.byref(pi))
    if not ok:
        err("CreateProcessW")
    print("[*] started pid=%d tid=%d" % (pi.dwProcessId, pi.dwThreadId))

    ev = DEBUG_EVENT()
    start = time.time()
    seen = 0
    MAXEVENTS = 40
    while True:
        if time.time() - start > timeout:
            print("[*] timeout, terminating")
            kernel32.TerminateProcess(pi.hProcess, 0)
            break
        if not kernel32.WaitForDebugEvent(ctypes.byref(ev), 1000):
            continue
        code = ev.dwDebugEventCode
        if code == 1:  # EXCEPTION_DEBUG_EVENT
            rec = ctypes.cast(ctypes.addressof(ev) + ev.EV_EXC_CODE,
                              ctypes.POINTER(ctypes.c_ulong * 4))
            exc_code = rec.contents[0]
            exc_addr = rec.contents[2]
            print("[EXC] pid=%d tid=%d code=0x%08x addr=0x%08x" %
                  (ev.dwProcessId, ev.dwThreadId, exc_code, exc_addr))
            if exc_code == EXCEPTION_BREAKPOINT:
                # 初始断点：抓主线程 EIP
                ctx = get_context(pi.hThread)
                if ctx:
                    print("      initial EIP = 0x%08x (Eax=0x%08x Esp=0x%08x)"
                          % (ctx.Eip, ctx.Eax, ctx.Esp))
            seen += 1
            kernel32.ContinueDebugEvent(ev.dwProcessId, ev.dwThreadId, 0x10002 if exc_code==EXCEPTION_BREAKPOINT else 0x10001)
        elif code == 3:  # CREATE_PROCESS_DEBUG_EVENT
            base = ctypes.cast(ctypes.addressof(ev) + ev.CP_BASE, ctypes.POINTER(ctypes.c_void_p)).contents.value
            startaddr = ctypes.cast(ctypes.addressof(ev) + ev.CP_START, ctypes.POINTER(ctypes.c_void_p)).contents.value
            print("[CREATE_PROCESS] base=0x%08x startAddr=0x%08x" % (base, startaddr))
            seen += 1
            kernel32.ContinueDebugEvent(ev.dwProcessId, ev.dwThreadId, 0x10002)
        elif code == 2:  # CREATE_THREAD_DEBUG_EVENT
            seen += 1
            kernel32.ContinueDebugEvent(ev.dwProcessId, ev.dwThreadId, 0x10002)
        elif code == 5:  # EXIT_PROCESS_DEBUG_EVENT
            exitcode = ctypes.cast(ctypes.addressof(ev) + ev.EP_EXITCODE, ctypes.POINTER(ctypes.c_ulong)).contents.value
            print("[EXIT_PROCESS] pid=%d exitCode=0x%08x" % (ev.dwProcessId, exitcode))
            kernel32.ContinueDebugEvent(ev.dwProcessId, ev.dwThreadId, 0x10002)
            break
        elif code == 6:  # EXIT_THREAD
            kernel32.ContinueDebugEvent(ev.dwProcessId, ev.dwThreadId, 0x10002)
        elif code == 8:  # LOAD_DLL
            kernel32.ContinueDebugEvent(ev.dwProcessId, ev.dwThreadId, 0x10002)
        elif code == 9:  # UNLOAD_DLL
            kernel32.ContinueDebugEvent(ev.dwProcessId, ev.dwThreadId, 0x10002)
        elif code == 4:  # OUTPUT_DEBUG_STRING
            kernel32.ContinueDebugEvent(ev.dwProcessId, ev.dwThreadId, 0x10002)
        else:
            kernel32.ContinueDebugEvent(ev.dwProcessId, ev.dwThreadId, 0x10002)
        if seen >= MAXEVENTS:
            print("[*] reached event cap, terminating")
            kernel32.TerminateProcess(pi.hProcess, 0)
            break
    print("[*] done")

if __name__ == "__main__":
    main()
