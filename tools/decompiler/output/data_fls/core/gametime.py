# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\core\gametime.py


def GetLocalTimeStamp(bTurnUTC8=False):
    import time
    iTimeStamp = time.time()
    if bTurnUTC8 and iTimeStamp:
        iTimeStamp = Turn2UTC8TimeStamp(iTimeStamp)
    return iTimeStamp


def GetLocalUTC8Date():
    iTimeStamp = GetLocalTimeStamp()
    return TimeStamp2Date(iTimeStamp)


def TimeStamp2Date(iTimeStamp):
    import time
    if iTimeStamp is not None:
        iTimeStamp = Turn2UTC8TimeStamp(iTimeStamp)
    try:
        tDate = time.localtime(iTimeStamp)
    except ValueError as ve:
        if iTimeStamp < 0:
            subStr = 'param is a negative value'
        else:
            subStr = 'sec=%s, %s' % (str(iTimeStamp), type(iTimeStamp))
        raise ValueError(str(ve) + '\n%s' % subStr)

    return tDate


def TimeDate2Stamp(tUTC8Date):
    import time
    iUTC8Stamp = time.mktime(tUTC8Date)
    iTimeStamp = Turn2RealTimeStamp(iUTC8Stamp)
    return iTimeStamp


def LocalTimeStr():
    import time
    return time.strftime('%Y-%m-%d %H:%M:%S', GetLocalUTC8Date())


def GetRunTime():
    import C_sys
    return C_sys.GetTime()


def Turn2UTC8TimeStamp(iTimeStamp):
    import datetime
    delta = datetime.datetime.fromtimestamp(0) - datetime.datetime.utcfromtimestamp(0)
    return max(0, iTimeStamp - (delta.days * 24 * 3600 + delta.seconds) + 28800)


def Turn2RealTimeStamp(iUTC8Stamp):
    import datetime
    delta = datetime.datetime.fromtimestamp(0) - datetime.datetime.utcfromtimestamp(0)
    iTimeStamp = max(0, iUTC8Stamp + (delta.days * 24 * 3600 + delta.seconds) - 28800)
    return iTimeStamp
