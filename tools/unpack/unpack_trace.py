# -*- coding: utf-8 -*-
"""从 OEP 起 TF 单步追踪 mx.exe，定位 VM -> 真实入口的交接。

原理：
  - 真实引擎代码在低地址段（.text/.rdata/.data/_dyprot 全部 VA < 0xB00000）；
  - VM 代码全在高地址段（>= 0xC50000）。
  - 从 OEP 单步，记录每条 EIP（去重计数）；一旦 EIP 落入 < 0xB00000
    即判定 VM 已把控制交还给真实代码（CRT 启动 / DllMain 真正入口），
    记录该交接目标并停止。
  - 同时把 VM 执行过的地址集合落盘，供后续刻画 VM 调度器/句柄使用。

用法: D:\Python315-32\python.exe unpack_trace.py <exe> [max_steps] [out_eipset]
"""
import sys, ctypes, ctypes.wintypes, time, os, struct

kernel32 = ctypes.windll.kernel32
ntdll = ctypes.windll.ntdll

DEBUG_ONLY_THIS_PROCESS = 0x00000002
CREATE_NEW_CONSOLE      = 0x00000010
CONTEXT_FULL            = 0x10007
CONTEXT_DEBUG_REGISTERS = 0x100010
PROCESS_ALL_ACCESS      = 0x1F0FFF
EXCEPTION_SINGLE_STEP   = 0x80000004
EFLAGS_TF              = 0x100

IMAGE_BASE = 0x00400000
OEP_VA     = 0x00cba0ae
REAL_CODE_MAX = 0x00B00000   # VA < 此值视为真实代码

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
    EV_EXC_CODE=12; EV_EXC_ADDR=24
    CP_HTHREAD=20
class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [("BaseAddress",ctypes.c_void_p),("AllocationBase",ctypes.c_void_p),
        ("AllocationProtect",ctypes.c_ulong),("RegionSize",ctypes.c_ulong),
        ("State",ctypes.c_ulong),("Protect",ctypes.c_ulong),("Type",ctypes.c_ulong)]

def SetBP(hthread, va):
    ctx=CONTEXT(); ctx.ContextFlags=CONTEXT_DEBUG_REGISTERS
    kernel32.GetThreadContext(hthread,ctypes.byref(ctx))
    ctx.Dr0=va; ctx.Dr7=0x1; ctx.Dr6=0
    kernel32.SetThreadContext(hthread,ctypes.byref(ctx))

def SetTF(hthread):
    ctx=CONTEXT(); ctx.ContextFlags=CONTEXT_FULL
    kernel32.GetThreadContext(hthread,ctypes.byref(ctx))
    ctx.EFlags |= EFLAGS_TF
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

def in_image(va):
    return 0x00400000 <= va < 0x00EA0000

def get_eip(hthr):
    ctx=CONTEXT(); ctx.ContextFlags=CONTEXT_FULL
    kernel32.GetThreadContext(hthr,ctypes.byref(ctx))
    return ctx.Eip, ctx.Esp

def read_ret(hproc, esp):
    buf=ctypes.create_string_buffer(4); rd=ctypes.c_ulong()
    if kernel32.ReadProcessMemory(hproc,ctypes.c_void_p(esp),buf,4,ctypes.byref(rd)):
        return struct.unpack("<I",buf[:4])[0]
    return 0

def main():
    exe=sys.argv[1]
    max_steps=int(sys.argv[2]) if len(sys.argv)>2 else 2000000
    outset=sys.argv[3] if len(sys.argv)>3 else os.path.join(os.path.dirname(os.path.abspath(__file__)),"vm_eipset.txt")
    si=STARTUPINFO(); si.cb=ctypes.sizeof(STARTUPINFO)
    pi=PROCESS_INFORMATION()
    ok=kernel32.CreateProcessW(ctypes.c_wchar_p(exe),None,None,None,False,
        DEBUG_ONLY_THIS_PROCESS|CREATE_NEW_CONSOLE,None,None,ctypes.byref(si),ctypes.byref(pi))
    if not ok: raise RuntimeError("CreateProcessW failed %d"%kernel32.GetLastError())
    print("[*] pid=%d"%pi.dwProcessId)
    HideDebugger(pi.hProcess)
    ev=DEBUG_EVENT(); start=time.time(); bp_set=False; oep_hit=False; hthr=None
    eipset={}; handoff=None; steps=0; tracing=False; skip_wait=False
    while True:
        if time.time()-start>1800:
            print("[!] global timeout"); break
        if not kernel32.WaitForDebugEvent(ctypes.byref(ev),500): continue
        code=ev.dwDebugEventCode
        if code==3:
            hthr=ctypes.cast(ctypes.addressof(ev)+ev.CP_HTHREAD,ctypes.POINTER(ctypes.c_void_p)).contents.value
            if not bp_set:
                try: SetBP(hthr,OEP_VA); bp_set=True
                except Exception as e: print("[!] SetBP",e)
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==1:
            exc_addr=ctypes.cast(ctypes.addressof(ev)+ev.EV_EXC_ADDR,ctypes.POINTER(ctypes.c_ulong)).contents.value
            if exc_addr==OEP_VA and not oep_hit:
                oep_hit=True
                print("[*] >>> OEP hit, switching to TF single-step trace")
                ClearHW(hthr)
                SetTF(hthr)
                tracing=True
                kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
                continue
            if tracing:
                eip,esp=get_eip(hthr)
                if skip_wait:
                    # 上一次在镜像外，已在返回地址下 HW BP；本次为 HW BP 命中 -> 回镜像
                    skip_wait=False
                    ClearHW(hthr)
                    if eip < REAL_CODE_MAX:
                        handoff=eip; print("[*] >>> HANDOFF(RET) to real code 0x%X steps=%d"%(eip,steps)); break
                    SetTF(hthr)
                    kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
                    continue
                # 普通 TF 单步
                if not in_image(eip):
                    # 踩进 OS 代码：在 [ESP] 返回地址下一次性 HW BP，放空跑
                    ret=read_ret(pi.hProcess, esp)
                    if ret and in_image(ret):
                        ctx=CONTEXT(); ctx.ContextFlags=CONTEXT_DEBUG_REGISTERS
                        kernel32.GetThreadContext(hthr,ctypes.byref(ctx))
                        ctx.Dr0=ret; ctx.Dr7=0x1; ctx.Dr6=0
                        kernel32.SetThreadContext(hthr,ctypes.byref(ctx))
                        skip_wait=True
                        kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
                        continue
                    else:
                        # 无法定位返回地址，继续 TF 单步（不计）
                        SetTF(hthr)
                        kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
                        continue
                eipset[eip]=eipset.get(eip,0)+1
                steps+=1
                if eip < REAL_CODE_MAX:
                    handoff=eip
                    print("[*] >>> HANDOFF to real code at 0x%X after %d steps"%(eip,steps))
                    break
                if steps>=max_steps:
                    print("[!] reached max_steps %d without handoff"%max_steps)
                    break
                SetTF(hthr)
                kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
            else:
                kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==5:
            print("[!] process exited (code 0x%X)"%ctypes.cast(ctypes.addressof(ev)+12,ctypes.POINTER(ctypes.c_ulong)).contents.value)
            break
        else:
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
    with open(outset,"w") as f:
        for a in sorted(eipset):
            f.write("0x%X %d\n"%(a,eipset[a]))
    print("[*] wrote %d unique EIPs -> %s"%(len(eipset),outset))
    if handoff is not None:
        print("[*] HANDOFF_TARGET=0x%X"%handoff)
    kernel32.TerminateProcess(pi.hProcess,0)
    kernel32.CloseHandle(pi.hProcess); kernel32.CloseHandle(pi.hThread)

if __name__=="__main__":
    main()
