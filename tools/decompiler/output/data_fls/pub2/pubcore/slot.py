# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\slot.py
__version__ = '0.0.1'
try:
    import C_slot
except ImportError:
    from slot_v1 import *
else:
    from slot_v2 import *
