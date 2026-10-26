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

版本闸门用法（判定任意 PySide6 版本是否干净）：

```bash
python3 -m venv /tmp/probe && /tmp/probe/bin/pip install PySide6-Essentials==<版本>
QT_QPA_PLATFORM=offscreen /tmp/probe/bin/python -X faulthandler sigprobe_version_gate.py
# QtWidgets 段需符号桩：LD_LIBRARY_PATH=<glstub 目录>；末行输出 PROBE-SURVIVED 为干净
```

## 文件清单

| 文件 | 说明 |
| --- | --- |
| `minsig2_unconnected_int_emit.py` | 最小复现：未连接 `Signal(int).emit(3)`×2000 → `bool_dealloc` abort（6.12.0 必崩） |
| `sigprobe_version_gate.py` | 版本闸门探针：int/str/object 信号 ×2000 + `QSpinBox.valueChanged`×500，输出各 delta 与 `PROBE-SURVIVED` |
| `refwatch_per_test_driver.py` | 逐测试 `sys.getrefcount(None)` 记录驱动（unittest discover 包装） |
| `reflog_854tests.txt` | 上述驱动的原始输出：854 行 `test-id \t rc_before \t rc_after`（6.12.0，崩前） |
