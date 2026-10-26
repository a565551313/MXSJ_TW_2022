import sys, gc
# 版本闸门探针（PR #90 审查轮加强版）：判定任意 PySide6 版本在本环境
# 是否有 shiboken 信号实参转换的 refcount bug（6.12.0 在 Python 3.11.2
# 上的形态：单例被按比例过度 DECREF，最终 bool_dealloc/none_dealloc abort）。
#
# 判定规则（回应审查意见「不能只看没崩」）：
#   * 每个操作跑两个窗口；第 1 窗吸收一次性常量噪声（实测干净版可现 ±1、+2），
#   * 任何窗口 true_delta < 0，或第 2 窗 none_delta < 0，或第 1 窗
#     none_delta <= -10（常量级解释不了的一次性大漏）→ PROBE-REFCOUNT-DRAIN，退出码 1；
#   * 崩溃版本根本到不了判定行（6.12.0 在信号段即 abort，退出码 134）；
#   * 干净 → 末行 PROBE-SURVIVED，退出码 0。
from PySide6.QtCore import QObject, Signal
class E(QObject):
    si = Signal(int); ss = Signal(str); so = Signal(object)
e = E()
def window(fn, n):
    gc.collect(); rc0 = sys.getrefcount(None); tb0 = sys.getrefcount(True)
    for _ in range(n):
        fn()
    gc.collect()
    return sys.getrefcount(None) - rc0, sys.getrefcount(True) - tb0
bad = []
for name, fn in (("int", lambda: e.si.emit(3)),
                 ("str", lambda: e.ss.emit("x")),
                 ("obj", lambda: e.so.emit("x"))):
    w1 = window(fn, 2000)
    w2 = window(fn, 2000)
    print(name, "w1", w1, "w2", w2, flush=True)
    if w1[1] < 0 or w2[1] < 0 or w2[0] < 0 or w1[0] <= -10:
        bad.append(name)
from PySide6.QtWidgets import QApplication, QSpinBox
app = QApplication([])
sp = QSpinBox(); sp.valueChanged.connect(lambda v: None)
def spinw():
    gc.collect(); rc0 = sys.getrefcount(None)
    for i in range(500):
        sp.setValue(i % 100)
    gc.collect()
    return (sys.getrefcount(None) - rc0, 0)
w1, w2 = spinw(), spinw()
print("spinbox", "w1", w1, "w2", w2, flush=True)
if w1[1] < 0 or w2[1] < 0 or w2[0] < 0 or w1[0] <= -10:
    bad.append("spinbox")
if bad:
    print("PROBE-REFCOUNT-DRAIN", ",".join(bad), flush=True)
    sys.exit(1)
print("PROBE-SURVIVED", flush=True)
