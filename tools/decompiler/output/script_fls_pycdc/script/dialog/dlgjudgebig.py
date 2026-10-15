# pycdc 交叉复核产物 · script.fls entry 154
# co_filename(原始)='script/dialog/dlgjudgebig.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_154.pyc (Python 2.5)

import interface
import net
import ui
RECORD_FIRST_X = 250
RECORD_FIRST_Y = 320
RECORD_SECOND_X = 250 + 85
RECORD_SECOND_Y = 320
RECORD_THIRD_X = 250 + 85 * 2
RECORD_THIRD_Y = 320
RECORD_FORTH_X = 250 + 85 * 3
RECORD_FORTH_Y = 320
RECORD_FIRTH_X = 250 + 85 * 4
RECORD_FIRTH_Y = 320
RECORD_PC_FIRST_X = 250
RECORD_PC_FIRST_Y = 90
RECORD_PC_SECOND_X = 250 + 85
RECORD_PC_SECOND_Y = 90
RECORD_PC_THIRD_X = 250 + 85 * 2
RECORD_PC_THIRD_Y = 90
RECORD_PC_FORTH_X = 250 + 85 * 3
RECORD_PC_FORTH_Y = 90
RECORD_PC_FIRTH_X = 250 + 85 * 4
RECORD_PC_FIRTH_Y = 90
CHANGE_POINT_X = 250 + 85 * 3
CHANGE_POINT_Y = 500
CHANGE_ADD_POINT_X = 250 + 60
CHANGE_ADD_POINT_Y = 500
BIG_STAR_X = 430 + 35
BIG_STAR_Y = 452
CHANGE_BUTTON_X = 250 + 85 * 2
CHANGE_BUTTON_Y = 235
INVEST_X = 250
INVEST_Y = 455
LEVEL_X = 500
LEVEL_Y = 455
SHOW_TOTAL_X = 480
SHOW_TOTAL_Y = 460
g_ChangeCard = { }
g_JudgebigDlg = None

def ModuleReset():
    global g_ChangeCard, g_JudgebigDlg
    g_ChangeCard = None
    g_JudgebigDlg = None


def Show1():
    global g_JudgebigDlg
    g_JudgebigDlg = CJudgeBig()


def UpdatePointAndLevel(point, level):
    g_JudgebigDlg.UpdatePointAndLevel(point, level)


def UpdatePlayerCard(card_data):
    g_JudgebigDlg.SendCard(card_data)


def UpdateResult(card_data, point, level):
    g_JudgebigDlg.GetCardResult(card_data, point, level)


def UpdateChangeCard(card_data):
    g_JudgebigDlg.UpdateChangeCard(card_data)


def UpdatePcChangeCard(card_data):
    g_JudgebigDlg.SetPcChangeCard(card_data)


def UpdateInvestChip(num, num1):
    g_JudgebigDlg.ShowInvestChip(num, num1)


class CMyButton(interface.CButton):
    
    def __init__(self, parent, filename, x, y, msgid = 0):
        interface.CImagesObject.__init__(self, parent, filename, interface.UIPath)
        interface.CClickObject.__init__(self, msgid)
        self.m_FName = filename
        self.SetPos(x, y)
        self._x = x
        self._y = y
        self.m_type = 0
        self.m_msgid = msgid

    
    def LeftUp(self):
        interface.CButton.LeftUp(self)
        if self.GetParent().record_nonce_type == 0:
            if self.m_type == 0:
                self.m_type = 1
                g_ChangeCard[self.m_msgid] = self.m_type
                self.GetParent().m_ChangeButton.SetShow(True)
                self.GetParent().m_ShowButton.SetShow(False)
                self.SetPos(self._x, self._y - 15)
            else:
                self.m_type = 0
                g_ChangeCard.pop(self.m_msgid)
                if len(g_ChangeCard) == 0:
                    self.GetParent().m_ChangeButton.SetShow(False)
                    self.GetParent().m_ShowButton.SetShow(True)
                
                self.SetPos(self._x, self._y)
        



class CJudgeBig(interface.CImagesObject, interface.CBase):
    
    def __init__(self):
        interface.CImagesObject.__init__(self, interface.CapturePanel, 'dialog/judge_big/bottom.igs', interface.UIPath)
        interface.Center(self)
        self.MessageProcess()
        self.Capture(1, 0)
        self.record_pc_card_type = 1
        self.record_pc_card = 1
        self.first_card = ui.CImage(self, 'dialog/judge_big/dragon.igs', interface.UIPath)
        self.first_card.SetPos(30, 270)
        self.second_card = ui.CImage(self, 'dialog/judge_big/cow.igs', interface.UIPath)
        self.second_card.SetPos(30, 315)
        self.third_card = ui.CImage(self, 'dialog/judge_big/ghost_king.igs', interface.UIPath)
        self.third_card.SetPos(30, 360)
        self.forth_card = ui.CImage(self, 'dialog/judge_big/wolf.igs', interface.UIPath)
        self.forth_card.SetPos(30, 400)
        self.fifth_card = ui.CImage(self, 'dialog/judge_big/rabbit.igs', interface.UIPath)
        self.fifth_card.SetPos(30, 445)
        self.sixth_card = ui.CImage(self, 'dialog/judge_big/big_grass.igs', interface.UIPath)
        self.sixth_card.SetPos(30, 485)
        self.m_Big_Star = ui.CImage(self, 'dialog/judge_big/big_star.igs', interface.UIPath)
        self.m_Big_Star.SetPos(BIG_STAR_X, BIG_STAR_Y)
        self.change_point = interface.CButton(self, 'dialog/judge_big/point_change.igs', 0, 0, 60)
        self.change_point.SetPos(CHANGE_POINT_X, CHANGE_POINT_Y)
        self.add_point = interface.CButton(self, 'dialog/judge_big/add_point.igs', 0, 0, 30)
        self.add_point.SetPos(CHANGE_ADD_POINT_X, CHANGE_ADD_POINT_Y)
        self.m_ChangeButton = interface.CButton(self, 'dialog/judge_big/changecard.igs', 0, 0, 62)
        self.m_ChangeButton.SetPos(CHANGE_BUTTON_X, CHANGE_BUTTON_Y)
        None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, **self).SetShow(False)
        self.m_StartButton = interface.CButton(self, 'dialog/judge_big/startgame.igs', 0, 0, 63)
        self.m_StartButton.SetPos(CHANGE_BUTTON_X, CHANGE_BUTTON_Y)
        self.m_StartButton.SetShow(True)
        self.m_ShowButton = interface.CButton(self, 'dialog/judge_big/show_card.igs', 0, 0, 64)
        self.m_ShowButton.SetPos(CHANGE_BUTTON_X, CHANGE_BUTTON_Y)
        self.m_ShowButton.SetShow(False)

    
    def SendCard(self, card_data):
        self.m_card_data = card_data
        self.record_pycommand = self.CreatePyCommand(2, self.InitCard)

    
    def UpdatePointAndLevel(self, point, level):
        (x, y) = self.GetPos()
        self.m_Point = interface.CTextObject(self, str(point), interface.FontLT14_3, 0, 0)
        self.m_Point.SetPos(x + 290, y + 22)
        self.ShowLevel(level)

    
    def SetPcChangeCard(self, card_data):
        self.pc_need_change_data = card_data
        self.record_pc_change_type = 0
        self.record_nonce_type = 0
        self.record_down_type = 0
        self.record_down_add_x = 0
        self.record_pc_pycommand = self.CreatePyCommand(1, self.ShowPcChangeCard)

    
    def ShowLevel(self, num):
        self.record_level = []
        data = num / 5
        if num >= 5:
            print 0x1D73681890A4662B2295555555L, 'ShowLevel', num
            (x, y) = self.GetPos()
            self.m_level = interface.CTextObject(self, str(data), interface.FontLT14_3, 0, 0)
            self.m_level.SetPos(SHOW_TOTAL_X, SHOW_TOTAL_Y)
            self.m_level.SetZ(1000)
        
        for i in range(0, num - data * 5):
            self.record_level.append(ui.CImage(self, 'dialog/judge_big/small_star.igs', interface.UIPath))
            self.record_level[len(self.record_level) - 1].SetPos(LEVEL_X + 30 * i, LEVEL_Y)
        

    
    def ShowPcChangeCard(self, obj):
        if self.record_pycommand is None:
            self.record_pc_change_type += 40
            if self.record_pc_change_type > 580 and self.record_down_type == 0:
                self.record_down_add_x = 1000
                self.record_down_type = 1
            
            if len(self.pc_need_change_data) == 0:
                self.record_nonce_type = 0
                return None
            
            if self.record_down_add_x - self.record_pc_change_type < 0 and self.record_down_type == 1:
                self.record_nonce_type = 0
                return None
            
            for i in self.pc_need_change_data:
                if i == 0:
                    self.my_pc_first_card.SetPos((RECORD_PC_FIRST_X - self.record_pc_change_type) + self.record_down_add_x, RECORD_PC_FIRST_Y)
                    continue
                if i == 1:
                    self.my_pc_second_card.SetPos((RECORD_PC_SECOND_X - self.record_pc_change_type) + self.record_down_add_x, RECORD_PC_SECOND_Y)
                    continue
                if i == 2:
                    self.my_pc_third_card.SetPos((RECORD_PC_THIRD_X - self.record_pc_change_type) + self.record_down_add_x, RECORD_PC_THIRD_Y)
                    continue
                if i == 3:
                    self.my_pc_forth_card.SetPos((RECORD_PC_FORTH_X - self.record_pc_change_type) + self.record_down_add_x, RECORD_PC_FORTH_Y)
                    continue
                if i == 4:
                    self.my_pc_fifth_card.SetPos((RECORD_PC_FIRTH_X - self.record_pc_change_type) + self.record_down_add_x, RECORD_PC_FIRTH_Y)
                    continue
            
        
        return ()

    
    def GetCardResult(self, card_data, point, level):
        print 0x2CF00C0D2284F138A1F4L, 'huan', card_data
        self.m_pc_data = card_data
        self.record_pc_card = 1
        self.record_pc_card_type = 0
        self.record_pc_pycommand = self.CreatePyCommand(2, self.ShowCardData)
        self.UpdatePointAndLevel(point, level)
        self.my_first_card.Enable(False)
        self.my_second_card.Enable(False)
        self.my_third_card.Enable(False)
        self.my_forth_card.Enable(False)
        self.my_fifth_card.Enable(False)

    
    def ReSetFirstType(self):
        self.m_StartButton.SetShow(True)
        self.m_ChangeButton.SetShow(False)
        self.m_ShowButton.SetShow(False)

    
    def ShowInvestChip(self, num, num1):
        self.my_invest_chip = []
        (x, y) = self.GetPos()
        self.m_Point = interface.CTextObject(self, str(num1), interface.FontLT14_3, 0, 0)
        self.m_Point.SetPos(x + 290, y + 22)
        print 242, 'ShowInvestChip', num
        for i in range(0, num):
            self.my_invest_chip.append(ui.CImage(self, 'dialog/judge_big/money.igs', interface.UIPath))
            self.my_invest_chip[len(self.my_invest_chip) - 1].SetPos(INVEST_X + 30 * i, INVEST_Y)
        

    
    def ShowCardData(self, obj):
        card_data = self.m_pc_data
        dispath = 30
        if self.record_pc_card == 1:
            if self.record_pc_card_type < 4:
                self.my_pc_first_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_first_card.SetPos(RECORD_PC_FIRST_X, RECORD_PC_FIRST_Y)
                self.record_pc_card_type += 1
            elif self.record_pc_card_type < 8:
                self.my_pc_first_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                self.my_pc_first_card.SetPos(RECORD_PC_FIRST_X, RECORD_PC_FIRST_Y - dispath)
                self.my_pc_first_card.SetFrame(self.record_pc_card_type - 3)
                self.record_pc_card_type += 1
            else:
                self.my_pc_first_card = ui.CImage(self, 'dialog/judge_big/%.2d.igs' % card_data[0], interface.UIPath)
                self.my_pc_first_card.SetPos(RECORD_PC_FIRST_X, RECORD_PC_FIRST_Y)
                self.record_pc_card += 1
                self.record_pc_card_type = 1
        elif self.record_pc_card == 2:
            if self.record_pc_card_type < 4:
                self.my_pc_second_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_second_card.SetPos(RECORD_PC_SECOND_X, RECORD_PC_SECOND_Y)
                self.record_pc_card_type += 1
            elif self.record_pc_card_type < 8:
                self.my_pc_second_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                self.my_pc_second_card.SetPos(RECORD_PC_SECOND_X, RECORD_PC_SECOND_Y - dispath)
                self.my_pc_second_card.SetFrame(self.record_pc_card_type - 3)
                self.record_pc_card_type += 1
            else:
                self.my_pc_second_card = ui.CImage(self, 'dialog/judge_big/%.2d.igs' % card_data[1], interface.UIPath)
                self.my_pc_second_card.SetPos(RECORD_PC_SECOND_X, RECORD_PC_SECOND_Y)
                self.record_pc_card += 1
                self.record_pc_card_type = 1
        elif self.record_pc_card == 3:
            if self.record_pc_card_type < 4:
                self.my_pc_third_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_third_card.SetPos(RECORD_PC_THIRD_X, RECORD_PC_THIRD_Y)
                self.record_pc_card_type += 1
            elif self.record_pc_card_type < 8:
                self.my_pc_third_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                self.my_pc_third_card.SetPos(RECORD_PC_THIRD_X, RECORD_PC_THIRD_Y - dispath)
                self.my_pc_third_card.SetFrame(self.record_pc_card_type - 3)
                self.record_pc_card_type += 1
            else:
                self.my_pc_third_card = ui.CImage(self, 'dialog/judge_big/%.2d.igs' % card_data[2], interface.UIPath)
                self.my_pc_third_card.SetPos(RECORD_PC_THIRD_X, RECORD_PC_THIRD_Y)
                self.record_pc_card += 1
                self.record_pc_card_type = 1
        elif self.record_pc_card == 4:
            if self.record_pc_card_type < 4:
                self.my_pc_forth_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_forth_card.SetPos(RECORD_PC_FORTH_X, RECORD_PC_FORTH_Y)
                self.record_pc_card_type += 1
            elif self.record_pc_card_type < 8:
                self.my_pc_forth_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                self.my_pc_forth_card.SetPos(RECORD_PC_FORTH_X, RECORD_PC_FORTH_Y - dispath)
                self.my_pc_forth_card.SetFrame(self.record_pc_card_type - 3)
                self.record_pc_card_type += 1
            else:
                self.my_pc_forth_card = ui.CImage(self, 'dialog/judge_big/%.2d.igs' % card_data[3], interface.UIPath)
                self.my_pc_forth_card.SetPos(RECORD_PC_FORTH_X, RECORD_PC_FORTH_Y)
                self.record_pc_card += 1
                self.record_pc_card_type = 1
        elif self.record_pc_card == 5:
            if self.record_pc_card_type < 4:
                self.my_pc_fifth_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_fifth_card.SetPos(RECORD_PC_FIRTH_X, RECORD_PC_FIRTH_Y)
                self.record_pc_card_type += 1
            elif self.record_pc_card_type < 8:
                self.my_pc_fifth_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                self.my_pc_fifth_card.SetPos(RECORD_PC_FIRTH_X, RECORD_PC_FIRTH_Y - dispath)
                self.my_pc_fifth_card.SetFrame(self.record_pc_card_type - 3)
                self.record_pc_card_type += 1
            else:
                self.record_pc_card += 1
                self.record_pc_card_type = 1
                self.my_pc_fifth_card = ui.CImage(self, 'dialog/judge_big/%.2d.igs' % card_data[4], interface.UIPath)
                self.my_pc_fifth_card.SetPos(RECORD_PC_FIRTH_X, RECORD_PC_FIRTH_Y)
                self.m_ShowButton.SetShow(False)
                self.ReSetFirstType()
                self.record_pc_pycommand.Release()
                self.record_pc_pycommand = None
        
        return ()

    
    def CleanCardData(self):
        change_card = { }
        self.my_pc_first_card = None
        self.my_first_card = None
        self.my_pc_second_card = None
        self.my_second_card = None
        self.my_pc_third_card = None
        self.my_third_card = None
        self.my_pc_forth_card = None
        self.my_forth_card = None
        self.my_pc_fifth_card = None
        self.my_fifth_card = None
        self.record_pc_card = 1
        self.record_pc_card_type = 0

    
    def UpdateChangeCard(self, card_data):
        self.record_player_change_data = card_data
        self.record_pycommand = self.CreatePyCommand(2, self.ShowChangeAction)

    
    def ShowChangeAction(self, obj):
        print 0xC65203EE20E38L, 'ShowChangeAction'
        self.record_nonce_type == 1
        for i in self.record_player_change_data:
            if i[0] == 0:
                if self.record_pc_card_type < 4:
                    self.my_first_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                    self.my_first_card.SetPos(RECORD_FIRST_X, RECORD_FIRST_Y)
                elif self.record_pc_card_type < 8:
                    self.my_first_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                    self.my_first_card.SetPos(RECORD_FIRST_X, RECORD_FIRST_Y - 30)
                    self.my_first_card.SetFrame(self.record_pc_card_type - 3)
                else:
                    self.my_first_card = CMyButton(self, 'dialog/judge_big/%.2d.igs' % i[1], RECORD_FIRST_X, RECORD_FIRST_Y, 50)
            self.record_pc_card_type < 4
            if i[0] == 1:
                if self.record_pc_card_type < 4:
                    self.my_second_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                    self.my_second_card.SetPos(RECORD_SECOND_X, RECORD_SECOND_Y)
                elif self.record_pc_card_type < 8:
                    self.my_second_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                    self.my_second_card.SetPos(RECORD_SECOND_X, RECORD_SECOND_Y - 30)
                    self.my_second_card.SetFrame(self.record_pc_card_type - 3)
                else:
                    self.my_second_card = CMyButton(self, 'dialog/judge_big/%.2d.igs' % i[1], RECORD_SECOND_X, RECORD_SECOND_Y, 51)
            self.record_pc_card_type < 4
            if i[0] == 2:
                if self.record_pc_card_type < 4:
                    self.my_third_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                    self.my_third_card.SetPos(RECORD_THIRD_X, RECORD_THIRD_Y)
                elif self.record_pc_card_type < 8:
                    self.my_third_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                    self.my_third_card.SetPos(RECORD_THIRD_X, RECORD_THIRD_Y - 30)
                    self.my_third_card.SetFrame(self.record_pc_card_type - 3)
                else:
                    self.my_third_card = CMyButton(self, 'dialog/judge_big/%.2d.igs' % i[1], RECORD_THIRD_X, RECORD_THIRD_Y, 52)
            self.record_pc_card_type < 4
            if i[0] == 3:
                if self.record_pc_card_type < 4:
                    self.my_forth_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                    self.my_forth_card.SetPos(RECORD_FORTH_X, RECORD_FORTH_Y)
                elif self.record_pc_card_type < 8:
                    self.my_forth_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                    self.my_forth_card.SetPos(RECORD_FORTH_X, RECORD_FORTH_Y - 30)
                    self.my_forth_card.SetFrame(self.record_pc_card_type - 3)
                else:
                    self.my_forth_card = CMyButton(self, 'dialog/judge_big/%.2d.igs' % i[1], RECORD_FORTH_X, RECORD_FORTH_Y, 53)
            self.record_pc_card_type < 4
            if self.record_pc_card_type < 4:
                self.my_fifth_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_fifth_card.SetPos(RECORD_FIRTH_X, RECORD_FIRTH_Y)
                continue
            if self.record_pc_card_type < 8:
                self.my_fifth_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                self.my_fifth_card.SetPos(RECORD_FIRTH_X, RECORD_FIRTH_Y - 30)
                self.my_fifth_card.SetFrame(self.record_pc_card_type - 3)
                continue
            self.my_fifth_card = CMyButton(self, 'dialog/judge_big/%.2d.igs' % i[1], RECORD_FIRTH_X, RECORD_FIRTH_Y, 54)
        
        self.record_pc_card_type += 1
        if self.record_pc_card_type > 8:
            self.record_pycommand.Release()
            self.record_pycommand = None
            self.my_first_card.Enable(False)
            self.my_second_card.Enable(False)
            self.my_third_card.Enable(False)
            self.my_forth_card.Enable(False)
            self.my_fifth_card.Enable(False)
            return None
        
        return ()

    
    def InitCard(self, obj):
        card_data = self.m_card_data
        self.record_nonce_type = 1
        if self.record_pc_card == 1:
            if self.record_pc_card_type < 4:
                self.my_pc_first_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_first_card.SetPos(RECORD_PC_FIRST_X, (RECORD_PC_FIRST_Y - 40) + 10 * self.record_pc_card_type)
                self.my_first_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_first_card.SetPos(RECORD_FIRST_X, (RECORD_FIRST_Y - 40) + 10 * self.record_pc_card_type)
                self.record_pc_card_type += 1
            elif self.record_pc_card_type < 8:
                self.my_first_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                self.my_first_card.SetPos(RECORD_FIRST_X, RECORD_FIRST_Y - 30)
                self.my_first_card.SetFrame(self.record_pc_card_type - 3)
                self.record_pc_card_type += 1
            else:
                self.my_pc_first_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_first_card.SetPos(RECORD_PC_FIRST_X, RECORD_PC_FIRST_Y)
                self.my_first_card = CMyButton(self, 'dialog/judge_big/%.2d.igs' % card_data[0], RECORD_FIRST_X, RECORD_FIRST_Y, 50)
                self.my_first_card.Enable(True)
                self.record_pc_card += 1
                self.record_pc_card_type = 1
        elif self.record_pc_card == 2:
            if self.record_pc_card_type < 4:
                self.my_pc_second_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_second_card.SetPos(RECORD_PC_SECOND_X, (RECORD_PC_SECOND_Y - 40) + 10 * self.record_pc_card_type)
                self.my_second_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_second_card.SetPos(RECORD_SECOND_X, (RECORD_SECOND_Y - 40) + 10 * self.record_pc_card_type)
                self.record_pc_card_type += 1
            elif self.record_pc_card_type < 8:
                self.my_second_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                self.my_second_card.SetPos(RECORD_SECOND_X, RECORD_SECOND_Y - 30)
                self.my_second_card.SetFrame(self.record_pc_card_type - 3)
                self.record_pc_card_type += 1
            else:
                self.my_pc_second_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_second_card.SetPos(RECORD_PC_SECOND_X, RECORD_PC_SECOND_Y)
                self.my_second_card = CMyButton(self, 'dialog/judge_big/%.2d.igs' % card_data[1], RECORD_SECOND_X, RECORD_SECOND_Y, 51)
                self.my_second_card.Enable(True)
                self.record_pc_card += 1
                self.record_pc_card_type = 1
        elif self.record_pc_card == 3:
            if self.record_pc_card_type < 4:
                self.my_pc_third_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_third_card.SetPos(RECORD_PC_THIRD_X, (RECORD_PC_THIRD_Y - 40) + 10 * self.record_pc_card_type)
                self.my_third_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_third_card.SetPos(RECORD_THIRD_X, (RECORD_THIRD_Y - 40) + 10 * self.record_pc_card_type)
                self.record_pc_card_type += 1
            elif self.record_pc_card_type < 8:
                self.my_third_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                self.my_third_card.SetPos(RECORD_THIRD_X, RECORD_THIRD_Y - 30)
                self.my_third_card.SetFrame(self.record_pc_card_type - 3)
                self.record_pc_card_type += 1
            else:
                self.my_pc_third_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_third_card.SetPos(RECORD_PC_THIRD_X, RECORD_PC_THIRD_Y)
                self.my_third_card = CMyButton(self, 'dialog/judge_big/%.2d.igs' % card_data[2], RECORD_THIRD_X, RECORD_THIRD_Y, 52)
                self.my_third_card.Enable(True)
                self.record_pc_card += 1
                self.record_pc_card_type = 1
        elif self.record_pc_card == 4:
            if self.record_pc_card_type < 4:
                self.my_pc_forth_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_forth_card.SetPos(RECORD_PC_FORTH_X, (RECORD_PC_FORTH_Y - 40) + 10 * self.record_pc_card_type)
                self.my_forth_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_forth_card.SetPos(RECORD_FORTH_X, (RECORD_FORTH_Y - 40) + 10 * self.record_pc_card_type)
                self.record_pc_card_type += 1
            elif self.record_pc_card_type < 8:
                self.my_forth_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                self.my_forth_card.SetPos(RECORD_FORTH_X, RECORD_FORTH_Y - 30)
                self.my_forth_card.SetFrame(self.record_pc_card_type - 3)
                self.record_pc_card_type += 1
            else:
                self.my_pc_forth_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_forth_card.SetPos(RECORD_PC_FORTH_X, RECORD_PC_FORTH_Y)
                self.my_forth_card = CMyButton(self, 'dialog/judge_big/%.2d.igs' % card_data[3], RECORD_FORTH_X, RECORD_FORTH_Y, 53)
                self.my_forth_card.Enable(True)
                self.record_pc_card += 1
                self.record_pc_card_type = 1
        elif self.record_pc_card == 5:
            if self.record_pc_card_type < 4:
                self.my_pc_fifth_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_fifth_card.SetPos(RECORD_PC_FIRTH_X, (RECORD_PC_FIRTH_Y - 40) + 10 * self.record_pc_card_type)
                self.my_fifth_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_fifth_card.SetPos(RECORD_FIRTH_X, (RECORD_FIRTH_Y - 40) + 10 * self.record_pc_card_type)
                self.record_pc_card_type += 1
            elif self.record_pc_card_type < 8:
                self.my_fifth_card = ui.CImage(self, 'dialog/judge_big/push_card.igs', interface.UIPath)
                self.my_fifth_card.SetPos(RECORD_FIRTH_X, RECORD_FIRTH_Y - 30)
                self.my_fifth_card.SetFrame(self.record_pc_card_type - 3)
                self.record_pc_card_type += 1
            else:
                self.my_pc_fifth_card = ui.CImage(self, 'dialog/judge_big/back.igs', interface.UIPath)
                self.my_pc_fifth_card.SetPos(RECORD_PC_FIRTH_X, RECORD_PC_FIRTH_Y)
                self.record_pc_card += 1
                self.record_pc_card_type = 1
                self.record_nonce_type = 0
                self.my_fifth_card = CMyButton(self, 'dialog/judge_big/%.2d.igs' % card_data[4], RECORD_FIRTH_X, RECORD_FIRTH_Y, 54)
                self.my_fifth_card.Enable(True)
                self.m_ShowButton.SetShow(True)
                self.record_pycommand.Release()
                self.record_pycommand = None
        
        return ()

    
    def RightUp(self):
        self.SetShow(False)

    
    def OnMessage(self, msgid):
        global g_ChangeCard
        if msgid == 30:
            print 'msgid', msgid
            C2SAddChip()
        
        if msgid == 63:
            self.CleanCardData()
            C2SSendCard()
            self.m_StartButton.SetShow(False)
        
        if msgid == 64:
            self.m_ShowButton.SetShow(False)
            C2SShowCard()
            self.record_nonce_type = 1
        
        if msgid == 62:
            self.m_ChangeButton.SetShow(False)
            C2SChangeCard(g_ChangeCard)
            g_ChangeCard = { }
        
        if msgid == 50:
            pass
        
        if msgid == 51:
            pass
        
        if msgid == 52:
            pass
        
        if msgid == 53:
            pass
        
        if msgid == 54:
            pass
        



def C2SSendCard():
    net.g_Net.PacketPrepare(77)
    net.g_Net.PacketAddI(1, 1)
    net.g_Net.PacketAddI(1, 1)
    net.g_Net.PacketSend()


def C2SShowCard():
    net.g_Net.PacketPrepare(77)
    net.g_Net.PacketAddI(1, 1)
    net.g_Net.PacketAddI(4, 1)
    net.g_Net.PacketSend()


def C2SChangeCard(data):
    net.g_Net.PacketPrepare(77)
    net.g_Net.PacketAddI(1, 1)
    net.g_Net.PacketAddI(3, 1)
    for i in data:
        net.g_Net.PacketAddI(i - 49, 1)
    
    net.g_Net.PacketSend()


def C2SAddChip():
    net.g_Net.PacketPrepare(77)
    net.g_Net.PacketAddI(1, 1)
    net.g_Net.PacketAddI(2, 1)
    net.g_Net.PacketSend()
