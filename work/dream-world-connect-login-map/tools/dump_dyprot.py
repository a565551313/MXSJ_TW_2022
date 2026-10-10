#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dump_dyprot.py -- read-only dump of the DuoyiProtect runtime-decrypted sections.

WHY
---
mx.exe / mxmain.dll ship two sections, `_dyprot0` and `_dyprot1`, whose on-disk
bytes are encrypted/compressed (Shannon entropy 7.85 / 7.72 vs 6.64 for `.text`).
The packer decrypts them into the process image at startup.  The game-channel
cipher (C_net::SetSeed -> 0x4c54f0 init / 0x4c5590 process) is a thunk that
`jmp`s into `_dyprot0`, so its real body is ONLY recoverable from a live process.

WHAT IT DOES
------------
Attaches read-only (PROCESS_VM_READ | PROCESS_QUERY_INFORMATION) to a running
mx.exe, reads `_dyprot0` and `_dyprot1` back and writes them to disk together
with a small JSON header (image base, section RVAs/sizes).

It does NOT write to the game process, does NOT patch anything, does NOT modify
any file in the game directory, and does not touch the network.

USAGE (Windows, on the machine that has the game)
-------------------------------------------------
1. Start the game normally and get as far as the account-login page.
2.   python dump_dyprot.py
   (optionally:  python dump_dyprot.py --out D:\tmp\dyprot)
3. Commit/copy the produced files next to this script's parent dir.

Output:  dyprot0.bin, dyprot1.bin, dyprot.json   (~5.2 MB total)

Requires: Windows, CPython 3.x, standard library only.
"""

from __future__ import annotations
import argparse
import ctypes
import json
import os
import struct
import sys
from ctypes import wintypes

# Everything below is Windows-only (ctypes.WinDLL).  Bail out early so the file
# can still be imported / syntax-checked on other platforms.
if sys.platform != 'win32':
    print(__doc__)
    print('\nThis tool only runs on Windows: it attaches read-only to the live '
          'mx.exe process.\nStart the game there, get to the account-login page, '
          'then run:\n\n    python tools/dump_dyprot.py\n')
    sys.exit(2)

# ---------------------------------------------------------------- constants
# From the on-disk PE headers of mx.exe (image base 0x00400000).
DEFAULT_IMAGE_BASE = 0x00400000
SECTIONS = {
    '_dyprot0': dict(rva=0x00547000, size=0x00316800),
    '_dyprot1': dict(rva=0x0085E000, size=0x001E3E00),
}
# Rebase fixups: the packer relocates the image, so we verify the base by
# checking the PE signature + OptionalHeader.ImageBase at runtime.
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
TH32CS_SNAPPROCESS = 0x00000002
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
MAX_PATH = 260

k32 = ctypes.WinDLL('kernel32', use_last_error=True)  # type: ignore[attr-defined]


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD),
        ('cntUsage', wintypes.DWORD),
        ('th32ProcessID', wintypes.DWORD),
        ('th32DefaultHeapID', ctypes.POINTER(ctypes.c_ulong)),
        ('th32ModuleID', wintypes.DWORD),
        ('cntThreads', wintypes.DWORD),
        ('th32ParentProcessID', wintypes.DWORD),
        ('pcPriClassBase', ctypes.c_long),
        ('dwFlags', wintypes.DWORD),
        ('szExeFile', wintypes.WCHAR * MAX_PATH),
    ]


k32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
k32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
k32.Process32FirstW.restype = wintypes.BOOL
k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
k32.Process32NextW.restype = wintypes.BOOL
k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
k32.OpenProcess.restype = wintypes.HANDLE
k32.CloseHandle.argtypes = [wintypes.HANDLE]
k32.CloseHandle.restype = wintypes.BOOL
k32.ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                  ctypes.c_void_p, ctypes.c_size_t,
                                  ctypes.POINTER(ctypes.c_size_t)]
k32.ReadProcessMemory.restype = wintypes.BOOL

try:
    psapi = ctypes.WinDLL('psapi', use_last_error=True)  # type: ignore[attr-defined]
except OSError:  # pragma: no cover
    psapi = ctypes.WinDLL('kernel32', use_last_error=True)  # type: ignore[attr-defined]

try:
    psapi.EnumProcessModulesEx
except AttributeError:  # pragma: no cover
    psapi.EnumProcessModulesEx = None


# ---------------------------------------------------------------- helpers
def find_pids_by_name(name: str):
    """Return [(pid, exe_name)] for every process whose image name matches."""
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == INVALID_HANDLE_VALUE or not snap:
        raise OSError('CreateToolhelp32Snapshot failed: %d' % ctypes.get_last_error())
    out = []
    try:
        pe = PROCESSENTRY32W()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        ok = k32.Process32FirstW(snap, ctypes.byref(pe))
        while ok:
            if pe.szExeFile.lower() == name.lower():
                out.append((pe.th32ProcessID, pe.szExeFile))
            ok = k32.Process32NextW(snap, ctypes.byref(pe))
    finally:
        k32.CloseHandle(snap)
    return out


def list_modules(pid: int):
    """Return [(base, size, basename)] for the modules of `pid`."""
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h:
        raise OSError('OpenProcess(%d) failed: %d' % (pid, ctypes.get_last_error()))
    try:
        mods = (wintypes.HANDLE * 1024)()
        needed = wintypes.DWORD(0)
        buf = ctypes.create_unicode_buffer(MAX_PATH)
        if psapi.EnumProcessModulesEx:
            psapi.EnumProcessModulesEx.argtypes = [wintypes.HANDLE,
                                                   ctypes.POINTER(wintypes.HANDLE * 1024),
                                                   wintypes.DWORD,
                                                   ctypes.POINTER(wintypes.DWORD),
                                                   wintypes.DWORD]
            psapi.EnumProcessModulesEx.restype = wintypes.BOOL
            if not psapi.EnumProcessModulesEx(h, ctypes.byref(mods),
                                              ctypes.sizeof(mods),
                                              ctypes.byref(needed), 0x03):
                raise OSError('EnumProcessModulesEx failed: %d' % ctypes.get_last_error())
        else:
            psapi.EnumProcessModules.argtypes = [wintypes.HANDLE,
                                                 ctypes.POINTER(wintypes.HANDLE * 1024),
                                                 wintypes.DWORD,
                                                 ctypes.POINTER(wintypes.DWORD)]
            psapi.EnumProcessModules.restype = wintypes.BOOL
            if not psapi.EnumProcessModules(h, ctypes.byref(mods),
                                            ctypes.sizeof(mods),
                                            ctypes.byref(needed)):
                raise OSError('EnumProcessModules failed: %d' % ctypes.get_last_error())
        psapi.GetModuleBaseNameW.argtypes = [wintypes.HANDLE, wintypes.HMODULE,
                                             ctypes.c_void_p, wintypes.DWORD]
        psapi.GetModuleBaseNameW.restype = wintypes.DWORD
        psapi.GetModuleInformation.argtypes = [wintypes.HANDLE, wintypes.HMODULE,
                                               ctypes.c_void_p, wintypes.DWORD]
        psapi.GetModuleInformation.restype = wintypes.BOOL

        n = min(needed.value // ctypes.sizeof(wintypes.HANDLE), 1024)
        res = []
        for i in range(n):
            base = mods[i]
            if not base:
                continue
            psapi.GetModuleBaseNameW(h, base, buf, MAX_PATH)
            mi = (ctypes.c_ulonglong * 3)()  # MODULEINFO{lpBase,SizeOfImage,EntryPoint}
            psapi.GetModuleInformation(h, base, ctypes.byref(mi), ctypes.sizeof(mi))
            res.append((int(base) if base else 0, int(mi[1]), buf.value))
        return res
    finally:
        k32.CloseHandle(h)


def read_mem(pid: int, addr: int, size: int, chunk: int = 0x10000) -> bytes:
    h = k32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    if not h:
        raise OSError('OpenProcess(%d) failed: %d' % (pid, ctypes.get_last_error()))
    out = bytearray()
    try:
        buf = ctypes.create_string_buffer(chunk)
        got = ctypes.c_size_t(0)
        pos = addr
        end = addr + size
        while pos < end:
            n = min(chunk, end - pos)
            if not k32.ReadProcessMemory(h, ctypes.c_void_p(pos), buf, n,
                                         ctypes.byref(got)):
                raise OSError('ReadProcessMemory at 0x%08x failed: %d'
                              % (pos, ctypes.get_last_error()))
            out += buf.raw[:got.value]
            if got.value == 0:
                raise OSError('short read at 0x%08x (page not resident)' % pos)
            pos += got.value
    finally:
        k32.CloseHandle(h)
    return bytes(out)


def verify_pe(pid: int, base: int) -> int:
    """Confirm `base` really holds the mx.exe image; return SizeOfImage."""
    hdr = read_mem(pid, base, 0x400)
    if hdr[:2] != b'MZ':
        raise OSError('no MZ at 0x%08x -- wrong module base?' % base)
    e_lfanew = struct.unpack_from('<I', hdr, 0x3C)[0]
    if hdr[e_lfanew:e_lfanew + 4] != b'PE\x00\x00':
        raise OSError('no PE signature at 0x%08x' % (base + e_lfanew))
    size_of_image = struct.unpack_from('<I', hdr, e_lfanew + 0x50)[0]
    return int(size_of_image)


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--process', default='mx.exe', help='image name of the game')
    ap.add_argument('--pid', type=int, default=0, help='use this pid directly')
    ap.add_argument('--out', default=None,
                    help='output directory (default: <repo>/work/dream-world-connect-login-map/evidence)')
    args = ap.parse_args()

    if sys.platform != 'win32':
        print('This tool only runs on Windows (it attaches to the live game process).')
        return 2

    if args.pid:
        pid = args.pid
    else:
        cands = find_pids_by_name(args.process)
        if not cands:
            print('No running process named %r.' % args.process)
            print('Start the game first and get to the account-login page, then retry.')
            return 1
        pid = cands[0][0]
        print('found %s -> pid %d' % (args.process, pid))

    mods = list_modules(pid)
    if not mods:
        raise OSError('cannot enumerate modules of pid %d' % pid)
    main_mod = mods[0]
    base, size_of_image, modname = main_mod
    print('main module: %s base=0x%08x size=0x%08x' % (modname, base, size_of_image))

    got = verify_pe(pid, base)
    print('PE header OK (SizeOfImage=0x%x)' % got)

    outdir = args.out or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'evidence')
    os.makedirs(outdir, exist_ok=True)

    meta = dict(process=args.process, pid=pid, image_base=base,
                size_of_image=size_of_image, main_module=modname,
                sections={})
    for name, info in SECTIONS.items():
        addr = base + info['rva']
        print('reading %-9s 0x%08x .. 0x%08x (%d bytes)'
              % (name, addr, addr + info['size'], info['size']))
        data = read_mem(pid, addr, info['size'])
        path = os.path.join(outdir, '%s.bin' % name.strip('_'))
        with open(path, 'wb') as f:
            f.write(data)
        print('  -> %s (%d bytes)' % (path, len(data)))
        meta['sections'][name] = dict(rva=info['rva'], size=info['size'],
                                      va=addr, file=os.path.basename(path),
                                      sha256=__import__('hashlib').sha256(data).hexdigest())

    jpath = os.path.join(outdir, 'dyprot.json')
    with open(jpath, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)
    print('wrote %s' % jpath)
    print('\nDone. Copy these three files back into the workspace.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
