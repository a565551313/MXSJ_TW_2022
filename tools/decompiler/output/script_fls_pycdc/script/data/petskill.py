# pycdc 交叉复核产物 · script.fls entry 3205
# co_filename(原始)='script/data/petskill.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3205.pyc (Python 2.5)


def GetData(id):
    
    try:
        return DATA[id]
    except KeyError:
        return {
            'type': 0,
            'name': '\xa5\xbc\xaa\xbe<%d>' % id,
            'desc': '\xa4\xa3\xa9\xfa\xa7\xde\xaf\xe0',
            'fpneed': '0',
            'mpneed': '0' }



def GetShape(id):
    if ICON_MAPPING.get(id):
        return ICON_MAPPING[id]
    elif DATA.get(id):
        return id
    else:
        return 0


def GetSkillID(name):
    for skillID, desc in DATA.items():
        if desc['name'] == name:
            return skillID
            continue
    


def GetDataByName(name):
    for skillID, desc in DATA.items():
        if desc['name'] == name:
            return desc
            continue
    


def GetPetSkillNameById(iID):
    if DATA.has_key(iID):
        return DATA[iID]['name']
    
    return ''


def IsPetSkill(iSkillID):
    return iSkillID in DATA

ICON_MAPPING = {
    155: 129,
    255: 229,
    355: 329,
    299: 220,
    298: 219,
    297: 222,
    197: 117,
    599: 515,
    191: 111,
    196: 116,
    198: 118,
    296: 230 }
# WARNING: Decompyle incomplete
