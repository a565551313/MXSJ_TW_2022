# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\publog.py
import publogging
LEVEL_DICT = {'DEBUG': (publogging.DEBUG), 
   'INFO': (publogging.INFO), 
   'WARNING': (publogging.WARNING), 
   'ERROR': (publogging.ERROR), 
   'CRITICAL': (publogging.CRITICAL)}
g_LoggerLevelDict = {}
g_PubHandler = None
g_GameHandler = None

def GetPubLogger(logName):
    handle = _GetPubHandle()
    logger = publogging.getLogger(logName)
    _SetLogLevel(logger, logName)
    logger.propagate = 0
    logger.addHandler(handle)
    return logger


def GetGameLogger(logName):
    handle = _GetGameHandle()
    logger = publogging.getLogger(logName)
    _SetLogLevel(logger, logName)
    logger.propagate = 0
    logger.addHandler(handle)
    return logger


def SetPubLogLevel(level):
    handle = _GetPubHandle()
    handle.setLevel(LEVEL_DICT[level])


def SetGameLogLevel(level):
    handle = _GetGameHandle()
    handle.setLevel(LEVEL_DICT[level])


def SetLogLevel(logName, level):
    g_LoggerLevelDict[logName] = LEVEL_DICT[level]
    logger = publogging.getLogger(logName)
    logger.setLevel(LEVEL_DICT[level])


def SetPackageLevel(package, level):
    for module in g_LoggerLevelDict.keys():
        if package in module:
            SetLogLevel(module, level)


def _SetLogLevel(logger, logName):
    level = g_LoggerLevelDict.get(logName)
    if not level:
        level = LEVEL_DICT['INFO']
    logger.setLevel(level)
    g_LoggerLevelDict[logName] = level


def _GetPubHandle():
    global g_PubHandler
    if not g_PubHandler:
        _CreateHandler()
    return g_PubHandler


def _GetGameHandle():
    global g_GameHandler
    if not g_GameHandler:
        _CreateHandler()
    return g_GameHandler


def _CreateHandler():
    global g_GameHandler
    global g_PubHandler
    formatter = publogging.Formatter('%(name)s: - %(levelname)s - %(message)s')
    g_PubHandler = publogging.StreamHandler()
    g_PubHandler.setLevel(publogging.DEBUG)
    g_PubHandler.setFormatter(formatter)
    g_GameHandler = publogging.StreamHandler()
    g_GameHandler.setLevel(publogging.DEBUG)
    g_GameHandler.setFormatter(formatter)
