# -*- coding: utf-8 -*-
"""诊断：在 OEP 命中时枚举进程内存区域，弄清真实代码到底在哪、是什么保护。"""
import sys, ctypes, ctypes.wintypes, time

kernel32 = ctypes.windll.kernel32
ntdll    = ctypes.windll.ntdll

DEBUG_ONLY_THIS_PROCESS = 0x00000002
CREATE_NEW_CONSOLE      = 0x00000010
CONTEXT_FULL            = 0x10007
CONTEXT_DEBUG_REGISTERS = 0x100010
EXC=1; CREATE_THREAD=2; CREATE_PROCESS=3; EXIT_PROCESS=5
STATUS_SINGLE_STEP=0x80000004
OEP_VA=0x00cba0ae
IMAGE_BASE=0x00400000

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
class MBI(ctypes.Structure):
    _fields_=[("BaseAddress",ctypes.c_void_p),("AllocationBase",ctypes.c_void_p),("AllocationProtect",ctypes.c_ulong),
        ("RegionSize",ctypes.c_ulong),("State",ctypes.c_ulong),("Protect",ctypes.c_ulong),("Type",ctypes.c_ulong)]

PROT={0x1:"R",0x2:"RW",0x4:"RWX",0x8:"RWXC",0x10:"E",0x20:"ER",0x40:"ERW",0x80:"ERWC",
      0x100:"G",0x200:"NOCACHE",0x400:"WRITECOMBINE",0x1000:"COMMIT",0x10000:"FREE"}
def protstr(p):
    s=""
    for k in (0x80,0x40,0x20,0x10,0x8,0x4,0x2,0x1):
        if p&k: s+=PROT.get(k,"?")
    if p&0x100: s+="|G"
    return s or hex(p)

def SetBP(ht,va):
    c=CTX(); c.ContextFlags=CONTEXT_DEBUG_REGISTERS
    kernel32.GetThreadContext(ht,ctypes.byref(c)); c.Dr0=va; c.Dr7=0x1; c.Dr6=0
    kernel32.SetThreadContext(ht,ctypes.byref(c))
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

def main():
    exe=sys.argv[1]
    si=SI(); si.cb=ctypes.sizeof(SI); pi=PI()
    ok=kernel32.CreateProcessW(ctypes.c_wchar_p(exe),None,None,None,False,
        DEBUG_ONLY_THIS_PROCESS|CREATE_NEW_CONSOLE,None,None,ctypes.byref(si),ctypes.byref(pi))
    if not ok: raise RuntimeError("CreateProcessW failed %d"%kernel32.GetLastError())
    print("[*] pid=%d"%pi.dwProcessId,flush=True)
    hp=pi.hProcess; ht=None; oep=False; ev=DE(); start=time.time()
    out=[]
    while True:
        if time.time()-start>300: print("[!] timeout",flush=True); break
        if not kernel32.WaitForDebugEvent(ctypes.byref(ev),500): continue
        code=ev.dwDebugEventCode
        if code==CREATE_PROCESS:
            ht=ctypes.cast(ctypes.addressof(ev)+ev.CP_HTHREAD,ctypes.POINTER(ctypes.c_void_p)).contents.value
            HideDbg(hp); SetBP(ht,OEP_VA)
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==CREATE_THREAD:
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==EXC:
            ec=ctypes.cast(ctypes.addressof(ev)+ev.EV_EXC_CODE,ctypes.POINTER(ctypes.c_ulong)).contents.value
            if ec==STATUS_SINGLE_STEP and not oep:
                c=CTX(); c.ContextFlags=CONTEXT_FULL
                kernel32.GetThreadContext(ht,ctypes.byref(c))
                if c.Eip==OEP_VA:
                    oep=True
                    print("[*] >>> OEP hit; enumerating memory...",flush=True)
                    # 枚举整个进程空间
                    mbi=MBI(); addr=0
                    while addr < 0x80000000:
                        if not kernel32.VirtualQueryEx(hp,ctypes.c_void_p(addr),ctypes.byref(mbi),ctypes.sizeof(mbi)):
                            break
                        base=ctypes.cast(mbi.BaseAddress,ctypes.c_void_p).value
                        if base is None:
                            break
                        size=mbi.RegionSize
                        if size is None: size=0
                        end=base+size
                        if mbi.State==0x1000:  # MEM_COMMIT
                            out.append((base,size,mbi.Protect,mbi.Type))
                        addr=end
                    # 打印与镜像/低地址相关的，以及所有可执行提交页
                    print("=== committed regions intersecting [0x400000,0xC50000) ===",flush=True)
                    for b,s,p,t in out:
                        if b+s>0x400000 and b<0xC50000:
                            print("  0x%X +0x%X  prot=%s type=%d"%(b,s,protstr(p),t),flush=True)
                    print("=== ALL committed EXECUTE regions (whole process) ===",flush=True)
                    for b,s,p,t in out:
                        if p&0xF0:
                            print("  0x%X +0x%X  prot=%s"%(b,s,protstr(p)),flush=True)
                    print("=== 0x821000 probe ===",flush=True)
                    mbi2=MBI()
                    if kernel32.VirtualQueryEx(hp,ctypes.c_void_p(0x821000),ctypes.byref(mbi2),ctypes.sizeof(mbi2)):
                        print("  0x821000 base=0x%X size=0x%X prot=%s state=%d"%(ctypes.cast(mbi2.BaseAddress,ctypes.c_void_p).value,mbi2.RegionSize,protstr(mbi2.Protect),mbi2.State),flush=True)
                    else:
                        print("  0x821000 VirtualQueryEx failed",flush=True)
                    break
            else:
                kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==EXIT_PROCESS:
            print("[!] exited before OEP",flush=True); break
        else:
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
    try: kernel32.TerminateProcess(hp,0)
    except: pass
    kernel32.CloseHandle(hp); kernel32.CloseHandle(pi.hThread)

if __name__=="__main__":
    main()
