# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubmain.py
__version__ = '0.0.7'
import sys
from pubcore import __framework__ as pubcore

def Initialize():
    return


def Start():
    pubcore.OnStarted()


def Loop(fCurTime):
    pubcore.OnUpdated(fCurTime)


def ModuleReset():
    return


def OnRestartClear():
    lTotlaPackage = [
     'pubcipher', 'pubcore', 'pubnet']
    for sPackage in lTotlaPackage:
        if sPackage in sys.modules:
            pModule = sys.modules[sPackage]
            if hasattr(pModule, 'OnRestartClear'):
                pModule.OnRestartClear()
