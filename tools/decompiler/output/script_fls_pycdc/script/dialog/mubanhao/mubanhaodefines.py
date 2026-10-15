# pycdc 交叉复核产物 · script.fls entry 3197
# co_filename(原始)='script/dialog/mubanhao/mubanhaodefines.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3197.pyc (Python 2.5)

PAGE_SHUXING = 1
PAGE_SKILL = 2
PAGE_XINFA = 3
PAGE_EQUIP = 4
PAGE_HORSE = 5
PAGE_XIULIAN = 6
PAGE_PET = 7
PAGE_RESOURE = 8
GRADE_BTN_30 = 30
GRADE_BTN_69 = 69
GRADE_BTN_89 = 89
GRADE_BTN_110 = 110
GRADE_BTN_140 = 140
LEVEL_LOW = 1
LEVEL_MID = 2
LEVEL_HIGH = 3
CLASS_TO_ADD_DOT = {
    0: [
        2,
        6,
        0,
        0,
        0],
    1: [
        2,
        0,
        6,
        0,
        0],
    2: [
        2,
        0,
        0,
        4,
        2],
    3: [
        2,
        0,
        0,
        2,
        4] }
EQUIP_LOC = (('loc_cap', '\xb4U\xa4l'), ('loc_weapon', '\xaaZ\xbe\xb9'), ('loc_cloth', '\xf1Z\xa5\xd2'), ('loc_sash', '\xb8y\xb1a'), ('loc_cuff', '\xc5@\xb5\xc3'), ('loc_special', '\xaak\xc4_'), ('loc_necklace', '\xb6\xb5\xc3\xec'), ('loc_ring', '\xa7\xd9\xab\xfc'), ('loc_shoe', '\xbec\xa4l'))
PROP_TUPLE = ('m_HP', 'm_HPMax', 'm_MP', 'm_MPMax', 'm_FP', 'm_FPMax', 'm_Att_All', 'm_Def_All', 'm_Spe_All', 'm_Resist_Xian', 'm_Resist_Gui', 'm_Resist_Yao', 'm_Resist_Zhi', 'm_Resist_Nian', 'm_Magdef_All', 'm_Grade', 'm_Desc', 'm_Shape')
PROP_2_NAME = {
    'm_HP': 'text_hp',
    'm_HPMax': 'text_hp',
    'm_MP': 'text_mp',
    'm_MPMax': 'text_mp',
    'm_FP': 'text_fp',
    'm_FPMax': 'text_fp',
    'm_Att_All': 'text_att',
    'm_Def_All': 'text_def',
    'm_Spe_All': 'text_spe',
    'm_Resist_Xian': 'text_xian',
    'm_Resist_Gui': 'text_gui',
    'm_Resist_Yao': 'text_yao',
    'm_Resist_Zhi': 'text_zhi',
    'm_Resist_Nian': 'text_nian',
    'm_Magdef_All': 'text_magdef' }
SPECIAL_2_ATTRLIST = {
    'm_HP': [
        'm_HP',
        'm_HPMax'],
    'm_HPMax': [
        'm_HP',
        'm_HPMax'],
    'm_MP': [
        'm_MP',
        'm_MPMax'],
    'm_MPMax': [
        'm_MP',
        'm_MPMax'],
    'm_FP': [
        'm_FP',
        'm_FPMax'],
    'm_FPMax': [
        'm_FP',
        'm_FPMax'] }
IDX_2_INFO = {
    1: ('m_oTizhiEdit', 'edit_Tizhi', 8),
    2: ('m_oLiliangEdit', 'edit_Liliang', 8),
    3: ('m_oMoliEdit', 'edit_Magic', 8),
    4: ('m_oMeiliEdit', 'edit_Meili', 8),
    5: ('m_oMinjieEdit', 'edit_Minjie', 8) }
CLASS_2_POINT = {
    0: [
        1,
        3,
        0,
        0,
        0],
    1: [
        1,
        0,
        3,
        0,
        0],
    2: [
        1,
        0,
        0,
        2,
        1],
    3: [
        1,
        0,
        0,
        1,
        2] }
E_CHARSKILL_BASE = 0
E_CHARSKILL_WUXUE = 2
E_CHARSKILL_LIFE = 3
E_CHARSKILL_JQ = 6
SKILL_TYPE_2_NAME = {
    E_CHARSKILL_BASE: '\xb0\xf2\xc2\xa6',
    E_CHARSKILL_WUXUE: '\xacy\xac\xa3',
    E_CHARSKILL_LIFE: '\xa5\xcd\xac\xa1',
    E_CHARSKILL_JQ: '\xbc@\xb1\xa1' }

def GET_BASE_ATTR(iSkillID, iLevel):
    ID2TEXT = {
        1101: '\xa7\xf0\xc0\xbb\xa4O+%d\xa1B\xc6F\xa4O+%d' % (iLevel * 2 + iLevel * iLevel / 100, iLevel + iLevel * iLevel / 200),
        1102: '\xa8\xbe\xbfm+%d' % (iLevel * 2 + iLevel * iLevel / 120),
        1103: '\xae\xf0\xa6\xe5\xa4W\xad\xad+%d' % (iLevel * 10 + iLevel * iLevel / 20),
        1104: '\xaak\xa4O\xa1B\xa4O\xb9D\xa4W\xad\xad+%d' % iLevel * 3 }
    return ID2TEXT.get(iSkillID, '')

SUB_PAGE_ZHAOSHI = 1
SUB_PAGE_SET_XINFA = 2
SKILL_MSG_2_LIUPAI_ID = {
    10: 1000,
    11: 1001,
    12: 1005,
    13: 1004,
    14: 1002,
    15: 1003,
    16: 1011,
    17: 1014,
    21: 1008,
    22: 1007,
    23: 1006,
    24: 1010,
    25: 1009,
    26: 0 }
S_SKILL_NEED = {
    11: 1001,
    12: 1005,
    13: 1004,
    14: 1002,
    15: 1003,
    16: 1011,
    17: 1014,
    21: 1008,
    22: 1007,
    23: 1006,
    24: 1010,
    25: 1009 }
S_RIGHT_UINAME = ('noname12', 'noname21', 'noname5', 'noname6', 'noname3', 'txt_Xibie', 'txt_WeiLi', 'txt_MaxLv', 'txt_ShuLv', 'leftpoint', 'rightpoint', 'txt_LiDi', 'img_cash', 'hot_cash', 'txt_QunGong', 'txt_LingQiao', 'txt_Nomal', 'txt_XiaoLv', 'txt_Use1', 'txt_Use2', 'txt_Use3', 'txt_Use4', 'noname33', 'noname28', 'txt_MingZhong', 'img_Tips1', 'img_Tips2', 'img_Tips3', 'btn_Study', 'liupai', 'res_n', 'speed', 'mana', 'fp', 'loc_fennu', 'at', 'res_d', 'stype', 'magicname', 'df', 'eff', 'power', 'dp', 'res_p', 'res_m', 'ar', 'usetips', 'attacktips', 'txt_magicinfo', 'btn_levelex', 'txt_cash', 'img_cashbg', 'btn_upgrade', 'btn_oneupgrade', 'btn_onekeylearntips')
SORT_UI_NAMES = (('txt_Use2', 'mana'), ('txt_Use3', 'fp'), ('txt_Use4', 'loc_fennu'))
S_RIGHT_PROPVIEW = ('m_oTips', 'm_DescText')
S_TIPS_NAMES = ('hloc_n', 'hloc_d', 'hloc_dp', 'hloc_df', 'hloc_at', 'hloc_p', 'hloc_f', 'hloc_fennu', 'hloc_fp', 'hloc_mana', 'hloc_m')
SORT_TIPS_NAME = (('txt_Use2', 'hloc_mana'), ('txt_Use3', 'hloc_fp'), ('txt_Use4', 'hloc_fennu'))
LOCAL_DATA_FILE = 'MuBanXinFaData'
RIGHT_MESSAGE_STATUS_ADD = 1
RIGHT_MESSAGE_STATUS_DEL = 2
EQUIP_DEFAULT_LIST = [
    '\xacO',
    '\xa7_']
EQUIP_KANGXING_LIST = [
    '\xa5P\xb3N\xa9\xe8\xa7\xdc',
    '\xb0\xad\xb3N\xa9\xe8\xa7\xdc',
    '\xa7\xaf\xb3N\xa9\xe8\xa7\xdc',
    '\xb4\xbc\xb3N\xa9\xe8\xa7\xdc',
    '\xa9\xc0\xb3N\xa9\xe8\xa7\xdc',
    '\xa9\xd2\xa6\xb3\xa7\xdc\xa9\xca']
EQUIP_ADD_LIST = [
    '\xc5\xe9\xbd\xe8',
    '\xa4O\xb6q',
    '\xc5]\xa4O',
    '\xbey\xa4O',
    '\xb1\xd3\xb1\xb6']
EQUIP_GEM_LIST = [
    '\xac\xf5\xc4_\xa5\xdb',
    '\xc2\xc5\xc4_\xa5\xdb',
    '\xb6\xc0\xc4_\xa5\xdb',
    '\xa4\xd3\xb6\xa7\xa5\xdb',
    '\xa4\xeb\xabG\xa5\xdb',
    '\xaa\xd9\xa7Q\xa4l',
    '\xb6\xc2\xc4_\xa5\xdb',
    '\xbe\xc7\xb2\xdf\xa5\xdb',
    '\xa9G\xb3N\xa5\xdb',
    '\xa5P\xc6F\xa5\xdb',
    '\xb0\xad\xc6F\xa5\xdb',
    '\xa7\xaf\xc6F\xa5\xdb',
    '\xb4\xbc\xc6F\xa5\xdb',
    '\xa9\xc0\xc6F\xa5\xdb',
    '\xa8B\xaf\xcd\xc6F\xa5\xdb']
EQUIP_WUXING_LIST = [
    '\xb5L',
    '\xaa\xf7',
    '\xa4\xec',
    '\xa4\xf4',
    '\xa4\xf5',
    '\xa4g']
EQUIP_DEGREE_LIST = [
    '\xb5}\xc1\xa1',
    '\xbb\xe9\xc2\xf8',
    '\xb8Y\xb1K',
    '\xba\xeb\xaf\xc2']
EQUIP_DIANHUA_LIST = [
    '\xaaZ\xbe\xb9',
    '\xf1Z\xa5\xd2',
    '\xa7\xd9\xab\xfc',
    '\xaak\xc4_']
EQUIP_FUMO = {
    '\xaaZ\xbe\xb9': '\xa7\xf0\xc0\xbb',
    '\xf1Z\xa5\xd2': '\xa8\xbe\xbfm',
    '\xb6\xb5\xc3\xec': '\xc6F\xa4O',
    '\xb8y\xb1a': '\xae\xf0\xa6\xe5',
    '\xbec\xa4l': '\xb3t\xab\xd7',
    '\xc5@\xb5\xc3': '\xa4O\xb9D',
    '\xb4U\xa4l': '\xaak\xa4O' }
SAFEDATA = {
    '\xaaZ\xbe\xb9': [
        '\xa7\xf0\xc0\xbb'],
    '\xf1Z\xa5\xd2': [
        '\xa8\xbe\xbfm'],
    '\xb4U\xa4l': [
        '\xa8\xbe\xbfm'],
    '\xbec\xa4l': [
        '\xa8\xbe\xbfm',
        '\xb3t\xab\xd7'],
    '\xc5@\xb5\xc3': [
        '\xa8\xbe\xbfm'],
    '\xb6\xb5\xc3\xec': [
        '\xa8\xbe\xbfm',
        '\xc6F\xa4O'],
    '\xa7\xd9\xab\xfc': [
        '\xa8\xbe\xbfm',
        '\xc6F\xa4O'],
    '\xb8y\xb1a': [
        '\xae\xf0\xa6\xe5'] }
PROPTYPE = {
    1: '\xa7\xf0\xc0\xbb',
    2: '\xc6F\xa4O',
    3: '\xae\xf0\xa6\xe5',
    4: '\xa8\xbe\xbfm',
    5: '\xb3t\xab\xd7',
    6: '\xa4O\xb9D',
    7: '\xaak\xa4O',
    8: '\xc5\xe9\xbd\xe8',
    9: '\xa4O\xb6q',
    10: '\xc5]\xa4O',
    11: '\xbey\xa4O',
    12: '\xb1\xd3\xb1\xb6',
    19: '\xa5P\xb3N\xa9\xe8\xa7\xdc',
    20: '\xb0\xad\xb3N\xa9\xe8\xa7\xdc',
    21: '\xa7\xaf\xb3N\xa9\xe8\xa7\xdc',
    22: '\xb4\xbc\xb3N\xa9\xe8\xa7\xdc',
    23: '\xa9\xc0\xb3N\xa9\xe8\xa7\xdc',
    38: '\xa9\xd2\xa6\xb3\xa7\xdc\xa9\xca' }
GEMTYPE = {
    1: '\xac\xf5\xc4_\xa5\xdb',
    2: '\xc2\xc5\xc4_\xa5\xdb',
    3: '\xb6\xc0\xc4_\xa5\xdb',
    4: '\xa4\xd3\xb6\xa7\xa5\xdb',
    5: '\xa4\xeb\xabG\xa5\xdb',
    6: '\xaa\xd9\xa7Q\xa4l',
    7: '\xb6\xc2\xc4_\xa5\xdb',
    8: '\xbe\xc7\xb2\xdf\xa5\xdb',
    9: '\xa9G\xb3N\xa5\xdb',
    10: '\xa5P\xc6F\xa5\xdb',
    11: '\xb0\xad\xc6F\xa5\xdb',
    12: '\xa7\xaf\xc6F\xa5\xdb',
    13: '\xb4\xbc\xc6F\xa5\xdb',
    14: '\xa9\xc0\xc6F\xa5\xdb',
    15: '\xa8B\xaf\xcd\xc6F\xa5\xdb' }
LIUPAITYPE = {
    24: '\xa9\xd2\xa6\xb3\xaaZ\xbe\xb9\xacy\xac\xa3\xa7\xde\xaf\xe0',
    25: '\xa9\xd2\xa6\xb3\xaak\xb3N\xacy\xac\xa3\xa7\xde\xaf\xe0',
    26: '\xa9\xd2\xa6\xb3\xacy\xac\xa3\xa7\xde\xaf\xe0',
    27: '\xbcC\xb3N\xa7\xde\xa5\xa9',
    28: '\xa4M\xaak\xa7\xde\xa5\xa9',
    29: '\xbaj\xaak\xa7\xde\xa5\xa9',
    30: '\xae\xb1\xaak\xa7\xde\xa5\xa9',
    31: '\xb5\xa7\xaak\xa7\xde\xa5\xa9',
    32: '\xbe\xa7\xbe\xc7\xb2z\xbd\xd7',
    33: '\xb9D\xb3N\xba\xeb\xadn',
    34: '\xa6\xf2\xbe\xc7\xb2z\xbd\xd7',
    35: '\xb3\xb1\xb6\xa7\xb1K\xb3N',
    36: '\xa7\xc5\xb3N\xaa\xbe\xc3\xd1',
    37: '\xb7t\xbe\xb9\xa7\xde\xa5\xa9' }
ZHENQITYPE = {
    1: '\xb5}\xc1\xa1',
    2: '\xbb\xe9\xc2\xf8',
    3: '\xb8Y\xb1K',
    4: '\xba\xeb\xaf\xc2' }
ZHENQI = {
    1: '\xb0\xae\xae\xf0',
    2: '\xa7I\xae\xf0',
    3: '\xc2\xf7\xae\xf0',
    4: '\xbe_\xae\xf0',
    5: '\xb4S\xae\xf0',
    6: '\xa7\xa2\xae\xf0',
    7: '\xa6\xe1\xae\xf0',
    8: '\xa9[\xae\xf0' }
GUAXIANG = {
    1201: '\xa6a\xbfA\xc1{',
    1202: '\xa4\xd1\xa4\xf5\xa6P\xa4H',
    1203: '\xa4\xf4\xa4\xf5\xacJ\xc0\xd9',
    1204: '\xa4s\xad\xb7\xc5\xdb',
    1205: '\xad\xb7\xa4s\xba\xa5',
    1206: '\xa4\xf5\xb9p\xbe\xbd\xb6\xdf',
    1207: '\xb9p\xa6a\xbf\xdd',
    1208: '\xbfA\xa4\xf4\xa7x',
    1209: '\xbfA\xa4\xd1\xc9[',
    1210: '\xa4\xd1\xa4\xf4\xb3^',
    1211: '\xa4s\xb9p\xc0[',
    1212: '\xad\xb7\xa6a\xc6[',
    1213: '\xb0\xae\xac\xb0\xa4\xd1',
    1214: '\xa7\xa2\xac\xb0\xa4\xf4',
    1215: '\xb4S\xac\xb0\xad\xb7',
    1216: '\xa6\xe1\xac\xb0\xa4s',
    1217: '\xa4\xf5\xa4\xd1\xa4j\xa6\xb3',
    1218: '\xa4\xf4\xa4s\xee\xbf',
    1219: '\xbfA\xa6a\xb5\xd1',
    1220: '\xb9p\xad\xb7\xf9\xda',
    1221: '\xa9[\xac\xb0\xa6a' }
GUAXIANGDESC = {
    1201: {
        1: '\xc5\xe9\xbd\xe8+8',
        2: '\xc5\xe9\xbd\xe8+10',
        3: '\xc5\xe9\xbd\xe8+12',
        4: '\xc5\xe9\xbd\xe8+15' },
    1202: {
        1: '\xa4O\xb6q+8',
        2: '\xa4O\xb6q+10',
        3: '\xa4O\xb6q+12',
        4: '\xa4O\xb6q+15' },
    1203: {
        1: '\xc5]\xa4O+8',
        2: '\xc5]\xa4O+10',
        3: '\xc5]\xa4O+12',
        4: '\xc5]\xa4O+15' },
    1204: {
        1: '\xbey\xa4O+8',
        2: '\xbey\xa4O+10',
        3: '\xbey\xa4O+12',
        4: '\xbey\xa4O+15' },
    1205: {
        1: '\xb1\xd3\xb1\xb6+8',
        2: '\xb1\xd3\xb1\xb6+10',
        3: '\xb1\xd3\xb1\xb6+12',
        4: '\xb1\xd3\xb1\xb6+15' },
    1206: {
        1: '\xaa\xab\xb2z\xa9R\xa4\xa4\xb2v+3%',
        2: '\xaa\xab\xb2z\xa9R\xa4\xa4\xb2v+4%',
        3: '\xaa\xab\xb2z\xa9R\xa4\xa4\xb2v+5%',
        4: '\xaa\xab\xb2z\xa9R\xa4\xa4\xb2v+7%' },
    1207: {
        1: '\xc0\xf2\xb1o\xb8g\xc5\xe7\xad\xc8+3%',
        2: '\xc0\xf2\xb1o\xb8g\xc5\xe7\xad\xc8+4%',
        3: '\xc0\xf2\xb1o\xb8g\xc5\xe7\xad\xc8+5%',
        4: '\xc0\xf2\xb1o\xb8g\xc5\xe7\xad\xc8+7%' },
    1208: {
        1: '\xb4\xee\xa4\xd6\xa9\xd2\xa8\xfc\xaa\xab\xb2z\xb6\xcb\xae`\xb5\xb2\xaaG3%',
        2: '\xb4\xee\xa4\xd6\xa9\xd2\xa8\xfc\xaa\xab\xb2z\xb6\xcb\xae`\xb5\xb2\xaaG4%',
        3: '\xb4\xee\xa4\xd6\xa9\xd2\xa8\xfc\xaa\xab\xb2z\xb6\xcb\xae`\xb5\xb2\xaaG5%',
        4: '\xb4\xee\xa4\xd6\xa9\xd2\xa8\xfc\xaa\xab\xb2z\xb6\xcb\xae`\xb5\xb2\xaaG7%' },
    1209: {
        1: '\xb4\xee\xa4\xd6\xa9\xd2\xa8\xfc\xaak\xb3N\xb6\xcb\xae`\xb5\xb2\xaaG3%',
        2: '\xb4\xee\xa4\xd6\xa9\xd2\xa8\xfc\xaak\xb3N\xb6\xcb\xae`\xb5\xb2\xaaG4%',
        3: '\xb4\xee\xa4\xd6\xa9\xd2\xa8\xfc\xaak\xb3N\xb6\xcb\xae`\xb5\xb2\xaaG5%',
        4: '\xb4\xee\xa4\xd6\xa9\xd2\xa8\xfc\xaak\xb3N\xb6\xcb\xae`\xb5\xb2\xaaG7%' },
    1210: {
        1: '\xabe3\xa6^\xa6X\xc0\xf2\xb1o\xc3B\xa5~\xa7\xf0\xc0\xbb\xc2I\xc1`\xadp5\xc2I',
        2: '\xabe3\xa6^\xa6X\xc0\xf2\xb1o\xc3B\xa5~\xa7\xf0\xc0\xbb\xc2I\xc1`\xadp6\xc2I',
        3: '\xabe3\xa6^\xa6X\xc0\xf2\xb1o\xc3B\xa5~\xa7\xf0\xc0\xbb\xc2I\xc1`\xadp7\xc2I',
        4: '\xabe3\xa6^\xa6X\xc0\xf2\xb1o\xc3B\xa5~\xa7\xf0\xc0\xbb\xc2I\xc1`\xadp9\xc2I' },
    1211: {
        1: '\xabe3\xa6^\xa6X\xc0\xf2\xb1o\xc3B\xa5~\xa8\xbe\xbfm\xc2I\xc1`\xadp5\xc2I',
        2: '\xabe3\xa6^\xa6X\xc0\xf2\xb1o\xc3B\xa5~\xa8\xbe\xbfm\xc2I\xc1`\xadp6\xc2I',
        3: '\xabe3\xa6^\xa6X\xc0\xf2\xb1o\xc3B\xa5~\xa8\xbe\xbfm\xc2I\xc1`\xadp7\xc2I',
        4: '\xabe3\xa6^\xa6X\xc0\xf2\xb1o\xc3B\xa5~\xa8\xbe\xbfm\xc2I\xc1`\xadp9\xc2I' },
    1212: {
        1: '\xabe3\xa6^\xa6X\xc0\xf2\xb1o\xc3B\xa5~\xa4z\xc2Z\xc2I\xc1`\xadp5\xc2I',
        2: '\xabe3\xa6^\xa6X\xc0\xf2\xb1o\xc3B\xa5~\xa4z\xc2Z\xc2I\xc1`\xadp6\xc2I',
        3: '\xabe3\xa6^\xa6X\xc0\xf2\xb1o\xc3B\xa5~\xa4z\xc2Z\xc2I\xc1`\xadp7\xc2I',
        4: '\xabe3\xa6^\xa6X\xc0\xf2\xb1o\xc3B\xa5~\xa4z\xc2Z\xc2I\xc1`\xadp9\xc2I' },
    1213: {
        1: '\xaa\xab\xb2z\xc3z\xc0\xbb\xb2v+1%',
        2: '\xaa\xab\xb2z\xc3z\xc0\xbb\xb2v+2%',
        3: '\xaa\xab\xb2z\xc3z\xc0\xbb\xb2v+3%',
        4: '\xaa\xab\xb2z\xc3z\xc0\xbb\xb2v+5%' },
    1214: {
        1: '\xaak\xb3N\xc3z\xc0\xbb\xb2v+1%',
        2: '\xaak\xb3N\xc3z\xc0\xbb\xb2v+2%',
        3: '\xaak\xb3N\xc3z\xc0\xbb\xb2v+3%',
        4: '\xaak\xb3N\xc3z\xc0\xbb\xb2v+5%' },
    1215: {
        1: '\xab\xca\xa6L\xbbP\xa7\xdc\xab\xca\xa6\xa8\xa5\\\xb2v+1%',
        2: '\xab\xca\xa6L\xbbP\xa7\xdc\xab\xca\xa6\xa8\xa5\\\xb2v+2%',
        3: '\xab\xca\xa6L\xbbP\xa7\xdc\xab\xca\xa6\xa8\xa5\\\xb2v+3%',
        4: '\xab\xca\xa6L\xbbP\xa7\xdc\xab\xca\xa6\xa8\xa5\\\xb2v+5%' },
    1216: {
        1: '\xab\xec\xb4_\xaak\xb3N\xae\xc4\xaaG+1%',
        2: '\xab\xec\xb4_\xaak\xb3N\xae\xc4\xaaG+2%',
        3: '\xab\xec\xb4_\xaak\xb3N\xae\xc4\xaaG+3%',
        4: '\xab\xec\xb4_\xaak\xb3N\xae\xc4\xaaG+5%' },
    1217: {
        1: '\xb6i\xa4J\xbe\xd4\xb0\xab\xc0\xf2\xb1o\xbc\xab\xab\xe3\xad\xc8+6',
        2: '\xb6i\xa4J\xbe\xd4\xb0\xab\xc0\xf2\xb1o\xbc\xab\xab\xe3\xad\xc8+8',
        3: '\xb6i\xa4J\xbe\xd4\xb0\xab\xc0\xf2\xb1o\xbc\xab\xab\xe3\xad\xc8+10',
        4: '\xb6i\xa4J\xbe\xd4\xb0\xab\xc0\xf2\xb1o\xbc\xab\xab\xe3\xad\xc8+14' },
    1218: {
        1: '\xaak\xb3N\xb6\xcb\xae`\xb5\xb2\xaaG+2%',
        2: '\xaak\xb3N\xb6\xcb\xae`\xb5\xb2\xaaG+3%',
        3: '\xaak\xb3N\xb6\xcb\xae`\xb5\xb2\xaaG+4%',
        4: '\xaak\xb3N\xb6\xcb\xae`\xb5\xb2\xaaG+6%' },
    1219: {
        1: '\xb3Q\xa1u\xab\xca\xa6L\xc3\xfe\xadt\xad\xb1\xae\xc4\xaaG\xa1v\xa9R\xa4\xa4\xae\xc9\xa1A\xa6\xb31%\xb7\xa7\xb2v\xa5\xce\xa9\xdb\xa6\xa1\xa4\xcf\xc0\xbb',
        2: '\xb3Q\xa1u\xab\xca\xa6L\xc3\xfe\xadt\xad\xb1\xae\xc4\xaaG\xa1v\xa9R\xa4\xa4\xae\xc9\xa1A\xa6\xb32%\xb7\xa7\xb2v\xa5\xce\xa9\xdb\xa6\xa1\xa4\xcf\xc0\xbb',
        3: '\xb3Q\xa1u\xab\xca\xa6L\xc3\xfe\xadt\xad\xb1\xae\xc4\xaaG\xa1v\xa9R\xa4\xa4\xae\xc9\xa1A\xa6\xb33%\xb7\xa7\xb2v\xa5\xce\xa9\xdb\xa6\xa1\xa4\xcf\xc0\xbb',
        4: '\xb3Q\xa1u\xab\xca\xa6L\xc3\xfe\xadt\xad\xb1\xae\xc4\xaaG\xa1v\xa9R\xa4\xa4\xae\xc9\xa1A\xa6\xb34%\xb7\xa7\xb2v\xa5\xce\xa9\xdb\xa6\xa1\xa4\xcf\xc0\xbb' },
    1220: {
        1: '\xb3Q\xa7\xf0\xc0\xbb\xa9R\xa4\xa4\xab\xe1\xa1A\xa6\xb31%\xb7\xa7\xb2v\xae\xda\xbe\xda\xbey\xa4O\xab\xec\xb4_\xae\xf0\xa6\xe5',
        2: '\xb3Q\xa7\xf0\xc0\xbb\xa9R\xa4\xa4\xab\xe1\xa1A\xa6\xb32%\xb7\xa7\xb2v\xae\xda\xbe\xda\xbey\xa4O\xab\xec\xb4_\xae\xf0\xa6\xe5',
        3: '\xb3Q\xa7\xf0\xc0\xbb\xa9R\xa4\xa4\xab\xe1\xa1A\xa6\xb33%\xb7\xa7\xb2v\xae\xda\xbe\xda\xbey\xa4O\xab\xec\xb4_\xae\xf0\xa6\xe5',
        4: '\xb3Q\xa7\xf0\xc0\xbb\xa9R\xa4\xa4\xab\xe1\xa1A\xa6\xb34%\xb7\xa7\xb2v\xae\xda\xbe\xda\xbey\xa4O\xab\xec\xb4_\xae\xf0\xa6\xe5' },
    1221: {
        1: '\xa8\xfc\xc3z\xc0\xbb\xb7\xa7\xb2v-1%',
        2: '\xa8\xfc\xc3z\xc0\xbb\xb7\xa7\xb2v-2%',
        3: '\xa8\xfc\xc3z\xc0\xbb\xb7\xa7\xb2v-3%',
        4: '\xa8\xfc\xc3z\xc0\xbb\xb7\xa7\xb2v-5%' } }
WUXING = {
    0: '\xb5L',
    1: '\xaa\xf7',
    2: '\xa4\xec',
    3: '\xa4g',
    4: '\xa4\xf4',
    5: '\xa4\xf5' }
TEXIAO = {
    1024: '\xb0l\xae\xb7',
    1025: '\xb1j\xa4\xc6\xa8\xbe\xbfm',
    1026: '\xb1j\xa4\xc6\xc5v\xab\xc2',
    1027: '\xc2y\xc6N',
    1028: '\xb7P\xaa\xbe',
    1029: '\xab\xfc\xb4\xa7',
    1030: '\xc3\xc4\xad\xbb\xa7l\xa6\xac',
    1031: '\xa5\xc3\xa4\xa3\xbfi\xb7l',
    1034: '\xa9\xf6\xa6\xa8\xaa\xf8',
    1036: '\xa4O\xbc\xc4\xa9\xdb\xa6\xa1\xbe\xd5\xaa\xf8',
    1037: '\xc6F\xa5\xa9\xa9\xdb\xa6\xa1\xbe\xd5\xaa\xf8',
    1038: '\xb4\xb6\xb3q\xa9\xdb\xa6\xa1\xbe\xd5\xaa\xf8',
    1039: '\xc3\xc4\xaev',
    1040: '\xa9\xaf\xb9B\xbc\xc6\xa6r1',
    1041: '\xa9\xaf\xb9B\xbc\xc6\xa6r2',
    1042: '\xa9\xaf\xb9B\xbc\xc6\xa6r3',
    1043: '\xa9\xaf\xb9B\xbc\xc6\xa6r4',
    1044: '\xa9\xaf\xb9B\xbc\xc6\xa6r5',
    1045: '\xa9\xaf\xb9B\xbc\xc6\xa6r6',
    1046: '\xa9\xaf\xb9B\xbc\xc6\xa6r7',
    1047: '\xa9\xaf\xb9B\xbc\xc6\xa6r8',
    1048: '\xa9\xaf\xb9B\xbc\xc6\xa6r9',
    1001: '\xa5\xb2\xb1\xfe',
    1002: '\xa8g\xbc\xc9',
    1003: '\xb3s\xc0\xbb',
    1004: '\xa4O\xbe_',
    1005: '\xc0\xbb\xb0h',
    1006: '\xc0\xbb\xbc\xec',
    1007: '\xc0\xbb\xa8\xee',
    1008: '\xc3z\xaf}\xc2I\xa5\xde',
    1009: '\xacy\xacP',
    1010: '\xaak\xb3N\xbc\xc9\xc0\xbb',
    1011: '\xbfU\xbfN',
    1012: '\xaf\xab\xb4\xbc\xa4\xa3\xb2M',
    1013: '\xae\xa3\xc0~',
    1014: '\xbe\xd4\xb0\xab\xad\xe3\xb3\xc6',
    1015: '\xa7\xf0\xc0\xbb\xb7\xc7\xb3\xc6',
    1016: '\xa8\xbe\xbfm\xad\xe3\xb3\xc6',
    1017: '\xa4z\xc2Z\xb7\xc7\xb3\xc6',
    1018: '\xa7\xd6\xb3t\xb7\xc7\xb3\xc6',
    1019: '\xaf\xab\xb9A',
    1020: '\xaf\xab\xaf\xa7',
    1021: '\xb0\xc7\xba\xf2\xaa\xba',
    1022: '\xbc\xab\xab\xe3',
    1023: '\xb0g\xc2\xdc' }
TEJI = {
    829: '\xaf}\xc5\xe9\xa6\xa1',
    2601: '\xac\xa1\xa6\xe5\xb3N',
    2602: '\xae\xf0\xc0\xf8\xb3N',
    2603: '\xa4\xdf\xc0\xf8\xb3N',
    2604: '\xa9R\xc0\xf8\xb3N',
    2605: '\xa7\xae\xa4\xe2\xa6^\xacK',
    2606: '\xac}\xb9\xee\xb3Z',
    2607: '\xc5X\xb0\xad\xb3Z',
    2608: '\xb0\xbd\xc5\xa7\xb3Z',
    2609: '\xa8\xeb\xa5\xd2\xb3Z',
    2610: '\xb2M\xa4\xdf\xa9G',
    2611: '\xb9\xe7\xa4\xdf\xa9G',
    2612: '\xa9\xfa\xc3\xe8\xa4\xee\xa4\xf4',
    2613: '\xaa\xf0\xbb\xee\xb3N',
    2614: '\xc4\xf2\xa9R\xb3N',
    2615: '\xa6^\xa4\xdf\xb3N',
    2616: '\xc2k\xa4\xdf\xb3N',
    2617: '\xbe\xae\xa4\xdf\xb3N',
    2618: '\xbbE\xa4\xdf\xb3N',
    2619: '\xa6^\xaf\xab\xb3N',
    2620: '\xc2k\xaf\xab\xb3N',
    2621: '\xbe\xae\xaf\xab\xb3N',
    2622: '\xbbE\xaf\xab\xb3N',
    2623: '\xa4\xdf\xaf\xab\xa6X\xa4@',
    2624: '\xb1j\xa4\xc6\xa7\xf0\xc0\xbb',
    2625: '\xaez\xa4\xc6\xa7\xf0\xc0\xbb',
    2626: '\xb1j\xa4\xc6\xa8\xbe\xbfm',
    2627: '\xaez\xa4\xc6\xa8\xbe\xbfm',
    2628: '\xb1j\xa4\xc6\xc5]\xa4O',
    2629: '\xaez\xa4\xc6\xc5]\xa4O',
    2630: '\xb1j\xa4\xc6\xc5]\xa7K',
    2631: '\xaez\xa4\xc6\xc5]\xa7K',
    2632: '\xacy\xa4\xf4\xb3Z',
    2633: '\xb0\xb1\xba\xa2\xb3N',
    2634: '\xa4\xaf\xa4\xdf\xa8}\xb3N',
    2635: '\xbf\xd0\xafe\xa7\xd2\xc2\xe5',
    2636: '\xba\xc6\xa8g\xb3s\xc0\xbb',
    2637: '\xba\xc6\xa8g\xaak\xb3s',
    2638: '\xa9\xdb\xb5L\xb1`\xa6\xa1',
    2639: '\xa6\xa1\xb5L\xb1`\xaak',
    2640: '\xa4\xc6\xc0I\xac\xb0\xa6i',
    2641: '\xaf}\xa4O\xa6\xa1',
    2642: '\xaf}\xc5]\xa6\xa1',
    2643: '\xaf}\xbey\xa6\xa1',
    2644: '\xaf}\xc5\xe9\xa6\xa1',
    2645: '\xa4\xf5\xb2\xbd\xa9G',
    2646: '\xaaL\xb2\xbd\xa9G',
    2647: '\xad\xb7\xb2\xbd\xa9G',
    2648: '\xb6\xb3\xb2\xbd\xa9G',
    2649: '\xabB\xb2\xbd\xa9G',
    2650: '\xb4\xb8\xb2\xbd\xa9G',
    2651: '\xc6F\xb7P\xb1j\xa4\xc6',
    2652: '\xc6F\xb7P\xaez\xa4\xc6',
    2653: '\xber\xb6\xbf\xb3N',
    2654: '\xaa\xbe\xa4v\xaa\xbe\xa9\xbc',
    2655: '\xaf\xba\xb8\xcc\xc2\xc3\xa4M',
    2656: '\xa4f\xbbe\xb8\xa1\xbcC',
    2657: '\xb4_\xb5d',
    2658: '\xa4j\xa6\xde\xc0Y\xa9G',
    2659: '\xaf}\xb8H\xb5L\xc2\xf9',
    2660: '\xa7l\xa6\xe5',
    2661: '\xa7l\xc5]',
    2662: '\xb7O\xaf\xe8\xb4\xb6\xab\xd7',
    4711: '\xb2V\xa8P\xc3z\xb5o',
    2664: '\xab\xe3\xb1\xd9\xb0\xae\xa9[',
    2665: '\xc5]\xb0\xca\xb0\xae\xa9[',
    2666: '\xbey\xb4b\xb0\xae\xa9[',
    2668: '\xae\xf0\xc2k\xb3N',
    2669: '\xa9R\xc2k\xb3N',
    2670: '\xa5|\xae\xfc\xaa@\xa5\xad',
    2671: '\xaf}\xa6\xe5\xa9G',
    2672: '\xaf}\xc5]\xa9G',
    2673: '\xaf}\xabl\xa9G' }
exec {
    '': None,
    '\xaaZ\xbe\xb9': {
        'bagua': [
            1219,
            1220],
        'texiao': [
            1001,
            1002,
            1003,
            1004,
            1005,
            1006,
            1007,
            1008,
            1009,
            1010,
            1011,
            1012,
            1013,
            1034,
            1041,
            1044,
            1047],
        'idxs': [
            '\xa7\xf0\xc0\xbb',
            '\xc4\xdd\xa9\xca1',
            '\xc4\xdd\xa9\xca2'],
        10: (55, 106, 7, 12, 4, 8),
        20: (90, 162, 9, 16, 5, 10),
        30: (125, 219, 10, 20, 6, 13),
        40: (160, 277, 12, 24, 7, 16),
        50: (195, 333, 14, 28, 8, 18),
        60: (230, 390, 16, 32, 9, 21),
        70: (265, 447, 18, 35, 10, 24),
        80: (300, 520, 20, 40, 12, 27),
        90: (335, 579, 22, 45, 13, 29),
        100: (370, 638, 24, 49, 15, 32),
        110: (405, 680, 26, 53, 16, 35),
        120: (637, 721, 28, 57, 17, 38) } } in {
    'bagua': [
        1201,
        1202,
        1203,
        1204,
        1205],
    'texiao': [
        1025,
        1026,
        1034,
        1040,
        1041,
        1042,
        1043,
        1044,
        1045,
        1046,
        1047,
        1048],
    'idxs': [
        '\xa8\xbe\xbfm',
        '\xa7\xf0\xc0\xbb',
        '\xc6F\xa4O',
        '\xa7\xdc1',
        '\xa7\xdc2',
        '\xc4\xdd\xa9\xca1',
        '\xc4\xdd\xa9\xca2'],
    10: (23, 66, 7, 12, 4, 7, 3, 5, 4, 6, 7, 11, 4, 7),
    20: (38, 95, 10, 16, 5, 9, 4, 7, 4, 7, 8, 15, 5, 9),
    30: (53, 124, 12, 20, 7, 11, 5, 8, 5, 8, 10, 19, 6, 11),
    40: (68, 154, 14, 25, 8, 13, 6, 10, 6, 9, 11, 24, 8, 13),
    50: (83, 183, 16, 29, 9, 15, 7, 11, 6, 10, 13, 28, 9, 15),
    60: (98, 213, 19, 33, 10, 17, 8, 13, 7, 11, 14, 32, 10, 17),
    70: (113, 241, 22, 36, 11, 19, 9, 14, 7, 12, 15, 37, 11, 19),
    80: (149, 270, 24, 40, 12, 22, 10, 16, 8, 13, 17, 41, 12, 22) }
del None[{
    '': None,
    '\xaaZ\xbe\xb9': {
        'bagua': [
            1219,
            1220],
        'texiao': [
            1001,
            1002,
            1003,
            1004,
            1005,
            1006,
            1007,
            1008,
            1009,
            1010,
            1011,
            1012,
            1013,
            1034,
            1041,
            1044,
            1047],
        'idxs': [
            '\xa7\xf0\xc0\xbb',
            '\xc4\xdd\xa9\xca1',
            '\xc4\xdd\xa9\xca2'],
        10: (55, 106, 7, 12, 4, 8),
        20: (90, 162, 9, 16, 5, 10),
        30: (125, 219, 10, 20, 6, 13),
        40: (160, 277, 12, 24, 7, 16),
        50: (195, 333, 14, 28, 8, 18),
        60: (230, 390, 16, 32, 9, 21),
        70: (265, 447, 18, 35, 10, 24),
        80: (300, 520, 20, 40, 12, 27),
        90: (335, 579, 22, 45, 13, 29),
        100: (370, 638, 24, 49, 15, 32),
        110: (405, 680, 26, 53, 16, 35),
        120: (637, 721, 28, 57, 17, 38) } }:]
None[90] = None // None
None[100] = (185, 329, 29, 49, 14, 26, 10, 16, 8, 13, 20, 49, 14, 25)
None[110] = (199, 355, 31, 53, 16, 27, 10, 16, 8, 13, 23, 53, 16, 27)
None[120] = (247, 376, 33, 57, 17, 29, 10, 16, 8, 13, 25, 57, 17, 29)
None['\xf1Z\xa5\xd2'] = None
None['\xaak\xc4_'] = {
    'bagua': [
        1217,
        1207],
    'texiao': [
        1027,
        1028,
        1034,
        1040,
        1041,
        1042,
        1043,
        1044,
        1045,
        1046,
        1047,
        1048],
    'idxs': [
        '\xa4O\xaak',
        '\xc4\xdd\xa9\xca1',
        '\xc4\xdd\xa9\xca2'],
    30: (13, 24, 9, 16, 6, 13),
    40: (18, 32, 10, 19, 7, 16),
    50: (23, 39, 12, 22, 8, 18),
    60: (27, 48, 13, 25, 9, 21),
    70: (31, 55, 15, 27, 10, 24),
    80: (38, 64, 17, 30, 12, 27),
    90: (43, 71, 19, 32, 13, 29),
    100: (48, 79, 20, 35, 14, 32),
    110: (52, 87, 23, 38, 16, 35),
    120: (57, 94, 26, 40, 18, 37) }
None['\xb4U\xa4l'] = {
    'bagua': [
        1206,
        1207,
        1217,
        1213,
        1214,
        1215,
        1216,
        1221],
    'texiao': [
        1034,
        1040,
        1041,
        1042,
        1043,
        1044,
        1045,
        1046,
        1047,
        1048],
    'idxs': [
        '\xa8\xbe\xbfm',
        '\xa4O\xaak',
        '\xc4\xdd\xa9\xca1',
        '\xc4\xdd\xa9\xca2'],
    10: (10, 32, 16, 34, 6, 11, 3, 7),
    20: (15, 40, 32, 68, 7, 13, 5, 9),
    30: (20, 49, 48, 101, 9, 16, 6, 11),
    40: (25, 58, 64, 135, 10, 18, 7, 13),
    50: (30, 66, 80, 169, 12, 22, 8, 15),
    60: (35, 73, 96, 202, 13, 25, 9, 17),
    70: (40, 82, 112, 236, 15, 27, 10, 19),
    80: (57, 92, 245, 269, 18, 30, 12, 20),
    90: (64, 99, 277, 303, 19, 32, 13, 23),
    100: (70, 108, 307, 334, 22, 34, 15, 26),
    110: (76, 117, 308, 324, 23, 38, 16, 27),
    120: (82, 123, 321, 354, 24, 40, 17, 29) }
None['\xbec\xa4l'] = {
    'bagua': [
        1204,
        1205],
    'texiao': [
        1024,
        1023,
        1036,
        1037,
        1038,
        1034,
        1040,
        1041,
        1042,
        1043,
        1044,
        1045,
        1046,
        1047,
        1048],
    'idxs': [
        '\xa8\xbe\xbfm',
        '\xc4\xdd\xa9\xca1',
        '\xc4\xdd\xa9\xca2',
        '\xa7\xdc1',
        '\xa7\xdc3',
        '\xa7\xdc2',
        '\xa4O\xaak',
        '\xb3t\xab\xd7'],
    10: (10, 32, 6, 11, 4, 7, 7, 11, 3, 6, 2, 7, 4, 8, 3, 16),
    20: (15, 40, 8, 13, 4, 9, 9, 14, 4, 7, 3, 9, 9, 15, 7, 25),
    30: (20, 48, 9, 16, 6, 11, 10, 17, 4, 8, 4, 10, 14, 24, 10, 33),
    40: (25, 58, 11, 19, 7, 13, 11, 19, 5, 9, 5, 13, 18, 31, 14, 40),
    50: (30, 66, 12, 22, 8, 15, 13, 23, 6, 10, 6, 14, 22, 39, 17, 49),
    60: (35, 74, 13, 25, 9, 17, 16, 27, 6, 11, 7, 16, 27, 48, 21, 57),
    70: (40, 81, 14, 27, 10, 19, 17, 29, 7, 12, 8, 17, 31, 55, 24, 66),
    80: (57, 92, 17, 30, 12, 21, 20, 33, 8, 13, 10, 20, 38, 64, 30, 73),
    90: (64, 99, 19, 33, 13, 23, 20, 33, 8, 13, 10, 20, 43, 71, 33, 81),
    100: (70, 107, 20, 35, 15, 25, 20, 33, 8, 13, 10, 20, 48, 77, 37, 90),
    110: (76, 115, 23, 38, 16, 27, 20, 33, 8, 13, 10, 20, 53, 87, 38, 97),
    120: (82, 123, 25, 40, 17, 29, 20, 33, 8, 13, 11, 20, 60, 93, 38, 102) }
None['\xa7\xd9\xab\xfc'] = {
    'bagua': [
        1202],
    'texiao': [
        1029,
        1030,
        1039,
        1034,
        1040,
        1041,
        1042,
        1043,
        1044,
        1045,
        1046,
        1047,
        1048],
    'idxs': [
        '\xa8\xbe\xbfm',
        '\xc4\xdd\xa9\xca1',
        '\xc4\xdd\xa9\xca2',
        '\xacy\xac\xa3\xa7\xde\xaf\xe01',
        '\xacy\xac\xa3\xa7\xde\xaf\xe02',
        '\xc6F\xa4O'],
    10: (6, 8, 6, 11, 4, 7, 0, 2, 0, 0, 9, 31),
    20: (6, 8, 8, 13, 4, 9, 0, 2, 0, 0, 13, 39),
    30: (6, 8, 9, 16, 6, 11, 2, 5, 1, 2, 18, 47),
    40: (6, 8, 11, 19, 7, 13, 3, 5, 1, 3, 23, 55),
    50: (6, 8, 12, 22, 8, 15, 3, 6, 1, 4, 27, 62),
    60: (6, 8, 13, 25, 9, 17, 3, 7, 2, 4, 31, 71),
    70: (6, 8, 14, 27, 10, 19, 4, 7, 2, 5, 36, 79),
    80: (7, 8, 17, 30, 12, 21, 5, 8, 4, 5, 43, 87),
    90: (7, 8, 19, 33, 13, 23, 5, 8, 4, 6, 48, 94),
    100: (7, 9, 20, 35, 15, 25, 5, 8, 4, 7, 52, 102),
    110: (7, 9, 23, 38, 16, 27, 5, 8, 5, 7, 57, 111),
    120: (7, 8, 24, 40, 17, 29, 5, 8, 4, 8, 61, 118) }
None['\xb8y\xb1a'] = {
    'bagua': [
        1201,
        1208,
        1209],
    'texiao': [
        1021,
        1022,
        1034,
        1040,
        1041,
        1042,
        1043,
        1044,
        1045,
        1046,
        1047,
        1048],
    'idxs': [
        '\xae\xf0\xa6\xe5',
        '\xc4\xdd\xa9\xca1',
        '\xc4\xdd\xa9\xca2',
        '\xa4O\xaak'],
    10: (55, 196, 6, 11, 3, 7, 4, 8),
    20: (111, 326, 8, 14, 5, 10, 9, 16),
    30: (166, 456, 9, 17, 6, 12, 13, 24),
    40: (222, 586, 10, 22, 7, 14, 18, 32),
    50: (277, 717, 12, 24, 8, 16, 22, 40),
    60: (332, 847, 13, 27, 9, 18, 26, 48),
    70: (388, 977, 14, 31, 11, 22, 30, 56),
    80: (466, 1107, 17, 34, 12, 24, 38, 64),
    90: (524, 1237, 19, 37, 13, 26, 42, 72),
    100: (582, 1368, 20, 40, 15, 28, 48, 80),
    110: (600, 1460, 22, 44, 16, 30, 52, 88),
    120: (1189, 1532, 26, 47, 18, 32, 57, 97) }
None['\xb6\xb5\xc3\xec'] = {
    'bagua': [
        1203],
    'texiao': [
        1019,
        1020,
        1034,
        1040,
        1041,
        1042,
        1043,
        1044,
        1045,
        1046,
        1047,
        1048],
    'idxs': [
        '\xc6F\xa4O',
        '\xc4\xdd\xa9\xca1',
        '\xc4\xdd\xa9\xca2',
        '\xa8\xbe\xbfm',
        '\xa4O\xaak'],
    10: (7, 40, 6, 11, 3, 7, 10, 16, 4, 8),
    20: (14, 56, 8, 14, 5, 10, 15, 25, 9, 16),
    30: (21, 73, 9, 17, 6, 12, 20, 33, 13, 24),
    40: (28, 89, 10, 22, 7, 14, 25, 43, 18, 32),
    50: (35, 106, 12, 24, 8, 16, 30, 50, 22, 40),
    60: (42, 121, 13, 27, 9, 18, 35, 58, 26, 48),
    70: (49, 138, 14, 31, 11, 22, 40, 68, 30, 56),
    80: (59, 154, 17, 34, 12, 24, 57, 76, 38, 64),
    90: (66, 171, 19, 37, 13, 26, 64, 85, 42, 72),
    100: (74, 186, 20, 40, 15, 28, 70, 91, 48, 80),
    110: (75, 198, 22, 44, 16, 30, 76, 100, 52, 88),
    120: (82, 214, 24, 45, 19, 32, 82, 108, 59, 93) }
None['\xc5@\xb5\xc3'] = {
    'bagua': [
        1210,
        1211,
        1212],
    'texiao': [
        1014,
        1015,
        1016,
        1017,
        1018,
        1034,
        1040,
        1041,
        1042,
        1043,
        1044,
        1045,
        1046,
        1047,
        1048],
    'idxs': [
        '\xa8\xbe\xbfm',
        '\xc4\xdd\xa9\xca1',
        '\xa7\xf0\xc0\xbb',
        '\xa7\xdc1',
        '\xa7\xdc2',
        '\xc6F\xa4O'],
    10: (10, 27, 1, 11, 8, 29, 5, 11, 3, 5, 4, 7),
    20: (15, 38, 2, 13, 11, 35, 6, 14, 4, 7, 5, 9),
    30: (20, 54, 3, 16, 14, 40, 7, 18, 4, 8, 6, 11),
    40: (25, 66, 3, 19, 17, 46, 8, 22, 5, 10, 8, 13),
    50: (30, 77, 3, 22, 20, 51, 9, 25, 6, 11, 9, 15),
    60: (35, 86, 4, 25, 23, 56, 10, 28, 7, 13, 9, 17),
    70: (40, 103, 4, 27, 26, 61, 12, 31, 8, 14, 11, 19),
    80: (57, 114, 6, 30, 30, 68, 13, 34, 10, 16, 12, 22),
    90: (64, 128, 7, 33, 33, 73, 13, 34, 10, 16, 13, 23),
    100: (70, 139, 7, 35, 36, 78, 13, 34, 10, 16, 14, 25),
    110: (76, 152, 7, 38, 39, 83, 13, 34, 10, 16, 16, 27),
    120: (82, 164, 8, 40, 45, 89, 13, 34, 10, 16, 18, 29) }
BUWEIS = None
