# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\createrole.py
import time, os, combdialog, combmacro, interface, ratio, ui, walker, misc
g_CreateHeroDlg = None
g_IsNewRoleCreated = False
g_FakeData = None
g_iEnterTime = None
g_CachedResObj = []
g_dSetupFirstInfo = None

def ModuleReset():
    global g_CachedResObj
    global g_CreateHeroDlg
    global g_FakeData
    global g_IsNewRoleCreated
    g_CreateHeroDlg = None
    g_IsNewRoleCreated = False
    g_FakeData = None
    g_CachedResObj = []
    return


EdgeFont12 = interface.FontLT12E_2
EdgeFont14 = interface.FontLT14E
EdgeFont14_2 = interface.FontLT14E_2
Font14 = interface.FontLT14
GradientEdgeFont14_2 = interface.FontLT14EG
GradientEdgeFont18_2 = interface.FontLT18EG
ROLE = [
 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
ROLEFORPATH = [TW_NOCHANGE('槱猀狨'), TW_NOCHANGE('羈魒鳶'), TW_NOCHANGE('錘疏桏'), TW_NOCHANGE('瑞鍊嫁'), TW_NOCHANGE('毞莽赽'), TW_NOCHANGE('堁拸陑'), TW_NOCHANGE('迶蹕价'), TW_NOCHANGE('筏ь⑦'), TW_NOCHANGE('僶盻赽'), TW_NOCHANGE(b'\xd1\xd7\xc8\xe7\xb7\xe7'), TW_NOCHANGE('ロ酵評'), TW_NOCHANGE(b'\xd7\xcf\xe6\xcc\xc8\xbb')]
ROLE_PATH_1024 = {'逍遙俠': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/0011_\xe5\xd0\xd2\xa3\xcf\xc0.png', 
   '霹靂火': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/0007_\xc5\xf9\xf6\xa8\xbb\xf0.png', 
   '風鈴兒': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/0002_\xb7\xe7\xc1\xe5\xb6\xf9.png', 
   '凌波燕': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/0005_\xc1\xe8\xb2\xa8\xd1\xe0.png', 
   '天蟬子': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/0004_\xcc\xec\xb2\xf5\xd7\xd3.png', 
   '玉羅剎': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/0001_\xd3\xf1\xc2\xde\xc9\xb2.png', 
   '淡清秋': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/0008_\xb5\xad\xc7\xe5\xc7\xef.png', 
   '雲無心': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/0003_\xd4\xc6\xce\xde\xd0\xc4.png', 
   '瀟湘子': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/0006_\xe4\xec\xcf\xe6\xd7\xd3.png', 
   '炎如風': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/0009_\xd1\xd7\xc8\xe7\xb7\xe7.png', 
   '千幻蝶': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/0000_\xc7\xa7\xbb\xc3\xb5\xfb.png', 
   '紫嫣然': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/0010_\xd7\xcf\xe6\xcc\xc8\xbb.png'}
ROLE_PATH_800 = {'逍遙俠': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/\xe5\xd0\xd2\xa3\xcf\xc0_800.png', 
   '霹靂火': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/\xc5\xf9\xf6\xa8\xbb\xf0_800.png', 
   '風鈴兒': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/\xb7\xe7\xc1\xe5\xb6\xf9_800.png', 
   '凌波燕': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/\xc1\xe8\xb2\xa8\xd1\xe0_800.png', 
   '天蟬子': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/\xcc\xec\xb2\xf5\xd7\xd3_800.png', 
   '玉羅剎': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/\xd3\xf1\xc2\xde\xc9\xb2_800.png', 
   '淡清秋': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/\xb5\xad\xc7\xe5\xc7\xef_800.png', 
   '雲無心': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/\xd4\xc6\xce\xde\xd0\xc4_800.png', 
   '瀟湘子': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/\xe4\xec\xcf\xe6\xd7\xd3_800.png', 
   '炎如風': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/\xd1\xd7\xc8\xe7\xb7\xe7_800.png', 
   '千幻蝶': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/\xc7\xa7\xbb\xc3\xb5\xfb_800.png', 
   '紫嫣然': b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/\xd7\xcf\xe6\xcc\xc8\xbb_800.png'}
ROLE_INFO = {'逍遙俠': '物理攻擊,劍法、筆法、拳法、刀法、槍法、暗器', 
   '霹靂火': '物理攻擊,劍法、筆法、拳法、刀法、槍法、暗器', 
   '風鈴兒': '物理攻擊,劍法、筆法、拳法、刀法、槍法、暗器', 
   '凌波燕': '物理攻擊,劍法、筆法、拳法、刀法、槍法、暗器', 
   '天蟬子': '法術攻擊,道家、儒法、巫術、鬼谷', 
   '玉羅剎': '法術攻擊,道家、儒法、巫術、鬼谷', 
   '淡清秋': '法術攻擊,道家、儒法、巫術、鬼谷', 
   '雲無心': '法術攻擊,道家、儒法、巫術、鬼谷', 
   '瀟湘子': '法術攻擊,佛家、儒法、陰陽', 
   '炎如風': '法術攻擊,佛家、儒法、陰陽', 
   '千幻蝶': '法術攻擊,佛家、儒法、陰陽', 
   '紫嫣然': '法術攻擊,佛家、儒法、陰陽'}
BAN_NAME_LIST = [
 3, 4, 
 6, 5, 
 8, 7, 
 10, 9, 
 11, 12, 
 13, 14, 
 54, 55]
LIUPAI_2_CLASS = {'劍': '戰士', 
   '刀': '戰士', 
   '槍': '戰士', 
   '拳': '戰士', 
   '筆': '戰士', 
   '暗器': '戰士', 
   '道法': '法師', 
   '儒法': '法師', 
   '巫法': '法師', 
   '鬼谷': '法師', 
   '佛學': '術士', 
   '陰陽': '術士', 
   '儒術': '術士'}
SETUP_TIME_FILE = [
 'ResLib.dll',
 'ndw',
 'mxupd.exe']

def SetNewCreateFlag(itype=False):
    global g_IsNewRoleCreated
    g_IsNewRoleCreated = itype
    return


def GetNewCreateFlag():
    return g_IsNewRoleCreated


def PreloadRes():
    import asynctaskqueue, asynctaskdefine, ratio
    if g_CachedResObj:
        return
    oQueue = asynctaskqueue.GetAsyncTaskQueue()
    setPng = set()
    setSpr = set()
    sFileName = 'login_new/createrole_item.dlg'
    (dUIInfoList, _) = combdialog.GetUIInfo(sFileName)
    if dUIInfoList:
        FilterPngAndSpr(setPng, setSpr, dUIInfoList)
    if ratio.Is800x600():
        sFileName = 'login_new/newcreaterole_800.dlg'
    else:
        sFileName = 'login_new/newcreaterole_1024.dlg'
    (dUIInfoList, _) = combdialog.GetUIInfo(sFileName)
    if dUIInfoList:
        FilterPngAndSpr(setPng, setSpr, dUIInfoList)
    for sSpr in setSpr:
        oQueue.InsertAsyncLoadPngTask(asynctaskdefine.TASK_TYPE_OTHER, sSpr, 'interface', misc.Functor(OnLoadOneSprFinish, sSpr, 'interface'))

    for sPng in setPng:
        oQueue.InsertAsyncLoadPngTask(asynctaskdefine.TASK_TYPE_OTHER, sPng, 'interface', misc.Functor(OnLoadOnePngFinish, sPng, 'interface'))

    for i in xrange(0, 12):
        sHeroName = ROLE[i]
        sBtnHeroPath1 = b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xc8\xcb\xce\xef\xcd\xb7\xcf\xf1/%s/0.png' % sHeroName
        sBtnHeroPath2 = b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xc8\xcb\xce\xef\xcd\xb7\xcf\xf1/%s/1.png' % sHeroName
        oQueue.InsertAsyncLoadPngTask(asynctaskdefine.TASK_TYPE_OTHER, sBtnHeroPath1, 'interface', misc.Functor(OnLoadOnePngFinish, sBtnHeroPath1, 'interface'))
        oQueue.InsertAsyncLoadPngTask(asynctaskdefine.TASK_TYPE_OTHER, sBtnHeroPath2, 'interface', misc.Functor(OnLoadOnePngFinish, sBtnHeroPath2, 'interface'))

    for i in xrange(0, 12):
        sHeroName = ROLE[i]
        sPath = b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xc8\xcb\xce\xef\xc3\xfb\xd7\xd6/\xbd\xc7\xc9\xab\xc3\xfb%s.png' % sHeroName
        oQueue.InsertAsyncLoadPngTask(asynctaskdefine.TASK_TYPE_OTHER, sPath, 'interface', misc.Functor(OnLoadOnePngFinish, sPath, 'interface'))

    return


def FilterPngAndSpr(setPng, setSpr, dUIInfoList):
    for dUIInfo in dUIInfoList:
        sPath = dUIInfo.get('sFileName', '')
        if sPath:
            if sPath.endswith('.png'):
                setPng.add(sPath)
            elif sPath.endswith('.spr'):
                setSpr.add(sPath)

    return


def OnLoadOnePngFinish(sPath, sPack, oTask):
    oObj = interface.CBitmapObject(None, sPath, sPack)
    oObj.SetShow(False)
    g_CachedResObj.append(oObj)
    return


def OnLoadOneSprFinish(sPath, sPack, oTask):
    oObj = interface.CSpriteObject(None, sPath, sPack)
    oObj.SetShow(False)
    g_CachedResObj.append(oObj)
    return


def ClearPreloadRes():
    global g_CachedResObj
    g_CachedResObj = []
    return


class CSelectPhoto(interface.CBoxObject):

    def __init__(self, parent, x, y, w, h, idx, dDesc):
        interface.CBoxObject.__init__(self, parent, w, h, 0, 0)
        self.SetPos(x, y)
        self.m_PhotoIndex = idx
        self.m_state = 'stand'
        self.m_Walker = walker.CFakeRole(self, -1, idx, dDesc)
        self.m_Walker.SetPos(w / 2, h - 10)
        return

    def ReSetDesc(self, dDesc):
        self.m_Walker.ChangeShape(self.m_PhotoIndex, dDesc)
        self.m_Walker.SetState(self.m_state)
        return

    def SetDirection(self, iDir):
        iDir = min(iDir, 31)
        iDir = max(iDir, 0)
        self.m_Walker.SetDirection(iDir)
        return

    def PlayEmote(self, state):
        if state == 'stand':
            self.m_Walker.SetEmote(0)
        else:
            _emoteid = {'attack': 9, 
               'walk': 8}
            self.m_Walker.PlayEmote(_emoteid[state])
        self.m_state = state
        return

    def GetState(self):
        return self.m_state


class CCreateRoleItem(combdialog.CCombSubWnd):

    def __init__(self, oParent, sBtnHeroPath, idx):
        combdialog.CCombSubWnd.__init__(self, oParent, 'login_new/createrole_item.dlg')
        self.GetObject('btn_hero3').SetPath(sBtnHeroPath + '1.png')
        self.GetObject('btn_hero1').SetPath(sBtnHeroPath + '0.png')
        self.m_idx = idx
        self.SetIgnoreEsc(True)
        return

    def SetDir(self, sDir):
        self.GetObject('btn_hero3').SetPos(*self.GetObject('loc_%s' % sDir).GetPos())
        self.GetObject('img_touxiangbg3').SetPos(*self.GetObject('loc_%s' % sDir).GetPos())
        self.GetObject('img_b2').SetPos(*self.GetObject('loc_%s' % sDir).GetPos())
        return

    def LeftUp(self):
        combdialog.CCombSubWnd.LeftUp(self)
        self.m_Fuc(100 + self.m_idx)
        self.OnClick()
        return

    def OnClick(self):
        self.GetObject('img_icon').SetShow(False)
        self.GetObject('img_touxiangbg3').SetShow(True)
        self.GetObject('img_b2').SetShow(True)
        self.GetObject('btn_hero3').SetShow(True)
        self.GetObject('img_touxiangbg1').SetShow(False)
        self.GetObject('img_b1').SetShow(False)
        self.GetObject('btn_hero1').SetShow(False)
        return

    def Leave(self):
        self.GetObject('img_icon').SetShow(False)
        return

    def Enter(self):
        self.GetObject('img_icon').SetShow(True)
        return

    def SetClickCallBack(self, func):
        self.m_Fuc = func
        return

    def ResetBack(self):
        self.GetObject('img_touxiangbg3').SetShow(False)
        self.GetObject('img_b2').SetShow(False)
        self.GetObject('btn_hero3').SetShow(False)
        self.GetObject('img_touxiangbg1').SetShow(True)
        self.GetObject('img_b1').SetShow(True)
        self.GetObject('btn_hero1').SetShow(True)
        return


class CCreateHeroDialog(combdialog.CCombPanel):

    class CMyEdit(interface.CEdit):

        def AddChar(self, c):
            if len(c) == 2 and ord(c[0]) == 169 and ord(c[1]) in (161, 162, 163):
                return
            interface.CEdit.AddChar(self, c)
            return

    ZHANSHI_LIUPAI = ('btn_zs_jian', 'btn_zs_bi', 'btn_zs_quan', 'btn_zs_dao', 'btn_zs_qiang',
                      'btn_zs_anqi')
    FASHI_LIUPAI = ('btn_fs_daofa', 'btn_fs_wufa', 'btn_fs_rufa', 'btn_fs_guigu')
    SHUSHI_LIUPAI = ('btn_ss_yinyang', 'btn_ss_foxue', 'btn_ss_rushu')
    LIUPAI_WORD = ('jian', 'bi', 'quan', 'dao', 'qiang', 'anqi', 'daofa', 'wushu',
                   'rufa', 'guigu', 'yinyang', 'foxue', 'rushu')
    CHOOSE_LIUPAI_COUNT = (ZHANSHI_LIUPAI, FASHI_LIUPAI, SHUSHI_LIUPAI)
    MSGID2LIUPAI = {13: '劍', 
       14: '筆', 
       15: '拳', 
       16: '刀', 
       17: '槍', 
       18: '暗器', 
       19: '道法', 
       20: '巫法', 
       21: '儒法', 
       22: '鬼谷', 
       23: '陰陽', 
       24: '佛學', 
       25: '儒術'}
    LIUPAI2ID = {'劍': 1001, 
       '刀': 1002, 
       '槍': 1003, 
       '拳': 1004, 
       '筆': 1005, 
       '暗器': 1011, 
       '道法': 1007, 
       '儒法': 1006, 
       '巫法': 1010, 
       '鬼谷': 1014, 
       '佛學': 1008, 
       '陰陽': 1009, 
       '儒術': 1006}

    def __init__(self, iNewCount=False):
        combdialog.CCombPanel.__init__(self, interface.DialogPanel, 'login_new/newcreaterole', bIsResize=True)
        self.m_iLastCreatTime = None
        self.m_oGuideTip = None
        self.m_CurChoose = ROLE[0]
        self.LoadHeroImg()
        (x, y, w, h) = self.GetLocData('box_fakerole')
        self.m_SelectPhoto = CSelectPhoto(self, x, y, w, h, 0, 0)
        self.m_Direction = 1
        self.m_State = 'stand'
        self.UpdateFakeRole()
        self.m_iLiuPai = -1
        self.m_iLiupaiType = -1
        self.m_Btns = []
        self.m_Btns.append(self.GetObject('btn_zs'))
        self.m_Btns.append(self.GetObject('btn_fs'))
        self.m_Btns.append(self.GetObject('btn_ss'))
        self.SetHighLightHide()
        self.m_LastSex = 1
        self.m_ChangeNameFlag = False
        self.InitSize()
        self.InitRoleIcon()
        self.InitSelectServerBtn()
        self.InitSelectLiuPaiBtn()
        self.GetObject('btn_return').SetShow(not iNewCount)
        import plotprodelay, frametaskmgr, cg
        frametaskmgr.GetFrameTaskMgr().AddDelayTask(0.1, cg.PreLoadCgBg)
        frametaskmgr.GetFrameTaskMgr().AddDelayTask(0.2, plotprodelay.PreLoadJuBen)
        frametaskmgr.GetFrameTaskMgr().AddDelayTask(0.3, plotprodelay.PreLoadJuQingRes)
        import timer
        timer.Timer(0.034, self.InitRandomName)
        return

    def InitRandomName(self):
        self.m_NameEdit = combmacro.CEDIT(self.CMyEdit, 'box_edit', self, interface.COLOR_5, Font14, interface.COLOR_5)
        self.m_NameEdit.SetTextAlign(interface.ALIGN_CENTER_MIDDLE)
        self.m_NameEdit.SetLimit(14)
        self.m_NameEdit.SetZ(1000)
        self.m_LastName = self.RandomName()
        self.m_NameEdit.SetText(self.m_LastName)
        return

    def BeIsCanChooseLiuPai(self):
        return True

    def SetBtnsShow(self, iGroup):
        import random
        bShowZhanshi = False
        bShowFashi = False
        bShowShushi = False
        if iGroup == 1:
            bShowZhanshi = True
        elif iGroup == 2:
            bShowFashi = True
        elif iGroup == 3:
            bShowShushi = True
        bChangeType = False
        if self.m_iLiupaiType != iGroup:
            self.m_iLiupaiType = iGroup
            self.m_iLiuPai = -1
            self.SetLiuPaiImagShow(self.m_iLiuPai)
            self.GetLiuPaiInfoShow(self.m_iLiuPai)
            bChangeType = True
        for sZhanshiBtn in self.ZHANSHI_LIUPAI:
            self.GetObject(sZhanshiBtn).SetShow(bShowZhanshi)
            if self.m_iLiuPai == -1:
                self.GetObject(sZhanshiBtn).SetSelect(False)

        for sFashiBtn in self.FASHI_LIUPAI:
            self.GetObject(sFashiBtn).SetShow(bShowFashi)
            if self.m_iLiuPai == -1:
                self.GetObject(sFashiBtn).SetSelect(False)

        for sShushiBtn in self.SHUSHI_LIUPAI:
            self.GetObject(sShushiBtn).SetShow(bShowShushi)
            if self.m_iLiuPai == -1:
                self.GetObject(sShushiBtn).SetSelect(False)

        if bChangeType and self.BeIsCanChooseLiuPai():
            self.GetObject(random.choice(self.CHOOSE_LIUPAI_COUNT[iGroup - 1])).LeftUp()
        return

    def SetLiuPaiImagShow(self, iLiupai):
        for (index, sLiupaiWord) in enumerate(self.LIUPAI_WORD):
            if iLiupai == index:
                self.GetObject('img_%s' % sLiupaiWord).SetShow(True)
            else:
                self.GetObject('img_%s' % sLiupaiWord).SetShow(False)

        return

    def GetLiuPaiInfoShow(self, iLiupai):
        if iLiupai == -1:
            iShowChangeJob = False
        else:
            iShowChangeJob = True
        self.GetObject('box_tedian').SetShow(iShowChangeJob)
        self.GetObject('img_qingxuanze').SetShow(not iShowChangeJob)
        self.GetObject('txt_tedian_title').SetShow(iShowChangeJob)
        self.GetObject('img_tedian_title').SetShow(iShowChangeJob)
        if iLiupai == -1:
            return
        import liupaiselinfodata
        sLiupaiInfos = liupaiselinfodata.DATA[self.m_iLiupaiType]
        for (index, data) in enumerate(sLiupaiInfos):
            if data[5] == self.LIUPAI_WORD[iLiupai]:
                return data[6]

        return

    def GetLiuPaiSkillID(self):
        if self.m_iLiuPai == -1:
            return
        sLiuPai = self.MSGID2LIUPAI[self.m_iLiuPai + 13]
        iSkillID = self.LIUPAI2ID[sLiuPai]
        return iSkillID

    def SetLiuPaiInfoText(self, sText):
        self.GetObject('box_tedian').SetText(sText)
        return

    def RefreshTitle(self):
        sLiuPai = self.MSGID2LIUPAI[self.m_iLiuPai + 13]
        self.GetObject('txt_school').SetText('%s·%s' % (LIUPAI_2_CLASS[sLiuPai], sLiuPai))
        return

    def InitRoleIcon(self):
        import timer
        self.m_lHeroItem = []
        for i in xrange(0, 12):
            sHeroName = ROLEFORPATH[i]
            sBtnHeroPath = b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xc8\xcb\xce\xef\xcd\xb7\xcf\xf1/%s/' % sHeroName
            oRoleItem = CCreateRoleItem(self.GetObject('loc_hero%s' % i), sBtnHeroPath, i)
            oRoleItem.GetObject('img_touxiangbg3').SetShow(False)
            oRoleItem.GetObject('img_b2').SetShow(False)
            oRoleItem.GetObject('btn_hero3').SetShow(False)
            oRoleItem.SetClickCallBack(self.OnMessage)
            oRoleItem.SetDir((i + 3) % 4)
            self.m_lHeroItem.append(oRoleItem)

        import random
        iRandomIdx = random.randint(0, 9)
        if 0 <= iRandomIdx <= 4:
            iBeginIdx = 0
        elif 5 <= iRandomIdx <= 7:
            iBeginIdx = 4
        else:
            iBeginIdx = 8
        iSelIdx = random.randint(0, 3) + iBeginIdx
        timer.Timer(0.0, self.m_lHeroItem[iSelIdx].LeftUp)
        return

    def InitSize(self):
        (self.m_Width, self.m_Height) = self.GetObject('loc_bg').GetSize()
        return

    def InitSelectServerBtn(self):
        r"""\xaa\xec\xa9l\xa4ƿ\xef\xbeܪA\xb0Ⱦ\xb9\xab\xf6\xb6s"""
        import netserver, misc
        if misc.IsTWServer():
            for sName in ('img_serverinfo', 'btn_SelectServer', 'CurServer1'):
                self.GetObject(sName) and self.GetObject(sName).SetShow(False)

            return
        if netserver.g_LoginServer and netserver.g_LoginServer[1]:
            sTxt = netserver.g_LoginServer[1]
        else:
            sTxt = '選擇服務器'
        obj = self.GetObject('btn_SelectServer')
        obj.SetText(sTxt)
        return

    def InitSelectLiuPaiBtn(self):
        for i in self.CHOOSE_LIUPAI_COUNT:
            for j in i:
                self.GetObject(j) and self.GetObject(j).SetSelectWithLight(True)

        return

    def CheckCreateTime(self):
        import C_sys, usermacro
        if self.m_iLastCreatTime is None:
            self.m_iLastCreatTime = C_sys.GetTime()
            return True
        iCurTime = C_sys.GetTime()
        if iCurTime - self.m_iLastCreatTime > 20000:
            self.m_iLastCreatTime = iCurTime
            return True
        else:
            usermacro.PROMPT_MSG(usermacro.TRYAGAIN)
            return False
        return

    def SetHighLightHide(self):
        for i in range(12):
            self.GetObject('img_icon%d' % i).SetShow(False)

        return

    def SetFakeRole(self, idx):
        (x, y, w, h) = self.GetLocData('box_fakerole')
        self.m_Direction = 1
        iDir = self.m_Direction
        if self.m_State == 'attack':
            iDir -= 1
        state = self.m_SelectPhoto.GetState()
        if 0 <= self.m_iLiuPai < 6:
            iWeaponIndex = self.m_iLiuPai + 1
        else:
            iWeaponIndex = 1
        dDesc = {'weapon': [iWeaponIndex, 3, 0], 'color': [
                   0, 0, 0], 
           'wing': [
                  0], 
           'Realcolor': [
                       0, 0, 0]}
        self.m_SelectPhoto = CSelectPhoto(self, x, y, w, h, idx, dDesc)
        self.m_SelectPhoto.SetDirection(iDir * 4)
        self.m_SelectPhoto.PlayEmote(state)
        return

    def SetFakeRoleWeaponKind(self):
        if 0 <= self.m_iLiuPai < 6:
            iWeaponKind = self.m_iLiuPai + 1
        else:
            iWeaponKind = 1
        dDesc = {'weapon': [iWeaponKind, 3, 0], 'color': [
                   0, 0, 0], 
           'wing': [
                  0], 
           'Realcolor': [
                       0, 0, 0]}
        if self.m_SelectPhoto:
            self.m_SelectPhoto.ReSetDesc(dDesc)
        return

    def SwitchClass(self, idx):
        sType = self.GetType(idx)
        self.GetObject('btn_fs').SetPath(b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xd6\xb0\xd2\xb5\xd1\xa1\xd4\xf1/\xb7\xa8\xca\xa6/0.png')
        self.GetObject('btn_zs').SetPath(b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xd6\xb0\xd2\xb5\xd1\xa1\xd4\xf1/\xd5\xbd\xca\xbf/0.png')
        self.GetObject('btn_ss').SetPath(b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xd6\xb0\xd2\xb5\xd1\xa1\xd4\xf1/\xca\xf5\xca\xbf/0.png')
        self.m_Btns[idx].SetPath(b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xd6\xb0\xd2\xb5\xd1\xa1\xd4\xf1/%s/1.png' % sType)
        self.CentClassImg()
        return

    def CentClassImg(self):
        oImg = self.GetObject('btn_fs')
        oLoc = self.GetObject('loc_class_fs')
        interface.AlignObjects(oImg, oLoc, interface.ALIGN_CENTER_MIDDLE)
        oImg = self.GetObject('btn_zs')
        oLoc = self.GetObject('loc_class_zs')
        interface.AlignObjects(oImg, oLoc, interface.ALIGN_CENTER_MIDDLE)
        oImg = self.GetObject('btn_ss')
        oLoc = self.GetObject('loc_class_ss')
        interface.AlignObjects(oImg, oLoc, interface.ALIGN_CENTER_MIDDLE)
        return

    def UpdateFakeRole(self):
        iDir = self.m_Direction
        if self.m_State == 'attack':
            iDir -= 1
        self.m_SelectPhoto.SetDirection(iDir * 4)
        self.m_SelectPhoto.PlayEmote(self.m_State)
        return

    def UpdateHeroInfo(self, heroName):
        imgList = self.m_HeroImgList.get(self.m_CurChoose)
        for img in imgList:
            img.SetShow(False)

        self.m_CurChoose = heroName
        if heroName not in ROLEFORPATH and heroName in ROLE:
            sHeroNamePath = ROLEFORPATH[ROLE.index(heroName)]
        else:
            sHeroNamePath = heroName
        self.GetObject('box_name').SetPath(b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xc8\xcb\xce\xef\xc3\xfb\xd7\xd6/\xbd\xc7\xc9\xab\xc3\xfb%s.png' % sHeroNamePath, interface.UIPath)
        sJieShao = ROLE_INFO.get(heroName)
        (sAttackType, sLiuPai) = sJieShao.split(',')
        self.GetObject('txt_shuxing').SetText(sAttackType)
        for i in range(1, 7):
            self.GetObject('txt_liupai%s' % i).SetShow(False)
            self.GetObject('img_fenge%s' % i).SetShow(False)

        i = 0
        for sLiuPai in sLiuPai.split('、'):
            i = i + 1
            self.GetObject('txt_liupai%s' % i).SetShow(True)
            self.GetObject('img_fenge%s' % i).SetShow(True)
            self.GetObject('txt_liupai%s' % i).SetText(sLiuPai)

        return

    def ShowRoleImg(self, idx):
        heroImgList = self.m_HeroImgList.get(ROLE[idx])
        for img in heroImgList:
            img.SetShow(True)

        return

    def LoadHeroImg(self):
        self.m_HeroImgList = {}
        for heroIdx in xrange(0, 12):
            imgList = []
            heroImg = self.GetObject('img_hero%d' % heroIdx)
            heroImg.SetShow(False)
            imgList.append(heroImg)
            self.m_HeroImgList[ROLE[heroIdx]] = imgList

        return

    def GetSex(self):
        if self.m_CurChoose in ('逍遙俠', '霹靂火', '天蟬子',
                                '雲無心', '瀟湘子',
                                '炎如風'):
            return 1
        else:
            return 2
        return

    def GetType(self, idx):
        if idx == 0:
            return TW_NOCHANGE('սʿ')
        elif idx == 1:
            return TW_NOCHANGE('楊呇')
        else:
            return TW_NOCHANGE('扲尪')
        return

    def RandomName(self):
        sex = self.GetSex()
        self.m_LastSex = sex
        import clientinterface
        while True:
            name = clientinterface.GetName(sex)
            if name == '':
                continue
            if len(name) < 3:
                continue
            if name[:2] == '※':
                continue
            if name.isdigit():
                continue
            if name.find(' ') != -1:
                continue
            break

        self.m_RandName = name
        return name

    def CreateRole(self):
        import usermacro, sound, clientinterface, sounddefine
        sound.Play(sounddefine.PATH_BTN_SOUND)
        info = {'逍遙俠': (1, 111, 0, 0), 
           '霹靂火': (3, 112, 0, 0), 
           '天蟬子': (1, 121, 0, 1), 
           '雲無心': (3, 122, 0, 1), 
           '瀟湘子': (1, 131, 0, 2), 
           '炎如風': (3, 132, 0, 2), 
           '凌波燕': (2, 211, 0, 0), 
           '風鈴兒': (4, 212, 0, 0), 
           '玉羅剎': (2, 221, 0, 1), 
           '淡清秋': (4, 222, 0, 1), 
           '千幻蝶': (2, 231, 0, 2), 
           '紫嫣然': (4, 232, 0, 2)}
        if not self.CheckCreateTime():
            return
        name = self.m_NameEdit.GetText()
        (valid, tipstr) = clientinterface.IsValidName(name, True)
        if not valid:
            usermacro.PROMPT_MSG(tipstr)
            return
        if name in BAN_NAME_LIST:
            usermacro.PROMPT_MSG('角色名字包含違禁詞彙')
            return
        liupaiskid = self.GetLiuPaiSkillID()
        if not liupaiskid:
            import dlgguidetips
            (x, y, w, h) = self.GetLocData('btn_ss_yinyang')
            self.m_oGuideTip = dlgguidetips.CGuideTips(self, '    請選擇流派', 3, x, y, w, h)
            self.m_oGuideTip.SetZ(100)
            return
        (icon, shape, color, major) = info[self.m_CurChoose]
        import netlogin

        def CreateRoleErr(err_id, err_msg):
            usermacro.PROMPT_MSG('創建角色未成功，請再次嘗試#r%s' % err_msg)
            netlogin.g_LoginErrorCallback = None
            return

        randflag = 0 if name == self.m_RandName else 1
        SetNewCreateFlag(True)
        CreateFakeData(name, icon, shape, major, randflag, liupaiskid)
        import misc
        if self.CheckSpecialEmail():
            self.DoPhraseCheck()
        elif not misc.IsTWServer() and netlogin.GetFakeRoleFlag():
            SetFakeData()
            netlogin.C2SLoginCreateRoleSucc()
        else:
            CheckAndSendRoleInfo()
            netlogin.C2SLoginPlayerAdd(name, icon, shape, color, major, randflag, liupaiskid)
        netlogin.g_LoginErrorCallback = CreateRoleErr
        return

    def CheckSpecialEmail(self):
        import checkemaildata, netlogin
        email = netlogin.g_CurrAccount
        findFlag = False
        for emailUrl in checkemaildata.PHRASE_DATA:
            if emailUrl in email:
                findFlag = True
                break

        levelFlag = True
        for info in netlogin.g_LoginRoleInfo:
            if info['Level'] >= 50:
                levelFlag = False
                break

        if findFlag and levelFlag and not getattr(self, 'm_PhraseFlag', False):
            self.m_PhraseFlag = True
            return True
        return False

    def DoPhraseCheck(self):
        import mxv
        mxv.ShowClientPhraseCheck(-1)
        return

    def BnEnter(self, msgid):
        idx = msgid - 100
        self.GetObject('img_icon%d' % idx).SetShow(True)
        return

    def BnLeave(self, msgid):
        idx = msgid - 100
        btnobj = self.GetObject('btn_hero%d' % idx)
        if hasattr(btnobj, 'm_DownFlag') and self.GetObject('btn_hero%d' % idx).m_DownFlag:
            return
        self.GetObject('img_icon%d' % idx).SetShow(False)
        return

    def BnLeftUp(self, msgid):
        self.SetHighLightHide()
        idx = msgid - 100
        for i in range(12):
            self.GetObject('btn_hero%d' % i).m_DownFlag = False

        self.GetObject('btn_hero%d' % idx).m_DownFlag = True
        self.GetObject('img_icon%d' % idx).SetShow(True)
        self.GetObject('img_b%d' % idx).SetShow(True)
        return

    def RefershBtnEnable(self, msgid):
        msgid2btnname = {8: 'btn_stand', 
           9: 'btn_run', 
           10: 'btn_attack'}
        for mid in msgid2btnname:
            self.GetObject(msgid2btnname[mid]).Enable(True)

        self.GetObject(msgid2btnname[msgid]).Enable(False)
        return

    def CreateRandomName(self):
        self.m_LastName = self.RandomName()
        self.m_NameEdit.SetText(self.m_LastName)
        return

    def SelectRoleImgIcon(self):
        for i in xrange(0, 12):
            oItem = self.m_lHeroItem[i]
            oItem.ResetBack()

        return

    def OnSelectServer(self, dServerInfo):
        r"""\xbf\xef\xbeܪA\xb0Ⱦ\xb9\xa6^\xbd\xd5"""
        import selectserver, netserver
        if netserver.g_LoginServer and netserver.g_LoginServer[0] == dServerInfo['district'] and netserver.g_LoginServer[1] == dServerInfo['name']:
            selectserver.Show(False)
            return
        if netserver.g_LoginServerID:
            import netlogin
            netlogin.C2SSelectOtherServer(netserver.g_LoginServerID)
        selectserver.TransferServer(dServerInfo)
        return

    def SelectServer(self):
        import selectserver
        selectserver.Show(True, self, misc.Functor(self.OnSelectServer))
        return

    def OnMessage(self, msgId):
        if msgId == 2:
            Show(False)
            import selectrole, sound, sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            selectrole.Show(True)
            import clickcounter
            clickcounter.LoginLog('創建角色頁-返回')
        elif msgId in (8, 9, 10):
            self.m_State = ('stand', 'walk', 'attack')[msgId - 8]
            self.UpdateFakeRole()
            self.RefershBtnEnable(msgId)
        elif msgId in (4, 5):
            if msgId == 5:
                if self.m_State in ('stand', 'walk'):
                    self.m_Direction -= 1
                else:
                    self.m_Direction -= 2
                if self.m_Direction < 0:
                    self.m_Direction = 7
            else:
                if self.m_State in ('stand', 'walk'):
                    self.m_Direction += 1
                else:
                    self.m_Direction += 2
                if self.m_Direction > 7:
                    self.m_Direction = 0
            self.UpdateFakeRole()
        elif msgId == 7:
            self.CreateRole()
            import clickcounter
            clickcounter.LoginLog('創建角色頁-創建角色')
        elif msgId == 11:
            self.CreateRandomName()
            self.m_ChangeNameFlag = True
        elif msgId == 12:
            self.SelectServer()
        elif msgId in xrange(100, 112):
            idx = msgId - 100
            iLiupaiType = idx / 4 + 1
            self.SetBtnsShow(iLiupaiType)
            self.UpdateHeroInfo(ROLE[idx])
            self.ShowRoleImg(idx)
            self.SelectRoleImgIcon()
            self.SetFakeRole((111, 112, 211, 212, 121, 122, 221, 222, 131, 132, 231,
                              232)[idx])
            self.SwitchClass(idx / 4)
            if hasattr(self, 'm_NameEdit'):
                roleName = self.m_NameEdit.GetText()
                if self.m_LastName != roleName:
                    self.m_ChangeNameFlag = True
                if self.m_LastName == roleName and not self.m_ChangeNameFlag:
                    self.CreateRandomName()
        elif 13 <= msgId <= 25:
            self.m_oGuideTip = None
            self.m_iLiuPai = msgId - 13
            self.SetLiuPaiImagShow(self.m_iLiuPai)
            sText = self.GetLiuPaiInfoShow(self.m_iLiuPai)
            self.SetLiuPaiInfoText(sText)
            self.SetFakeRoleWeaponKind()
            self.RefreshTitle()
            self.m_Direction = 1
            self.UpdateFakeRole()
        return


def CreateFakeData(name, icon, shape, major, randflag, liupai):
    global g_FakeData
    data = {}
    data['Name'] = name
    data['Icon'] = icon
    data['Shape'] = shape
    data['School'] = major
    data['randomflag'] = randflag
    data['Level'] = 0
    data['Photo'] = (icon - 1) % 12 + 1
    data['Point'] = 0
    data['Race'] = 0
    data['time'] = 1
    data['delstate'] = 0
    data['ID'] = 0
    data['Desc'] = 0
    data['liupai'] = liupai
    g_FakeData = data
    return


def SetFakeData():
    import netlogin
    netlogin.SetFakeRoleInfo(g_FakeData)
    netlogin.OnSuccessCreateRole()
    return


def GetClientSetupInfo():
    global g_dSetupFirstInfo
    if g_dSetupFirstInfo is None:
        g_dSetupFirstInfo = {}
        iTimeList = []
        for sPath in SETUP_TIME_FILE:
            try:
                if os.path.exists(sPath):
                    iTimeList.append(os.path.getctime(sPath))
            except:
                pass

        if iTimeList:
            iMinTime = int(min(iTimeList))
            iDiff = int(time.time()) - iMinTime
            g_dSetupFirstInfo['iSetupTime'] = iDiff / 86400
        else:
            g_dSetupFirstInfo['iSetupTime'] = 0
        iMinTime = None
        sMinFile = None
        try:
            if os.path.isdir('users'):
                for sPath in os.listdir('users'):
                    if sPath.endswith('.d'):
                        iTime = os.path.getctime(os.path.join('users', sPath))
                        if iMinTime is None or iTime < iMinTime:
                            iMinTime = iTime
                            sMinFile = sPath

        except Exception, e:
            LOG_DEBUG('讀取users出錯', e)
        else:
            if sMinFile:
                sMinFile = os.path.splitext(sMinFile)[0]
                iFileLen = len(sMinFile)
                if '@' in sMinFile:
                    iTargetIdx = 0
                    for iIdx in xrange(iFileLen - 1, 0, -1):
                        if not sMinFile[iIdx].isdigit():
                            iTargetIdx = iIdx
                            break

                    sAccount = sMinFile[0:iTargetIdx + 1]
                    sUser = sMinFile[iTargetIdx + 1:]
                elif sMinFile.isdigit() and iFileLen > 11:
                    sAccount = sMinFile[0:11]
                    sUser = sMinFile[11:]
                elif sMinFile.startswith('#') and iFileLen % 2 == 1 and sMinFile[1:iFileLen / 2 + 1] == sMinFile[iFileLen / 2 + 1:]:
                    sAccount = sMinFile[0:iFileLen / 2 + 1]
                    sUser = sAccount
                else:
                    sAccount = ''
                    sUser = ''
            else:
                sAccount = ''
                sUser = ''
            g_dSetupFirstInfo['sAccount'] = sAccount
            g_dSetupFirstInfo['sUser'] = sUser
    return g_dSetupFirstInfo


def CheckAndSendRoleInfo():
    if misc.IsTWServer():
        return
    import netlogin
    dClientSetupInfo = GetClientSetupInfo()
    LOG_DEBUG('CheckAndSendRoleInfo', dClientSetupInfo)
    if dClientSetupInfo['iSetupTime'] < 0 or dClientSetupInfo['iSetupTime'] > 65535:
        iSetupTime = 65535
    else:
        iSetupTime = dClientSetupInfo['iSetupTime']
    netlogin.C2GSRoleInfoLog(iSetupTime, dClientSetupInfo['sAccount'])
    return


def CheckClientUseInfo():
    if misc.IsTWServer():
        return
    import netcommon, cfg
    dClientSetupInfo = GetClientSetupInfo()
    if dClientSetupInfo['iSetupTime'] < 0 or dClientSetupInfo['iSetupTime'] > 65535:
        iSetupTime = 65535
    else:
        iSetupTime = dClientSetupInfo['iSetupTime']
    sLoginInfos = cfg.GetData('mx.ini', 'Game', 'LoginTime')
    if sLoginInfos is None:
        sLoginInfos = ''
    sLoginInfoLst = sLoginInfos.split(',')
    iLoginTimeLst = []
    for sLoginInfo in sLoginInfoLst:
        if sLoginInfo:
            try:
                (sHeroID, sLoginTime) = sLoginInfo.split(':')
                iLoginTimeLst.append(int(sLoginTime))
            except ValueError:
                continue

    if iLoginTimeLst:
        iLastLoginTime = max(iLoginTimeLst)
    else:
        iLastLoginTime = 0
    iSerCurTime = misc.GetServerCurrentTime()
    iDiff = int(iSerCurTime) - iLastLoginTime
    iNotLoginDay = iDiff / 86400
    netcommon.C2GSClientNotLoginDay(iSetupTime, iNotLoginDay)
    LOG_DEBUG('LoginInfoLog', time.localtime(iSerCurTime), time.localtime(iLastLoginTime), iSetupTime, iNotLoginDay)
    return


def Show(isShow=True, iNewCount=False):
    global g_CreateHeroDlg
    global g_iEnterTime
    if isShow:
        import C_sys
        g_CreateHeroDlg = CCreateHeroDialog(iNewCount)
        g_iEnterTime = C_sys.GetTime()
    else:
        g_CreateHeroDlg and g_CreateHeroDlg.SetShow(False)
        g_CreateHeroDlg = None
        if g_iEnterTime:
            import C_sys, netlogin, misc
            iHideTime = C_sys.GetTime()
            iDeltaTime = (iHideTime - g_iEnterTime) / 10000.0
            if not misc.IsTWServer():
                netlogin.C2SRoleCreateUIStayTime(iDeltaTime)
            g_iEnterTime = None
    return


return
