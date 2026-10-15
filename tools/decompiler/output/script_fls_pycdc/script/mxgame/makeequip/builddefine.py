# pycdc 交叉复核产物 · script.fls entry 4648
# co_filename(原始)='script/mxgame/makeequip/builddefine.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4648.pyc (Python 2.5)

import itemdefine
TYPE_REBUILD = 1
TYPE_BUILD = 2
TYPE_KEY_MENU_OR_NPC = 1
TYPE_KEY_SYMBOL = 2
TYPE_KEY_SALE = 3
TYPE_KEY_SUPER_SYMBOL = 4
TYPE_LV_UP_MSG = {
    TYPE_BUILD: '\xa7A\xa9\xd2\xa8\xcf\xa5\xce\xaa\xba\xa6\xca\xb7\xd2\xba\xeb\xc5K\xaa\xba\xb5\xa5\xaf\xc5\xb0\xaa\xa9\xf3\xbbs\xb3y\xab\xfc\xabn\xae\xd1\xa1A\xbbs\xb3y\xaa\xba\xb8\xcb\xb3\xc6\xb5\xa5\xaf\xc5\xb1N\xb7|\xb5\xa5\xa6P\xa9\xf3\xbbs\xb3y\xab\xfc\xabn\xae\xd1\xaa\xba\xb5\xa5\xaf\xc5\xa1A\xbd\xd0\xb0\xdd\xa7A\xacO\xadn\xab\xf6\xb7\xd3\xa6\xb9\xa4\xe8\xae\xd7\xbbs\xa7@\xb8\xcb\xb3\xc6',
    TYPE_REBUILD: '\xa7A\xa8\xcf\xa5\xce\xaa\xba\xb8\xcb\xb3\xc6\xad\xab\xb3y\xba\xeb\xb5\xd8\xaa\xba\xb5\xa5\xaf\xc5\xb0\xaa\xa9\xf3\xb8\xcb\xb3\xc6\xb5\xa5\xaf\xc5\xa1A\xacO\xa7_\xbb\xdd\xadn\xc4~\xc4\xf2\xbbs\xb3y' }
TAB_BUILD = 2
TAB_REBUILD = 3
TAB_GEM = 4
TAB_GOSSIP = 5
TAB_POINT = 6
TYPE_MAIN_DLG_BUILD = 'TYPE_DLG_BUILD'
TYPE_MAIN_DLG_REBUILD = 'TYPE_MAIN_DLG_REBUILD'
TYPE_MAIN_DLG_GEM = 'TYPE_MAIN_DLG_GEM'
TYPE_MAIN_DLG_TAB_GOSSIP = 'TYPE_MAIN_DLG_TAB_GOSSIP'
TYPE_MAIN_DLG_POINT = 'TYPE_MAIN_DLG_POINT'
TYPE_REBUIL_DLG_REBUIL = 'TYPE_REBUIL_DLG_REBUIL'
TYPE_REBUIL_DLG_INDENTIFY = 'TYPE_REBUIL_DLG_INDENTIFY'
TYPE_REBUIL_DLG_COMPOSITE = 'TYPE_REBUIL_DLG_COMPOSITE'
TYPE_REBUIL_DLG_SMELTING = 'TYPE_REBUIL_DLG_SMELTING'
TYPE_REBUIL_DLG_KAIQIAO_CHANGE = 'TYPE_REBUIL_DLG_KAIQIAO_CHANGE'
TYPE_EQUIP_STONE = 3
TYPE_EQUIP_IDENTIFY = 4
TYPE_SKILL_BUILD = 1111
TYPE_ITEM_BOOK = 1
TYPE_ITEM_IRON = 2
TYPE_ITEM_EQUIP = 3
TYPE_ITEM_ESSENCE = 4
TYPE_ITEM_IDENTIFY = 5
TYPE_ITEM_GOLD = 6
TYPE_ITEM_SYMBOL = 7
DIAGRAMS_REPLACE_STATE_NONE = 1
DIAGRAMS_REPLACE_STATE_APPLIED = 2
DIAGRAMS_REPLACE_STATE_ENABLED = 3
TYPE_PREVIEW_BASE = 1
TYPE_PREVIEW_RAMDON_1 = 2
TYPE_PREVIEW_RAMDON_2 = 3
TYPE_PREVIEW = {
    TYPE_PREVIEW_RAMDON_1: '\xc0H\xbe\xf7\xb0\xf2\xc2\xa6\xc4\xdd\xa9\xca\xa1G\xa5H\xa4U\xc4\xdd\xa9\xca\xc0H\xbe\xf7\xa5X\xb2{\xa4@\xba\xd8',
    TYPE_PREVIEW_RAMDON_2: '\xaa\xfe\xa5[\xc4\xdd\xa9\xca\xa1G\xa5H\xa4U\xc4\xdd\xa9\xca\xc0H\xbe\xf7\xa5X\xb2{\xa4@\xba\xd8',
    TYPE_PREVIEW_BASE: '\xa9T\xa9w\xb0\xf2\xc2\xa6\xc4\xdd\xa9\xca\xa1G\xa5H\xa4U\xc4\xdd\xa9\xca\xa5\xb2\xa9w\xa5X\xb2{' }
ID2Weapon = {
    1: '\xb4U\xa4l',
    2: '\xaaZ\xbe\xb9',
    3: '\xf1Z\xa5\xd2',
    4: '\xb8y\xb1a',
    5: '\xc5@\xb5\xc3',
    6: '\xaak\xc4_',
    7: '\xb6\xb5\xc3\xec',
    8: '\xa7\xd9\xab\xfc',
    9: '\xbec\xa4l' }
ATTR2NAME = {
    'Dam': '\xa7\xf0\xc0\xbb',
    'Magdef': '\xc6F\xa4O',
    'Spe': '\xb3t\xab\xd7',
    'Def': '\xa8\xbe\xbfm',
    'HP': '\xae\xf0\xa6\xe5',
    'SingleAttr': '\xb3\xe6\xc4\xdd\xa9\xca',
    'DoubleAttr': '\xc2\xf9\xc4\xdd\xa9\xca',
    'FP': '\xa4O\xb9D',
    'MP': '\xaak\xa4O',
    'MagSkill': '\xaak\xb3N\xacy\xac\xa3',
    'PhySkill': '\xaa\xab\xb2z\xacy\xac\xa3',
    'AllSkill': '\xa9\xd2\xa6\xb3\xacy\xac\xa3',
    'SingleSkill': '\xb3\xe6\xacy\xac\xa3',
    'DoubleSkill': '\xc2\xf9\xacy\xac\xa3',
    'TripleSkill': '\xa4T\xacy\xac\xa3',
    'ResMag': '\xa5\xfe\xa7\xdc\xa9\xca',
    'SingleRes': '\xb3\xe6\xa7\xdc\xa9\xca',
    'DoubleRes': '\xc2\xf9\xa7\xdc\xa9\xca' }
ATTR2SORT = {
    '\xa7\xf0\xc0\xbb': 1,
    '\xa8\xbe\xbfm': 2,
    '\xc6F\xa4O': 3,
    '\xae\xf0\xa6\xe5': 4,
    '\xb3t\xab\xd7': 5,
    '\xa4O\xb9D': 6,
    '\xaak\xa4O': 7,
    '\xb3\xe6\xa7\xdc\xa9\xca': 8,
    '\xc2\xf9\xa7\xdc\xa9\xca': 9,
    '\xa5\xfe\xa7\xdc\xa9\xca': 10,
    '\xb3\xe6\xc4\xdd\xa9\xca': 11,
    '\xc2\xf9\xc4\xdd\xa9\xca': 12,
    '\xaak\xb3N\xacy\xac\xa3': 16,
    '\xaa\xab\xb2z\xacy\xac\xa3': 17,
    '\xa9\xd2\xa6\xb3\xacy\xac\xa3': 18,
    '\xb3\xe6\xacy\xac\xa3': 13,
    '\xc2\xf9\xacy\xac\xa3': 14,
    '\xa4T\xacy\xac\xa3': 15 }
EQUIPID2BASEATTR = {
    itemdefine.EQUIP_SWORD: ('Dam',),
    itemdefine.EQUIP_PEN: ('Dam',),
    itemdefine.EQUIP_UNARMED: ('Dam',),
    itemdefine.EQUIP_BLADE: ('Dam',),
    itemdefine.EQUIP_STICK: ('Dam',),
    itemdefine.EQUIP_ARMOR: ('Def',),
    itemdefine.EQUIP_WAIST: ('HP', 'MP', 'FP'),
    itemdefine.EQUIP_NECKLACE: ('Def', 'Magdef', 'MP', 'FP'),
    itemdefine.EQUIP_HEAD: ('Def', 'FP', 'MP'),
    itemdefine.EQUIP_BOOT: ('Def', 'FP', 'MP', 'Spe'),
    itemdefine.EQUIP_GLOVE: ('Def',),
    itemdefine.EQUIP_RING: ('Def', 'Magdef'),
    itemdefine.EQUIP_MAGIC: ('Def', 'FP'),
    itemdefine.EQUIP_THROWING: ('Dam',) }
EQUIPID2JTATTR = {
    itemdefine.EQUIP_SWORD: ('Dam',),
    itemdefine.EQUIP_PEN: ('Dam',),
    itemdefine.EQUIP_UNARMED: ('Dam',),
    itemdefine.EQUIP_BLADE: ('Dam',),
    itemdefine.EQUIP_STICK: ('Dam',),
    itemdefine.EQUIP_ARMOR: ('Def',),
    itemdefine.EQUIP_WAIST: (),
    itemdefine.EQUIP_NECKLACE: ('Magdef',),
    itemdefine.EQUIP_HEAD: ('Def',),
    itemdefine.EQUIP_BOOT: ('Def',),
    itemdefine.EQUIP_GLOVE: ('Dam',),
    itemdefine.EQUIP_RING: ('Magdef',),
    itemdefine.EQUIP_MAGIC: (),
    itemdefine.EQUIP_THROWING: ('Dam',) }
RANDOM_ATTR = ('SingleAttr', 'DoubleAttr')
TYPE2NAME = {
    1: '\xbcC',
    2: '\xb5\xa7',
    3: '\xae\xb1',
    4: '\xa4M',
    5: '\xbaj',
    6: '\xf1Z\xa5\xd2',
    7: '\xb8y\xb1a',
    8: '\xb6\xb5\xc3\xec',
    9: '\xb4U\xa4l',
    10: '\xb9u',
    11: '\xc5@\xb5\xc3',
    12: '\xa7\xd9\xab\xfc',
    13: '\xaak\xc4_',
    14: '\xb7t\xbe\xb9' }
KEY_GAS_OPERATE = 'GAS_OPERATE'
TYPE_GAS_OPERATE_OPEN = 'TYPE_OPERATE_OPEN'
TYPE_GAS_OPERATE_UP = 'TYPE_GAS_OPERATE_UP'
ID2Bagua = {
    1: '\xa6a\xbfA\xc1{',
    2: '\xa4\xd1\xa4\xf5\xa6P\xa4H',
    3: '\xa4\xf4\xa4\xf5\xacJ\xc0\xd9',
    4: '\xa4s\xad\xb7\xc5\xdb',
    5: '\xad\xb7\xa4s\xba\xa5',
    6: '\xa4\xf5\xb9p\xbe\xbd\xb6\xdf',
    7: '\xb9p\xa6a\xbf\xdd',
    8: '\xbfA\xa4\xf4\xa7x',
    9: '\xbfA\xa4\xd1\xc9[',
    10: '\xa4\xd1\xa4\xf4\xb3^',
    11: '\xa4s\xb9p\xc0[',
    12: '\xad\xb7\xa6a\xc6[',
    17: '\xa4\xf5\xa4\xd1\xa4j\xa6\xb3',
    18: '\xa4\xf4\xa4s\xee\xbf',
    19: '\xbfA\xa6a\xb5\xd1',
    20: '\xb9p\xad\xb7\xf9\xda',
    13: '\xb0\xae\xac\xb0\xa4\xd1',
    14: '\xa7\xa2\xac\xb0\xa4\xf4',
    15: '\xb4S\xac\xb0\xad\xb7',
    16: '\xa6\xe1\xac\xb0\xa4s',
    21: '\xa9[\xac\xb0\xa6a',
    22: '\xc2\xf7\xac\xb0\xa4\xf5',
    23: '\xa7I\xac\xb0\xbfA',
    24: '\xbe_\xac\xb0\xb9p',
    25: '\xa6a\xa4\xf5\xa9\xfa\xa6i',
    26: '\xa4\xd1\xb9p\xb5L\xa6k',
    27: '\xa4\xf4\xa4\xd1\xbb\xdd',
    28: '\xa4s\xa4\xd1\xa4j\xafb',
    29: '\xad\xb7\xa4\xd1\xa4p\xafb' }
Bagua2ID = []([ (v, k) for k, v in ID2Bagua.items() ])
ATTR2TYPE = {
    'JIBEN_ATTR': 1,
    'JICHU_ATTR': 2,
    'FUJIA_ATTR': 3,
    'QITA_ATTR': 4,
    'TESHU_ATTR': 5 }
ATTRLIST = [
    '\xa7\xf0\xc0\xbb',
    '\xa8\xbe\xbfm',
    '\xc6F\xa4O',
    '\xae\xf0\xa6\xe5',
    '\xb3t\xab\xd7',
    '\xb3\xe6\xc4\xdd\xa9\xca',
    '\xc2\xf9\xc4\xdd\xa9\xca',
    '\xa4O\xb9D',
    '\xaak\xa4O',
    '\xaak\xb3N\xacy\xac\xa3',
    '\xaa\xab\xb2z\xacy\xac\xa3',
    '\xa9\xd2\xa6\xb3\xacy\xac\xa3',
    '\xb3\xe6\xacy\xac\xa3',
    '\xc2\xf9\xacy\xac\xa3',
    '\xa4T\xacy\xac\xa3',
    '\xa5\xfe\xa7\xdc\xa9\xca',
    '\xb3\xe6\xa7\xdc\xa9\xca',
    '\xc2\xf9\xa7\xdc\xa9\xca']
BaguaID2Zhenqi = {
    1: (8, 2),
    2: (1, 3),
    3: (6, 3),
    4: (7, 5),
    5: (5, 7),
    6: (3, 4),
    7: (4, 8, 2),
    8: (2, 6),
    9: (2, 1),
    10: (1, 6),
    11: (7, 4),
    12: (5, 8),
    13: (1, 1, 1),
    14: (6, 6, 6),
    15: (5, 5, 5),
    16: (7, 7, 7),
    17: (3, 1),
    18: (6, 7),
    19: (2, 8),
    20: (4, 5),
    21: (8, 8, 8),
    22: (3, 3, 3),
    23: (2, 2, 2),
    24: (4, 4, 4),
    25: (8, 8, 8),
    26: (1, 1, 1),
    27: (6, 6, 6),
    28: (7, 7, 7),
    29: (5, 5, 5) }
TIANJINCUI_TAB = {
    0: {
        2: (1, 1, 1, 1),
        3: (1, 1, 1, 1) },
    1: {
        2: (1, 2, 2, 4),
        3: (2, 2, 4, 8) },
    2: {
        2: (2, 3, 4, 8),
        3: (3, 4, 12, 16) },
    3: {
        2: (2, 4, 8, 12),
        3: (4, 8, 16, 24) } }
ID2Zhenqi = {
    1: '\xb0\xae\xae\xf0[1]',
    2: '\xa7I\xae\xf0[2]',
    3: '\xc2\xf7\xae\xf0[3]',
    4: '\xbe_\xae\xf0[4]',
    5: '\xb4S\xae\xf0[5]',
    6: '\xa7\xa2\xae\xf0[6]',
    7: '\xa6\xe1\xae\xf0[7]',
    8: '\xa9[\xae\xf0[8]' }
Gas2PinZhi = {
    '\xb5}\xc1\xa1': 1,
    '\xbb\xe9\xc2\xf8': 2,
    '\xb8Y\xb1K': 3,
    '\xba\xeb\xaf\xc2': 4 }
PinZhi2Gas = {
    1: '\xb5}\xc1\xa1',
    2: '\xbb\xe9\xc2\xf8',
    3: '\xb8Y\xb1K',
    4: '\xba\xeb\xaf\xc2' }
~JNRKhS^UjRwRst = [
    68501,
    68502,
    68503,
    68504,
    68505,
    68506,
    68507,
    68508,
    68509,
    68510,
    68511,
    68512,
    68513]
Type2ShapeList = {
    '\xaaZ\xbe\xb9': ((50000, 59999), (68001, 68041), (68501, 68505), 68513, 68361),
    '\xb4U\xa4l': ((60000, 60999),),
    '\xf1Z\xa5\xd2': ((61000, 61999),),
    '\xbec\xa4l': ((62000, 62999),),
    '\xc5@\xb5\xc3': ((63000, 63999),),
    '\xb6\xb5\xc3\xec': ((64000, 64999),),
    '\xa7\xd9\xab\xfc': ((65000, 65999),),
    '\xb8y\xb1a': ((66000, 66999),),
    '\xaak\xc4_': ((67000, 67999),) }
Material2Shape = {
    '\xa4p\xa4\xd1\xaa\xf7\xb2f': [
        26904,
        30117],
    '\xb0\xae\xae\xf0[1]': [
        26871],
    '\xa7I\xae\xf0[2]': [
        26872],
    '\xc2\xf7\xae\xf0[3]': [
        26873],
    '\xbe_\xae\xf0[4]': [
        26874],
    '\xb4S\xae\xf0[5]': [
        26875],
    '\xa7\xa2\xae\xf0[6]': [
        26876],
    '\xa6\xe1\xae\xf0[7]': [
        26877],
    '\xa9[\xae\xf0[8]': [
        26878],
    '\xa4K\xa8\xf6\xafu\xae\xf0': [
        73577] }
Material2ShapeNew = {
    '\xa4p\xa4\xd1\xaa\xf7\xb2f': [
        26904,
        30117],
    '\xa4K\xa8\xf6\xafu\xae\xf0': [
        73577] }
Bagua2Ratio = {
    1: 100,
    2: 100,
    3: 100,
    4: 100,
    5: 100,
    6: 40,
    8: 40,
    9: 40,
    10: 40,
    11: 40,
    12: 40,
    17: 40,
    18: 40,
    19: 35,
    20: 35,
    7: 40,
    13: 30,
    14: 30,
    15: 30,
    16: 30,
    21: 30,
    22: 100,
    23: 100,
    24: 100,
    25: 100,
    26: 100,
    27: 100,
    28: 100,
    29: 100 }
100[26] = {
    1: 100,
    2: 100,
    3: 100,
    4: 100,
    5: 100,
    6: 40,
    8: 40,
    9: 40,
    10: 40,
    11: 40,
    12: 40,
    17: 40,
    18: 40,
    19: 35,
    20: 35,
    7: 40,
    13: 40,
    14: 40,
    15: 40,
    16: 40,
    21: 40,
    22: 100,
    23: 100,
    24: 100,
    27: 100,
    28: 100,
    29: 100 } // 25
BAGUA2RATIONEW = {
    1: 100,
    2: 100,
    3: 100,
    4: 100,
    5: 100,
    6: 40,
    8: 40,
    9: 40,
    10: 40,
    11: 40,
    12: 40,
    17: 40,
    18: 40,
    19: 35,
    20: 35,
    7: 40,
    13: 40,
    14: 40,
    15: 40,
    16: 40,
    21: 40,
    22: 100,
    23: 100,
    24: 100,
    27: 100,
    28: 100,
    29: 100 }
TYPE2OBJECT = {
    TYPE_ITEM_BOOK: '\xae\xd1',
    TYPE_ITEM_IRON: '\xc5K',
    TYPE_ITEM_EQUIP: '\xaaZ\xbe\xb9',
    TYPE_ITEM_ESSENCE: '\xad\xab\xb3y\xba\xeb\xb5\xd8' }
TYPE_TO_NAME = {
    1: ('sword', itemdefine.EQUIP_SWORD),
    2: ('blade', itemdefine.EQUIP_BLADE),
    3: ('spear', itemdefine.EQUIP_STICK),
    4: ('fist', itemdefine.EQUIP_UNARMED),
    5: ('pen', itemdefine.EQUIP_PEN),
    6: ('anqi', itemdefine.EQUIP_THROWING),
    7: ('cap', itemdefine.EQUIP_HEAD),
    8: ('cloth', itemdefine.EQUIP_ARMOR),
    9: ('shoes', itemdefine.EQUIP_BOOT),
    10: ('cuff', itemdefine.EQUIP_GLOVE),
    11: ('necklace', itemdefine.EQUIP_NECKLACE),
    12: ('ring', itemdefine.EQUIP_RING),
    13: ('sash', itemdefine.EQUIP_TALISMAN),
    14: ('magic', itemdefine.EQUIP_MAGIC) }
MAKE_SKILL_BUILD = 1111
MAKE_SKILL_TAILOR = 1112
MAKE_SKILL_ALCHEMY = 1113
MALE_SKILL_NAME = 'MALE_SKILL_NAME'
MALE_SKILL_DATA = {
    MAKE_SKILL_BUILD: {
        MALE_SKILL_NAME: '\xa5\xb4\xb3y' },
    MAKE_SKILL_TAILOR: {
        MALE_SKILL_NAME: '\xb5\xf4\xc1_' },
    MAKE_SKILL_ALCHEMY: {
        MALE_SKILL_NAME: '\xb7\xd2\xaa\xf7' } }
EQUIPPOS2SKILL = {
    itemdefine.EQUIPPOS_CAP: MAKE_SKILL_TAILOR,
    itemdefine.EQUIPPOS_WEAPON: MAKE_SKILL_BUILD,
    itemdefine.EQUIPPOS_CLOTH: MAKE_SKILL_TAILOR,
    itemdefine.EQUIPPOS_SASH: MAKE_SKILL_TAILOR,
    itemdefine.EQUIPPOS_CUFF: MAKE_SKILL_BUILD,
    itemdefine.EQUIPPOS_MAGIC: MAKE_SKILL_ALCHEMY,
    itemdefine.EQUIPPOS_NECKLACE: MAKE_SKILL_ALCHEMY,
    itemdefine.EQUIPPOS_RING: MAKE_SKILL_ALCHEMY,
    itemdefine.EQUIPPOS_SHOSE: MAKE_SKILL_TAILOR }
SKILL2SALELEVELTYPE = {
    MAKE_SKILL_BUILD: 'dazao',
    MAKE_SKILL_TAILOR: 'caifeng',
    MAKE_SKILL_ALCHEMY: 'lianjin' }
SKILL_TO_WEAPON_TYPE = {
    1111: [
        itemdefine.EQUIP_SWORD,
        itemdefine.EQUIP_BLADE,
        itemdefine.EQUIP_STICK,
        itemdefine.EQUIP_PEN,
        itemdefine.EQUIP_UNARMED,
        itemdefine.EQUIP_THROWING,
        itemdefine.EQUIP_GLOVE],
    1112: [
        itemdefine.EQUIP_ARMOR,
        itemdefine.EQUIP_WAIST,
        itemdefine.EQUIP_HEAD,
        itemdefine.EQUIP_BOOT],
    1113: [
        itemdefine.EQUIP_MAGIC,
        itemdefine.EQUIP_NECKLACE,
        itemdefine.EQUIP_RING] }
WEAPON_TYPE_TO_SKILL = {
    itemdefine.EQUIP_SWORD: 1111,
    itemdefine.EQUIP_BLADE: 1111,
    itemdefine.EQUIP_STICK: 1111,
    itemdefine.EQUIP_PEN: 1111,
    itemdefine.EQUIP_UNARMED: 1111,
    itemdefine.EQUIP_THROWING: 1111,
    itemdefine.EQUIP_GLOVE: 1111,
    itemdefine.EQUIP_ARMOR: 1112,
    itemdefine.EQUIP_WAIST: 1112,
    itemdefine.EQUIP_HEAD: 1112,
    itemdefine.EQUIP_BOOT: 1112,
    itemdefine.EQUIP_MAGIC: 1113,
    itemdefine.EQUIP_NECKLACE: 1113,
    itemdefine.EQUIP_RING: 1113 }
SKILL_ID_TO_EQUIP_TYPE = {
    1001: itemdefine.EQUIP_SWORD,
    1002: itemdefine.EQUIP_BLADE,
    1003: itemdefine.EQUIP_STICK,
    1004: itemdefine.EQUIP_UNARMED,
    1005: itemdefine.EQUIP_PEN,
    1011: itemdefine.EQUIP_THROWING }

def GetLiupai2WeaponType(iLiupai):
    '''
\t\xacy\xac\xa3ID\xc0\xf2\xb1o\xaaZ\xbe\xb9\xc3\xfe\xab\xac
\t:param iLiupai:
\t:return: \xaaZ\xbe\xb9\xc3\xfe\xab\xac
\t'''
    return SKILL_ID_TO_EQUIP_TYPE.get(iLiupai)

LV_TO_RE_BUILD_SHAPE = {
    0: 70611,
    10: 70611,
    20: 70611,
    30: 70611,
    40: 70611,
    50: 70612,
    60: (70613, 30411),
    70: (70614, 30412),
    80: (70615, 30413),
    90: (70616, 30414),
    100: (70617, 30415),
    110: (70618, 30416),
    120: 70619,
    130: 70620,
    140: 70746 }

def IsReBuildShape(iShape):
    for idx, oValue in LV_TO_RE_BUILD_SHAPE.iteritems():
        if isinstance(oValue, int) and oValue == iShape:
            return True
            continue
        if isinstance(oValue, tuple) and iShape in oValue:
            return True
            continue
    
    return False

OBJECT2TYPE = []([ (v, k) for k, v in TYPE2OBJECT.items() ])
KEY_MAKE_MONEY = 'KEY_MAKE_MONEY'
KEY_MONEY_POWER = 'KEY_MONEY_POWER'
KEY_MONEY_CHECK_UP = 'KEY_MONEY_CHECK_UP'
KEY_MONEY_BUY_SYMBOL_MAKE = 'KEY_MONEY_BUY_SYMBOL_MAKE'
KEY_MONEY_SAVING = 'KEY_MONEY_SAVING'
KEY_WEAPON_STONE_NUM = 'KEY_WEAPON_STONE_NUM'
KEY_TI_LI = 'KEY_TI_LI'
KEY_SKILL_LV = 'KEY_SKILL_LV'
KEY_WEAPON_GRADE = 'KEY_WEAPON_GRADE'
KEY_MAKE_GOLD = 'KEY_MAKE_GOLD'
KEY_PREVIEW_ITEM = 'KEY_PREVIEW_ITEM'
KEY_RPLCASH = 'KEY_RPLCASH'
KEY_RESUME_TYPE = 'KEY_RESUME_TYPE'
KEY_RESUME_VALUE = 'KEY_RESUME_VALUE'
KEY_CZPAY_TYPE = 'KEY_CZPAY_TYPE'
KEY_CZPAY_VALUE = 'KEY_CZPAY_VALUE'
KEY_ZZFPAY_TYPE = 'KEY_ZZFPAY_TYPE'
KEY_ZZFPAY_VALUE = 'KEY_ZZFPAY_VALUE'
RESUMETYPE_GOLD = 1
RESUMETYPE_MXB = 2
RESUMETYPE_RPLCASH = 3
RESUMETYPE_CASH = 4
MAKE_INFO_DATA = {
    KEY_MAKE_MONEY: 0,
    KEY_MONEY_POWER: 0,
    KEY_MONEY_CHECK_UP: 0,
    KEY_MONEY_BUY_SYMBOL_MAKE: 0,
    KEY_WEAPON_STONE_NUM: 0,
    KEY_TI_LI: 0,
    KEY_SKILL_LV: 0,
    KEY_WEAPON_GRADE: 0,
    KEY_MAKE_GOLD: 0,
    KEY_RPLCASH: 0,
    KEY_PREVIEW_ITEM: [],
    KEY_RESUME_TYPE: RESUMETYPE_RPLCASH,
    KEY_RESUME_VALUE: 0,
    KEY_MONEY_SAVING: 0 }
MAX_SKILL_LV = 200
MAX_ITEM_POS = 999
TYPE_SMELTING_NONE = 0
TYPE_SMELTING_APPLY = 1
TYPE_SMELTING_MAKE_SURE = 2
TYPE_SMELTING_CANCEL = 3
KEY_SMELTING_MODE = 'KEY_SMELTING_MODE'
KEY_SMELTING_FRACTION = 'KEY_SMELTING_FRACTION'
KEY_SMELTING_NEED_TIME = 'KEY_SMELTING_NEED_TIME'
KEY_SMELTING_LAST_TIME = 'KEY_SMELTING_LAST_TIME'
DATA_SMELTING = {
    KEY_SMELTING_MODE: TYPE_SMELTING_NONE,
    KEY_SMELTING_FRACTION: 0,
    KEY_SMELTING_NEED_TIME: 0,
    KEY_SMELTING_LAST_TIME: 0 }
TYPE_MONEY_CASH = 'TYPE_MONEY_CASH'
TYPE_MONEY_GOLD = 'TYPE_MONEY_GOLD'
TYPE_MONEY_MX_CASH = 'TYPE_MONEY_MX_CASH'
KEY_NEED_INDEX = 'KEY_NEED_INDEX'
KEY_NEED_SHAPE = 'KEY_NEED_SHAPE'
KEY_NEED_ITEM_LV = 'KEY_NEED_ITEM_LV'
KEY_NEED_ITEM_CLASS = 'KEY_NEED_ITEM_CLASS'
KEY_NEED_ITEM_NAME = 'KEY_NEED_ITEM_NAME'
KEY_NEED_GOLD = 'KEY_NEED_GOLD'
KEY_NEED_MXB = 'KEY_NEED_MXB'
KEY_NEED_CASH = 'KEY_NEED_CASH'
KEY_NEED_AMOUNT = 'KEY_NEED_AMOUNT'
KEY_NEED_AMOUNT_TYPE = 'KEY_NEED_AMOUNT_TYPE'
KEY_NEED_AMOUNT_SUM = 'KEY_NEED_AMOUNT_SUM'
DATA_NEED_ITEM = {
    KEY_NEED_SHAPE: 0,
    KEY_NEED_ITEM_LV: 0,
    KEY_NEED_ITEM_CLASS: 0,
    KEY_NEED_ITEM_NAME: '',
    KEY_NEED_GOLD: 0,
    KEY_NEED_MXB: 0,
    KEY_NEED_CASH: 0,
    KEY_NEED_AMOUNT: 1,
    KEY_NEED_AMOUNT_TYPE: 0,
    KEY_NEED_AMOUNT_SUM: 0 }
TYPE_NEED_ITEM = 'TYPE_NEED_ITEM'
DIANHUA_PAGE_DIANHUA = 'DIANHUA_DIANHUA'
DIANHUA_PAGE_FUMO = 'DIANHUA_FUMO'
DIANHUA_PAGE_REPAIR = 'DIANHUA_REPAIR'
DIANHUA_PAGE_TRAN = 'DIANHUA_TRAN'
DIANHUATYPE_RANDOM = 0
DIANHUATYPE_STR = 1
DIANHUATYPE_CON = 2
DIANHUATYPE_MAG = 3
DIANHUATYPE_CHA = 4
DIANHUATYPE_DEX = 5
DIANHUATYPE_CHOOSE = 6
DIANHUATYPE_2NAME = {
    DIANHUATYPE_STR: '\xa4O\xb6q',
    DIANHUATYPE_CON: '\xc5\xe9\xbd\xe8',
    DIANHUATYPE_MAG: '\xc5]\xa4O',
    DIANHUATYPE_CHA: '\xbey\xa4O',
    DIANHUATYPE_DEX: '\xb1\xd3\xb1\xb6' }
OPEN_QUICKBUYDLG_2XIULIAN = 1
SHAPE_MAX_GEM = 26015
KEY_MAKE_SYMBOL_VITALITY = 'KEY_MAKE_SYMBOL_VITALITY'
DATA_MAKE_SYMBOL = {
    KEY_MAKE_SYMBOL_VITALITY: 0 }
COLOR_NEED = '#cff7200'
KEY_OPEN_AUTO_MAKE = 'KEY_OPEN_AUTO_MAKE'
KEY_AUTO_MAKE_FLAG = 'KEY_AUTO_MAKE_FLAG'
FLAG_KEY_TJ = 1
FLAG_KEY_TX = 2
FLAG_KEY_GOOD = 4

def LogMakeEquip(*args):
    LOG_DEBUG('>>>>>>>>>>>>>>LogMakeEquip>>>>>>>>>>>>>>>>>>')
    LOG_DEBUG(*args)
    LOG_DEBUG('<<<<<<<<<<<<<<LogMakeEquip<<<<<<<<<<<<<<<<<<')
