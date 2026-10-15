# pycdc 交叉复核产物 · script.fls entry 2018
# co_filename(原始)='script/data/teammatchdata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2018.pyc (Python 2.5)

g_OldData = { }

def ModuleReset():
    for iTar in g_OldData:
        DATA[iTar] = g_OldData[iTar]
    


def GetName(iTar):
    if DATA.get(iTar, None) and DATA[iTar].get('sName', None):
        return DATA[iTar]['sName']
    


def GetChildren(iTar):
    if not DATA.get(iTar, None) or iTar % 100 != 0:
        return None
    
    iHundNum = iTar / 100
    iStart = iHundNum * 100 + 1
    iEnd = (iHundNum + 1) * 100
    iChildList = []
    for i in xrange(iStart, iEnd):
        if DATA.get(i, None):
            iChildList.append(i)
            continue
    
    if len(iChildList) > 0:
        return iChildList
    


def GetLimitInfo(iTar):
    dLimit = { }
    if iTar not in DATA:
        return None
    
    dInfo = DATA[iTar]
    dLimit['iLv'] = dInfo.get('iGrade', None)
    dLimit['iSerLv'] = dInfo.get('iSerLv', None)
    dLimit['iSerDay'] = dInfo.get('iSerDay', None)
    dLimit['iKFstate'] = dInfo.get('iState', None)
    dLimit['iStartTime'] = dInfo.get('iStartTime', None)
    dLimit['iEndTime'] = dInfo.get('iEndTime', None)
    dLimit['tDateInfo'] = dInfo.get('tDateInfo', None)
    return dLimit


def UpdateLimitTime(iTar, iStartTimeStamp):
    import time
    import misc
    if iTar not in DATA:
        return None
    
    if iTar not in g_OldData:
        g_OldData[iTar] = misc.DeepCopy(DATA[iTar])
    
    dInfo = misc.DeepCopy(g_OldData[iTar])
    oNewStartTime = time.localtime(iStartTimeStamp)
    (iOldStartHour, iOldStartMin) = dInfo['iStartTime']
    iNewStartHour = oNewStartTime.tm_hour
    iNewStartMin = oNewStartTime.tm_min
    iHourDff = iNewStartHour - iOldStartHour
    iMinDff = iNewStartMin - iOldStartMin
    (iOldEndHour, iOldEndMin) = dInfo['iEndTime']
    iNewEndHour = 0
    iNewEndMin = iOldEndMin + iMinDff
    if iNewEndMin >= 60:
        iNewEndMin -= 60
        iNewEndHour += 1
    elif iNewEndMin < 0:
        iNewEndMin += 60
        iNewEndHour -= 1
    
    iNewEndHour = (iNewEndHour + iOldEndHour + iHourDff + 24) % 24
    if (iHourDff < 0 or iHourDff == 0) and iMinDff < 0:
        dInfo['iStartTime'] = ((iNewStartHour, iNewStartMin), (iOldStartHour, iOldStartMin))
        dInfo['iEndTime'] = ((iNewEndHour, iNewEndMin), (iOldEndHour, iOldEndMin))
    else:
        dInfo['iStartTime'] = ((iOldStartHour, iOldStartMin), (iNewStartHour, iNewStartMin))
        dInfo['iEndTime'] = ((iOldEndHour, iOldEndMin), (iNewEndHour, iNewEndMin))
    dOldDateInfo = dInfo['tDateInfo']
    if dOldDateInfo[0] == 1:
        lNewDay = [
            oNewStartTime.tm_wday + 1]
        if isinstance(dOldDateInfo[2], int):
            lNewDay.append(dOldDateInfo[2])
        else:
            lNewDay.extend(list(dOldDateInfo[2]))
        dInfo['tDateInfo'] = (1, dOldDateInfo[1], tuple(lNewDay))
    else:
        iWeek = misc.GetServerWeek(iStartTimeStamp)
        dInfo['tDateInfo'] = (2, iWeek, oNewStartTime.tm_wday + 1)
    DATA[iTar] = dInfo


def GetAdvanceFuBen():
    return [
        1104,
        1105,
        1106,
        1107,
        1108,
        1109,
        1110,
        1111,
        1112]


def GetCalendarID(iTar):
    dData = DATA.get(iTar, { })
    return dData.get('iCalendarID', 0)

{
    'iCalendarID': 1054,
    'iEndTime': (19, 44),
    'iGrade': 30,
    'iSerDay': 0,
    'iSerLv': 0 }[{
    'iCalendarID': 1054,
    'iEndTime': (19, 44),
    'iGrade': 30,
    'iSerDay': 0,
    'iSerLv': 0 }:(18, 30)] = {
    'iCalendarID': 1054,
    'iEndTime': (19, 44),
    'iGrade': 30,
    'iSerDay': 0,
    'iSerLv': 0 }
None['iState'] = 0
None['sName'] = '\xc0\xb0\xac\xa3\xbcy\xa8\xe5'
None['tDateInfo'] = (1, 0, 4)
None[1612] = None
DATA = None
