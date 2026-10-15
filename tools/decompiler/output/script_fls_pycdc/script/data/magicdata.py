# pycdc 交叉复核产物 · script.fls entry 4329
# co_filename(原始)='script/data/magicdata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4329.pyc (Python 2.5)

TYPE2CLASS = {
    0: '\xa5\xfe\xb3\xa1',
    11: '\xbcC\xa9\xdb\xa6\xa1',
    12: '\xb5\xa7\xa9\xdb\xa6\xa1',
    13: '\xae\xb1\xa9\xdb\xa6\xa1',
    14: '\xa4M\xa9\xdb\xa6\xa1',
    15: '\xbaj\xa9\xdb\xa6\xa1',
    16: '\xb7t\xbe\xb9\xa9\xdb\xa6\xa1',
    17: '\xb0\xad\xa8\xa6\xa9\xdb\xa6\xa1',
    21: '\xa6\xf2\xbe\xc7',
    22: '\xb9D\xaea',
    23: '\xbe\xa7\xbe\xc7',
    24: '\xa7\xc5\xb3N',
    25: '\xb3\xb1\xb6\xa7\xb3N' }
NEEDWEAPON = {
    11: 0,
    12: 4,
    13: 3,
    14: 1,
    15: 2,
    16: 5 }

def GetData(id):
    
    try:
        return DATA[id]
    except KeyError:
        return {
            'name': '\xa5\xbc\xaa\xbe<%d>' % id,
            'desc': '\xa4\xa3\xa9\xfa\xa9\xdb\xa6\xa1',
            'type': 11,
            'invalid': True }



def IsDestMagic(iPerform, sDest):
    dData = GetData(iPerform)
    if dData.get('invalid', False):
        iMagicID = GetMapping(iPerform)
        if not iMagicID:
            iMagicID = iPerform
        
        dData = GetData(iMagicID)
        if not dData:
            return False
        
    
    sType = dData.get('magicphysic', '')
    return sType == sDest


def IsSpecial(idx):
    
    try:
        magicInfo = DATA[idx]
        return magicInfo['genre'] == '\xafS\xa7\xde'
    except KeyError:
        return False



def IsMagic(iMagicID):
    if iMagicID in DATA:
        return True
    else:
        return False


def GetMapping(id):
    
    try:
        return MAGIC_MAPPING[id]
    except KeyError:
        return id



def GetAllMagicByLiuPai(liupai, iClass, bIsRepetition = False):
    type = {
        1001: 11,
        1002: 14,
        1003: 15,
        1004: 13,
        1005: 12,
        1011: 16,
        1006: 23,
        1007: 22,
        1008: 21,
        1009: 25,
        1010: 24,
        1014: 17 }.get(liupai)
    if not type:
        return None
    
    skillLst = []
    normalSkillLst = []
    skillNamelst = []
    for magicID, dct in DATA.iteritems():
        if dct['type'] == type:
            if bIsRepetition is False:
                if dct['name'] not in skillNamelst:
                    skillNamelst.append(dct['name'])
                    if '\xa6\xca\xaf\xc5\xa9\xdb\xa6\xa1' in dct['genre']:
                        skillLst.append(magicID)
                    else:
                        normalSkillLst.append(magicID)
                
            elif '\xa6\xca\xaf\xc5\xa9\xdb\xa6\xa1' in dct['genre']:
                skillLst.append(magicID)
            else:
                normalSkillLst.append(magicID)
        bIsRepetition is False
    
    skillLst.extend(normalSkillLst)
    if liupai == 1006:
        idLst = None if iClass == 1 else (2338, 2339, 2341)
        for id in idLst:
            skillLst.remove(id)
        
    
    if liupai == 1001:
        skillLst.remove(1190)
    
    return skillLst


def GetPerformTypeBySkillID(iSkillID):
    import performorderdata
    typeDict = performorderdata.GetTypeData(1001)
    dSkillData = GetData(iSkillID)
    if dSkillData['stype'] in typeDict and iSkillID not in (2313, 2529):
        sPerformType = dSkillData['stype']
    else:
        sPerformType = dSkillData['class']
    return sPerformType


def GetRecommendSkillByType(iType, sAttr):
    import dlgcustommagic
    import warui
    import hero
    import defines
    readyMagicLst = dlgcustommagic.GetReadyMagic()
    iPlayerCareer = hero.GetProp('m_Class')
    if iType == 0:
        if iPlayerCareer == defines.CAREER_SS:
            iSkillLst = None if sAttr not in FSMAGIC_LIST else FSMAGIC_LIST[sAttr]
        elif iPlayerCareer == defines.CAREER_FS:
            iSkillLst = []
        elif sAttr not in ZSXIBIE_LIST:
            pass
        
        iSkillLst = ZSXIBIE_LIST[sAttr]
        for iSkillID in iSkillLst:
            if iSkillID in readyMagicLst:
                (_, bNot) = warui.GetMagicInfo(iSkillID)
                if not bNot:
                    return iSkillID
                
            bNot
        
    elif iPlayerCareer != defines.CAREER_ZS:
        iSkillLst = None if sAttr not in FSKANGXING_LIST else FSKANGXING_LIST[sAttr]
    elif sAttr not in ZSKANGXING_LIST:
        pass
    
    iSkillLst = ZSKANGXING_LIST[sAttr]
    for iSkillID in iSkillLst:
        if iSkillID in readyMagicLst:
            (_, bNot) = warui.GetMagicInfo(iSkillID)
            if not bNot:
                return iSkillID
            
        bNot
    

# WARNING: Decompyle incomplete
