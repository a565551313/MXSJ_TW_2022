# pycdc 交叉复核产物 · script.fls entry 3664
# co_filename(原始)='script/data/mxcarddata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3664.pyc (Python 2.5)


def GetCardInfo(iType, id):
    return (ATTENDANTDATA, MAGICDATA, WEAPONDATA)[iType].get(id)


def GetAttendantInfo(id):
    return ATTENDANTDATA.get(id)


def GetMagicInfo(id):
    return MAGICDATA.get(id)


def GetWeaponInfo(id):
    return WEAPONDATA.get(id)


def GetCardColor(iType, id):
    data = (ATTENDANTDATA, MAGICDATA, WEAPONDATA)[iType].get(id)
    color = {
        '\xb3p\xbb\xbb\xabL': '\xbb\xc9',
        '\xa4\xa4\xa5\xdf': '\xbb\xc8',
        '\xab\xd5\xad\xdf\xaa\xf8\xa6\xd1': '\xb5\xb5',
        '\xb6\xb3\xb5\xea\xa4W\xa5P': '\xaa\xf7',
        '\xadl\xa5\xcd': '\xbb\xc8' }[data['species']]
    return color


def GetCardCost(iType, cid):
    data = (ATTENDANTDATA, MAGICDATA, WEAPONDATA)[iType].get(cid)
    return data.get('cost', 0)

# WARNING: Decompyle incomplete
