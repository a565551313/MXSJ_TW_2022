# pycdc 交叉复核产物 · script.fls entry 1381
# co_filename(原始)='script/data/cookdata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1381.pyc (Python 2.5)


def HasData(iShape):
    return iShape in DATA


def GetData(iShape):
    if iShape in DATA:
        return DATA[iShape]
    else:
        return {
            'name': '\xa5\xbc\xaa\xbe<%d>' % iShape,
            'desc': '\xa4\xa3\xa9\xfa\xb5\xe6\xc3\xd0',
            'type': 0,
            'base_lv': 0,
            'learn_lv': 0,
            'max': 0,
            'feel': 0,
            'food': 0,
            'fp': 0,
            'mp': 0,
            'hp': 0,
            'invalid': True }


def GetCost(iShape):
    if iShape not in DATA:
        return -1
    
    dInfo = DATA[iShape]
    if 'cost' not in dInfo:
        if dInfo['feel'] == 0 and dInfo['food'] == 0:
            iEatCost = 0
            iPackCost = dInfo['base_lv']
        else:
            iEatCost = dInfo['base_lv'] / 2 + 5
            iPackCost = (dInfo['base_lv'] / 2 + 5) * 2
        iEatCost = int(iEatCost * 0.8)
        iPackCost = int(iPackCost * 0.8)
        dInfo['cost'] = (iEatCost, iPackCost)
    
    return dInfo['cost']

None = {
    'name': '\xacM\xb3\xb7\xa8I\xad\xbb\xb9T',
    'type': 1,
    'base_lv': 150,
    'learn_lv': 150,
    'feel': 5 } / 'max'
if 5:
    None[21446] = {
        'name': '\xb8U\xaa\xe1\xbeK\xa5P\xc5S',
        'type': 2,
        'base_lv': 150,
        'learn_lv': 150,
        'max': 5,
        'feel': 6,
        'food': 5,
        'fp': 0.5,
        'mp': 1.5,
        'hp': 1,
        'desc': '\xac\xc3\xa9_\xaa\xe1\xbbe\xb0t\xa5H\xc3\xa3\xbc\xdf\xa5\xc9\xc5S\xc6C\xa6\xa8\xa1A\xaf\xab\xa5P\xb9\xc1\xa4F\xa4]\xb3\xb3\xbeK\xa8\xe4\xa4\xa4#r\xa1i\xa4f\xa8\xfd\xa1j\xb2\xa2' }
None[21447] = {
    'name': '\xa4\xd1\xa4\xf5\xc5Q\xa4\xfd\xc3\xc9',
    'type': 0,
    'base_lv': 160,
    'learn_lv': 160,
    'max': 5,
    'feel': 6,
    'food': 5,
    'fp': 1.5,
    'mp': 0.5,
    'hp': 1,
    'desc': '\xc6F\xbc\xee\xa4\xa7\xc3\xc9\xa6\xf5\xa5H\xa9_\xb4\xd4\xa1A\xa5H\xa4\xa3\xb7\xc0\xc6F\xa4\xf5\xb2i\xb5N\xa6\xd3\xa6\xa8\xa1C\xbb\xb6\xa8\xfd\xc5Q\xb9D\xa1A\xad\xb9\xa5\xce\xab\xe1\xa8\xcf\xa4H\xabl\xa4O\xad\xbf\xbcW#r\xa1i\xa4f\xa8\xfd\xa1j\xbb\xb6' }
None[21448] = {
    'name': '\xb6\xb3\xae\xfc\xa5P\xb0\xd1\xb4\xf6',
    'type': 1,
    'base_lv': 160,
    'learn_lv': 160,
    'max': 5,
    'feel': 6,
    'food': 5,
    'fp': 1,
    'mp': 1,
    'hp': 1,
    'desc': '\xb6\xb3\xae\xfc\xa4\xa4\xaa\xba\xb8U\xa5j\xa5P\xb0\xd1\xa1A\xa4\xf0\xb6\xb7\xa5\xf4\xa6\xf3\xa6\xf5\xae\xc6\xa1A\xa4J\xa4\xf4\xbaC\xcdW\xa1A\xb6\xbc\xa4\xa7\xa8\xcf\xa4H\xb2\xe6\xadL\xb4\xab\xb0\xa9\xa1A\xc6F\xa5x\xb2M\xa9\xfa#r\xa1i\xa4f\xa8\xfd\xa1j\xad\xbb' }
None[21449] = {
    'name': '\xc3\xa3\xaaG\xa9\xc9\xa5P\xbf|',
    'type': 2,
    'base_lv': 160,
    'learn_lv': 160,
    'max': 5,
    'feel': 6,
    'food': 5,
    'fp': 0.5,
    'mp': 1.5,
    'hp': 1,
    'desc': '\xa4d\xa6~\xc3\xa3\xaaG\xa1A\xa8\xfa\xa5P\xae\xe8\xa5\xc4\xb2G\xa4J\xbf|\xa1A\xbe\xee\xb3\xaf\xc3\xa3\xaaG\xa9\xf3\xa4W\xa1C\xb2\xa2\xa8\xfd\xb1y\xb5M\xa1A\xa8\xcf\xa4H\xa6p\xb7\xf6\xa6p\xbeK#r\xa1i\xa4f\xa8\xfd\xa1j' }
DATA = None
