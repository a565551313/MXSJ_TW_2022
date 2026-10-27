# -*- coding: utf-8 -*-
"""用硬件执行断点(HW BP)定位 VM -> 真实代码交接点。

为什么不用 PAGE_GUARD：本壳的解密代码在解密真实代码时会 VirtualProtect 改写页保护，
会把我们之前打的 PAGE_GUARD 清掉，导致漏掉交接。
硬件执行断点(DR0-3)是 CPU 级、与页保护无关，且只在"执行"该地址时触发，
因此 VM 读页解密(数据访问)不会误触发，只在真正跳去执行真实代码时触发 = 交接。

候选交接地址（真实代码区段的起始，最可能就是解密后入口）：
  0x7DB000  (RWX 解密区 A 起点)
  0x822000  (RWX 解密区 B 起点)
  0x401000  (原始 .text 起点)
  0x6B0000  (原始 .text 尾/.rdata 前)
进程以调试方式自由运行（不单步）；首个命中的 HW 执行断点地址即交接目标。

用法: D:/Python315-32/python.exe unpack_hwbp.py <exe> [out]
"""
import sys, ctypes, ctypes.wintypes, time, os

kernel32 = ctypes.windll.kernel32
ntdll    = ctypes.windll.ntdll

DEBUG_ONLY_THIS_PROCESS = 0x00000002
CREATE_NEW_CONSOLE      = 0x00000010
CONTEXT_FULL            = 0x10007
CONTEXT_DEBUG_REGISTERS = 0x100010
EXC=1; CREATE_THREAD=2; CREATE_PROCESS=3; EXIT_PROCESS=5
STATUS_SINGLE_STEP=0x80000004   # HW 断点以该码上报
STATUS_BREAKPOINT =0x80000003

CANDIDATES = [0x7DB000, 0x822000, 0x401000, 0x6B0000]
OEP_VA = 0x00cba0ae   # 壳解完后的原始入口（VA，基址 0x400000）

class SI(ctypes.Structure):
    _fields_=[("cb",ctypes.c_ulong),("lpReserved",ctypes.c_void_p),("lpDesktop",ctypes.c_void_p),
        ("lpTitle",ctypes.c_void_p),("dwX",ctypes.c_ulong),("dwY",ctypes.c_ulong),("dwXSize",ctypes.c_ulong),
        ("dwYSize",ctypes.c_ulong),("dwXCountChars",ctypes.c_ulong),("dwYCountChars",ctypes.c_ulong),
        ("dwFillAttribute",ctypes.c_ulong),("dwFlags",ctypes.c_ulong),("wShowWindow",ctypes.c_ushort),
        ("cbReserved2",ctypes.c_ushort),("lpReserved2",ctypes.c_void_p),("hStdInput",ctypes.c_void_p),
        ("hStdOutput",ctypes.c_void_p),("hStdError",ctypes.c_void_p)]
class PI(ctypes.Structure):
    _fields_=[("hProcess",ctypes.c_void_p),("hThread",ctypes.c_void_p),("dwProcessId",ctypes.c_ulong),("dwThreadId",ctypes.c_ulong)]
class CTX(ctypes.Structure):
    _fields_=[("ContextFlags",ctypes.c_ulong),("Dr0",ctypes.c_ulong),("Dr1",ctypes.c_ulong),("Dr2",ctypes.c_ulong),
        ("Dr3",ctypes.c_ulong),("Dr6",ctypes.c_ulong),("Dr7",ctypes.c_ulong),("FloatSave",ctypes.c_byte*112),
        ("SegGs",ctypes.c_ulong),("SegFs",ctypes.c_ulong),("SegEs",ctypes.c_ulong),("SegDs",ctypes.c_ulong),
        ("Edi",ctypes.c_ulong),("Esi",ctypes.c_ulong),("Ebx",ctypes.c_ulong),("Edx",ctypes.c_ulong),
        ("Ecx",ctypes.c_ulong),("Eax",ctypes.c_ulong),("Ebp",ctypes.c_ulong),("Eip",ctypes.c_ulong),
        ("SegCs",ctypes.c_ulong),("EFlags",ctypes.c_ulong),("Esp",ctypes.c_ulong),("SegSs",ctypes.c_ulong),
        ("ExtendedRegisters",ctypes.c_byte*512)]
class DE(ctypes.Structure):
    _fields_=[("dwDebugEventCode",ctypes.c_ulong),("dwProcessId",ctypes.c_ulong),("dwThreadId",ctypes.c_ulong),("_pad",ctypes.c_byte*200)]
    EV_EXC_CODE=12; EV_EXC_ADDR=24; CP_HTHREAD=20

def HideDbg(hp):
    class PBI(ctypes.Structure):
        _fields_=[("ExitStatus",ctypes.c_long),("PebBaseAddress",ctypes.c_void_p),("AffinityMask",ctypes.c_void_p),
            ("BasePriority",ctypes.c_long),("UniqueProcessId",ctypes.c_void_p),("InheritedFrom",ctypes.c_void_p)]
    p=PBI(); r=ctypes.c_ulong()
    ntdll.NtQueryInformationProcess(hp,0,ctypes.byref(p),ctypes.sizeof(p),ctypes.byref(r))
    if p.PebBaseAddress:
        z=ctypes.c_char(b'\x00'); w=ctypes.c_ulong()
        kernel32.WriteProcessMemory(hp,ctypes.c_void_p(p.PebBaseAddress+2),ctypes.byref(z),1,ctypes.byref(w))
    v=ctypes.c_ulong(0); ntdll.NtSetInformationProcess(hp,7,ctypes.byref(v),4)
    v2=ctypes.c_ulong(1); ntdll.NtSetInformationProcess(hp,0x1f,ctypes.byref(v2),4)

def SetHWExec(ht, addrs):
    c=CTX(); c.ContextFlags=CONTEXT_DEBUG_REGISTERS
    kernel32.GetThreadContext(ht,ctypes.byref(c))
    c.Dr0=addrs[0] if len(addrs)>0 else 0
    c.Dr1=addrs[1] if len(addrs)>1 else 0
    c.Dr2=addrs[2] if len(addrs)>2 else 0
    c.Dr3=addrs[3] if len(addrs)>3 else 0
    c.Dr6=0
    # DR7: 各 BP 设为"本地执行断点"。L0..L3 = bits 0,2,4,6；类型/长度全 0(执行)
    dr7=0
    for i in range(min(len(addrs),4)):
        dr7 |= (1 << (2*i))   # Li
    c.Dr7=dr7
    kernel32.SetThreadContext(ht,ctypes.byref(c))

def main():
    exe=sys.argv[1]
    out=sys.argv[2] if len(sys.argv)>2 else os.path.join(os.path.dirname(os.path.abspath(__file__)),"handoff.txt")
    si=SI(); si.cb=ctypes.sizeof(SI); pi=PI()
    ok=kernel32.CreateProcessW(ctypes.c_wchar_p(exe),None,None,None,False,
        DEBUG_ONLY_THIS_PROCESS|CREATE_NEW_CONSOLE,None,None,ctypes.byref(si),ctypes.byref(pi))
    if not ok: raise RuntimeError("CreateProcessW failed %d"%kernel32.GetLastError())
    print("[*] pid=%d; HW exec BPs @ %s"%(pi.dwProcessId,",".join("0x%X"%a for a in CANDIDATES)),flush=True)
    hp=pi.hProcess; ht=None; handoff=None; start=time.time(); hits=0; ev=DE()
    oep_hit=False; armed=False
    while True:
        if time.time()-start>600:
            print("[!] global timeout",flush=True); break
        if not kernel32.WaitForDebugEvent(ctypes.byref(ev),500): continue
        code=ev.dwDebugEventCode
        if code==CREATE_PROCESS:
            ht=ctypes.cast(ctypes.addressof(ev)+ev.CP_HTHREAD,ctypes.POINTER(ctypes.c_void_p)).contents.value
            HideDbg(hp)
            # 先下 OEP 硬件断点（用于门控：解壳完成才允许看守交接）
            c=CTX(); c.ContextFlags=CONTEXT_DEBUG_REGISTERS
            kernel32.GetThreadContext(ht,ctypes.byref(c)); c.Dr0=OEP_VA; c.Dr7=0x1; c.Dr6=0
            kernel32.SetThreadContext(ht,ctypes.byref(c))
            print("[*] OEP HW BP set @0x%X; waiting for unpacker..."%OEP_VA,flush=True)
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==CREATE_THREAD:
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==EXC:
            ec=ctypes.cast(ctypes.addressof(ev)+ev.EV_EXC_CODE,ctypes.POINTER(ctypes.c_ulong)).contents.value
            if ec==STATUS_SINGLE_STEP and not oep_hit:
                c=CTX(); c.ContextFlags=CONTEXT_FULL
                kernel32.GetThreadContext(ht,ctypes.byref(c))
                if c.Eip==OEP_VA:
                    oep_hit=True
                    # 解壳完成：此时再给真实代码区起始下执行断点（避免解壳期误触发）
                    SetHWExec(ht,CANDIDATES)
                    armed=True
                    print("[*] >>> OEP hit; real-code HW BPs armed; running free...",flush=True)
                    kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
                    continue
                else:
                    kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
            elif ec==STATUS_SINGLE_STEP and oep_hit and armed:
                c=CTX(); c.ContextFlags=CONTEXT_FULL
                kernel32.GetThreadContext(ht,ctypes.byref(c))
                eip=c.Eip
                if eip in CANDIDATES:
                    handoff=eip; hits+=1
                    print("[*] >>> HANDOFF: HW exec BP hit at 0x%X"%eip,flush=True)
                    break
                else:
                    kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
            elif ec==STATUS_BREAKPOINT:
                kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
            else:
                kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==EXIT_PROCESS:
            print("[!] process exited before handoff",flush=True); break
        else:
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
    if handoff is not None:
        with open(out,"w") as f:
            f.write("HANDOFF_TARGET=0x%X\n"%handoff)
            f.write("candidates=%s\n"%",".join("0x%X"%a for a in CANDIDATES))
            f.write("vm_region=0x947000-0xE42000 real_regions=0x401000-0x6B0000,0x7DB000-0x947000\n")
        print("[*] wrote handoff target -> %s"%out,flush=True)
    else:
        print("[!] no HW BP hit (candidates not executed as entry). Need exact addr.",flush=True)
    try: kernel32.TerminateProcess(hp,0)
    except: pass
    kernel32.CloseHandle(hp); kernel32.CloseHandle(pi.hThread)

if __name__=="__main__":
    main()
