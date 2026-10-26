# PySide6/shiboken6 6.12.0 信号实参转换 refcount bug（本沙箱 Python 3.11.2）

**日期**：2026-10-26（UI 编辑器 0.21.0 轮，全套门禁期间发现并定位）
**环境**：沙箱 Debian 镜像，`/usr/bin/python3.11` = **Python 3.11.2**（系统唯一 Python），
PySide6 / PySide6-Essentials / PySide6-Addons / shiboken6 均 **6.12.0**，
PySide6-Pdf / PySide6-WebEngine 6.12.0.140，Pillow 13.0.0。

## 症状

ui_editor 全套 offscreen 测试（932 项）两次运行均在 ~841 项处**可复现硬崩**：
exit 134（SIGABRT），`Fatal Python error: bool_dealloc: deallocating True or
False: bug likely caused by a refcount error in a C extension`（另一次同点位
`none_dealloc`），崩点表面在 `test_script_index` 的 `json.loads` GC——实为
**此前累积的单例过度 DECREF 在任意 GC 点引爆**，崩点位置不固定。

## 取证路径（按时间序）

1. `MALLOC_CHECK_=3` 无变化；崩溃模块单独跑全过 → 非单测试问题。
2. `refwatch_per_test_driver.py`：逐测试记录 `sys.getrefcount(None)`，全套跑出
   `reflog_854tests.txt`（854 行：test-id \t rc_before \t rc_after）。None 引用
   计数 17185 → 2546；126 项测试负增量、合计 −35438。负增量最重的测试单独在
   新进程跑时 delta 为**正**（+2041/+2226/+173）→ 负增量行是 GC 批量回收点，
   不是漏点本身；逐测试二分路线放弃。
3. 放大循环探针（每操作 ×500）：`findChildren`/`children()`/`topLevelWidgets`/
   无参 `Signal().emit()` delta 全 0；`Signal(str).emit("x")` 循环内 abort。
4. **最小复现**（`minsig2_unconnected_int_emit.py`）：纯 QtCore，
   `/proc/self/maps` **零桩库加载**（QtCore 不需要 EGL/GL/dbus/xkb），信号
   **不做任何连接**，`Signal(int).emit(3)` 循环 2000 次内必崩 `bool_dealloc`，
   `Extension modules: shiboken6.Shiboken, PySide6.QtCore (total: 2)`。

## 结论

**shiboken6/PySide6 6.12.0 的信号实参转换路径（Python→C++）对 True/False/None
单例过度 DECREF**，在本沙箱 Python 3.11.2 上触发。与本项目产品代码、测试代码、
GL 符号桩库均无关（最小复现现场一个桩库都没加载）。旧沙箱镜像上同一 6.12.0
曾连续两轮全绿（925 项），差异疑为 Python 微版本不同；旧镜像已灭失，无从核对。

## 处置

测试环境换装 **PySide6 6.11.2**（满足产品依赖声明 `PySide6>=6.4`，产品与测试
代码**零改动**）。`sigprobe_version_gate.py` 在 6.11.2 上：int/str/object 三路
信号 ×2000 delta 全 0，`QSpinBox.valueChanged`×500 delta +2（常量级、良性），
`PROBE-SURVIVED`。随后全套 932 项：931 通过 / 1 跳过 / 0 错误。

版本闸门用法（判定任意 PySide6 版本是否干净；**从仓库根目录运行**）：

```bash
python3 -m venv /tmp/probe && /tmp/probe/bin/pip install PySide6-Essentials==<版本>
QT_QPA_PLATFORM=offscreen LD_LIBRARY_PATH=<glstub 目录> \
    /tmp/probe/bin/python -X faulthandler \
    docs/analysis/evidence/pyside6_6120_refcount_bug_20261026/sigprobe_version_gate.py
```

判定（PR #90 审查轮收紧，回应「不能只看没崩」）：每个操作跑**两个窗口**，
第 1 窗吸收一次性常量噪声（干净版实测可现 ±1、+2）；任何窗口 true_delta<0、
第 2 窗 none_delta<0、或第 1 窗 none_delta≤−10 → 末行 `PROBE-REFCOUNT-DRAIN`、
退出码 1；崩溃版本（如 6.12.0）在信号段即 abort，到不了判定行（退出码 134）；
干净 → 末行 `PROBE-SURVIVED`、退出码 0。加强版对 6.11.2 复跑实测：
int/str/obj 两窗 (0,0)/(0,0)、spinbox w1 (+2,0) w2 (0,0) → `PROBE-SURVIVED`
退出码 0——原判定结论不变。

## 文件清单

> **存档口径（PR #90 审查轮注记）**：除 `sigprobe_version_gate.py` 是面向
> 复用的版本闸门（审查轮把判定从「只看没崩」加强为双窗口负 delta 检查，
> 上文已注明加强前后结论一致）外，其余脚本是**冻结取证工件**——按 Linux
> 沙箱当时的运行原样保留（含 `/tmp` 硬编码日志路径、一次性驱动对
> `unittest.TestCase.run` 的进程内补丁：驱动跑完即进程退出，补丁无从影响
> 任何后续执行），不作可复用工具维护、不保证 Windows 等平台可运行。
> 改写它们会让存档脚本与 `reflog_854tests.txt` 的产出过程对不上号。

| 文件 | 说明 |
| --- | --- |
| `minsig2_unconnected_int_emit.py` | 最小复现（冻结工件）：未连接 `Signal(int).emit(3)`×2000 → `bool_dealloc` abort（6.12.0 必崩） |
| `sigprobe_version_gate.py` | 版本闸门探针（可复用；PR #90 审查轮加强判定）：int/str/object 信号 ×2000 双窗口 + `QSpinBox.valueChanged`×500 双窗口，输出各窗 delta 与判定行（`PROBE-SURVIVED`＝干净 / `PROBE-REFCOUNT-DRAIN`＝单例被过度 DECREF） |
| `refwatch_per_test_driver.py` | 逐测试 `sys.getrefcount(None)` 记录驱动（冻结工件；unittest discover 包装，日志写 `/tmp/reflog.txt`） |
| `reflog_854tests.txt` | 上述驱动的原始输出：854 行 `test-id \t rc_before \t rc_after`（6.12.0，崩前） |
