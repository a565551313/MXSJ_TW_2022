# pycdc 交叉复核产物 · script.fls entry 1235
# co_filename(原始)='script/data/magicperformdata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1235.pyc (Python 2.5)

import innerversion
import permission
import charpath
PACKAGE = 'magicres'

def IsNewMagic(iPerformID):
    if iPerformID in ONLYNEWLIST:
        return charpath.IsUseNewRes()
    
    return iPerformID in PERFORMDATA


def IsPreload(iPerformID):
    return GetResInfoByPerformID(iPerformID)['bPreload']


def GetResInfoByPerformID(iPerformID):
    dPerformInfo = PERFORMDATA[iPerformID]
    dResInfo = RESDATA[dPerformInfo['iResID']]
    return dResInfo


def GetPathAndName(iPerformID, iSide):
    dPerformInfo = PERFORMDATA[iPerformID]
    dResInfo = RESDATA[dPerformInfo['iResID']]
    sSkillPath = dResInfo['sSkillPath']
    if not sSkillPath:
        sSkillPath = '%s/%.4d' % (PACKAGE, dPerformInfo['iResID'])
    
    if dResInfo['bAB']:
        if iSide:
            sSkillPath = '%s_a.skill' % sSkillPath
        else:
            sSkillPath = '%s_b.skill' % sSkillPath
    else:
        sSkillPath = '%s.skill' % sSkillPath
    if dPerformInfo['iNameType']:
        if dPerformInfo['iMgcID'] == 0:
            sSkillName = dPerformInfo['sName']
        else:
            sSkillName = GetMagicName(dPerformInfo['iMgcID'])
    else:
        sSkillName = ''
    dRet = {
        'sPath': sSkillPath,
        'sName': sSkillName,
        'iNameType': dPerformInfo['iNameType'] }
    if 'sSpecialEff' in dPerformInfo:
        dRet['sSpecialEff'] = dPerformInfo['sSpecialEff']
    
    return dRet


def GetMagicName(iMgcID):
    import petskill
    import specialdata
    import magicdata
    if iMgcID in petskill.DATA:
        return petskill.GetData(iMgcID)['name']
    elif iMgcID in specialdata.DATA:
        return specialdata.GetData(iMgcID)['name']
    else:
        return magicdata.GetData(iMgcID)['name']


def InitInnerData():
    global RESDATA, PERFORMDATA, ONLYNEWLIST, INNER_PERFORMDATA, INNERONLYNEWLIST
    if permission.IsUseNewChar():
        
        try:
            import new_magicperformdata
            new_magicperformdata.MergeData()
            RESDATA = new_magicperformdata.RESDATA
            PERFORMDATA = new_magicperformdata.PERFORMDATA
            ONLYNEWLIST = new_magicperformdata.ONLYNEWLIST
            INNER_PERFORMDATA = new_magicperformdata.INNER_PERFORMDATA
            INNERONLYNEWLIST = new_magicperformdata.INNERONLYNEWLIST

    
    MergeData()


def MergeData():
    if innerversion.IsInnerVer() or permission.IsUseNewChar():
        PERFORMDATA.update(INNER_PERFORMDATA)
        ONLYNEWLIST.extend(INNERONLYNEWLIST)
    

None[2320] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2321] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2323] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2324] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2326] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2330] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2333] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2334] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2336] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2337] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2338] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2339] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2340] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2341] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2342] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2403] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2404] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2405] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2414] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2415] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2416] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2421] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2426] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2427] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2429] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2430] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2432] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2433] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2434] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2435] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2436] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2437] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2438] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2504] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2505] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2506] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2507] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2508] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2510] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2513] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2516] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2525] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2526] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2528] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2529] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2530] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2536] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2537] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[2538] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[4815] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[4816] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[4817] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[4818] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[4819] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[4820] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[4821] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[4822] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[4823] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[4824] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[4825] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[17360] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[17361] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[17370] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[17371] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[17380] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[17381] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[19001] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': 'magicres/story/19001' }
None[19016] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': 'magicres/story/19016' }
None[19018] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': 'magicres/story/19018' }
None[19042] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': 'magicres/story/19042' }
None[19045] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': 'magicres/story/19017' }
None[19048] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': 'magicres/story/19048' }
None[19901] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': 'magicres/story/19901' }
None[19902] = {
    'bAB': True,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': 'magicres/story/19902' }
None[21030] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[21040] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[21050] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[21070] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[21090] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[21180] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[21190] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[21320] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[26360] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': True,
    'bPreload': False,
    'sSkillPath': '' }
None[26361] = {
    'bAB': False,
    'bGoBack': True,
    'bPhy': True,
    'bPreload': False,
    'sSkillPath': '' }
None[26362] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': True,
    'bPreload': False,
    'sSkillPath': '' }
None[26363] = {
    'bAB': False,
    'bGoBack': True,
    'bPhy': True,
    'bPreload': False,
    'sSkillPath': '' }
None[26364] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': True,
    'bPreload': False,
    'sSkillPath': '' }
None[26365] = {
    'bAB': False,
    'bGoBack': True,
    'bPhy': True,
    'bPreload': False,
    'sSkillPath': '' }
None[26366] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': True,
    'bPreload': False,
    'sSkillPath': '' }
None[26367] = {
    'bAB': False,
    'bGoBack': True,
    'bPhy': True,
    'bPreload': False,
    'sSkillPath': '' }
None[26368] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': True,
    'bPreload': False,
    'sSkillPath': '' }
None[26369] = {
    'bAB': False,
    'bGoBack': True,
    'bPhy': True,
    'bPreload': False,
    'sSkillPath': '' }
None[45437] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[45438] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[45439] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
None[66667] = {
    'bAB': False,
    'bGoBack': False,
    'bPhy': False,
    'bPreload': False,
    'sSkillPath': '' }
RESDATA = None
PERFORMDATA = {
    580: {
        'iMgcID': 580,
        'iNameType': 1,
        'iResID': 580,
        'sName': '' },
    581: {
        'iMgcID': 581,
        'iNameType': 1,
        'iResID': 581,
        'sName': '' },
    583: {
        'iMgcID': 583,
        'iNameType': 0,
        'iResID': 583,
        'sName': '' },
    1009: {
        'iMgcID': 1009,
        'iNameType': 0,
        'iResID': 1009,
        'sName': '' },
    1701: {
        'iMgcID': 1701,
        'iNameType': 1,
        'iResID': 1701,
        'sName': '' },
    1702: {
        'iMgcID': 1702,
        'iNameType': 1,
        'iResID': 1702,
        'sName': '' },
    1704: {
        'iMgcID': 1704,
        'iNameType': 1,
        'iResID': 1704,
        'sName': '' },
    1705: {
        'iMgcID': 1705,
        'iNameType': 1,
        'iResID': 1705,
        'sName': '' },
    1706: {
        'iMgcID': 1706,
        'iNameType': 1,
        'iResID': 1706,
        'sName': '' },
    1711: {
        'iMgcID': 1711,
        'iNameType': 1,
        'iResID': 1711,
        'sName': '' },
    1712: {
        'iMgcID': 1712,
        'iNameType': 1,
        'iResID': 1712,
        'sName': '' },
    1713: {
        'iMgcID': 1713,
        'iNameType': 1,
        'iResID': 1713,
        'sName': '' },
    1714: {
        'iMgcID': 1714,
        'iNameType': 1,
        'iResID': 1714,
        'sName': '' },
    1715: {
        'iMgcID': 1715,
        'iNameType': 1,
        'iResID': 1715,
        'sName': '' },
    1716: {
        'iMgcID': 1716,
        'iNameType': 1,
        'iResID': 1716,
        'sName': '' },
    1717: {
        'iMgcID': 1717,
        'iNameType': 1,
        'iResID': 1717,
        'sName': '' },
    1721: {
        'iMgcID': 1721,
        'iNameType': 1,
        'iResID': 1721,
        'sName': '' },
    1722: {
        'iMgcID': 1722,
        'iNameType': 1,
        'iResID': 1722,
        'sName': '' },
    1723: {
        'iMgcID': 1723,
        'iNameType': 1,
        'iResID': 1723,
        'sName': '' },
    1724: {
        'iMgcID': 1724,
        'iNameType': 1,
        'iResID': 1724,
        'sName': '' },
    1725: {
        'iMgcID': 1725,
        'iNameType': 1,
        'iResID': 1725,
        'sName': '' },
    1726: {
        'iMgcID': 1726,
        'iNameType': 1,
        'iResID': 1726,
        'sName': '' },
    1727: {
        'iMgcID': 1727,
        'iNameType': 1,
        'iResID': 1727,
        'sName': '' },
    1728: {
        'iMgcID': 1728,
        'iNameType': 1,
        'iResID': 1728,
        'sName': '' },
    1729: {
        'iMgcID': 1729,
        'iNameType': 1,
        'iResID': 1729,
        'sName': '' },
    1736: {
        'iMgcID': 1736,
        'iNameType': 2,
        'iResID': 1736,
        'sName': '' },
    1737: {
        'iMgcID': 1737,
        'iNameType': 2,
        'iResID': 1737,
        'sName': '' },
    1738: {
        'iMgcID': 1738,
        'iNameType': 2,
        'iResID': 1738,
        'sName': '' },
    2102: {
        'iMgcID': 2102,
        'iNameType': 1,
        'iResID': 2102,
        'sName': '' },
    2104: {
        'iMgcID': 2104,
        'iNameType': 1,
        'iResID': 2104,
        'sName': '' },
    2105: {
        'iMgcID': 2105,
        'iNameType': 1,
        'iResID': 2105,
        'sName': '' },
    2106: {
        'iMgcID': 2106,
        'iNameType': 1,
        'iResID': 2106,
        'sName': '' },
    2107: {
        'iMgcID': 2107,
        'iNameType': 1,
        'iResID': 2107,
        'sName': '' },
    2108: {
        'iMgcID': 2108,
        'iNameType': 1,
        'iResID': 2108,
        'sName': '' },
    2109: {
        'iMgcID': 2109,
        'iNameType': 1,
        'iResID': 2109,
        'sName': '' },
    2117: {
        'iMgcID': 2117,
        'iNameType': 1,
        'iResID': 2117,
        'sName': '' },
    2118: {
        'iMgcID': 2118,
        'iNameType': 1,
        'iResID': 2118,
        'sName': '' },
    2119: {
        'iMgcID': 2119,
        'iNameType': 1,
        'iResID': 2119,
        'sName': '' },
    2122: {
        'iMgcID': 2122,
        'iNameType': 1,
        'iResID': 2122,
        'sName': '' },
    2123: {
        'iMgcID': 2123,
        'iNameType': 1,
        'iResID': 2123,
        'sName': '' },
    2125: {
        'iMgcID': 2125,
        'iNameType': 1,
        'iResID': 2125,
        'sName': '' },
    2128: {
        'iMgcID': 2128,
        'iNameType': 1,
        'iResID': 2128,
        'sName': '' },
    2132: {
        'iMgcID': 2132,
        'iNameType': 1,
        'iResID': 2132,
        'sName': '' },
    2136: {
        'iMgcID': 2136,
        'iNameType': 2,
        'iResID': 2136,
        'sName': '' },
    2137: {
        'iMgcID': 2137,
        'iNameType': 2,
        'iResID': 2137,
        'sName': '' },
    2138: {
        'iMgcID': 2138,
        'iNameType': 2,
        'iResID': 2138,
        'sName': '' },
    2301: {
        'iMgcID': 2301,
        'iNameType': 1,
        'iResID': 2301,
        'sName': '' },
    2302: {
        'iMgcID': 2302,
        'iNameType': 1,
        'iResID': 2302,
        'sName': '' },
    2305: {
        'iMgcID': 2305,
        'iNameType': 1,
        'iResID': 2305,
        'sName': '' },
    2306: {
        'iMgcID': 2306,
        'iNameType': 1,
        'iResID': 2306,
        'sName': '' },
    2308: {
        'iMgcID': 2308,
        'iNameType': 1,
        'iResID': 2308,
        'sName': '' },
    2312: {
        'iMgcID': 2312,
        'iNameType': 1,
        'iResID': 2312,
        'sName': '' },
    2314: {
        'iMgcID': 2314,
        'iNameType': 1,
        'iResID': 2314,
        'sName': '' },
    2316: {
        'iMgcID': 2316,
        'iNameType': 1,
        'iResID': 2316,
        'sName': '' },
    2318: {
        'iMgcID': 2318,
        'iNameType': 1,
        'iResID': 2318,
        'sName': '' },
    2319: {
        'iMgcID': 2319,
        'iNameType': 1,
        'iResID': 2319,
        'sName': '' },
    2320: {
        'iMgcID': 2320,
        'iNameType': 1,
        'iResID': 2320,
        'sName': '' },
    2321: {
        'iMgcID': 2321,
        'iNameType': 1,
        'iResID': 2321,
        'sName': '' },
    2323: {
        'iMgcID': 2323,
        'iNameType': 1,
        'iResID': 2323,
        'sName': '' },
    2326: {
        'iMgcID': 2326,
        'iNameType': 1,
        'iResID': 2326,
        'sName': '' },
    2333: {
        'iMgcID': 2333,
        'iNameType': 1,
        'iResID': 2333,
        'sName': '' },
    2334: {
        'iMgcID': 2334,
        'iNameType': 1,
        'iResID': 2334,
        'sName': '' },
    2399: {
        'iMgcID': 2399,
        'iNameType': 0,
        'iResID': 2301,
        'sName': '' },
    2403: {
        'iMgcID': 2403,
        'iNameType': 1,
        'iResID': 2403,
        'sName': '' },
    2404: {
        'iMgcID': 2404,
        'iNameType': 1,
        'iResID': 2404,
        'sName': '' },
    2405: {
        'iMgcID': 2405,
        'iNameType': 1,
        'iResID': 2405,
        'sName': '' },
    2414: {
        'iMgcID': 2414,
        'iNameType': 1,
        'iResID': 2414,
        'sName': '' },
    2415: {
        'iMgcID': 2415,
        'iNameType': 1,
        'iResID': 2415,
        'sName': '' },
    2416: {
        'iMgcID': 2416,
        'iNameType': 1,
        'iResID': 2416,
        'sName': '' },
    2421: {
        'iMgcID': 2421,
        'iNameType': 1,
        'iResID': 2421,
        'sName': '' },
    2426: {
        'iMgcID': 2426,
        'iNameType': 1,
        'iResID': 2426,
        'sName': '' },
    2427: {
        'iMgcID': 2427,
        'iNameType': 1,
        'iResID': 2427,
        'sName': '' },
    2429: {
        'iMgcID': 2429,
        'iNameType': 1,
        'iResID': 2429,
        'sName': '' },
    2430: {
        'iMgcID': 2430,
        'iNameType': 1,
        'iResID': 2430,
        'sName': '' },
    2432: {
        'iMgcID': 2432,
        'iNameType': 1,
        'iResID': 2432,
        'sName': '' },
    2433: {
        'iMgcID': 2433,
        'iNameType': 1,
        'iResID': 2433,
        'sName': '' },
    2434: {
        'iMgcID': 2434,
        'iNameType': 1,
        'iResID': 2434,
        'sName': '' },
    2435: {
        'iMgcID': 2435,
        'iNameType': 1,
        'iResID': 2435,
        'sName': '' },
    2436: {
        'iMgcID': 2436,
        'iNameType': 2,
        'iResID': 2436,
        'sName': '' },
    2437: {
        'iMgcID': 2437,
        'iNameType': 2,
        'iResID': 2437,
        'sName': '' },
    2438: {
        'iMgcID': 2438,
        'iNameType': 2,
        'iResID': 2438,
        'sName': '' },
    4815: {
        'iMgcID': 0,
        'iNameType': 0,
        'iResID': 4815,
        'sName': '' },
    4816: {
        'iMgcID': 0,
        'iNameType': 0,
        'iResID': 4816,
        'sName': '' },
    4818: {
        'iMgcID': 0,
        'iNameType': 1,
        'iResID': 4818,
        'sName': '\xc6F\xc2\xc3\xaew' },
    4819: {
        'iMgcID': 0,
        'iNameType': 1,
        'iResID': 4819,
        'sName': '\xa5\xc9\xc0s\xbdL' },
    4820: {
        'iMgcID': 0,
        'iNameType': 1,
        'iResID': 4820,
        'sName': '\xc5]\xb8t\xbb\xc9\xbe\xb9' },
    4821: {
        'iMgcID': 0,
        'iNameType': 1,
        'iResID': 4821,
        'sName': '\xc2\xe0\xc0s\xb3\xfd' },
    4822: {
        'iMgcID': 0,
        'iNameType': 1,
        'iResID': 4822,
        'sName': '\xbbb\xa6\xe7\xa4M' },
    4823: {
        'iMgcID': 0,
        'iNameType': 1,
        'iResID': 4823,
        'sName': '\xa5\xc3\xc6F\xa4M' },
    4824: {
        'iMgcID': 0,
        'iNameType': 1,
        'iResID': 4824,
        'sName': '\xa4C\xacP\xa4M' },
    4825: {
        'iMgcID': 0,
        'iNameType': 1,
        'iResID': 4825,
        'sName': '\xad{\xbc\xd3\xc3\xb9\xa4M' },
    4826: {
        'iMgcID': 0,
        'iNameType': 1,
        'iResID': 4817,
        'sName': '\xb3g\xafT\xb3\xfd' },
    4856: {
        'iMgcID': 4856,
        'iNameType': 1,
        'iResID': 1727,
        'sName': '' },
    5032: {
        'iMgcID': 5032,
        'iNameType': 0,
        'iResID': 2123,
        'sName': '' },
    17010: {
        'iMgcID': 1701,
        'iNameType': 1,
        'iResID': 1701,
        'sName': '' },
    17030: {
        'iMgcID': 1703,
        'iNameType': 1,
        'iResID': 1703,
        'sName': '' },
    17031: {
        'iMgcID': 1703,
        'iNameType': 0,
        'iResID': 1703,
        'sName': '' },
    17060: {
        'iMgcID': 1706,
        'iNameType': 1,
        'iResID': 1706,
        'sName': '' },
    17160: {
        'iMgcID': 1716,
        'iNameType': 1,
        'iResID': 1716,
        'sName': '' },
    17170: {
        'iMgcID': 1717,
        'iNameType': 1,
        'iResID': 1717,
        'sName': '' },
    17210: {
        'iMgcID': 1721,
        'iNameType': 1,
        'iResID': 1721,
        'sName': '' },
    17230: {
        'iMgcID': 1723,
        'iNameType': 1,
        'iResID': 1723,
        'sName': '' },
    17250: {
        'iMgcID': 1725,
        'iNameType': 1,
        'iResID': 1725,
        'sName': '' },
    17260: {
        'iMgcID': 1726,
        'iNameType': 1,
        'iResID': 1726,
        'sName': '' },
    17270: {
        'iMgcID': 1727,
        'iNameType': 1,
        'iResID': 1727,
        'sName': '' },
    17360: {
        'iMgcID': 1736,
        'iNameType': 2,
        'iResID': 17360,
        'sName': '' },
    17361: {
        'iMgcID': 1736,
        'iNameType': 2,
        'iResID': 17361,
        'sName': '' },
    17370: {
        'iMgcID': 1737,
        'iNameType': 2,
        'iResID': 17370,
        'sName': '' },
    17371: {
        'iMgcID': 1737,
        'iNameType': 2,
        'iResID': 17371,
        'sName': '' },
    17380: {
        'iMgcID': 1738,
        'iNameType': 2,
        'iResID': 17380,
        'sName': '' },
    17381: {
        'iMgcID': 1738,
        'iNameType': 2,
        'iResID': 17381,
        'sName': '' },
    19001: {
        'iMgcID': 0,
        'iNameType': 0,
        'iResID': 19001,
        'sName': '' },
    19016: {
        'iMgcID': 0,
        'iNameType': 0,
        'iResID': 19016,
        'sName': '' },
    19042: {
        'iMgcID': 0,
        'iNameType': 0,
        'iResID': 19042,
        'sName': '' },
    19045: {
        'iMgcID': 0,
        'iNameType': 0,
        'iResID': 19045,
        'sName': '' },
    19046: {
        'iMgcID': 0,
        'iNameType': 0,
        'iResID': 19018,
        'sName': '' },
    19048: {
        'iMgcID': 19048,
        'iNameType': 0,
        'iResID': 19048,
        'sName': '' },
    19901: {
        'iMgcID': 19901,
        'iNameType': 0,
        'iResID': 19901,
        'sName': '' },
    19902: {
        'iMgcID': 19902,
        'iNameType': 0,
        'iResID': 19902,
        'sName': '' },
    21040: {
        'iMgcID': 2104,
        'iNameType': 1,
        'iResID': 2104,
        'sName': '',
        'sSpecialEff': 'p' },
    21050: {
        'iMgcID': 2105,
        'iNameType': 1,
        'iResID': 2105,
        'sName': '',
        'sSpecialEff': 'p' },
    21070: {
        'iMgcID': 2107,
        'iNameType': 1,
        'iResID': 2107,
        'sName': '',
        'sSpecialEff': 'p' },
    21090: {
        'iMgcID': 2109,
        'iNameType': 1,
        'iResID': 2109,
        'sName': '',
        'sSpecialEff': 'p' },
    21180: {
        'iMgcID': 2118,
        'iNameType': 1,
        'iResID': 2118,
        'sName': '',
        'sSpecialEff': 'p' },
    21190: {
        'iMgcID': 2119,
        'iNameType': 1,
        'iResID': 2119,
        'sName': '',
        'sSpecialEff': 'p' },
    21320: {
        'iMgcID': 2132,
        'iNameType': 1,
        'iResID': 2132,
        'sName': '',
        'sSpecialEff': 'p' },
    21360: {
        'iMgcID': 2136,
        'iNameType': 2,
        'iResID': 2136,
        'sName': '',
        'sSpecialEff': 'r' },
    21361: {
        'iMgcID': 2136,
        'iNameType': 2,
        'iResID': 2136,
        'sName': '',
        'sSpecialEff': 'b' },
    21370: {
        'iMgcID': 2137,
        'iNameType': 2,
        'iResID': 2137,
        'sName': '',
        'sSpecialEff': 'w' },
    21371: {
        'iMgcID': 2137,
        'iNameType': 2,
        'iResID': 2137,
        'sName': '',
        'sSpecialEff': 'r' },
    21380: {
        'iMgcID': 2138,
        'iNameType': 2,
        'iResID': 2138,
        'sName': '',
        'sSpecialEff': 'b' },
    21381: {
        'iMgcID': 2138,
        'iNameType': 2,
        'iResID': 2138,
        'sName': '',
        'sSpecialEff': 'r' },
    23010: {
        'iMgcID': 2301,
        'iNameType': 1,
        'iResID': 2301,
        'sName': '',
        'sSpecialEff': 'b' },
    23060: {
        'iMgcID': 2306,
        'iNameType': 1,
        'iResID': 2306,
        'sName': '',
        'sSpecialEff': 'pu' },
    23140: {
        'iMgcID': 2314,
        'iNameType': 1,
        'iResID': 2314,
        'sName': '',
        'sSpecialEff': 'b' },
    23180: {
        'iMgcID': 2318,
        'iNameType': 1,
        'iResID': 2318,
        'sName': '',
        'sSpecialEff': 'p' },
    23190: {
        'iMgcID': 2319,
        'iNameType': 1,
        'iResID': 2319,
        'sName': '',
        'sSpecialEff': 'w' },
    23200: {
        'iMgcID': 2320,
        'iNameType': 1,
        'iResID': 2320,
        'sName': '',
        'sSpecialEff': 'w' },
    23210: {
        'iMgcID': 2321,
        'iNameType': 1,
        'iResID': 2321,
        'sName': '',
        'sSpecialEff': 'r' },
    23230: {
        'iMgcID': 2323,
        'iNameType': 1,
        'iResID': 2323,
        'sName': '',
        'sSpecialEff': 'p' },
    23330: {
        'iMgcID': 2333,
        'iNameType': 1,
        'iResID': 2333,
        'sName': '',
        'sSpecialEff': 'w' },
    23340: {
        'iMgcID': 2334,
        'iNameType': 1,
        'iResID': 2334,
        'sName': '',
        'sSpecialEff': 'w' },
    23990: {
        'iMgcID': 2399,
        'iNameType': 0,
        'iResID': 2301,
        'sName': '',
        'sSpecialEff': 'b' },
    24030: {
        'iMgcID': 2403,
        'iNameType': 1,
        'iResID': 2403,
        'sName': '',
        'sSpecialEff': 'r' },
    24050: {
        'iMgcID': 2405,
        'iNameType': 1,
        'iResID': 2405,
        'sName': '',
        'sSpecialEff': 'r' },
    24260: {
        'iMgcID': 2426,
        'iNameType': 1,
        'iResID': 2426,
        'sName': '',
        'sSpecialEff': 'r' },
    24290: {
        'iMgcID': 2429,
        'iNameType': 1,
        'iResID': 2429,
        'sName': '',
        'sSpecialEff': 'r' },
    24330: {
        'iMgcID': 2433,
        'iNameType': 1,
        'iResID': 2433,
        'sName': '',
        'sSpecialEff': 'r' },
    24340: {
        'iMgcID': 2434,
        'iNameType': 1,
        'iResID': 2434,
        'sName': '',
        'sSpecialEff': 'r' },
    24360: {
        'iMgcID': 2436,
        'iNameType': 2,
        'iResID': 2436,
        'sName': '',
        'sSpecialEff': 'g' },
    24361: {
        'iMgcID': 2436,
        'iNameType': 2,
        'iResID': 2436,
        'sName': '',
        'sSpecialEff': 'r' },
    24370: {
        'iMgcID': 2437,
        'iNameType': 2,
        'iResID': 2437,
        'sName': '',
        'sSpecialEff': 'w' },
    24371: {
        'iMgcID': 2437,
        'iNameType': 2,
        'iResID': 2437,
        'sName': '',
        'sSpecialEff': 'y' },
    24380: {
        'iMgcID': 2438,
        'iNameType': 2,
        'iResID': 2438,
        'sName': '',
        'sSpecialEff': 'r' },
    24381: {
        'iMgcID': 2438,
        'iNameType': 2,
        'iResID': 2438,
        'sName': '',
        'sSpecialEff': 'g' },
    26360: {
        'iMgcID': 2636,
        'iNameType': 3,
        'iResID': 26360,
        'sName': '' },
    26361: {
        'iMgcID': 2636,
        'iNameType': 0,
        'iResID': 26361,
        'sName': '' },
    26362: {
        'iMgcID': 2636,
        'iNameType': 3,
        'iResID': 26362,
        'sName': '' },
    26363: {
        'iMgcID': 2636,
        'iNameType': 0,
        'iResID': 26363,
        'sName': '' },
    26364: {
        'iMgcID': 2636,
        'iNameType': 3,
        'iResID': 26364,
        'sName': '' },
    26365: {
        'iMgcID': 2636,
        'iNameType': 0,
        'iResID': 26365,
        'sName': '' },
    26366: {
        'iMgcID': 2636,
        'iNameType': 3,
        'iResID': 26366,
        'sName': '' },
    26367: {
        'iMgcID': 2636,
        'iNameType': 0,
        'iResID': 26367,
        'sName': '' },
    26368: {
        'iMgcID': 2636,
        'iNameType': 3,
        'iResID': 26368,
        'sName': '' },
    26369: {
        'iMgcID': 2636,
        'iNameType': 0,
        'iResID': 26369,
        'sName': '' },
    45437: {
        'iMgcID': 0,
        'iNameType': 0,
        'iResID': 45437,
        'sName': '' },
    45438: {
        'iMgcID': 0,
        'iNameType': 0,
        'iResID': 45438,
        'sName': '' },
    45439: {
        'iMgcID': 0,
        'iNameType': 0,
        'iResID': 45439,
        'sName': '' } }
INNER_PERFORMDATA = { }
ONLYNEWLIST = [
    26360,
    26361,
    26362,
    26363,
    26364,
    26365,
    26366,
    26367,
    26368,
    26369]
INNERONLYNEWLIST = []
