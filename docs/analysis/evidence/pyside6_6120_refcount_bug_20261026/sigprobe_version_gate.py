import sys, gc
from PySide6.QtCore import QObject, Signal
class E(QObject):
    si = Signal(int); ss = Signal(str); so = Signal(object)
e = E()
for name, fn in (("int", lambda: e.si.emit(3)),
                 ("str", lambda: e.ss.emit("x")),
                 ("obj", lambda: e.so.emit("x"))):
    gc.collect(); rc0 = sys.getrefcount(None); tb0 = sys.getrefcount(True)
    for _ in range(2000):
        fn()
    gc.collect()
    print(name, "none_delta", sys.getrefcount(None) - rc0,
          "true_delta", sys.getrefcount(True) - tb0, flush=True)
from PySide6.QtWidgets import QApplication, QSpinBox
app = QApplication([])
sp = QSpinBox(); sp.valueChanged.connect(lambda v: None)
gc.collect(); rc0 = sys.getrefcount(None)
for i in range(500):
    sp.setValue(i % 100)
gc.collect()
print("spinbox none_delta", sys.getrefcount(None) - rc0, flush=True)
print("PROBE-SURVIVED", flush=True)
