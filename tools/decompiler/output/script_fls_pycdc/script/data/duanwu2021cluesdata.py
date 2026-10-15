# pycdc 交叉复核产物 · script.fls entry 318
# co_filename(原始)='script/data/duanwu2021cluesdata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_318.pyc (Python 2.5)


def GetAllCluesByMysteryID(iID):
    lClues = []
    for dItem in DATA.itervalues():
        if dItem['MysteryID'] == iID:
            lClues.append(dItem['Clues'])
            continue
    
    return lClues


def GetCluesByID(iID):
    if iID not in DATA:
        return ''
    
    return DATA[iID]['Clues']


def GetHideData():
    return [
        '???',
        '???',
        '???']

'C' / {
    'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xb0]\xb0g',
    'MysteryID': 4245 } ** 'Type'[1108] = {
    'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xb0]\xb0g',
    'MysteryID': 4245 }
DATA = {
    1001: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xba\xf1\xb7N\xa4p\xc2\xed',
        'MysteryID': 4248,
        'Type': 'A' },
    1002: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xaaF\xa4\xe8\xa4p\xc2\xed',
        'MysteryID': 4248,
        'Type': 'A' },
    1003: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xb0]\xaf\xab\xa8\xb5\xb9C\xa4\xa7\xa6a',
        'MysteryID': 4248,
        'Type': 'A' },
    1004: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa6\xd1\xa4H',
        'MysteryID': 4248,
        'Type': 'B' },
    1005: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa5\xd5\xc5\xbd',
        'MysteryID': 4248,
        'Type': 'B' },
    1006: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xacb\xa7\xfa',
        'MysteryID': 4248,
        'Type': 'B' },
    1007: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa5\xd5\xbev',
        'MysteryID': 4248,
        'Type': 'B' },
    1008: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa4\xd2\xa4l',
        'MysteryID': 4248,
        'Type': 'C' },
    1009: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa6\xd1\xaev',
        'MysteryID': 4248,
        'Type': 'C' },
    1010: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xb1\xd0\xae\xd1\xa8|\xa4H',
        'MysteryID': 4248,
        'Type': 'C' },
    1011: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xa4\xeb\xb7\xd3\xa4\xa7\xab\xb0',
        'MysteryID': 4349,
        'Type': 'A' },
    1012: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xc1c\xb5\xd8\xa4\xa7\xab\xb0',
        'MysteryID': 4349,
        'Type': 'A' },
    1013: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xc5]\xb1\xda\xa4J\xabI\xb2\xd7\xc2I',
        'MysteryID': 4349,
        'Type': 'A' },
    1014: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa4\xa4\xa6~\xa4H',
        'MysteryID': 4349,
        'Type': 'B' },
    1015: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa9x\xb3T\xa5[\xa8\xad',
        'MysteryID': 4349,
        'Type': 'B' },
    1016: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa4\xe2\xab\xf9\xa5\xc9\xaaO',
        'MysteryID': 4349,
        'Type': 'B' },
    1017: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xafQ\xaf\xbd\xb4U',
        'MysteryID': 4349,
        'Type': 'B' },
    1018: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xb4I\xbb\xa8',
        'MysteryID': 4349,
        'Type': 'C' },
    1019: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa9x\xad\xfb',
        'MysteryID': 4349,
        'Type': 'C' },
    1020: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xc1\xbf\xa8s\xa6W\xc5A',
        'MysteryID': 4349,
        'Type': 'C' },
    1021: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xba\xf1\xb7N\xb0\xea\xb3\xa3',
        'MysteryID': 4330,
        'Type': 'A' },
    1022: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xa7g\xa5D\xc2\xed\xa6u',
        'MysteryID': 4330,
        'Type': 'A' },
    1023: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xaaL\xa4\xa4\xa4\xa7\xab\xb0',
        'MysteryID': 4330,
        'Type': 'A' },
    1024: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xb3\xb1\xb6\xa7\xaak\xa7\xfa',
        'MysteryID': 4330,
        'Type': 'B' },
    1025: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa8\xad\xac\xef\xb9D\xb3T',
        'MysteryID': 4330,
        'Type': 'B' },
    1026: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xc0Y\xc0\xb9\xb5\xb5\xaba',
        'MysteryID': 4330,
        'Type': 'B' },
    1027: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa5\xd5\xc5\xbd',
        'MysteryID': 4330,
        'Type': 'B' },
    1028: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xb0\xea\xaev',
        'MysteryID': 4330,
        'Type': 'C' },
    1029: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xaa\xf8\xa6\xd1',
        'MysteryID': 4330,
        'Type': 'C' },
    1030: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa4H\xbbP\xb4\xcb\xaaL',
        'MysteryID': 4330,
        'Type': 'C' },
    1031: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xabn\xa4\xe8\xa7\xf8\xc2\xed',
        'MysteryID': 4202,
        'Type': 'A' },
    1032: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xc1{\xae\xfc\xa7\xf8\xb2\xf8',
        'MysteryID': 4202,
        'Type': 'A' },
    1033: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xaaw\xaaw\xb9M\xa6a',
        'MysteryID': 4202,
        'Type': 'A' },
    1034: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xb0\xfc\xa4k',
        'MysteryID': 4202,
        'Type': 'B' },
    1035: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa4\xa5\xba\xa1',
        'MysteryID': 4202,
        'Type': 'B' },
    1036: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa4\xe2\xab\xf9\xb5\xb7\xa4y',
        'MysteryID': 4202,
        'Type': 'B' },
    1037: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xb5\xb5\xb5o',
        'MysteryID': 4202,
        'Type': 'B' },
    1038: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa5D\xb0\xfc',
        'MysteryID': 4202,
        'Type': 'C' },
    1039: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xaea\xaa\xf8',
        'MysteryID': 4202,
        'Type': 'C' },
    1040: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xbc\xf6\xa4\xdf\xa4j\xb6\xfd',
        'MysteryID': 4202,
        'Type': 'C' },
    1041: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xae\xfc\xa5~\xa4\xa7\xa6a',
        'MysteryID': 4348,
        'Type': 'A' },
    1042: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xa8\xe2\xad\xd3\xa5\xa8\xa4j\xae\xfc\xc1\xb3',
        'MysteryID': 4348,
        'Type': 'A' },
    1043: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xaaw\xaaw\xb9M\xa6a',
        'MysteryID': 4348,
        'Type': 'A' },
    1044: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xabC\xa6~',
        'MysteryID': 4348,
        'Type': 'B' },
    1045: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xabT\xa8q',
        'MysteryID': 4348,
        'Type': 'B' },
    1046: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa4\xe2\xab\xf9\xae\xd1\xa8\xf7',
        'MysteryID': 4348,
        'Type': 'B' },
    1047: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xae\xd1\xa5\xcd\xb3T',
        'MysteryID': 4348,
        'Type': 'B' },
    1048: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xae\xd1\xa5\xcd',
        'MysteryID': 4348,
        'Type': 'C' },
    1049: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xb8\xd6\xa4H',
        'MysteryID': 4348,
        'Type': 'C' },
    1050: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa8q\xa4~',
        'MysteryID': 4348,
        'Type': 'C' },
    1051: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xaaF\xa4\xe8\xa4p\xc2\xed',
        'MysteryID': 4265,
        'Type': 'A' },
    1052: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xb0]\xaf\xab\xa8\xb5\xb9C\xa4\xa7\xa6a',
        'MysteryID': 4265,
        'Type': 'A' },
    1053: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xb6\xc0\xa4g\xa4s\xa8\xa6',
        'MysteryID': 4265,
        'Type': 'A' },
    1054: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa6\xa8\xa6~\xa8k\xa9\xca',
        'MysteryID': 4265,
        'Type': 'B' },
    1055: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa6\xbd\xa4y',
        'MysteryID': 4265,
        'Type': 'B' },
    1056: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xb5\xb5\xa6\xe2\xb8y\xb1a',
        'MysteryID': 4265,
        'Type': 'B' },
    1057: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa7\xa7\xba~',
        'MysteryID': 4265,
        'Type': 'B' },
    1058: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa7\xf3\xa4\xd2',
        'MysteryID': 4265,
        'Type': 'C' },
    1059: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa6u\xa4s\xa4H',
        'MysteryID': 4265,
        'Type': 'C' },
    1060: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa8\xb5\xc5\xde\xad\xfb',
        'MysteryID': 4265,
        'Type': 'C' },
    1061: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xb7\xa6\xbe\xf0\xa8F\xc5y',
        'MysteryID': 4308,
        'Type': 'A' },
    1062: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xa4@\xad\xd3\xa5\xa8\xab\xac\xae\xfc\xc1\xb3',
        'MysteryID': 4308,
        'Type': 'A' },
    1063: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xa5|\xb8t\xc3~\xc1{\xa6a',
        'MysteryID': 4308,
        'Type': 'A' },
    1064: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xc2\xc5\xb5\xb7\xb8\xc8',
        'MysteryID': 4308,
        'Type': 'B' },
    1065: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa6\xe7\xb1a\xc4\xc6\xc4\xc6',
        'MysteryID': 4308,
        'Type': 'B' },
    1066: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xba\xea\xb5o',
        'MysteryID': 4308,
        'Type': 'B' },
    1067: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa4\xd6\xa4k',
        'MysteryID': 4308,
        'Type': 'B' },
    1068: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa4j\xaea\xbb\xd3\xa8q',
        'MysteryID': 4308,
        'Type': 'C' },
    1069: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xc6[\xae\xfc\xb2Q\xa4k',
        'MysteryID': 4308,
        'Type': 'C' },
    1070: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa4d\xaa\xf7\xa4p\xa9j',
        'MysteryID': 4308,
        'Type': 'C' },
    1071: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xb4I\xb1f\xb3\xa3\xab\xb0',
        'MysteryID': 4228,
        'Type': 'A' },
    1072: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xa7g\xa5D\xc2\xed\xa6u',
        'MysteryID': 4228,
        'Type': 'A' },
    1073: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xa5\xad\xad\xec\xa4\xa7\xb0\xea',
        'MysteryID': 4228,
        'Type': 'A' },
    1074: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa6\xa8\xa6~\xa8k\xa9\xca',
        'MysteryID': 4228,
        'Type': 'B' },
    1075: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xc2\xc5\xa6\xe2\xc0Y\xa4y',
        'MysteryID': 4228,
        'Type': 'B' },
    1076: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xab\xf9\xa4M\xa4j\xba~',
        'MysteryID': 4228,
        'Type': 'B' },
    1077: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xb6\xc0\xb0\xa8\xa5\xd2',
        'MysteryID': 4228,
        'Type': 'B' },
    1078: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xadx\xa9x',
        'MysteryID': 4228,
        'Type': 'C' },
    1079: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xaa\xf8\xa9x',
        'MysteryID': 4228,
        'Type': 'C' },
    1080: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xaaZ\xaev',
        'MysteryID': 4228,
        'Type': 'C' },
    1081: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xc5]\xb1\xda\xa4J\xabI\xa4\xa7\xb8\xf4',
        'MysteryID': 4326,
        'Type': 'A' },
    1082: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xc6F\xb6\xf0\xc1q\xa5\xdf',
        'MysteryID': 4326,
        'Type': 'A' },
    1083: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xa5|\xb8t\xc3~\xc1{\xa6a',
        'MysteryID': 4326,
        'Type': 'A' },
    1084: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xbf\xdf\xa6\xd5',
        'MysteryID': 4326,
        'Type': 'B' },
    1085: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xb5\xb3\xa4\xf2',
        'MysteryID': 4326,
        'Type': 'B' },
    1086: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xb2\xd3\xa7\xc0',
        'MysteryID': 4326,
        'Type': 'B' },
    1087: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa7Q\xa4\xf6',
        'MysteryID': 4326,
        'Type': 'B' },
    1088: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xc3~\xb1\xda',
        'MysteryID': 4326,
        'Type': 'C' },
    1089: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa4p\xa7\xaf',
        'MysteryID': 4326,
        'Type': 'C' },
    1090: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xb7R\xa6Y\xb3\xbd',
        'MysteryID': 4326,
        'Type': 'C' },
    1091: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xb6\xb3\xba\xdd\xa4\xa7\xab\xb0',
        'MysteryID': 4332,
        'Type': 'A' },
    1092: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xa7g\xa5D\xc2\xed\xa6u',
        'MysteryID': 4332,
        'Type': 'A' },
    1093: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xb6\xc0\xa4g\xb0\xaa\xad\xec',
        'MysteryID': 4332,
        'Type': 'A' },
    1094: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa4\xd6\xa4k',
        'MysteryID': 4332,
        'Type': 'B' },
    1095: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa4\xe2\xab\xf9\xaa\xf8\xbcC',
        'MysteryID': 4332,
        'Type': 'B' },
    1096: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xb5\xb5\xa6\xe2\xb8y\xb1a',
        'MysteryID': 4332,
        'Type': 'B' },
    1097: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xac\xf5\xa6\xe2\xb0\xa8\xa7\xc0',
        'MysteryID': 4332,
        'Type': 'B' },
    1098: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa4k\xabL',
        'MysteryID': 4332,
        'Type': 'C' },
    1099: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa4y\xb9\xf6',
        'MysteryID': 4332,
        'Type': 'C' },
    1100: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa4k\xa4\xa4\xbb\xa8\xaaN',
        'MysteryID': 4332,
        'Type': 'C' },
    1101: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xb9\xda\xa4\xdb\xaec\xb7\xb5',
        'MysteryID': 4245,
        'Type': 'A' },
    1102: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xa7g\xa5D\xc2\xed\xa6u',
        'MysteryID': 4245,
        'Type': 'A' },
    1103: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xae\xfc\xa5~\xa4\xa7\xa6a',
        'MysteryID': 4245,
        'Type': 'A' },
    1104: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xb6\xc0\xb4U',
        'MysteryID': 4245,
        'Type': 'B' },
    1105: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa4\xe2\xb4\xa3\xa4\xf4\xb3\xfd',
        'MysteryID': 4245,
        'Type': 'B' },
    1106: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xaa\xd3\xa9\xdc\xa6\xbd\xa4y',
        'MysteryID': 4245,
        'Type': 'B' },
    1107: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xc2\xc5\xb8y\xb1a',
        'MysteryID': 4245,
        'Type': 'B' },
    1109: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xbd\xe4\xae{',
        'MysteryID': 4245,
        'Type': 'C' },
    1110: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa4\xa3\xa8}\xabC\xa6~',
        'MysteryID': 4245,
        'Type': 'C' },
    1111: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xbd_\xc1J\xa4p\xb7\xcb',
        'MysteryID': 4220,
        'Type': 'A' },
    1112: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xac\xf5\xb8\xad\xc4\xc6\xb8\xa8',
        'MysteryID': 4220,
        'Type': 'A' },
    1113: {
        'Clues': '\xa6a\xc2I\xbdu\xaf\xc1\xa1G\xa5\xad\xad\xec\xa4\xa7\xa6a',
        'MysteryID': 4220,
        'Type': 'A' },
    1114: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xac\xf5\xa8{\xb0\xc2',
        'MysteryID': 4220,
        'Type': 'B' },
    1115: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa4p\xc4|\xa4l',
        'MysteryID': 4220,
        'Type': 'B' },
    1116: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xa8\xaa\xb8}',
        'MysteryID': 4220,
        'Type': 'B' },
    1117: {
        'Clues': '\xa5~\xa7\xce\xbdu\xaf\xc1\xa1G\xaa\xf8\xa9R\xc2\xea',
        'MysteryID': 4220,
        'Type': 'B' },
    1118: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa8\xe0\xb5\xa3',
        'MysteryID': 4220,
        'Type': 'C' },
    1119: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa8k\xab\xc4',
        'MysteryID': 4220,
        'Type': 'C' },
    1120: {
        'Clues': '\xa8\xad\xa5\xf7\xbdu\xaf\xc1\xa1G\xa4p\xa4\xe5\xa6\xb1\xacP',
        'MysteryID': 4220,
        'Type': 'C' },
    9996: {
        'Clues': '1,2,3,4,5,6,7',
        'MysteryID': 1,
        'Type': '' },
    9997: {
        'Clues': '1,2,3,4,5,6,7,8,9',
        'MysteryID': 2,
        'Type': '' },
    9998: {
        'Clues': '1,2,3,4,5,6,7,8,9,10,11,12',
        'MysteryID': 3,
        'Type': '' },
    9999: {
        'Clues': '1,2,3,4,5,6,7,8,9,10,11,12',
        'MysteryID': 4,
        'Type': '' } }
