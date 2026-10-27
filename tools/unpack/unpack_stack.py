# -*- coding: utf-8 -*-
"""OEP 后让进程自由跑一段时间（VM 跑完交接、真实引擎运行），然后挂起主线程回溯调用栈，
从栈底最早的一帧反推"真实入口"候选地址。比猜地址下硬件断点可靠，也比全量单步快。

用法: D:/Python315-32/python.exe unpack_stack.py <exe> [seconds] [out]
"""
import sys, ctypes, ctypes.wintypes, time, os, struct

kernel32 = ctypes.windll.kernel32
ntdll    = ctypes.windll.ntdll

DEBUG_ONLY_THIS_PROCESS = 0x00000002
CREATE_NEW_CONSOLE      = 0x00000010
CONTEXT_FULL            = 0x10007
CONTEXT_DEBUG_REGISTERS = 0x100010
EXC=1; CREATE_THREAD=2; CREATE_PROCESS=3; EXIT_PROCESS=5
STATUS_SINGLE_STEP=0x80000004
OEP_VA=0x00cba0ae

REAL_REGIONS=[(0x401000,0x6B0000),(0x7DB000,0x947000)]
VM_REGION=(0x947000,0xE42000)

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

def in_real(v):
    return any(a<=v<b for a,b in REAL_REGIONS)
def in_vm(v):
    return VM_REGION[0]<=v<VM_REGION[1]

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
    T=float(sys.argv[2]) if len(sys.argv)>2 else 15.0
    out=sys.argv[3] if len(sys.argv)>3 else os.path.join(os.path.dirname(os.path.abspath(__file__)),"stack_walk.txt")
    si=SI(); si.cb=ctypes.sizeof(SI); pi=PI()
    ok=kernel32.CreateProcessW(ctypes.c_wchar_p(exe),None,None,None,False,
        DEBUG_ONLY_THIS_PROCESS|CREATE_NEW_CONSOLE,None,None,ctypes.byref(si),ctypes.byref(pi))
    if not ok: raise RuntimeError("CreateProcessW failed %d"%kernel32.GetLastError())
    print("[*] pid=%d; free-run after OEP for %.1fs"%(pi.dwProcessId,T),flush=True)
    hp=pi.hProcess; ht=None; oep_hit=False; oep_t=None; ev=DE(); start=time.time()
    lines=[]
    while True:
        if time.time()-start>600:
            lines.append("[!] timeout"); break
        # OEP 后自由跑满 T 秒 -> 挂起主线程
        if oep_hit and oep_t is not None and (time.time()-oep_t)>=T:
            kernel32.SuspendThread(ht)
            c=CTX(); c.ContextFlags=CONTEXT_FULL
            kernel32.GetThreadContext(ht,ctypes.byref(c))
            lines.append("=== suspended @ %.1fs after OEP ==="%(time.time()-oep_t))
            lines.append("EIP=0x%X ESP=0x%X EBP=0x%X EAX=0x%X EBX=0x%X ECX=0x%X EDX=0x%X ESI=0x%X EDI=0x%X"%(
                c.Eip,c.Esp,c.Ebp,c.Eax,c.Ebx,c.Ecx,c.Edx,c.Esi,c.Edi))
            lines.append("EIP in_real=%s in_vm=%s"%(in_real(c.Eip),in_vm(c.Eip)))
            # 读栈：从 ESP 向上 256KB
            N=0x40000
            # 分 4KB 块读，容忍不可读页（ERROR_PARTIAL_COPY 299）
            data=b""
            addr=c.Esp
            read_pages=0
            for k in range(N//0x1000):
                buf=ctypes.create_string_buffer(0x1000); rd=ctypes.c_ulong()
                if kernel32.ReadProcessMemory(hp,ctypes.c_void_p(addr),buf,0x1000,ctypes.byref(rd)) and rd.value>0:
                    data += buf[:rd.value] + b"\x00"*(0x1000-rd.value)
                    read_pages+=1
                else:
                    data += b"\x00"*0x1000
                addr+=0x1000
            nread=len(data)
            if read_pages:
                hits=[]
                for i in range(0,nread-3,4):
                    v=struct.unpack("<I",data[i:i+4])[0]
                    if in_real(v) or in_vm(v):
                        hits.append((c.Esp+i, v))
                lines.append("=== stack slots pointing into image (ESP=0x%X, pages read %d, bytes 0x%X) ==="%(c.Esp,read_pages,nread))
                lines.append("total slots: %d"%len(hits))
                # 栈向下增长：地址越高 = 越早的帧
                hits.sort(key=lambda t:-t[0])
                for slot,v in hits[:80]:
                    tag="REAL" if in_real(v) else "VM"
                    lines.append("  [0x%X] = 0x%X  (%s)"%(slot,v,tag))
                # 最早(最高地址)的真实区返回地址
                earliest_real=[h for h in hits if in_real(h[1])]
                if earliest_real:
                    lines.append("")
                    lines.append("EARLIEST_REAL_FRAME=0x%X (stack slot 0x%X)"%(earliest_real[0][1],earliest_real[0][0]))
                    lines.append("DEEPEST_REAL_FRAME =0x%X (stack slot 0x%X)"%(earliest_real[-1][1],earliest_real[-1][0]))
            else:
                lines.append("[!] ReadProcessMemory failed (err %d)"%kernel32.GetLastError())
            break
        if not kernel32.WaitForDebugEvent(ctypes.byref(ev),200): continue
        code=ev.dwDebugEventCode
        if code==CREATE_PROCESS:
            ht=ctypes.cast(ctypes.addressof(ev)+ev.CP_HTHREAD,ctypes.POINTER(ctypes.c_void_p)).contents.value
            HideDbg(hp)
            c=CTX(); c.ContextFlags=CONTEXT_DEBUG_REGISTERS
            kernel32.GetThreadContext(ht,ctypes.byref(c)); c.Dr0=OEP_VA; c.Dr7=0x1; c.Dr6=0
            kernel32.SetThreadContext(ht,ctypes.byref(c))
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==CREATE_THREAD:
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==EXC:
            ec=ctypes.cast(ctypes.addressof(ev)+ev.EV_EXC_CODE,ctypes.POINTER(ctypes.c_ulong)).contents.value
            if ec==STATUS_SINGLE_STEP and not oep_hit:
                c=CTX(); c.ContextFlags=CONTEXT_FULL
                kernel32.GetThreadContext(ht,ctypes.byref(c))
                if c.Eip==OEP_VA:
                    oep_hit=True; oep_t=time.time()
                    # 清掉 OEP 断点，之后完全自由跑（不单步）
                    c2=CTX(); c2.ContextFlags=CONTEXT_DEBUG_REGISTERS
                    kernel32.GetThreadContext(ht,ctypes.byref(c2)); c2.Dr7=0; c2.Dr0=0
                    kernel32.SetThreadContext(ht,ctypes.byref(c2))
                    lines.append("[*] OEP hit @0x%X; running free..."%OEP_VA)
                    kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
                    continue
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==EXIT_PROCESS:
            lines.append("[!] process exited"); break
        else:
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
    with open(out,"w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines),flush=True)
    try: kernel32.TerminateProcess(hp,0)
    except: pass
    kernel32.CloseHandle(hp); kernel32.CloseHandle(pi.hThread)

if __name__=="__main__":
    main()
