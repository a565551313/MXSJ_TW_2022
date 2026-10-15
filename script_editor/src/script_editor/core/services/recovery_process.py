"""Bounded, cancellable subprocess transport. Never executes recovered modules."""

from __future__ import annotations

import os
import signal
import subprocess
import threading
import time
from dataclasses import dataclass


class RecoveryCancelled(ValueError):
    pass


class RecoveryProcessError(ValueError):
    def __init__(self, status):
        self.status = status
        message = (
            "恢复引擎超过时间限制；模块未执行、原包未修改"
            if status == "timeout"
            else "恢复引擎未完成：" + status
        )
        super().__init__(message)


@dataclass(frozen=True)
class ProcessOutput:
    status: str
    returncode: int
    stdout: bytes
    stderr: bytes


def run_bounded(command, *, timeout=30, cancel=None, cwd=None, limit=2 * 1024 * 1024):
    if timeout <= 0 or limit <= 0:
        raise ValueError("invalid process limits")
    if cancel is not None and cancel.is_set():
        return ProcessOutput("cancelled", -1, b"", b"")
    overflow = threading.Event()
    buffers = [bytearray(), bytearray()]
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=os.name != "nt",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )

    def drain(stream, buffer):
        try:
            while chunk := stream.read(16384):
                remaining = limit - len(buffer)
                buffer.extend(chunk[:remaining])
                if len(chunk) > remaining:
                    overflow.set()
        finally:
            stream.close()

    threads = [
        threading.Thread(target=drain, args=(stream, buffer), daemon=True)
        for stream, buffer in zip(
            (process.stdout, process.stderr), buffers, strict=True
        )
    ]
    for thread in threads:
        thread.start()
    deadline = time.monotonic() + timeout
    status = "finished"
    try:
        while process.poll() is None or any(t.is_alive() for t in threads):
            if cancel is not None and cancel.is_set():
                status = "cancelled"
                break
            if overflow.is_set():
                status = "output_limit"
                break
            if time.monotonic() >= deadline:
                status = "timeout"
                break
            time.sleep(0.02)
    finally:
        if status != "finished":
            if os.name == "nt":
                if process.poll() is None:
                    process.kill()  # Standalone Windows parsers spawn no children.
            else:
                try:
                    os.killpg(process.pid, signal.SIGKILL)  # win-ok: POSIX branch only
                except ProcessLookupError:
                    pass
        process.wait()
        for thread in threads:
            thread.join(timeout=2)
    if overflow.is_set() and status == "finished":
        status = "output_limit"
    return ProcessOutput(
        status, process.returncode, bytes(buffers[0]), bytes(buffers[1])
    )
