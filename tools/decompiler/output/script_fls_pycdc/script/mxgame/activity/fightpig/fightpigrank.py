# pycdc 交叉复核产物 · script.fls entry 4967
# co_filename(原始)='script/mxgame/activity/fightpig/fightpigrank.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4967.pyc (Python 2.5)

import combdialog
import interface
import combmacro

def ShowDlg():
    global g_FightPigRankDlg
    g_FightPigRankDlg = CFightPigRank()


class CFightPigRank(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog4/fightpig/ranking.dlg')
        self.m_tabRank = self.GetObject('tab_rank')
        lstData = [
            '111111',
            '222222',
            '333333',
            '444444']
        self.RefreshTable(lstData)
        self.ShowServerLVLimit()

    
    def RefreshTable(self, lstRank):
        self.m_tabRank.Clear()
        self.m_tabRank.AddTextItem(lstRank)
        self.m_tabRank.ResetItems()
        self.m_tabRank.ResetScrollBar()

    
    def CloseWindow(self):
        global g_FightPigRankDlg
        g_FightPigRankDlg = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid <= msgid:
            pass
        elif msgid <= 4:
            LOG_DEBUG('\xa6V\xaaA\xb0\xc8\xbe\xb9\xbd\xd0\xa8D%d\xacP\xaa\xba\xabH\xae\xa7', msgid)
        elif msgid <= msgid:
            pass
        elif msgid < interface.RIGHT_BUTTON_MESSAGE:
            LOG_DEBUG('\xc2I\xc0\xbb\xa4F%s', str(msgid))
        

    
    def ShowInfo(self, id, \xe8\xe7me, kind, coutry, ilv, arr):
        self.m_Infos = []
        import avatar
        self.m_Photo = avatar.GetBigImgBy4Int(self, arr[0], arr[1], arr[2], arr[3])
        (x, y) = self.GetObject('box_icon').GetPos()
        self.m_Photo.SetPos(x + 6, y + 6)
        self.m_ID = id
        self.m_Name = \xe8\xe7me
        lst = [
            ('txt_name', \xe8\xe7me),
            ('txt_id', '%d' % id),
            ('txt_class', kind),
            ('txt_coutry', coutry),
            ('txt_lv', '%d' % ilv)]
        for obj_name, txt in lst:
            txtobj = combmacro.CTEXT(interface.CTextObject, obj_name, self, txt, interface.FontLT14_3, interface.COLOR_9)
            self.m_Infos.append(txtobj)
        

    
    def ShowServerLVLimit(self):
        import hero
        color = interface.COLOR_56
        self.m_LvLimitTxt = combmacro.CreateText(interface.CTextObject, 'txt_lvlimit', self, str(hero.g_Prop.m_GradeLimit) + '\xaf\xc5', interface.FontLT12_1, color, spacing = 0, align = interface.ALIGN_LEFT | interface.ALIGN_MIDDLE)
