# -*- coding: utf-8 -*-
"""定位 VM -> 真实代码的"交接点"，不单步、不踩 OS，靠 PAGE_GUARD。

原理：
  - 真实引擎代码全在低地址段（VA < VM_START = 0xC50000）；
  - VM 代码全在高地址段（>= 0xC50000）。
  - 关键：被 DuoyiProtect 加壳的 exe 在 CREATE_PROCESS 时真实代码页还不存在
    （壳在运行期 VirtualAlloc+解密才铺好）。因此本脚本：
      1) 在 OEP(0xcba0ae) 下 HW 断点；壳跑完、OEP 命中时真实代码页已就绪；
      2) 此时再把低地址段所有"可执行且已提交"的页打上 PAGE_GUARD；
      3) 放开进程自由运行（不单步），VM 在高地址跑调度循环（原生速度），
         一旦它把控制流交还低地址真实代码——CPU 取低地址第一条指令触发
         GUARD 异常，该 EIP 即交接目标。
  - 若 GUARD 异常来自高地址指令对低地址页的"数据读"（VM 读常量），则 EIP
    落高地址，把该页重新打 GUARD 并继续自由跑，不误判。
  - 完全不单步，因此不会陷进 OS 代码，速度极快。

用法: D:/Python315-32/python.exe unpack_handoff.py <exe> [out]
"""
import sys, ctypes, ctypes.wintypes, time, os

kernel32 = ctypes.windll.kernel32
ntdll    = ctypes.windll.ntdll

DEBUG_ONLY_THIS_PROCESS = 0x00000002
CREATE_NEW_CONSOLE      = 0x00000010
PROCESS_ALL_ACCESS      = 0x1F0FFF
CONTEXT_FULL            = 0x10007
CONTEXT_DEBUG_REGISTERS = 0x100010

EXC            = 1
CREATE_THREAD  = 2
CREATE_PROCESS = 3
EXIT_PROCESS   = 5

PAGE_GUARD        = 0x100
MEM_COMMIT        = 0x1000

IMAGE_BASE   = 0x00400000
GUARD_MIN    = 0x00401000
REAL_CODE_MAX= 0x00C50000   # VA < 此值视为真实代码；低于它的所有可执行页打 GUARD
VM_START     = 0x00C50000   # VA >= 此值视为 VM 代码
OEP_VA       = 0x00cba0ae   # 壳解完后的原始入口（VA，基址 0x400000）

STATUS_GUARD_PAGE_VIOLATION = 0x80000001
STATUS_SINGLE_STEP          = 0x80000004   # HW 断点也以该码上报

class STARTUPINFO(ctypes.Structure):
    _fields_ = [("cb",ctypes.c_ulong),("lpReserved",ctypes.c_void_p),("lpDesktop",ctypes.c_void_p),
        ("lpTitle",ctypes.c_void_p),("dwX",ctypes.c_ulong),("dwY",ctypes.c_ulong),("dwXSize",ctypes.c_ulong),
        ("dwYSize",ctypes.c_ulong),("dwXCountChars",ctypes.c_ulong),("dwYCountChars",ctypes.c_ulong),
        ("dwFillAttribute",ctypes.c_ulong),("dwFlags",ctypes.c_ulong),("wShowWindow",ctypes.c_ushort),
        ("cbReserved2",ctypes.c_ushort),("lpReserved2",ctypes.c_void_p),("hStdInput",ctypes.c_void_p),
        ("hStdOutput",ctypes.c_void_p),("hStdError",ctypes.c_void_p)]
class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [("hProcess",ctypes.c_void_p),("hThread",ctypes.c_void_p),
        ("dwProcessId",ctypes.c_ulong),("dwThreadId",ctypes.c_ulong)]
class CONTEXT(ctypes.Structure):
    _fields_ = [("ContextFlags",ctypes.c_ulong),("Dr0",ctypes.c_ulong),("Dr1",ctypes.c_ulong),
        ("Dr2",ctypes.c_ulong),("Dr3",ctypes.c_ulong),("Dr6",ctypes.c_ulong),("Dr7",ctypes.c_ulong),
        ("FloatSave",ctypes.c_byte*112),("SegGs",ctypes.c_ulong),("SegFs",ctypes.c_ulong),
        ("SegEs",ctypes.c_ulong),("SegDs",ctypes.c_ulong),("Edi",ctypes.c_ulong),("Esi",ctypes.c_ulong),
        ("Ebx",ctypes.c_ulong),("Edx",ctypes.c_ulong),("Ecx",ctypes.c_ulong),("Eax",ctypes.c_ulong),
        ("Ebp",ctypes.c_ulong),("Eip",ctypes.c_ulong),("SegCs",ctypes.c_ulong),("EFlags",ctypes.c_ulong),
        ("Esp",ctypes.c_ulong),("SegSs",ctypes.c_ulong),("ExtendedRegisters",ctypes.c_byte*512)]
class DEBUG_EVENT(ctypes.Structure):
    _fields_ = [("dwDebugEventCode",ctypes.c_ulong),("dwProcessId",ctypes.c_ulong),
        ("dwThreadId",ctypes.c_ulong),("_pad",ctypes.c_byte*200)]
    EV_EXC_CODE=12; EV_EXC_ADDR=24; CP_HTHREAD=20
class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [("BaseAddress",ctypes.c_void_p),("AllocationBase",ctypes.c_void_p),
        ("AllocationProtect",ctypes.c_ulong),("RegionSize",ctypes.c_ulong),
        ("State",ctypes.c_ulong),("Protect",ctypes.c_ulong),("Type",ctypes.c_ulong)]

def is_exec(p):
    return bool(p & 0xF0)   # 0x20/0x40/0x80 都是可执行保护

def SetBP(hthread, va):
    ctx=CONTEXT(); ctx.ContextFlags=CONTEXT_DEBUG_REGISTERS
    kernel32.GetThreadContext(hthread,ctypes.byref(ctx))
    ctx.Dr0=va; ctx.Dr7=0x1; ctx.Dr6=0
    kernel32.SetThreadContext(hthread,ctypes.byref(ctx))

def ClearHW(hthread):
    ctx=CONTEXT(); ctx.ContextFlags=CONTEXT_DEBUG_REGISTERS
    kernel32.GetThreadContext(hthread,ctypes.byref(ctx))
    ctx.Dr7=0; ctx.Dr0=0
    kernel32.SetThreadContext(hthread,ctypes.byref(ctx))

def HideDebugger(hproc):
    class PBI(ctypes.Structure):
        _fields_=[("ExitStatus",ctypes.c_long),("PebBaseAddress",ctypes.c_void_p),
            ("AffinityMask",ctypes.c_void_p),("BasePriority",ctypes.c_long),
            ("UniqueProcessId",ctypes.c_void_p),("InheritedFrom",ctypes.c_void_p)]
    p=PBI(); r=ctypes.c_ulong()
    ntdll.NtQueryInformationProcess(hproc,0,ctypes.byref(p),ctypes.sizeof(p),ctypes.byref(r))
    if p.PebBaseAddress:
        z=ctypes.c_char(b'\x00'); w=ctypes.c_ulong()
        kernel32.WriteProcessMemory(hproc,ctypes.c_void_p(p.PebBaseAddress+2),ctypes.byref(z),1,ctypes.byref(w))
    v=ctypes.c_ulong(0); ntdll.NtSetInformationProcess(hproc,7,ctypes.byref(v),4)
    v2=ctypes.c_ulong(1); ntdll.NtSetInformationProcess(hproc,0x1f,ctypes.byref(v2),4)

def guard_pages(hproc):
    """给 [GUARD_MIN, REAL_CODE_MAX) 内所有已提交可执行页打 PAGE_GUARD，返回已打页数。"""
    mbi=MEMORY_BASIC_INFORMATION(); n=0; addr=GUARD_MIN
    while addr < REAL_CODE_MAX:
        if not kernel32.VirtualQueryEx(hproc,ctypes.c_void_p(addr),ctypes.byref(mbi),ctypes.sizeof(mbi)):
            break
        base=ctypes.cast(mbi.BaseAddress,ctypes.c_void_p).value
        size=mbi.RegionSize
        end=base+size
        if mbi.State==MEM_COMMIT and is_exec(mbi.Protect):
            old=ctypes.c_ulong()
            newp=mbi.Protect|PAGE_GUARD
            if kernel32.VirtualProtectEx(hproc,ctypes.c_void_p(base),size,newp,ctypes.byref(old)):
                n+=1
        addr=end
    return n

def reguard_page(hproc, va):
    mbi=MEMORY_BASIC_INFORMATION()
    if not kernel32.VirtualQueryEx(hproc,ctypes.c_void_p(va),ctypes.byref(mbi),ctypes.sizeof(mbi)):
        return False
    base=ctypes.cast(mbi.BaseAddress,ctypes.c_void_p).value
    old=ctypes.c_ulong()
    newp=mbi.Protect|PAGE_GUARD
    return bool(kernel32.VirtualProtectEx(hproc,ctypes.c_void_p(base),mbi.RegionSize,newp,ctypes.byref(old)))

def get_eip(hthr):
    ctx=CONTEXT(); ctx.ContextFlags=CONTEXT_FULL
    kernel32.GetThreadContext(hthr,ctypes.byref(ctx))
    return ctx.Eip

def _run():
    exe=sys.argv[1]
    out=sys.argv[2] if len(sys.argv)>2 else os.path.join(os.path.dirname(os.path.abspath(__file__)),"handoff.txt")
    si=STARTUPINFO(); si.cb=ctypes.sizeof(STARTUPINFO)
    pi=PROCESS_INFORMATION()
    ok=kernel32.CreateProcessW(ctypes.c_wchar_p(exe),None,None,None,False,
        DEBUG_ONLY_THIS_PROCESS|CREATE_NEW_CONSOLE,None,None,ctypes.byref(si),ctypes.byref(pi))
    if not ok: raise RuntimeError("CreateProcessW failed %d"%kernel32.GetLastError())
    print("[*] pid=%d"%pi.dwProcessId, flush=True)
    hproc=pi.hProcess; hthr=None; handoff=None; oep_hit=False; guarded=0
    start=time.time(); datareads=0; trips=0; ev=DEBUG_EVENT()
    while True:
        if time.time()-start>1800:
            print("[!] global timeout", flush=True); break
        if not kernel32.WaitForDebugEvent(ctypes.byref(ev),500): continue
        code=ev.dwDebugEventCode
        if code==CREATE_PROCESS:
            hthr=ctypes.cast(ctypes.addressof(ev)+ev.CP_HTHREAD,ctypes.POINTER(ctypes.c_void_p)).contents.value
            HideDebugger(hproc)
            try: SetBP(hthr,OEP_VA)
            except Exception as e: print("[!] SetBP",e,flush=True)
            print("[*] OEP HW BP set @0x%X; waiting for unpacker..."%OEP_VA, flush=True)
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==CREATE_THREAD:
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==EXC:
            exc_code=ctypes.cast(ctypes.addressof(ev)+ev.EV_EXC_CODE,ctypes.POINTER(ctypes.c_ulong)).contents.value
            exc_addr=ctypes.cast(ctypes.addressof(ev)+ev.EV_EXC_ADDR,ctypes.POINTER(ctypes.c_ulong)).contents.value
            if exc_code==STATUS_SINGLE_STEP and not oep_hit:
                eip=get_eip(hthr)
                if eip==OEP_VA:
                    oep_hit=True
                    print("[*] >>> OEP hit @0x%X; unpacking done, guarding real-code pages..."%OEP_VA, flush=True)
                    guarded=guard_pages(hproc)
                    print("[*] guarded %d executable pages in [0x%X,0x%X); running free..."%(guarded,GUARD_MIN,REAL_CODE_MAX), flush=True)
                    ClearHW(hthr)
                    kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
                    continue
                else:
                    # 其它单步（理论上不应有，因为我们没开 TF）——放行
                    kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
            elif exc_code==STATUS_GUARD_PAGE_VIOLATION and oep_hit:
                trips+=1
                eip=get_eip(hthr)
                if eip < REAL_CODE_MAX:
                    handoff=eip
                    print("[*] >>> HANDOFF: first low-region fetch at 0x%X (trip#%d)"%(eip,trips), flush=True)
                    break
                else:
                    datareads+=1
                    reguard_page(hproc, exc_addr)
                    if datareads % 5000 == 0:
                        print("[.] datareads=%d trips=%d (VM reading low pages...)"%(datareads,trips), flush=True)
                    kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
            else:
                kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==EXIT_PROCESS:
            print("[!] process exited (code 0x%X) before handoff"%ctypes.cast(ctypes.addressof(ev)+12,ctypes.POINTER(ctypes.c_ulong)).contents.value, flush=True)
            break
        else:
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
    if handoff is not None:
        with open(out,"w") as f:
            f.write("HANDOFF_TARGET=0x%X\n"%handoff)
            f.write("dataread_trips=%d total_trips=%d guarded_pages=%d\n"%(datareads,trips,guarded))
            f.write("oep=0x%X real_code_max=0x%X\n"%(OEP_VA,REAL_CODE_MAX))
        print("[*] wrote handoff target -> %s"%out, flush=True)
    else:
        print("[!] no handoff found (oep_hit=%s guarded=%d datareads=%d trips=%d)"%(oep_hit,guarded,datareads,trips), flush=True)
    try: kernel32.TerminateProcess(hproc,0)
    except: pass
    kernel32.CloseHandle(hproc); kernel32.CloseHandle(pi.hThread)

if __name__=="__main__":
    _run()
