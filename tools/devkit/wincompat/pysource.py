"""Python 源码检查：基于 ``ast``，只读不执行。

覆盖的是“在 Linux 上写完、拿到 Windows 上才炸”的高频点：

* 文本文件读写没写 ``encoding``（Windows 默认 GBK，中文 JSON/CSV 直接
  ``UnicodeDecodeError``）；
* ``fcntl``/``os.killpg``/``signal.SIGKILL`` 这类 POSIX 专用 API；
* 硬编码 ``/tmp``、``/home`` 路径；
* 用字面量 ``python3`` 启动子进程（Windows 上通常只有 ``python`` / ``py``）；
* 约定项：GUI 框架必须是 PySide6。

启发式说明：``read_text``/``write_text`` 只按方法名匹配（不做类型推断），
同名的自定义方法会误报——在该行加 ``# win-ok`` 即可豁免。
"""

from __future__ import annotations

import ast
import re

from wincompat.model import SUPPRESS_MARKER, Finding, Severity, make_finding

POSIX_ONLY_MODULES = frozenset(
    {
        "fcntl",
        "pwd",
        "grp",
        "termios",
        "tty",
        "pty",
        "posix",
        "curses",
        "resource",
        "syslog",
        "readline",
    }
)
POSIX_ONLY_OS_ATTRS = frozenset(
    {
        "fork",
        "forkpty",
        "killpg",
        "getpgid",
        "getpgrp",
        "setsid",
        "setpgid",
        "setpgrp",
        "getuid",
        "geteuid",
        "getgid",
        "getegid",
        "setuid",
        "setgid",
        "getgroups",
        "chown",
        "lchown",
        "fchown",
        "chroot",
        "mkfifo",
        "mknod",
        "statvfs",
        "sync",
        "getloadavg",
        "nice",
        "openpty",
        "wait",
        "wait3",
        "wait4",
        "WNOHANG",
    }
)
POSIX_ONLY_SIGNAL_ATTRS = frozenset(
    {
        "SIGKILL",
        "SIGHUP",
        "SIGUSR1",
        "SIGUSR2",
        "SIGALRM",
        "SIGCHLD",
        "SIGQUIT",
        "SIGPIPE",
        "SIGSTOP",
        "SIGCONT",
        "SIGTSTP",
        "SIGWINCH",
        "SIGBUS",
        "alarm",
        "pause",
        "setitimer",
        "pthread_kill",
        "pthread_sigmask",
    }
)
GUI_MODULES = {
    "tkinter": "tkinter",
    "Tkinter": "tkinter",
    "PyQt4": "PyQt4",
    "PyQt5": "PyQt5",
    "PyQt6": "PyQt6",
    "wx": "wxPython",
    "gi": "GTK/PyGObject",
    "kivy": "Kivy",
    "dearpygui": "DearPyGui",
    "toga": "Toga",
}
SUBPROCESS_FUNCS = frozenset({"run", "Popen", "call", "check_call", "check_output"})
OS_SHELL_FUNCS = frozenset({"system", "popen"})
IMPORT_ERROR_NAMES = frozenset(
    {"ImportError", "ModuleNotFoundError", "Exception", "BaseException"}
)

POSIX_PATH_RE = re.compile(r"^/(tmp|home|usr|var|opt|etc|root|mnt|dev|proc|srv)(/|$)")
PYTHON_LITERAL_RE = re.compile(r"^python(3(\.\d+)?)?(\.exe)?$")
PLATFORM_GUARD_RE = re.compile(r"sys\.platform|os\.name|platform\.system\(")


def _import_error_lines(tree: ast.AST) -> set[int]:
    """收集位于 ``try: ... except ImportError`` 主体内的行号。"""
    lines: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        guarded = False
        for handler in node.handlers:
            if handler.type is None:
                guarded = True
                break
            names = [
                n.id if isinstance(n, ast.Name) else getattr(n, "attr", "")
                for n in (
                    handler.type.elts
                    if isinstance(handler.type, ast.Tuple)
                    else [handler.type]
                )
            ]
            if any(name in IMPORT_ERROR_NAMES for name in names):
                guarded = True
                break
        if guarded and node.body:
            first = node.body[0].lineno
            last = node.body[-1].end_lineno or first
            lines.update(range(first, last + 1))
    return lines


def _docstring_ids(tree: ast.AST) -> set[int]:
    ids: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(
            node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
        ):
            continue
        body = node.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            ids.add(id(body[0].value))
    return ids


def _first_command_token(node: ast.AST | None) -> str | None:
    """从子进程调用的第一个参数里取出命令名（字面量时）。"""
    if isinstance(node, ast.List | ast.Tuple) and node.elts:
        node = node.elts[0]
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        tokens = node.value.strip().split()
        return tokens[0] if tokens else None
    return None


def _mode_is_text(call: ast.Call, mode_index: int) -> bool | None:
    """返回 open() 的模式是否为文本：True/False；模式不是字面量时返回 None。

    ``mode_index`` 是 mode 的位置参数下标：内置 ``open(file, mode)`` 为 1，
    ``Path(...).open(mode)`` 为 0。
    """
    mode_node: ast.AST | None = None
    if len(call.args) > mode_index:
        mode_node = call.args[mode_index]
    for keyword in call.keywords:
        if keyword.arg == "mode":
            mode_node = keyword.value
    if mode_node is None:
        return True
    if isinstance(mode_node, ast.Constant) and isinstance(mode_node.value, str):
        return "b" not in mode_node.value
    return None


def _has_keyword(call: ast.Call, name: str) -> bool:
    return any(keyword.arg == name for keyword in call.keywords)


class _Visitor(ast.NodeVisitor):
    def __init__(self, rel: str, tree: ast.AST, source: str) -> None:
        self.rel = rel
        self.findings: list[Finding] = []
        self.guarded_lines = _import_error_lines(tree)
        self.docstring_ids = _docstring_ids(tree)
        self.has_platform_guard = bool(PLATFORM_GUARD_RE.search(source))
        self.os_names: set[str] = set()
        self.signal_names: set[str] = set()
        self.subprocess_names: set[str] = set()
        self.subprocess_funcs: set[str] = set()
        self.path_reported_lines: set[int] = set()

    # -- 工具 -------------------------------------------------------------

    def _add(self, line: int, code: str, detail: str = "", **kw: object) -> None:
        self.findings.append(make_finding(self.rel, line, code, detail, **kw))

    def _posix_severity(self, line: int) -> tuple[Severity | None, str]:
        if line in self.guarded_lines:
            return Severity.WARNING, "（在 try/except 内，请确认异常分支有回退）"
        if self.has_platform_guard:
            return Severity.WARNING, "（文件内有平台判断，请确认已分支处理）"
        return None, ""

    def _report_posix(self, line: int, code: str, what: str) -> None:
        severity, note = self._posix_severity(line)
        self._add(line, code, f"{what}{note}", severity=severity)

    # -- import ---------------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            top = alias.name.split(".")[0]
            bound = alias.asname or top
            if top in POSIX_ONLY_MODULES:
                self._report_posix(node.lineno, "WIN303", alias.name)
            if top in GUI_MODULES:
                self._add(node.lineno, "CONV001", GUI_MODULES[top])
            if alias.name == "os":
                self.os_names.add(bound)
            elif alias.name == "signal":
                self.signal_names.add(bound)
            elif alias.name == "subprocess":
                self.subprocess_names.add(bound)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        top = module.split(".")[0]
        if node.level == 0 and top in POSIX_ONLY_MODULES:
            self._report_posix(node.lineno, "WIN303", module)
        if node.level == 0 and top in GUI_MODULES:
            self._add(node.lineno, "CONV001", GUI_MODULES[top])
        for alias in node.names:
            if module == "os" and alias.name in POSIX_ONLY_OS_ATTRS:
                self._report_posix(node.lineno, "WIN304", f"os.{alias.name}")
            elif module == "signal" and alias.name in POSIX_ONLY_SIGNAL_ATTRS:
                self._report_posix(node.lineno, "WIN304", f"signal.{alias.name}")
            elif module == "subprocess" and alias.name in SUBPROCESS_FUNCS:
                self.subprocess_funcs.add(alias.asname or alias.name)
        self.generic_visit(node)

    # -- 属性访问 ---------------------------------------------------------

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name):
            owner = node.value.id
            if owner in self.os_names and node.attr in POSIX_ONLY_OS_ATTRS:
                self._report_posix(node.lineno, "WIN304", f"os.{node.attr}")
            elif owner in self.signal_names and node.attr in POSIX_ONLY_SIGNAL_ATTRS:
                self._report_posix(node.lineno, "WIN304", f"signal.{node.attr}")
        self.generic_visit(node)

    # -- 调用 -------------------------------------------------------------

    @staticmethod
    def _open_mode_index(func: ast.AST) -> int | None:
        """是 open 调用时返回 mode 的位置参数下标，否则返回 None。"""
        if isinstance(func, ast.Name):
            return 1 if func.id == "open" else None
        if isinstance(func, ast.Attribute) and func.attr == "open":
            value = func.value
            if isinstance(value, ast.Name) and value.id == "io":
                return 1
            if isinstance(value, ast.Call):
                callee = value.func
                name = (
                    callee.id
                    if isinstance(callee, ast.Name)
                    else getattr(callee, "attr", "")
                )
                if name == "Path":
                    return 0
        return None

    def _is_subprocess_call(self, func: ast.AST) -> bool:
        if isinstance(func, ast.Name):
            return func.id in self.subprocess_funcs
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            owner = func.value.id
            if owner in self.subprocess_names and func.attr in SUBPROCESS_FUNCS:
                return True
            if owner in self.os_names and func.attr in OS_SHELL_FUNCS:
                return True
        return False

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        mode_index = self._open_mode_index(func)
        if mode_index is not None:
            if not _has_keyword(node, "encoding") and _mode_is_text(node, mode_index):
                self._add(node.lineno, "WIN301")
        elif (
            isinstance(func, ast.Attribute)
            and func.attr in {"read_text", "write_text"}
            and not _has_keyword(node, "encoding")
        ):
            self._add(node.lineno, "WIN302", f"{func.attr}()")
        elif self._is_subprocess_call(func) and node.args:
            command = _first_command_token(node.args[0])
            if command and PYTHON_LITERAL_RE.match(command):
                self._add(node.lineno, "WIN306", f"'{command}'")
        self.generic_visit(node)

    # -- 字符串字面量 -----------------------------------------------------

    def visit_Constant(self, node: ast.Constant) -> None:
        value = node.value
        if (
            isinstance(value, str)
            and id(node) not in self.docstring_ids
            and node.lineno not in self.path_reported_lines
            and POSIX_PATH_RE.match(value)
        ):
            self.path_reported_lines.add(node.lineno)
            shown = value if len(value) <= 60 else value[:57] + "..."
            self._add(node.lineno, "WIN305", repr(shown))


def check_python_source(rel: str, source: str) -> list[Finding]:
    """检查一份 Python 源码文本，返回未被 ``# win-ok`` 豁免的发现。"""
    try:
        tree = ast.parse(source, filename=rel)
    except (SyntaxError, ValueError) as exc:
        line = getattr(exc, "lineno", None) or 0
        return [
            make_finding(
                rel,
                line,
                "WIN307",
                f"{type(exc).__name__}: {exc.msg}"
                if isinstance(exc, SyntaxError)
                else str(exc),
            )
        ]
    visitor = _Visitor(rel, tree, source)
    visitor.visit(tree)

    lines = source.splitlines()
    marker = SUPPRESS_MARKER.lower()
    kept = []
    for finding in visitor.findings:
        if 0 < finding.line <= len(lines) and marker in lines[finding.line - 1].lower():
            continue
        kept.append(finding)
    return sorted(set(kept))


def check_python_bytes(rel: str, data: bytes) -> list[Finding]:
    """从字节内容开始检查：先按 UTF-8（允许 BOM）解码，失败则记一条 INFO 并跳过。"""
    try:
        source = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        return [make_finding(rel, 0, "WIN307", f"非 UTF-8 编码（{exc.reason}）")]
    return check_python_source(rel, source)
