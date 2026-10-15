# pycdc 交叉复核产物 · script.fls entry 2297
# co_filename(原始)='script/dialog/dlgxiuwei.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2297.pyc (Python 2.5)

import interface
import item
import wrapinterface
import combdialog
import combmacro
g_TradeCeterDlg = None

def ModuleReset():
    global g_TradeCeterDlg
    g_TradeCeterDlg = None


class CTradeCenterDialog(combdialog.CCombDialog):
    LOCTXT = [
        'loc_gold',
        'loc_wood',
        'loc_water',
        'loc_fire',
        'loc_soil']
    NAME = [
        '\xaa\xf7',
        '\xa4\xec',
        '\xa4\xf4',
        '\xa4\xf5',
        '\xa4g']
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/xiuwei.dlg')
        interface.Center(self)
        btn_name = [
            '\xad\xd7\xac\xb0']
        self.m_Btns = []
        for i, v in enumerate(btn_name):
            msgid = 11 + i
            data = [
                'combdialog/\xb0\xb4\xc5\xa5/\xb7\xd6\xc0\xe0\xb0\xb4\xc5\xa5.igs',
                v,
                msgid,
                0]
            data.reverse()
            it = combdialog.CTextButton(self, data)
            it.SetPos(21, 38 + i * 24)
            self.m_Btns.append(it)
        
        self.m_SelectedItem = None
        import wrapinterface
        
        class CNumEdit((wrapinterface.CNumberEdit,)):
            
            def AddChar(self, char):
                wrapinterface.CNumberEdit.AddChar(self, char)
                self.OnChange()

            
            def DeleteChar(self):
                wrapinterface.CNumberEdit.DeleteChar(self)
                self.OnChange()

            
            def OnChange(self):
                self.GetParent().OnChange(self)


        
        class CBuyNumEdit((wrapinterface.CNumberEdit,)):
            
            def AddChar(self, char):
                wrapinterface.CNumberEdit.AddChar(self, char)
                self.OnChange()

            
            def DeleteChar(self):
                wrapinterface.CNumberEdit.DeleteChar(self)
                self.OnChange()

            
            def OnChange(self):
                
                try:
                    num = int(self.GetText())
                except:
                    num = 0

                if num > 20:
                    num = 20
                    self.SetText('20')
                    import usermacro
                    usermacro.PROMPT_MSG('\xc1\xca\xb6R\xc1`\xbc\xc6\xa4\xa3\xaf\xe0\xb6W\xb9L20')
                
                parent = self.GetParent()
                parent.m_BuyAmount = num


        self.m_Locs = []
        for loc_name in self.LOCTXT:
            it = combmacro.CEDIT(CNumEdit, loc_name, self, 16777215, interface.FontLT14_3)
            it.SetLimit(4)
            self.m_Locs.append(it)
        
        loc_len = len(self.m_Locs)
        for idx, it in enumerate(self.m_Locs):
            it.SetNextEdit(self.m_Locs[(idx + 1) % loc_len])
        
        import dlgmap
        dlgmap.DisableMinimap(True)
        self.m_BuyAmountTxt = it = combmacro.CEDIT(CBuyNumEdit, 'loc_num', self, 16777215, interface.FontLT14_3)
        self.m_XiuWei = None
        self.m_XiuWeiVal = None

    
    def OnChange(self, active):
        count = 0
        max_t = 20
        for idx, it in enumerate(self.m_Locs):
            if it != active:
                txt = it.GetText()
                
                try:
                    num = int(txt)
                except:
                    num = 0

                count += num
                continue
        
        txt = active.GetText()
        
        try:
            num = int(txt)
        except:
            num = 0

        if count + num > max_t:
            num = max_t - count
            active.SetText(str(num))
            import usermacro
            usermacro.PROMPT_MSG('\xa8C\xa6\xb8\xa7I\xb4\xab\xaa\xba\xad\xd7\xac\xb0\xc1`\xbc\xc6\xa4\xa3\xaf\xe0\xb6W\xb9L%d' % max_t)
        
        total = 0
        for idx, it in enumerate(self.m_Locs):
            txt = None == it()
            
            try:
                num = int(txt)
                price = self.m_BuyList[idx][3]
            except:
                num = 0
                price = 0

            total += num * price
        
        self.m_ChaosTxt = combmacro.CTEXT(interface.CTextObject, 'loc_chaos', self, str(total), interface.FontLT14_3, 16777215)

    
    def UpdateXiuWei(self, data):
        self.m_XiuWei = []
        self.m_XiuWeiVal = []
        ctrls = [
            'txt_gold',
            'txt_wood',
            'txt_water',
            'txt_fire',
            'txt_soil',
            'txt_chaos']
        for i, name in enumerate(ctrls):
            it = combmacro.CTEXT(interface.CTextObject, name, self, str(data[i]), interface.FontLT14_3, 16777215)
            self.m_XiuWei.append(it)
            self.m_XiuWeiVal.append(data[i])
        

    
    def SetBuyList(self, buylist):
        self.m_BuyList = buylist
        gl = self.GetObject('tab_list')
        gl.Clear()
        for id, amount, sale, price, last in buylist:
            name = self.NAME[id - 1]
            it = gl.AddTextItem((name, str(sale), str(price), str(amount)), hot = 0)
            it.m_ID = id
            self._addpricediff(it, price - last)
        
        gl.ResetScrollBar()
        gl.ResetItems(0)

    
    def UpdateGoods(self, id, amount, sale, price, last):
        import itemdata
        gl = self.GetObject('tab_list')
        for idx, it in enumerate(self.m_BuyList):
            if it[0] == id:
                name = self.NAME[id - 1]
                self.m_BuyList[idx] = (id, amount, sale, price, last)
                gl.SetItemText(gl.m_Items[idx], (name, str(sale), str(price), str(amount)))
                self._addpricediff(gl.m_Items[idx], price - last)
                break
                continue
        
        gl.ResetItems()
        if self.20 is not None:
            gl.m_Items[self.20].Select(True)
        

    
    def _addpricediff(self, it, pd):
        s = '--'
        color = 0
        if pd < 0:
            s = '%d' % pd
            color = 49152
        elif pd > 0:
            s = '+%d' % pd
            color = 12582912
        
        combmacro.SetTableItemText(it, 4, s, color)

    
    def DrawTotalPrice(self, idx):
        if idx is not None:
            total = self.m_BuyList[idx][2] * self.m_BuyAmount
        else:
            total = 0
        color = 0
        own = 0
        if self.m_XiuWeiVal is not None:
            own = self.m_XiuWeiVal[5]
        
        if own < total:
            color = interface.COLOR_30
        
        self.m_BuyTotalPrice = combmacro.CTEXT(interface.CTextObject, 'loc_total', self, str(total), interface.FontLT14_3, color)

    
    def OnBuy(self, idx, inc = 1):
        if idx is None:
            self.m_BuyTarget = None
            self.m_BuyAmount = 0
        elif self.m_BuyTarget != idx:
            self.m_BuyTarget = idx
            self.m_BuyAmount = inc
        else:
            self.m_BuyAmount += inc
        self.m_BuyAmountTxt.SetText(str(self.m_BuyAmount))
        self.DrawTotalPrice(idx)

    
    def DoBuy(self):
        if self.m_BuyTarget is None:
            return None
        
        import netnpc
        netnpc.C2SNpcTCXiuWeiBuy(self.m_BuyTarget + 1, self.m_BuyAmount)

    
    def DoSell(self):
        data = []
        for it in self.m_Locs:
            txt = it.GetText()
            
            try:
                num = int(txt)
            except:
                num = 0

            data.append(num)
        
        import netnpc
        netnpc.C2SNpcTCXiuWeiSale(data)

    
    def OnActive(self, idx):
        for b in self.m_Btns:
            b.Enable(True)
        
        self.m_Btns[idx].Enable(False)
        self.m_CurrentDir = idx
        self.OnBuy(None)

    
    def CloseWindow(self):
        global g_TradeCeterDlg
        import netnpc
        import dlgmap
        netnpc.C2SNpcTCClose()
        dlgmap.DisableMinimap(False)
        g_TradeCeterDlg = None

    
    def OnMessage(self, msgid):
        print 'msgid', msgid
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 9:
            self.DoSell()
        elif msgid == 10:
            self.DoBuy()
        elif msgid <= msgid:
            pass
        elif msgid < len(self.m_Btns):
            pass
        elif msgid < msgid:
            pass
        elif msgid < 200:
            pos = msgid - 101
            self.m_SelectedItem = pos
            self.OnBuy(pos)
        



def Show(idir, buylist):
    global g_TradeCeterDlg
    
    try:
        g_TradeCeterDlg.SetShow(True)
    except:
        g_TradeCeterDlg = CTradeCenterDialog()

    g_TradeCeterDlg.OnActive(idir)
    g_TradeCeterDlg.SetBuyList(buylist)


def UpdateGoods(id, amount, sale, price, last):
    
    try:
        g_TradeCeterDlg.UpdateGoods(id, amount, sale, price, last)
    except:
        pass



def UpdateXiuWei(data):
    
    try:
        g_TradeCeterDlg.UpdateXiuWei(data)
    except:
        pass
