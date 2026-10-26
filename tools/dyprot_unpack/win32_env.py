#!/usr/bin/env python3
"""模擬器裡那份「夠殼用的 Windows」：常數、API 樁、參數個數表。

`install_api(rt)` 只要求傳進來的物件有 `uc`（Unicorn）、`alloc()`、`read_str()`、
`procs`、`exports`，不直接依賴 `dyprot_emulate.Runtime`（避免循環匯入）。

殼是拿名字去假 DLL 的匯出表裡查 API 的，所以「匯出名字清單」和「真的會執行
的 Python 實作」必須對得上：`EXTRA_EXPORTS` 決定匯出表裡有哪些名字，
`install_api()` 決定其中哪些有語意、其餘按 `ARG_COUNTS` 正確清棧後回 0。

限度：只做記憶體、模組、時間、TLS、臨界區這些殼會碰到的東西；沒有檔案系統、
沒有視窗訊息循環、沒有執行緒排程。行為對不上時寧可回 0 並記錄，也不要假裝。
"""

from __future__ import annotations

import struct
import time

BASE = 0x400000
STACK = 0x20000000
STACK_SIZE = 0x400000
HEAP = 0x28000000
HEAP_SIZE = 0x1000000
STUB = 0x60000000
STUB_SIZE = 0x40000
PEB = 0x8000
SENTINEL = 0xFFFFFFFF
MODULE_BASE = {
    "kernel32.dll": 0x50000000,
    "ntdll.dll": 0x51000000,
    "user32.dll": 0x52000000,
    "advapi32.dll": 0x53000000,
}


class ProcessExit(Exception):
    """殼自己叫了 `ExitProcess`：不是我們的錯，記下來就好。"""

    def __init__(self, code: int):
        super().__init__(f"ExitProcess({code})")
        self.code = code


def stdcall(count: int):
    """標記樁的 stdcall 參數個數（被調方清棧）。"""

    def decorate(fn):
        fn.argc = count
        return fn

    return decorate


EXTRA_EXPORTS = """
VirtualAlloc VirtualFree VirtualProtect VirtualQuery VirtualLock VirtualUnlock
GetModuleHandleA GetModuleHandleW LoadLibraryA LoadLibraryW LoadLibraryExA
GetProcAddress FreeLibrary GetModuleFileNameA GetModuleFileNameW
IsDebuggerPresent CheckRemoteDebuggerPresent GetTickCount QueryPerformanceCounter
QueryPerformanceFrequency GetSystemInfo GetNativeSystemInfo GetVersion GetVersionExA
GetVersionExW GetCurrentProcess GetCurrentThread GetCurrentThreadId
GetCurrentProcessId GetLastError SetLastError CloseHandle CreateFileA CreateFileW
ReadFile WriteFile SetFilePointer GetFileSize GetFileAttributesA LocalAlloc LocalFree
GlobalAlloc GlobalFree HeapAlloc HeapFree HeapReAlloc HeapSize GetProcessHeap
HeapCreate HeapDestroy Sleep TerminateProcess ExitProcess CreateThread
WaitForSingleObject GetSystemTimeAsFileTime GetLocalTime GetSystemTime
InitializeCriticalSection EnterCriticalSection LeaveCriticalSection
DeleteCriticalSection InterlockedIncrement InterlockedDecrement InterlockedExchange
InterlockedCompareExchange TlsAlloc TlsGetValue TlsSetValue TlsFree EncodePointer
DecodePointer GetCommandLineA GetCommandLineW GetEnvironmentStringsW
FreeEnvironmentStringsW WideCharToMultiByte MultiByteToWideChar lstrlenA lstrlenW
GetSystemDirectoryA GetWindowsDirectoryA GetTempPathA OutputDebugStringA
OutputDebugStringW SetUnhandledExceptionFilter UnhandledExceptionFilter
FlushInstructionCache GetThreadContext SetThreadContext ResumeThread SuspendThread
GetProcessWindowStation GetThreadDesktop GetUserObjectInformationA
GetUserObjectInformationW SetProcessWindowStation SetThreadDesktop
GetUserDefaultLCID GetSystemDefaultLCID GetLocaleInfoA GetTimeZoneInformation
RtlUnwind RaiseException RtlCaptureContext RtlLookupFunctionEntry RtlVirtualUnwind
NtQueryInformationProcess NtSetInformationThread NtQuerySystemInformation NtClose
QueryFullProcessImageNameW GetUserDefaultUILanguage GetSystemDefaultUILanguage
GetStartupInfoA GetStartupInfoW GetStdHandle SetHandleInformation LoadLibraryExW
SetErrorMode SetConsoleCtrlHandler CreateEventA SetEvent WaitForMultipleObjects
ReleaseMutex CreateMutexA SwitchToThread GetSystemDefaultLangID GetUserDefaultLangID
GetACP GetOEMCP GetCPInfo IsValidCodePage GetStringTypeW GetStringTypeA
CharUpperA CharUpperW CharLowerA CharLowerW GetModuleHandleExA GetModuleHandleExW
FindResourceA LoadResource LockResource SizeofResource FindResourceW
""".split()

# 未實作函式也必須知道參數個數（stdcall 由被調方清棧），否則棧會歪。
ARG_COUNTS = {
    "FreeLibrary": 1,
    "GetProcAddress": 2,
    "VirtualFree": 3,
    "VirtualLock": 2,
    "VirtualUnlock": 2,
    "CloseHandle": 1,
    "CreateFileW": 7,
    "WriteFile": 5,
    "SetFilePointer": 4,
    "GetFileSize": 2,
    "GetFileAttributesA": 1,
    "LocalFree": 1,
    "GlobalFree": 1,
    "HeapReAlloc": 4,
    "HeapSize": 3,
    "HeapDestroy": 1,
    "TerminateProcess": 2,
    "ExitProcess": 1,
    "CreateThread": 6,
    "WaitForSingleObject": 2,
    "GetSystemTime": 1,
    "InterlockedCompareExchange": 3,
    "GetThreadContext": 2,
    "SetThreadContext": 2,
    "ResumeThread": 1,
    "SuspendThread": 1,
    "GetUserObjectInformationA": 5,
    "GetUserObjectInformationW": 5,
    "GetLocaleInfoA": 4,
    "GetTimeZoneInformation": 1,
    "RaiseException": 4,
    "RtlUnwind": 4,
    "NtQueryInformationProcess": 5,
    "NtSetInformationThread": 4,
    "NtQuerySystemInformation": 4,
    "NtClose": 1,
    "QueryFullProcessImageNameW": 4,
    "GetStartupInfoA": 1,
    "GetStartupInfoW": 1,
    "GetStdHandle": 1,
    "SetHandleInformation": 3,
    "LoadLibraryExW": 3,
    "SetErrorMode": 1,
    "SetConsoleCtrlHandler": 2,
    "CreateEventA": 4,
    "SetEvent": 1,
    "WaitForMultipleObjects": 4,
    "ReleaseMutex": 1,
    "CreateMutexA": 3,
    "GetSystemDefaultLangID": 0,
    "GetUserDefaultLangID": 0,
    "GetACP": 0,
    "GetOEMCP": 0,
    "GetCPInfo": 2,
    "IsValidCodePage": 1,
    "GetStringTypeW": 4,
    "GetStringTypeA": 5,
    "CharUpperA": 1,
    "CharUpperW": 1,
    "CharLowerA": 1,
    "CharLowerW": 1,
    "GetModuleHandleExA": 3,
    "GetModuleHandleExW": 3,
    "FindResourceA": 3,
    "FindResourceW": 3,
    "LoadResource": 2,
    "LockResource": 1,
    "SizeofResource": 3,
    "EnumSystemLocalesA": 2,
    "GetVersionExW": 1,
    "WideCharToMultiByte": 8,
    "MultiByteToWideChar": 6,
    "lstrlenA": 1,
    "lstrlenW": 1,
    "OutputDebugStringA": 1,
    "OutputDebugStringW": 1,
    "SetUnhandledExceptionFilter": 1,
    "UnhandledExceptionFilter": 1,
    "RtlCaptureContext": 1,
    "RtlLookupFunctionEntry": 3,
    "RtlVirtualUnwind": 6,
    "GetUserDefaultUILanguage": 0,
    "GetSystemDefaultUILanguage": 0,
}


def install_api(rt) -> None:
    """把可用的 Win32 語意接到 `rt`（記憶體配置、模組、版本、時鐘、TLS…）。"""

    @stdcall(2)
    def LocalAlloc(flags, size):
        return rt.alloc(size)

    @stdcall(2)
    def GlobalAlloc(flags, size):
        return rt.alloc(size)

    @stdcall(3)
    def HeapAlloc(heap, flags, size):
        return rt.alloc(size)

    @stdcall(4)
    def VirtualAlloc(addr, size, kind, prot):
        return addr or rt.alloc(size, 0x1000)

    @stdcall(4)
    def VirtualProtect(addr, size, new, old):
        rt.uc.mem_write(old, struct.pack("<I", 0x40))
        return 1

    @stdcall(3)
    def VirtualQuery(addr, buf, size):
        rt.uc.mem_write(
            buf,
            struct.pack(
                "<IIIIIII", BASE, BASE, 0x1000, 0x1000, 0x2000, 0x04, 0x1000000
            ),
        )
        return 28

    @stdcall(4)
    def VirtualQueryEx(handle, addr, buf, size):
        return VirtualQuery(addr, buf, size)

    @stdcall(1)
    def GetModuleHandleA(name):
        if not name:
            return BASE
        text = rt.read_str(name).lower()
        if "mxmain" in text or "mx.exe" in text:
            return BASE
        return rt.module_base(text)

    @stdcall(1)
    def GetModuleHandleW(name):
        if not name:
            return BASE
        text = rt.read_str(name, True).lower()
        if "mxmain" in text or "mx.exe" in text:
            return BASE
        return rt.module_base(text)

    @stdcall(1)
    def LoadLibraryA(name):
        return rt.module_base(rt.read_str(name).lower() or "unknown.dll")

    @stdcall(1)
    def LoadLibraryW(name):
        return rt.module_base(rt.read_str(name, True).lower() or "unknown.dll")

    @stdcall(2)
    def GetProcAddress(handle, name):
        if name and name < 0x10000:  # 序數匯出，這裡只回通用樁
            return rt.generic
        resolved = rt.exports.get(rt.read_str(name))
        return resolved if resolved is not None else rt.generic

    @stdcall(3)
    def GetModuleFileNameA(handle, buf, size):
        text = b"C:\\game\\mxmain.dll\x00"
        rt.uc.mem_write(buf, text[:size])
        return min(len(text) - 1, size)

    @stdcall(3)
    def GetModuleFileNameW(handle, buf, size):
        text = "C:\\game\\mxmain.dll".encode("utf-16-le") + b"\x00\x00"
        rt.uc.mem_write(buf, text[: size * 2])
        return min(len(text) // 2 - 1, size)

    @stdcall(0)
    def GetProcessHeap():
        return HEAP

    @stdcall(3)
    def HeapCreate(flags, initial, maximum):
        return HEAP

    @stdcall(0)
    def IsDebuggerPresent():
        return 0

    @stdcall(2)
    def CheckRemoteDebuggerPresent(handle, out):
        rt.uc.mem_write(out, struct.pack("<I", 0))
        return 1

    @stdcall(0)
    def GetTickCount():
        return int(time.time() * 1000) & 0x7FFFFFFF

    @stdcall(1)
    def QueryPerformanceCounter(out):
        rt.uc.mem_write(out, struct.pack("<Q", int(time.time() * 1e6)))
        return 1

    @stdcall(1)
    def QueryPerformanceFrequency(out):
        rt.uc.mem_write(out, struct.pack("<Q", 1000000))
        return 1

    @stdcall(1)
    def GetSystemInfo(out):
        rt.uc.mem_write(
            out,
            struct.pack(
                "<IIIIIIIII", 0, 0x1000, 0x10000, 0x7FFFFFFF, 1, 0, 0, 0, 0
            ),
        )
        return 0

    @stdcall(1)
    def GetNativeSystemInfo(out):
        return GetSystemInfo(out)

    @stdcall(0)
    def GetVersion():
        return 0x0A280105

    @stdcall(1)
    def GetVersionExA(out):
        rt.uc.mem_write(out, struct.pack("<IIII", 0x114, 6, 1, 7601))
        return 1

    @stdcall(1)
    def GetVersionExW(out):
        return GetVersionExA(out)

    @stdcall(0)
    def GetCurrentProcess():
        return 0xFFFFFFFF

    @stdcall(0)
    def GetCurrentThread():
        return 0xFFFFFFFE

    @stdcall(0)
    def GetCurrentThreadId():
        return 0x1234

    @stdcall(0)
    def GetCurrentProcessId():
        return 0x1234

    @stdcall(1)
    def SetLastError(code):
        return 0

    @stdcall(0)
    def GetLastError():
        return 0

    @stdcall(1)
    def Sleep(ms):
        return 0

    @stdcall(1)
    def EncodePointer(ptr):
        return ptr

    @stdcall(1)
    def DecodePointer(ptr):
        return ptr

    @stdcall(3)
    def FlushInstructionCache(handle, addr, size):
        return 1

    @stdcall(1)
    def InitializeCriticalSection(addr):
        rt.uc.mem_write(addr, b"\x00" * 24)
        return 0

    @stdcall(1)
    def EnterCriticalSection(addr):
        return 0

    @stdcall(1)
    def LeaveCriticalSection(addr):
        return 0

    @stdcall(1)
    def DeleteCriticalSection(addr):
        return 0

    @stdcall(0)
    def TlsAlloc():
        return 1

    @stdcall(1)
    def TlsGetValue(index):
        return 0

    @stdcall(2)
    def TlsSetValue(index, value):
        return 1

    @stdcall(1)
    def TlsFree(index):
        return 1

    @stdcall(1)
    def InterlockedIncrement(addr):
        value = struct.unpack("<I", rt.uc.mem_read(addr, 4))[0] + 1
        rt.uc.mem_write(addr, struct.pack("<I", value))
        return value

    @stdcall(1)
    def InterlockedDecrement(addr):
        value = struct.unpack("<I", rt.uc.mem_read(addr, 4))[0] - 1
        rt.uc.mem_write(addr, struct.pack("<I", value))
        return value

    @stdcall(2)
    def InterlockedExchange(addr, value):
        old = struct.unpack("<I", rt.uc.mem_read(addr, 4))[0]
        rt.uc.mem_write(addr, struct.pack("<I", value))
        return old

    @stdcall(1)
    def GetSystemTimeAsFileTime(out):
        rt.uc.mem_write(out, struct.pack("<Q", 0x01D6A00000000000))
        return 0

    @stdcall(1)
    def GetLocalTime(out):
        rt.uc.mem_write(out, struct.pack("<8H", 2026, 10, 26, 3, 12, 0, 0, 0))
        return 0

    @stdcall(1)
    def OutputDebugStringA(text):
        return 0

    @stdcall(1)
    def OutputDebugStringW(text):
        return 0

    @stdcall(1)
    def FreeLibrary(handle):
        return 1

    @stdcall(0)
    def GetProcessWindowStation():
        return 0x700

    @stdcall(1)
    def GetThreadDesktop(thread):
        return 0x704

    @stdcall(5)
    def GetUserObjectInformationW(handle, index, buf, size, needed):
        if needed:
            rt.uc.mem_write(needed, struct.pack("<I", 8))
        return 1

    @stdcall(1)
    def ExitProcess(code):
        raise ProcessExit(code)

    @stdcall(5)
    def GetUserObjectInformationA(handle, index, buf, size, needed):
        if needed:
            rt.uc.mem_write(needed, struct.pack("<I", 8))
        return 1

    @stdcall(1)
    def SetProcessWindowStation(handle):
        return 1

    @stdcall(1)
    def SetThreadDesktop(handle):
        return 1

    @stdcall(0)
    def GetUserDefaultLCID():
        return 0x804

    @stdcall(0)
    def GetSystemDefaultLCID():
        return 0x804

    @stdcall(4)
    def GetLocaleInfoA(lcid, kind, buf, size):
        text = b"zh-CN\x00"
        rt.uc.mem_write(buf, text[:size])
        return min(len(text) - 1, size)

    @stdcall(1)
    def GetTimeZoneInformation(out):
        rt.uc.mem_write(out, b"\x00" * 172)
        return 1

    @stdcall(2)
    def GetSystemDirectoryA(buf, size):
        text = b"C:\\Windows\\system32\x00"
        rt.uc.mem_write(buf, text[:size])
        return min(len(text) - 1, size)

    @stdcall(2)
    def GetWindowsDirectoryA(buf, size):
        text = b"C:\\Windows\x00"
        rt.uc.mem_write(buf, text[:size])
        return min(len(text) - 1, size)

    @stdcall(2)
    def GetTempPathA(size, buf):
        text = b"C:\\Temp\\\x00"
        rt.uc.mem_write(buf, text[:size])
        return min(len(text) - 1, size)

    for fn in (
        LocalAlloc, GlobalAlloc, HeapAlloc, VirtualAlloc, VirtualProtect,
        VirtualQuery, VirtualQueryEx, GetModuleHandleA, GetModuleHandleW,
        LoadLibraryA, LoadLibraryW, GetProcAddress, GetModuleFileNameA,
        GetModuleFileNameW, GetProcessHeap, HeapCreate, IsDebuggerPresent,
        CheckRemoteDebuggerPresent, GetTickCount, QueryPerformanceCounter,
        QueryPerformanceFrequency, GetSystemInfo, GetNativeSystemInfo, GetVersion,
        GetVersionExA, GetVersionExW, GetCurrentProcess,
        GetCurrentThread, GetCurrentThreadId, GetCurrentProcessId,
        SetLastError, GetLastError,
        Sleep, EncodePointer, DecodePointer, FlushInstructionCache,
        InitializeCriticalSection, EnterCriticalSection, LeaveCriticalSection,
        DeleteCriticalSection, TlsAlloc, TlsGetValue, TlsSetValue, TlsFree,
        InterlockedIncrement, InterlockedDecrement, InterlockedExchange,
        GetSystemTimeAsFileTime, GetLocalTime,
        OutputDebugStringA, OutputDebugStringW,
        FreeLibrary, GetProcessWindowStation, GetThreadDesktop,
        GetUserObjectInformationA, GetUserObjectInformationW, ExitProcess,
        SetProcessWindowStation, SetThreadDesktop,
        GetUserDefaultLCID, GetSystemDefaultLCID,
        GetLocaleInfoA, GetTimeZoneInformation, GetSystemDirectoryA,
        GetWindowsDirectoryA,
        GetTempPathA,
    ):
        rt.procs[fn.__name__] = fn
