import sys, gc
from PySide6.QtCore import QObject, Signal
class E(QObject):
    sigint = Signal(int)
e = E()   # 完全不 connect
gc.collect(); rc0 = sys.getrefcount(None)
for _ in range(2000):
    e.sigint.emit(3)
gc.collect()
print("unconnected emit delta", sys.getrefcount(None) - rc0, flush=True)
tb = sys.getrefcount(True), sys.getrefcount(False)
print("True/False refcounts:", tb, flush=True)
