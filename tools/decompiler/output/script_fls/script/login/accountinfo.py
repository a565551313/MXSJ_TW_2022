# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\accountinfo.py
import C_object, interface, wrapinterface, combdialog, combmacro
g_Page = 0

class _Bar(C_object.CBoxObject):

    def __init__(self, parent, w, h, txt):
        C_object.CBoxObject.__init__(self, parent, w, h, 4235414, 256)
        self.m_Txt = C_object.CTextObject(self, txt, interface.FontLT14E_1, 0)
        (tw, th) = self.m_Txt.GetSize()
        self.m_Txt.SetPos((w - tw + 1) / 2, 0)
        return


class _BuyBarContainer(C_object.CImagesObject, interface.CBase):

    def __init__(self, parent, idx, record):
        C_object.CImagesObject.__init__(self, parent, 'login/buy_card_record_bar.igs', interface.UIPath)
        self.MessageProcess()
        self.m_Idx = idx
        self.m_CardInfo = record
        self.m_Select = False
        self.m_Bars = []
        import time
        timestr = '%d-%.2d-%.2d %.2d:%.2d' % time.localtime(record[0])[:5]
        self.AddBar(150, 14, 1, 1, timestr)
        self.AddBar(156, 14, 152, 1, record[1])
        self.AddBar(156, 14, 309, 1, record[2])
        self.AddBar(163, 14, 466, 1, record[3])
        return

    def AddBar(self, w, h, x, y, txt):
        bar = _Bar(self, w, h, txt)
        bar.SetPos(x, y)
        self.m_Bars.append(bar)
        return

    def Enter(self):
        if self.m_Select:
            return
        for bar in self.m_Bars:
            bar.qGVaMNor(11271408)

        return

    def Leave(self):
        if self.m_Select:
            return
        for bar in self.m_Bars:
            bar.qGVaMNor(4235414)

        return

    def LeftUp(self):
        if self.m_Select:
            return
        self.Select(True)
        self.GetParent().Select(self.m_Idx)
        return

    def Select(self, flag):
        self.m_Select = flag
        if flag:
            for bar in self.m_Bars:
                bar.qGVaMNor(16772992)

        else:
            for bar in self.m_Bars:
                bar.qGVaMNor(4235414)

        return


class CBuyCardRecord(combdialog.CCombPanel):

    def __init__(self, parent, records):
        combdialog.CCombPanel.__init__(self, parent, 'login/buy_card_record.dlg')
        import time
        lst_rec = self.GetObject('lst_rec')
        for (i, info) in enumerate(records):
            it = lst_rec.AddTextItem(('%d-%.2d-%.2d %.2d:%.2d' % time.localtime(info[0])[:5]).center(24) + info[1].center(20) + info[2].center(21) + info[3].center(21))
            it.m_CardInfo = info

        lst_rec.ResetItems()
        lst_rec.ResetScrollBar()
        (x, y) = self.GetObject('prev').GetPos()
        self.m_PrevPage = wrapinterface.CLoginSmallButton(self, 'login/btn_small.igs', x, y, '上一頁', 5)
        (x, y) = self.GetObject('next').GetPos()
        self.m_NextPage = wrapinterface.CLoginSmallButton(self, 'login/btn_small.igs', x, y, '下一頁', 6)
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            import sound
            sound.Play('action/button.wav')
            it = combmacro.GetSelectedItemFromList(self.GetObject('lst_rec'))
            if it:
                ShowBuyCardRecord(False)
                import cardcharge
                cardcharge.Show(True)
                cardcharge.SetCodeAndPwd(it.m_CardInfo[2], it.m_CardInfo[3])
        elif msgid == 2:
            ShowBuyCardRecord(False)
            import selectrole, sound
            sound.Play('action/button.wav')
            selectrole.Show(True)
        elif msgid == 5:
            import netlogin, sound
            sound.Play('action/button.wav')
            if netlogin.g_BuyCardRecordPage == None or netlogin.g_BuyCardRecordPage == 1:
                return
            netlogin.C2SGetBuyCardRecord(netlogin.g_BuyCardRecordPage - 1)
        elif msgid == 6:
            import netlogin, sound
            sound.Play('action/button.wav')
            if netlogin.g_BuyCardRecordFlag == 1:
                return
            elif netlogin.g_BuyCardRecordPage == None:
                netlogin.C2SGetBuyCardRecord(1)
            else:
                netlogin.C2SGetBuyCardRecord(netlogin.g_BuyCardRecordPage + 1)
        return


class _ConsumeBarContainer(_BuyBarContainer):
    DESC = {1: '點卡充值', 
       2: '轉會員時間', 3: '點卡轉寄售', 4: '綁定帳號', 
       5: '解綁帳號', 6: '轉換世貢', 7: '購買包月', 
       8: '購買寄售卡', 9: '賣出寄售卡', 10: '領取充值獎勵', 
       11: '轉計費點', 21: '直充點數', 
       23: '直充寄售', 24: '補償點數', 
       25: '補償寄售卡', 26: '清收過期點數', 27: '清收過期寄售卡', 100: '其他'}

    def __init__(self, parent, idx, record):
        C_object.CImagesObject.__init__(self, parent, 'login/account_cons_bar.igs', interface.UIPath)
        self.MessageProcess()
        self.m_Idx = idx
        self.m_Select = False
        self.m_Bars = []
        import time
        timestr = '%d-%.2d-%.2d %.2d:%.2d' % time.localtime(record[0])[:5]
        self.AddBar(127, 14, 0, 1, timestr)
        if self.DESC.has_key(record[1]):
            desc = self.DESC[record[1]]
        else:
            desc = '其他'
        self.AddBar(123, 14, 214, 1, desc)
        self.AddBar(123, 14, 338, 1, str(record[3]))
        txt = str(record[2])
        p = txt.find('-')
        if p >= 0:
            txt = txt[p + 1:]
        self.AddBar(123, 14, 462, 1, txt)
        if record[1] == 7:
            txt = '%d-%.2d-%.2d %.2d:%.2d' % time.localtime(record[4])[:5]
            self.AddBar(127, 14, 586, 1, txt)
        else:
            self.AddBar(127, 14, 586, 1, str(record[4]))
        return


class CAccountConsume(combdialog.CCombPanel):

    def __init__(self, parent, records):
        combdialog.CCombPanel.__init__(self, parent, 'login/account_consume.dlg')
        DESC = {1: '點卡充值', 
           2: '轉會員時間', 3: '點卡轉寄售', 4: '綁定帳號', 
           5: '解綁帳號', 6: '轉換世貢', 7: '購買包月', 
           8: '購買寄售卡', 9: '賣出寄售卡', 10: '領取充值獎勵', 
           11: '轉計費點', 21: '直充點數', 
           23: '直充寄售', 24: '補償點數', 
           25: '補償寄售卡', 26: '清收過期點數', 27: '清收過期寄售卡', 100: '其他'}
        import time
        lst_rec = self.GetObject('lst_rec')
        for (i, info) in enumerate(records):
            if DESC.has_key(info[1]):
                desc = DESC[info[1]]
            else:
                desc = '其他'
            txt = str(info[2])
            p = txt.find('-')
            if p >= 0:
                txt = txt[p + 1:]
            if info[1] == 7:
                left = '%d-%.2d-%.2d %.2d:%.2d' % time.localtime(info[4])[:5]
            else:
                left = str(info[4])
            lst_rec.AddTextItem(('%d-%.2d-%.2d %.2d:%.2d' % time.localtime(info[0])[:5]).center(24) + desc.center(20) + str(info[3]).center(21) + txt.center(21) + left.center(21))

        lst_rec.ResetItems()
        lst_rec.ResetScrollBar()
        (x, y) = self.GetObject('prev').GetPos()
        self.m_PrevPage = wrapinterface.CLoginSmallButton(self, 'login/btn_small.igs', x, y, '上一頁', 5)
        (x, y) = self.GetObject('next').GetPos()
        self.m_NextPage = wrapinterface.CLoginSmallButton(self, 'login/btn_small.igs', x, y, '下一頁', 6)
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            ShowAccountConsume(False)
            import selectrole, sound
            sound.Play('action/button.wav')
            selectrole.Show(True)
        elif msgid == 5:
            import netlogin, sound
            sound.Play('action/button.wav')
            if netlogin.g_ConsumePage == None or netlogin.g_ConsumePage == 1:
                return
            netlogin.C2SGetConsumeRecord(netlogin.g_ConsumePage - 1)
        elif msgid == 6:
            import netlogin, sound
            sound.Play('action/button.wav')
            if netlogin.g_ConsumeFlag == 1:
                return
            elif netlogin.g_ConsumePage == None:
                netlogin.C2SGetConsumeRecord(1)
            else:
                netlogin.C2SGetConsumeRecord(netlogin.g_ConsumePage + 1)
        return


def ShowBuyCardRecord(flag, record=None):
    global g_BuyCardRecord
    if flag:
        g_BuyCardRecord = CBuyCardRecord(interface.DialogPanel, record)
    else:
        g_BuyCardRecord = None
    return


def ShowAccountConsume(flag, record=None):
    global g_AccountConsume
    if flag:
        g_AccountConsume = CAccountConsume(interface.DialogPanel, record)
    else:
        g_AccountConsume = None
    return


return
# global g_Page ## Warning: Unused global
