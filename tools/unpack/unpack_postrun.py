# -*- coding: utf-8 -*-
"""DuoyiProtect 转储（OEP 之后延迟转储，捕获解密后的 VM handler 与真实代码）。

流程：
  1) 拉起 mx.exe，anti-anti-debug（清 PEB.BeingDebugged、伪装调试端口）；
  2) 主线程 HW BP(DR0)=OEP，等壳解密跳到 OEP；
  3) OEP 命中后【不立即转储】，而是放行继续跑 post_delay 秒，
     让 VM 解释器解密 handler、执行保护逻辑、转入真实引擎代码；
  4) 延迟到后挂起主线程，平铺转储整个镜像 -> mx_unpacked_post.bin；
  5) 强杀。

这样 post 转储里那些 OEP 瞬间还是密文的 VM handler 区域会变成明文，
可被 IDA 静态反编译。

用法: D:\Python315-32\python.exe unpack_postrun.py <exe> [post_delay_sec] [out_bin]
"""
import sys, ctypes, ctypes.wintypes, time, os

kernel32 = ctypes.windll.kernel32
ntdll = ctypes.windll.ntdll

DEBUG_ONLY_THIS_PROCESS = 0x00000002
CREATE_NEW_CONSOLE      = 0x00000010
CONTEXT_DEBUG_REGISTERS = 0x100010
PROCESS_ALL_ACCESS      = 0x1F0FFF

EXCEPTION_SINGLE_STEP   = 0x80000004
IMAGE_BASE = 0x00400000
OEP_VA     = 0x00cba0ae

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

def SetBP(hthread):
    ctx=CONTEXT(); ctx.ContextFlags=CONTEXT_DEBUG_REGISTERS
    kernel32.GetThreadContext(hthread,ctypes.byref(ctx))
    ctx.Dr0=OEP_VA; ctx.Dr7=0x1; ctx.Dr6=0
    kernel32.SetThreadContext(hthread,ctypes.byref(ctx))
    print("[*] HW BP on OEP 0x%08x"%OEP_VA)

def HideDebugger(hproc):
    # 简化：清 BeingDebugged + 伪装端口
    pbi=ctypes.c_void_p(); 
    # 用 NtQueryInformationProcess 取 PEB
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
    print("[*] anti-anti-debug applied")

def DumpImage(hproc,outpath,imagesize):
    dump=bytearray(imagesize); addr=IMAGE_BASE; end=IMAGE_BASE+imagesize; regions=0
    while addr<end:
        mbi=MEMORY_BASIC_INFORMATION()
        if not kernel32.VirtualQueryEx(hproc,ctypes.c_void_p(addr),ctypes.byref(mbi),ctypes.sizeof(mbi)):
            break
        if mbi.State==0x1000 and (mbi.Protect&0xFF) not in (0,0x01):
            size=mbi.RegionSize; buf=ctypes.create_string_buffer(size); rd=ctypes.c_ulong()
            if kernel32.ReadProcessMemory(hproc,ctypes.c_void_p(addr),buf,size,ctypes.byref(rd)):
                off=addr-IMAGE_BASE; dump[off:off+rd.value]=buf[:rd.value]; regions+=1
            addr+=size
        else:
            addr+=mbi.RegionSize
    open(outpath,"wb").write(dump)
    print("[*] dumped %d regions -> %s (%d bytes)"%(regions,outpath,len(dump)))

def main():
    exe=sys.argv[1]; post_delay=float(sys.argv[2]) if len(sys.argv)>2 else 4.0
    outp=sys.argv[3] if len(sys.argv)>3 else os.path.join(os.path.dirname(os.path.abspath(__file__)),"mx_unpacked_post.bin")
    imagesize=int(sys.argv[4]) if len(sys.argv)>4 else 0xA60000
    si=STARTUPINFO(); si.cb=ctypes.sizeof(STARTUPINFO)
    pi=PROCESS_INFORMATION()
    ok=kernel32.CreateProcessW(ctypes.c_wchar_p(exe),None,None,None,False,
        DEBUG_ONLY_THIS_PROCESS|CREATE_NEW_CONSOLE,None,None,ctypes.byref(si),ctypes.byref(pi))
    if not ok: raise RuntimeError("CreateProcessW failed %d"%kernel32.GetLastError())
    print("[*] pid=%d"%pi.dwProcessId)
    HideDebugger(pi.hProcess)
    ev=DEBUG_EVENT(); start=time.time(); bp_set=False; oep_hit=False; hthr=None
    while True:
        if time.time()-start>post_delay+120:
            print("[!] overall timeout"); break
        if not kernel32.WaitForDebugEvent(ctypes.byref(ev),1000): continue
        code=ev.dwDebugEventCode
        if code==3:
            hthr=ctypes.cast(ctypes.addressof(ev)+ev.CP_HTHREAD,ctypes.POINTER(ctypes.c_void_p)).contents.value
            if not bp_set:
                try: SetBP(hthr); bp_set=True
                except Exception as e: print("[!] SetBP",e)
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==1:
            exc_addr=ctypes.cast(ctypes.addressof(ev)+ev.EV_EXC_ADDR,ctypes.POINTER(ctypes.c_ulong)).contents.value
            if exc_addr==OEP_VA and not oep_hit:
                oep_hit=True
                print("[*] >>> OEP hit, letting it run %s sec to decrypt VM handlers"%post_delay)
                kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
                # 等延迟
                time.sleep(post_delay)
                # 挂起主线程后转储
                if hthr: kernel32.SuspendThread(hthr)
                DumpImage(pi.hProcess,outp,imagesize)
                break
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
        elif code==5:
            print("[!] process exited before/at OEP"); break
        else:
            kernel32.ContinueDebugEvent(ev.dwProcessId,ev.dwThreadId,0x10002)
    kernel32.TerminateProcess(pi.hProcess,0)
    kernel32.CloseHandle(pi.hProcess); kernel32.CloseHandle(pi.hThread)
    print("[*] done, oep_hit=%s"%oep_hit)

if __name__=="__main__":
    main()
