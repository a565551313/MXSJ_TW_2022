# pycdc 交叉复核产物 · script.fls entry 3108
# co_filename(原始)='script/dialog/dlgexitinfo.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3108.pyc (Python 2.5)

import interface
import combdialog
import combmacro
import wrapinterface
import wraplinkobj
import syncoperate
import ui
import misc
import popupmgr
import popupdefine
import nethero
g_ExitInfo = None
g_OrgTask = (3015, 3017)
g_SelectData = []
g_FestivalID = 9000
g_oExtInfoCB = None

def ModuleReset():
    global g_ExitInfo, g_OrgTask, g_oExtInfoCB
    g_ExitInfo = None
    g_OrgTask = (3015, 3017)
    g_oExtInfoCB = None


def OpenExitInfoDlg():
    SendCloseLog()
    import main
    oDlg = CNewExitDialog(interface.DialogPanel, ('\xa5\xbf\xa6b\xb1q\xaaA\xb0\xc8\xbe\xb9\xc0\xf2\xa8\xfa\xabH\xae\xa7...', '\xa5\xbf\xa6b\xb1q\xaaA\xb0\xc8\xbe\xb9\xc0\xf2\xa8\xfa\xabH\xae\xa7...', '\xa5\xbf\xa6b\xb1q\xaaA\xb0\xc8\xbe\xb9\xc0\xf2\xa8\xfa\xabH\xae\xa7...', '\xa5\xbf\xa6b\xb1q\xaaA\xb0\xc8\xbe\xb9\xc0\xf2\xa8\xfa\xabH\xae\xa7...'))
    interface.Center(oDlg)
    main.g_ExitDialog = oDlg
    nethero.C2SGetDayMessage()


def SendCloseLog():
    import traceback
    import statisticsignal
    tracebackList = traceback.format_stack()
    tracebackList.pop()
    sStack = '\n' + ''.join(tracebackList)
    if 'HideWindow' in sStack:
        statisticsignal.Emit(statisticsignal.SS_CLOSE_GAME_WITH_TYPE, 2)
        LOG_DEBUG('\xb0h\xa5X\xb9C\xc0\xb8', 2)
    elif 'CQuitItem.OnExit' in sStack:
        statisticsignal.Emit(statisticsignal.SS_CLOSE_GAME_WITH_TYPE, 1)
        LOG_DEBUG('\xb0h\xa5X\xb9C\xc0\xb8', 1)
    else:
        statisticsignal.Emit(statisticsignal.SS_CLOSE_GAME_WITH_TYPE, 3)
        LOG_DEBUG('\xb0h\xa5X\xb9C\xc0\xb8', 3)


def SetExtInfoCB(oExtInfoCB):
    global g_oExtInfoCB
    g_oExtInfoCB = oExtInfoCB


def UpdateOfflineDialog(tDaymsg):
    global g_oExtInfoCB
    import main
    if main.g_ExitDialog:
        main.g_ExitDialog.UpdateDayMsg(tDaymsg)
    
    if g_oExtInfoCB and callable(g_oExtInfoCB):
        g_oExtInfoCB(tDaymsg)
        g_oExtInfoCB = None
    


class CTextCheckButton(interface.CButton):
    
    def __init__(self, parent, data, width, filename, x, y, msgid = 0, sShowTxt = None):
        interface.CButton.__init__(self, parent, filename, x, y, msgid)
        color = interface.COLOR_88
        if sShowTxt is None:
            text = data['show']
        else:
            text = sShowTxt
        oTestTextObject = wrapinterface.WrapRichText(parent, 1000, interface.FontLT14_3, text, color)
        (w, _) = oTestTextObject.GetSize()
        if w > width - 40:
            textList = text.split()
            self.m_TipsText = '#r'.join(textList)
            text = str(textList[0])
        else:
            self.m_TipsText = ''
            if interface.STYLE:
                text = interface.Replace(text).replace('#Y', '#cFFA054')
            
        self.m_Text = wrapinterface.WrapRichText(parent, width - 30, interface.FontLT14_3, text, color)
        import style
        (_, offsety) = style.GetIntTuple('dlgexitinfo.CTextCheckButton', 'data_init_offset')
        self.m_Text.SetPos(28, offsety)
        self.m_Selected = False
        self.m_Data = data
        self.SetSelect(data['select'])

    
    def LeftDown(self):
        interface.CClickObject.LeftDown(self)

    
    def LeftUp(self):
        if self.m_Selected:
            self.SetSelect(False)
        else:
            self.SetSelect(True)
            import clickcounter
            clickcounter.Log(self.m_Data['show'].split('#')[0].strip())
        interface.CClickObject.LeftUp(self)

    
    def SetSelect(self, sel):
        if self.m_Selected == sel:
            return None
        
        self.m_Selected = sel
        self.m_Data['select'] = sel
        if sel:
            self.SetFrame(2)
        else:
            self.SetFrame(0)
        self.GetParent().GetParent().GetParent().SelectChange()

    
    def IsSelected(self):
        return self.m_Selected

    
    def CreateTips(self):
        if self.m_TipsText:
            sTips = self.m_TipsText.replace('#B', '#G')
            self.m_Tips = wrapinterface.CTextTips(None, -1, sTips, interface.FontLT14_3, direct = 3, owner = self.GetParent())
        

    
    def DeleteTips(self):
        self.m_Tips = None

    
    def Enter(self):
        pass

    
    def Leave(self):
        pass



class CExitInfoDialog(combdialog.CCombDialog, wraplinkobj.CLinkCursor):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/exitinfofilter.dlg')
        wraplinkobj.CLinkCursor.__init__(self)
        interface.Center(self)
        self.m_Data = []
        self.m_Filter = {
            'all': 1,
            'day': 0,
            'week': 0,
            'daily': 0 }
        self.GetObject('select_all').SetSelect(True)
        desc = '\xb3Q\xa4\xc4\xbf\xef\xaa\xba\xabH\xae\xa7\xb1\xf8\xa5\xd8\xb1N\xb7|\xc5\xe3\xa5\xdc\xa6b\xb0h\xa5X\xabH\xae\xa7\xac\xc9\xad\xb1\xaa\xba\xa4\xb5\xa4\xe9\xabH\xae\xa7\xa4\xa4'
        color = interface.COLOR_58
        self.m_LocDesc = combmacro.CRICHTEXT(interface.CRichTextObject, 'loc_desc', self, desc, interface.FontLT14_3, color)

    
    def Refresh(self, data = None):
        self.m_DescTxt = None
        if data is None:
            data = self.m_Data
        else:
            self.m_Data = data
        for i, key in enumerate(self.m_Filter):
            self.m_Filter[key] = self.GetObject('select_%s' % key).IsSelected()
        
        tab_list = self.GetObject('tab_list')
        w = tab_list.m_ItemWidth
        tab_list.Clear()
        import style
        for i, v in enumerate(data):
            if not self.m_Filter['all']:
                if not v['type'] == 1 or self.m_Filter['day']:
                    if (v['type'] == 2 or self.m_Filter['week'] or self.m_Filter['daily']) and v['select']:
                        it = tab_list.AddTextItem('')
                        it.m_ID = v['idx']
                        it.m_Type = v['type']
                        (x, y) = style.GetIntTuple(self.GetDlgPath(), 'data_item_pos')
                        path = style.GetStr(self.GetDlgPath(), 'data_btn_path')
                        if '#r' in v['show']:
                            (sShowTxt, sExtLine) = v['show'].split('#r')
                        else:
                            sShowTxt = None
                            sExtLine = None
                        it.m_Text = CTextCheckButton(it, v, w, path, x, y, sShowTxt = sShowTxt)
                        self.DealExtLine(tab_list, it, sExtLine)
                        continue
        
        tab_list.ResetScrollBar()
        tab_list.ResetItems()

    
    def DealExtLine(self, oListObj, oItemObj, sExt):
        if not sExt:
            return None
        
        oText = oListObj.AddRichTextItem(interface.Replace(sExt), interface.COLOR_88, interface.ALIGN_LEFT_MIDDLE, 112)
        oText.m_Text = None
        oText.m_ID = oItemObj.m_ID
        oText.m_Type = oItemObj.m_Type

    
    def ListSelect(self, item):
        iId = item.m_ID
        import exitinfodata
        import permission
        if iId in exitinfodata.DATA:
            txt = exitinfodata.DATA[iId]['desc']
            if iId in (20, 21):
                if permission.IsOpenNewFuBenAmount():
                    if iId == 20:
                        txt = '\xb0\xc6\xa5\xbb\xa6\xb8\xbc\xc6#r#r\xac\xdb\xc3\xf6NPC\xa1G#r#s(18,\xac\xef\xa6\xe6\xaa\xcc,1,\xa9\xfa\xa4\xeb\xab\xb0,200,164,0)#r#r\xc2\xb2\xa4\xb6\xa1G#r\xa1i\xa8C\xa4\xd1\xa5i\xb6i\xa4J\xb0\xc6\xa5\xbb\xaa\xba\xa6\xb8\xbc\xc6\xa1j#r2+\xa1]\xaaA\xb0\xc8\xbe\xb9\xb5\xa5\xaf\xc5/10\xa1^/1.5\xa1]#Y\xb5\xf9\xa1G\xa8C\xa6\xb8\xadp\xba\xe2\xb5\xb2\xaaG\xa6\xb3\xa4p\xbc\xc6\xc2I\xaa\xba\xabh\xac\xd9\xa5h\xa4p\xbc\xc6\xc2I#n\xa1^\xa1A\xb3\xcc\xa6h\xa4\xa3\xb6W\xb9L7\xa6\xb8'
                    else:
                        txt = '\xb0\xc6\xa5\xbb\xa6\xb8\xbc\xc6#r#r\xac\xdb\xc3\xf6NPC\xa1G#r#s(18,\xac\xef\xa6\xe6\xaa\xcc,1,\xa9\xfa\xa4\xeb\xab\xb0,200,164,0)#r#r\xc2\xb2\xa4\xb6\xa1G#r\xa1i\xa8C\xb6g\xa5i\xb6l\xa1O\xb5\xc3\xa0\xbe\xaf\xbf\xa3\xbd\xb9\xc3\xa4o&w42.\xa4X\xafD\xb5\xcd\xbb\xbc\xb0\xa0\xaa\xc0*45\xa4[/0.6\xa1]#Y\xb5\xf9\xa1G\xa8C\xa6\xb8\xadp\xba\xe2\xb5\xb2\xaaG\xa6\xb3\xa4p\xbc\xc6\xc2I\xaa\xba\xabh\xac\xd9\xa5h\xa4p\xbc\xc6\xc2I#n\xa1^\xa1A\xb3\xcc\xa6h\xa4\xa3\xb6W\xb9L30\xa6\xb8'
                
            
            if interface.IsNewStyle():
                txt = txt.replace('#Y', '#cED8200').replace('#G', '#c12A42E').replace('#c00FFFF', '#c0A83F5')
            elif interface.STYLE:
                txt = txt.replace('#Y', '#cF8FC90').replace('#G', '#c1BFF1B')
            
            parent = self.GetObject('frm_Box')
            (w, h) = parent.GetSize()
            self.m_DescTxt = wrapinterface.WrapRichText(self, w - 10, interface.FontLT14_3, txt, interface.COLOR_78)
            (x, y) = parent.GetPos()
            self.m_DescTxt.SetPos(x + 5, y + 5)
        

    
    def LeftUp(self):
        combdialog.CCombDialog.LeftUp(self)
        if getattr(self, 'm_DescTxt', None):
            import cursor
            import wrapui
            (x, y) = cursor.GetPos()
            rt = self.m_DescTxt
            (rx, ry) = rt.GetScreenPos()
            iId = int(rt.ClickID(x - rx, y - ry))
            if rt.m_LinkObj.get(iId):
                obj = rt.m_LinkObj[iId]
                obj.m_MaxClientNum = wrapui.g_MaxClientNum
                obj.OnLeftUp(rx, ry)
            
        

    
    def Enter(self):
        wraplinkobj.CLinkCursor.Enter(self)
        combdialog.CCombDialog.Enter(self)

    
    def Leave(self):
        wraplinkobj.CLinkCursor.Leave(self)
        combdialog.CCombDialog.Leave(self)

    
    def GetLinkObjAttr(self):
        linkDict = None
        if getattr(self, 'm_DescTxt', None):
            linkDict = self.m_DescTxt.m_LinkObj
        
        return (getattr(self, 'm_DescTxt', None), linkDict)

    
    def OnEnterLinkCallBack(self, clickid = 0):
        rt = self.m_DescTxt
        import wrapui
        import wrapinterface
        if rt.m_LinkObj.get(clickid) and isinstance(rt.m_LinkObj[clickid], wrapui.CAutoGotoBase):
            self.m_TaskTips = wrapinterface.CTextTips(None, -1, '\xc2I\xc0\xbb\xa6W\xa6r\xa5i\xa6\xdb\xb0\xca\xb4M\xb8\xf4', interface.FontLT14_3)
        

    
    def OnLeaveLinkCallBack(self):
        self.m_TaskTips = None

    
    def SelectChange(self):
        count = 0
        for i, v in enumerate(self.m_Data):
            if v['select']:
                count += 1
                continue
        
        if count <= 18:
            color = interface.COLOR_154
        else:
            color = interface.COLOR_30
        self.m_SelectCountTxt = combmacro.CTEXT(interface.CTextObject, 'loc_num', self, '%d/18' % count, interface.FontLT14_3, color)

    
    def OnItemEnter(self, it):
        oText = it.m_Text
        if oText:
            oText.CreateTips()
        

    
    def OnItemLeave(self, it):
        oText = it.m_Text
        if oText:
            oText.DeleteTips()
        

    
    def CloseWindow(self):
        global g_ExitInfo
        g_ExitInfo = None

    
    def OnMessage(self, msgid):
        if msgid in (3, 4):
            self.CloseWindow()
        elif msgid == 2:
            flag1 = 0
            flag2 = 0
            count = 0
            for i, v in enumerate(self.m_Data):
                if v['select']:
                    idx = v['idx']
                    if idx < 31:
                        flag1 |= 1 << idx
                    else:
                        flag2 |= 1 << idx - 31
                    count += 1
                    continue
            
            if count > 18:
                import usermacro
                usermacro.PROMPT_MSG('\xa4\xb5\xa4\xe9\xabH\xae\xa7\xa4\xa4\xa5u\xaf\xe0\xb3]\xb8m\xc5\xe3\xa5\xdc18\xba\xd8\xabH\xae\xa7\xb1\xf8\xa5\xd8')
                return None
            
            import nethero
            nethero.C2SSaveSet(flag1, flag2)
            import main
            main.ExitGame()
            nethero.C2SGetDayMessage()
            self.CloseWindow()
        elif msgid == 6:
            self.m_Filter['all'] = self.m_Filter['all'] + 1 & 1
            self.GetObject('select_all').SetSelect(True)
            self.Refresh()
        elif msgid == 7:
            self.m_Filter['day'] = self.m_Filter['day'] + 1 & 1
            self.GetObject('select_day').SetSelect(True)
            self.Refresh()
        elif msgid == 8:
            self.m_Filter['week'] = self.m_Filter['week'] + 1 & 1
            self.GetObject('select_week').SetSelect(True)
            self.Refresh()
        elif msgid == 9:
            self.m_Filter['daily'] = self.m_Filter['daily'] + 1 & 1
            self.GetObject('select_daily').SetSelect(True)
            self.Refresh()
        elif msgid < msgid:
            pass
        elif msgid < interface.RIGHT_BUTTON_MESSAGE:
            idx = msgid - 101
            tab_list = self.GetObject('tab_list')
            if idx < len(tab_list.m_Items):
                self.ListSelect(tab_list.m_Items[idx])
            
        



class CRichTxtList(interface.CList):
    
    class CMyRichText(wrapinterface.WrapRichText):
        
        def __init__(self, parent, w, fontid, txt, normalcolor = None):
            wrapinterface.WrapRichText.__init__(self, parent, w, fontid, txt, normalcolor)
            (bw, bh) = self.GetSize()
            self.m_NotiBox = interface.CNotifyBox(self, bw, bh, 0, 0, 1)
            self.m_Link = None

        
        def OnEnter(self, msgid):
            if self.m_LinkObj:
                self.m_Link = self.m_LinkObj[0]
                self.m_Link.OnEnter()
            

        
        def OnLeave(self, msgid):
            if self.m_Link:
                self.m_Link.OnLeave()
            

        
        def GetPar(self):
            
            try:
                par = self.GetParent()
            except SystemError:
                par = None

            return par

        
        def LeftDown(self):
            pass

        
        def LeftUp(self):
            par = self.GetPar()
            if par:
                par.LeftUp()
            

        
        def RightUp(self):
            par = self.GetPar()
            if par:
                par.RightUp()
            

        
        def OnMouseWheelDown(self, p):
            par = self.GetPar()
            if par:
                par.MouseWheelDown(p)
            

        
        def OnMouseWheelUp(self, p):
            par = self.GetPar()
            if par:
                par.MouseWheelUp(p)
            


    
    def __init__(self, parent, x, y, w, h, color, alpha, hspace = 0):
        interface.CList.__init__(self, parent, x, y, w, h, color, alpha, hspace)

    
    def AddTextItem(self, txt, fontid, w, color):
        item = self.CMyRichText(self, w, fontid, txt, color)
        self.AddItem(item)
        return item

    
    def LeftUp(self):
        if self.GetParent().GetParent():
            self.GetParent().GetParent().LeftUp()
        

    
    def RightUp(self):
        if self.GetParent().GetParent():
            self.GetParent().GetParent().RightUp()
        



class CMyBox(interface.CClickBox):
    
    class CMyRichText(wrapinterface.WrapRichText):
        
        def __init__(self, parent, w, fontid, txt, normalcolor = None):
            wrapinterface.WrapRichText.__init__(self, parent, w, fontid, txt, normalcolor)
            (bw, bh) = self.GetSize()
            self.m_NotiBox = interface.CNotifyBox(self, bw, bh, 0, 0, 1)
            self.m_Link = None

        
        def OnEnter(self, msgid):
            if self.m_LinkObj:
                self.m_Link = self.m_LinkObj[0]
                self.m_Link.OnEnter()
            

        
        def OnLeave(self, msgid):
            if self.m_Link:
                self.m_Link.OnLeave()
            

        
        def GetPar(self):
            
            try:
                par = self.GetParent()
            except SystemError:
                par = None

            return par

        
        def LeftUp(self):
            if self.m_LinkObj:
                self.m_LinkObj[0].OnLeftUp()
            

        
        def LeftDown(self):
            pass

        
        def RightUp(self):
            pass

        
        def OnMouseWheelDown(self, p):
            self.GetParent().MouseWheelDown(p)

        
        def OnMouseWheelUp(self, p):
            self.GetParent().MouseWheelUp(p)


    
    def __init__(self, parent, leftText, rightText, fontid, w, color, isCenter = False):
        interface.CClickBox.__init__(self, parent, w, 30, alpha = 0)
        self.m_width = w
        if leftText:
            self.m_LeftRichText = self.CMyRichText(self, w, fontid, leftText, color)
            interface.CenterLeft(self.m_LeftRichText, 4)
        
        if rightText:
            self.m_RightRichText = self.CMyRichText(self, w, fontid, rightText, color)
            interface.CenterRight(self.m_RightRichText)
        
        if isCenter:
            self.m_LeftRichText = interface.CTextObject(self, leftText, fontid, color)
            interface.Center(self.m_LeftRichText)
        

    
    def MouseWheelDown(self, p):
        oPar = self.GetParent()
        if hasattr(oPar, 'MouseWheelDown'):
            oPar.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        oPar = self.GetParent()
        if hasattr(oPar, 'MouseWheelUp'):
            oPar.MouseWheelUp(p)
        

    
    def GetSize(self):
        return (self.m_width - 15, 30)



class CToDayBox(CMyBox):
    
    def __init__(self, parent, data, fontid, w, color):
        CMyBox.__init__(self, parent, data['left'], data['right'], fontid, w, color)
        lst = data['icon']
        self.m_oIconList = []
        bakIcon = None
        (_, boxH) = self.GetSize()
        for idx, path in enumerate(lst):
            if path is None:
                continue
            
            oIcon = CIcon(self, path)
            if bakIcon is None:
                iconW = 0
            else:
                (iconW, _) = bakIcon.GetSize()
            (_, iconH) = oIcon.GetSize()
            x = 100 + idx * iconW
            y = (boxH - iconH >> 1) - 2
            oIcon.SetPos(x, y)
            bakIcon = oIcon
            self.m_oIconList.append(oIcon)
        



class CTomorrowBox(CMyBox):
    
    def __init__(self, parent, data, fontid, w, color):
        CMyBox.__init__(self, parent, data['left'], data['right'], fontid, w, color)



class CIcon(interface.CBase, ui.CImage):
    
    def __init__(self, parent, path, sDir = interface.UIPath):
        pathLst = path.split('|')
        if len(pathLst) < 2:
            sPath = path
            self.m_iIconType = 0
        else:
            sPath = pathLst[1]
            self.m_iIconType = int(pathLst[0])
        ui.CImage.__init__(self, parent, sPath, sDir)
        self.MessageProcess()
        self.m_Tips = None

    
    def Enter(self):
        import calendardata
        if self.m_iIconType == 0:
            return None
        
        tip_str = calendardata.GetRewardTipsByType(self.m_iIconType)
        if tip_str:
            self.m_Tips = wrapinterface.CTextTips(self.GetParent().GetParent(), -1, tip_str, interface.FontLT14_3, direct = 1)
            self.m_Tips.Topmost()
            print 'Tip Z-Order: %d   Icon Z-Order: %d' % (self.m_Tips.GetZ(), self.GetZ())
        

    
    def Leave(self):
        self.m_Tips = None



class CNewExitDialog(combdialog.CCombDialog):
    FLAG2COLOR = {
        1: '#B',
        2: '#cAFAFAF' }
    
    def __init__(self, parent, ext):
        combdialog.CCombDialog.__init__(self, parent, 'dialog/schedule_new/offline1.dlg')
        self.m_dTodayList = []
        self.m_dTomorrowList = []
        self.UpdateDayMsg(ext)
        self.m_Switch = 0
        self.WriteClickLog()

    
    def WriteClickLog(self):
        import clickcounter
        clickcounter.TaskLog('\xb7s\xa4\xe2-\xa5\xb4\xb6}\xb0h\xa5X\xac\xc9\xad\xb1')

    
    def GetColorText(self, stime, name, idx):
        text = '%s %s#r' % (stime, name)
        if idx == 2:
            flag = CalcFlag(self.m_NowTime, stime)
            if flag:
                text = '%s%s#n' % (self.FLAG2COLOR[flag], text)
            
        
        return text

    
    def DealExt(self, ext):
        if type(ext[0]) == str:
            return ext
        
        import calendardata
        import servercalendardata
        import limitserver
        import permission
        import misc
        import time
        tempTime = time.localtime(misc.GetServerCurrentTime())
        self.m_NowTime = '%.2d:%.2d' % (tempTime[3], tempTime[4])
        lNewExt = []
        for i in range(3):
            sText = ''
            if i == 0:
                for tmpData in ext[i]:
                    iHuodongID = tmpData[0]
                    sExt = tmpData[1]
                    dDailyData = calendardata.GetDailyData(iHuodongID)
                    if iHuodongID != g_FestivalID:
                        sLinkText = dDailyData['link']
                        if iHuodongID in g_OrgTask:
                            sExtData = sExt.split('|')
                            sLinkText = sLinkText.replace('\xab\xdd\xa9w', sExtData[1])
                            sExt = sExtData[0]
                        
                    else:
                        sLinkText = dDailyData['link'].replace('\xb8`\xa4\xe9', '%s\xc2\xa7\xaa\xab' % tmpData[2])
                        sExt = '#R\xa5\xbc\xbb\xe2\xa8\xfa#n'
                    sText += '%s %s#r' % (sLinkText, sExt)
                
            elif i in (1, 3):
                self.m_dTodayList = ext[1]
                self.m_dTomorrowList = ext[3]
                self.SetTodayInfo()
            else:
                templist = []
                for tmpData in ext[i]:
                    iHuodongID = tmpData[0]
                    sExt = tmpData[1]
                    if permission.CalendarTest():
                        (iHdTime, sName) = servercalendardata.GetData(iHuodongID)
                    else:
                        (iHdTime, sName) = calendardata.GetData(iHuodongID)
                    if iHuodongID == g_FestivalID:
                        sName = sName.replace('\xb8`\xa4\xe9', tmpData[2])
                    
                    templist.append((iHdTime, sName))
                
                templist.sort(key = (lambda x: x[0]))
                for data in templist:
                    sText += self.GetColorText(data[0], data[1], i)
                
            lNewExt.append(sText)
        
        return lNewExt

    
    def UpdateDayMsg(self, ext):
        ext = self.DealExt(ext)
        self.m_txtInfo = []
        for i in range(0, 4):
            if i in (1, 3):
                continue
            
            text = ext[i]
            richLst = self.GetObject('lst_%s' % i)
            richLst.Clear()
            (w, h) = richLst.GetSize()
            if interface.IsOldStyle():
                w -= 10
            
            text = interface.ReplaceRed(text)
            text = interface.Replace(text)
            if interface.IsStyle1():
                text = text.replace('#cAFAFAF', '#c6E6E6E')
            
            if interface.IsStyle3():
                text = text.replace('#cAFAFAF', '#c787878')
                text = text.replace('#Y', '#cED8200')
            
            if interface.IsStyle4():
                text = text.replace('#cAFAFAF', '#c787878')
                text = text.replace('#Y', '#cED8200')
                text = text.replace('#c5DB0FE', '#c286ad6')
            
            txtLst = text.split('#r')
            for txt in txtLst:
                if txt:
                    if len(txt.split(' ')) == 2:
                        leftText = txt.split(' ')[0]
                        rightText = txt.split(' ')[1]
                    else:
                        leftText = txt
                        rightText = ' '
                    box = CMyBox(richLst, leftText, rightText, interface.FontLT14_3, w, interface.COLOR_4)
                    richLst.AddItem(box)
                    if i == 0 and leftText == '\xa5\xad\xa7\xa1\xa8C\xa4p\xae\xc9':
                        self.ShowFullTips(richLst, w)
                    
                leftText == '\xa5\xad\xa7\xa1\xa8C\xa4p\xae\xc9'
            
            richLst.ResetItems()
            richLst.ResetScrollBar()
        

    
    def UpdateTodayActivity(self, text):
        import re
        text = interface.ReplaceRed(text)
        text = interface.Replace(text)
        if interface.IsStyle1():
            text = text.replace('#cAFAFAF', '#c6E6E6E')
        
        if interface.IsStyle3():
            text = text.replace('#cAFAFAF', '#c787878')
            text = text.replace('#Y', '#cED8200')
        
        if interface.IsStyle4():
            text = text.replace('#cAFAFAF', '#c787878')
            text = text.replace('#Y', '#cED8200')
            text = text.replace('#c5DB0FE', '#c286ad6')
        
        txtLst = text.split('#r')
        tableObj = self.GetObject('loc_info3')
        tableObj.Clear()
        for txt in txtLst:
            if txt:
                if len(txt.split(' ')) == 2:
                    oItemList = []
                    oBox = tableObj.AddBoxItem()
                    (sTime, sActivityName) = txt.split(' ')
                    iTextColor = None
                    if sTime.find('#c') >= 0:
                        iTextColorList = re.findall('#c\\w\\w\\w\\w\\w\\w', sTime)
                        iTextColor = None if iTextColorList else None
                    
                    if iTextColor:
                        sActivityName = '%s%s' % (iTextColor, sActivityName)
                    
                    (w, h) = oBox.GetSize()
                    iColor = tableObj.GetNormalTextColor()
                    oTimeObj = ui.CRichTextObject(oBox, w, h, sTime, interface.FontLT14_3, iColor)
                    oActivityName = wrapinterface.WrapRichTextWithLinkCursor(oBox, w, interface.FontLT14_3, sActivityName, iColor)
                    oItemList.append(oTimeObj)
                    oItemList.append(oActivityName)
                    tableObj.AddItemExtend(oBox, oItemList, bChangeColor = False)
                
            len(txt.split(' ')) == 2
        
        tableObj.ResetItems()
        tableObj.ResetScrollBar()

    
    def SetTodayInfo(self):
        import calendardata
        lTodayInfo = calendardata.GetAllCanShowDailyData()
        for tmpData in self.m_dTodayList:
            iId = tmpData[0]
            bRepeat = False
            for val in lTodayInfo:
                if val['Id'] == iId:
                    bRepeat = True
                    break
                    continue
            
            if bRepeat:
                continue
            
            dData = calendardata.GetDailyData(iId)
            lTodayInfo.append(dData)
        
        lTodayInfo = self.SortData(lTodayInfo)
        if not lTodayInfo or len(lTodayInfo) <= 0:
            return None
        
        totayLst = []
        for val in lTodayInfo:
            tmp = { }
            (sLeft, sRight) = self.GetLinkText(val['Id'])
            tmp['left'] = sLeft
            tmp['right'] = sRight
            lst = []
            lst.append(val['icon1'])
            lst.append(val['icon2'])
            tmp['icon'] = lst
            totayLst.append(tmp)
        
        self.SetTodayInfoView(totayLst)

    
    def GetTaskDataById(self, iFindid):
        if len(self.m_dTodayList) <= 0:
            return None
        
        for tmpData in self.m_dTodayList:
            iId = tmpData[0]
            if iFindid == iId:
                return tmpData
                continue
        

    
    def SetTodayInfoView(self, lst):
        richLst = self.GetObject('lst_1')
        richLst.Clear()
        (w, h) = richLst.GetSize()
        style = interface.GetStyle()
        if style not in (3, 4):
            w = w - 8
        
        for val in lst:
            box = CToDayBox(richLst, val, interface.FontLT14_3, w, interface.COLOR_4)
            richLst.AddItem(box)
        
        richLst.ResetItems()
        richLst.ResetScrollBar()
        self.SetTomorrowInfo()

    
    def SetTomorrowInfo(self):
        if len(self.m_dTomorrowList) <= 0:
            return None
        
        import advancenoticedata
        tomorrowList = []
        for tmpData in self.m_dTomorrowList:
            iId = tmpData[0]
            data = advancenoticedata.GetName(iId)
            tmp = { }
            tmp['left'] = data['name']
            tmp['right'] = data['desc']
            tomorrowList.append(tmp)
        
        richLst = self.GetObject('lst_1')
        (w, h) = richLst.GetSize()
        style = interface.GetStyle()
        if style not in (3, 4):
            w = w - 8
        
        noBox = CMyBox(richLst, '', '', interface.FontLT14_6, w, interface.COLOR_4)
        richLst.AddItem(noBox)
        font = self.GetObject('text_todayTitle').GetFont()
        color = self.GetObject('text_todayTitle').GetColor()
        tmpBox = CMyBox(richLst, '\xa9\xfa\xa4\xe9\xb9w\xa7i', '', font, w, color, True)
        richLst.AddItem(tmpBox)
        for val in tomorrowList:
            box = CTomorrowBox(richLst, val, interface.FontLT14_3, w, interface.COLOR_4)
            richLst.AddItem(box)
        
        richLst.ResetItems()
        richLst.ResetScrollBar()

    
    def GetLinkText(self, iID):
        import calendardata
        import hero
        iMyGrade = hero.GetProp('m_Grade')
        dDailyData = calendardata.GetDailyData(iID)
        if iID == g_FestivalID:
            tData = self.GetTaskDataById(iID)
            sName = None if tData else '\xa5\xbc\xaa\xbe'
            slinkText = dDailyData['link'].replace('\xb8`\xa4\xe9', '%s\xc2\xa7\xaa\xab' % sName)
            sProgess = '#R\xa5\xbc\xbb\xe2\xa8\xfa#n'
        elif iID in g_OrgTask:
            slinkText = dDailyData['link']
            tData = self.GetTaskDataById(iID)
            sExt = None if tData else ''
            if sExt:
                sExtData = sExt.split('|')
                slinkText = slinkText.replace('\xab\xdd\xa9w', sExtData[-1])
                slinkText = slinkText.replace(' \xa4u\xa7@\xa6\xb8\xbc\xc6', '\xa4u\xa7@')
                sProgess = sExtData[0]
            else:
                sProgess = sExt
                if sProgess is None and iMyGrade < dDailyData['lockGrade']:
                    sProgess = dDailyData['unlockText']
                
        else:
            slinkText = dDailyData['link']
            tData = self.GetTaskDataById(iID)
            sProgess = None if tData else None
            if sProgess is None and iMyGrade < dDailyData['lockGrade']:
                sProgess = dDailyData['unlockText']
            
        sProgess = self.TextColorChange(sProgess)
        return (slinkText, sProgess)

    
    def TextColorChange(self, text):
        text = interface.ReplaceRed(text)
        text = interface.Replace(text)
        if interface.IsStyle1():
            text = text.replace('#cAFAFAF', '#c6E6E6E')
        
        if interface.IsStyle3():
            text = text.replace('#cAFAFAF', '#c787878')
            text = text.replace('#Y', '#cED8200')
        
        if interface.IsStyle4():
            text = text.replace('#cAFAFAF', '#c787878')
            text = text.replace('#Y', '#cED8200')
            text = text.replace('#c5DB0FE', '#c286ad6')
        
        return text

    
    def SortData(self, dInfoLst):
        if len(dInfoLst) <= 0:
            return None
        
        import hero
        iMyGrade = hero.GetProp('m_Grade')
        unLockLst = []
        lockLst = []
        for val in dInfoLst:
            if iMyGrade < val['lockGrade']:
                unLockLst.append(val)
                continue
            lockLst.append(val)
        
        sorted(unLockLst, key = (lambda s: s['Id']), reverse = False)
        sorted(lockLst, key = (lambda s: s['Id']), reverse = False)
        lockLst.extend(unLockLst)
        return lockLst

    
    def UpdateTodayMessage(self, text):
        text = interface.ReplaceRed(text)
        text = interface.Replace(text)
        if interface.IsStyle1():
            text = text.replace('#cAFAFAF', '#c6E6E6E')
        
        if interface.IsStyle3():
            text = text.replace('#cAFAFAF', '#c787878')
            text = text.replace('#Y', '#cED8200')
        
        if interface.IsStyle4():
            text = text.replace('#cAFAFAF', '#c787878')
            text = text.replace('#Y', '#cED8200')
            text = text.replace('#c5DB0FE', '#c286ad6')
        
        txtLst = text.split('#r')
        self.CreatePngList(txtLst)

    
    def CreatePngList(self, txtLst):
        self.m_oItemList = self.GetObject('lst_dft_002')
        doubleItem = CDoubleItem(self.GetObject('lst_dft_002'))
        self.m_oItemList.AddItem(doubleItem)
        for txt in txtLst:
            if doubleItem.GetCount() == 2:
                doubleItem = CDoubleItem(self.GetObject('lst_dft_002'))
                self.GetObject('lst_dft_002').AddItem(doubleItem)
            
            if txt:
                doubleItem.AddItem(CActivityItem(doubleItem, txt))
                continue
        
        self.GetObject('lst_dft_002').Refresh()
        self.GetObject('lst_dft_002').ResetScrollBar()

    
    def ShowFullTips(self, oList, w):
        sRetList = self.GetExitDesc()
        if not sRetList:
            return None
        
        for sLine in sRetList:
            oBox = CMyBox(oList, '', '', interface.FontLT14_3, w, interface.COLOR_168)
            oBox.m_oRtText = wrapinterface.WrapRichTextWithLinkCursor(oBox, w, interface.FontLT14_3, sLine, interface.COLOR_168)
            interface.CenterLeft(oBox.m_oRtText, 4)
            oBox.m_oRtText.SetIgnoreParent(True)
            oList.AddItem(oBox)
        

    
    def GetExitDesc(self):
        import hero
        import returnrewardmgr
        if hero.IsExpOver() and hero.IsMoneyOver():
            sTxtList = [
                '#R\xa7A\xb7\xed\xabe\xb8g\xc5\xe7\xa9M\xb2{\xaa\xf7\xb6W\xb9L\xc4\xe2\xb1a\xa4W\xad\xad\xa1A\xbd\xd0#n',
                '#R\xa4\xce\xae\xc9\xb3B\xb2z#n']
        elif hero.IsExpOver():
            sTxtList = [
                '#R\xa7A\xb7\xed\xabe\xb8g\xc5\xe7\xb6W\xb9L\xc4\xe2\xb1a\xa4W\xad\xad\xa1A\xbd\xd0\xa4\xce\xae\xc9\xb3B#n',
                '#R\xb2z\xa1A\xa7_\xabh\xb6W\xa5X\xb3\xa1\xa4\xc0\xb1N\xae\xf8\xa5\xa2#n']
        elif hero.IsMoneyOver():
            sTxtList = [
                '#R\xa7A\xb7\xed\xabe\xb2{\xaa\xf7\xb6W\xb9L\xc4\xe2\xb1a\xa4W\xad\xad\xa1A\xbd\xd0\xa4\xce\xae\xc9\xb3B#n',
                '#R\xb2z\xa1A\xa7_\xabh\xb6W\xa5X\xb3\xa1\xa4\xc0\xb1N\xc2\xe0\xac\xb0\xa9\xe8\xa5\xce\xaa\xf7#n']
        else:
            sDesc = returnrewardmgr.GetReturnRewardMgr().GetNewExitDesc()
            if sDesc:
                sTxtList = [
                    sDesc]
            else:
                sTxtList = []
        return sTxtList

    
    def GetTips(self):
        import cursor
        (x, y) = cursor.GetPos()
        for rt in self.m_txtInfo:
            if rt.GetParent().GetParent().GetShow():
                (STYLE, ry) = rt.GetScreenPos()
                iId = int(rt.ClickID(x - STYLE, y - ry))
                if rt.m_LinkObj.get(iId):
                    return rt.m_LinkObj[iId]
                
            rt.m_LinkObj.get(iId)
        

    
    def LeftUp(self):
        combdialog.CCombDialog.LeftUp(self)
        ob = self.GetTips()
        if ob:
            ob.OnLeftUp()
        

    
    def OnSelect(self, ctrl):
        _enable = (100, 101)
        selectcolor = interface.COLOR_296
        color = interface.COLOR_285
        self.GetObject('btn_page1').SetTextColor(color)
        self.GetObject('btn_page2').SetTextColor(color)
        self.GetObject('btn_page1').Enable(True)
        self.GetObject('btn_page2').Enable(True)
        if ctrl.m_MsgID in _enable:
            self.OnSwitch(ctrl.m_MsgID)
            ctrl.Enable(False)
            ctrl.SetTextColor(selectcolor)
        
        return True

    
    def OnSwitch(self, itype):
        self.m_Switch = itype

    
    def OnExit(self):
        import main
        C2IMScreenShotPath()
        main.doexit(None)
        self.CloseWindow()

    
    def OnReturn(self):
        import main
        main.doreturn(interface.CBaseObject(None))
        self.CloseWindow()

    
    def CloseWindow(self):
        import main
        main.docancel(self)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 6:
            if syncoperate.IsAttaching():
                return None
            
            self.CheckShowExitTips(1)
        elif msgid == 5:
            if syncoperate.IsAttaching():
                return None
            
            self.CheckShowExitTips(2)
        elif msgid == 7:
            self.CloseWindow()
        elif msgid == 8:
            import dlgcalendar
            dlgcalendar.C2SOpenCalendar()
            self.CloseWindow()
        elif msgid == 9:
            import nethero
            nethero.C2SOpenFilter()
            self.CloseWindow()
        

    
    def CheckShowExitTips(self, iType):
        import hero
        import dlgnpc
        import cfg
        iHide = cfg.GetData('mx.ini', 'Game', 'HideExitTip')
        sMsg = ''
        sTipType = None if iType == 1 else '\xad\xab\xb7s\xb5n\xbf\xfd'
        if hero.IsMoneyOver():
            sMsg = '\xb1z\xb7\xed\xabe\xc4\xe2\xb1a#R\xb2{\xaa\xf7\xb6W\xb9L\xa4W\xad\xad#n\xa1A\xa6p#B\xa4\xb5\xa4\xe9\xa4\xba#n\xa4\xa3\xa4\xce\xae\xc9\xb3B\xb2z\xa1A\xb6W\xa5X\xb3\xa1\xa4\xc0\xb1N#R\xc2\xe0\xac\xb0\xa9\xe8\xa5\xce\xaa\xf7#n\xa1C#r\xbdT\xbb{%s\xb6\xdc\xa1H\nQ\xbdT\xbb{%s' % (sTipType, sTipType)
            dlgnpc.ShowClientDlg(sMsg, '', misc.Functor(self.OnExitTipDlg, iType))
        elif iHide and int(iHide) == 1:
            self.DoExit(iType)
        elif hero.IsExpOver():
            sMsg = '\xb1z\xb7\xed\xabe\xc4\xe2\xb1a#R\xb8g\xc5\xe7\xb6W\xb9L\xa4W\xad\xad#n\xa1A\xa6p#B\xa4\xb5\xa4\xe9\xa4\xba#n\xa4\xa3\xa4\xce\xae\xc9\xb3B\xb2z\xa1A\xb6W\xa5X\xb3\xa1\xa4\xc0\xb1N#R\xae\xf8\xa5\xa2#n\xa1C#r\xbdT\xbb{%s\xb6\xdc\xa1H\nQ\xbdT\xbb{%s\nQ%s\xa5B\xa5H\xab\xe1\xa4\xa3\xa6A\xb4\xa3\xa5\xdc' % (sTipType, sTipType, sTipType)
        
        if sMsg:
            dlgnpc.ShowClientDlg(sMsg, '', misc.Functor(self.OnExitTipDlg, iType))
        else:
            self.DoExit(iType)

    
    def OnExitTipDlg(self, iType, iMsgID):
        import cfg
        if iMsgID == 1:
            self.DoExit(iType)
        elif iMsgID == 2:
            cfg.SaveData('mx.ini', 'Game', 'HideExitTip', 1)
            self.DoExit(iType)
        

    
    def DoExit(self, iType):
        if iType == 1:
            self.OnExit()
        else:
            self.OnReturn()



class CActivityItem(combdialog.CAttachCombDialog):
    
    def __init__(self, parent, txt):
        combdialog.CAttachCombDialog.__init__(self, parent, 'dialog/schedule_new/todaynews.dlg')
        self.m_oText = None
        self.InitData(txt)

    
    def SetContentTips(self, sTips, iDir = 2):
        oHlocTips = self.GetObject('hloc_tips')
        oHlocTips.SetTips(sTips, iDir)

    
    def InitData(self, txt):
        if len(txt.split(' ')) >= 2:
            sTextList = txt.split(' ')
            sActivityName = sTextList[0]
            if len(sTextList) > 2:
                sSchedule = '\xb2\xbe\xa4J\xacd\xac\xdd\xb8\xd4\xb1\xa1'
                sTips = '#r'.join(sTextList[1:])
                self.SetContentTips(sTips)
            else:
                sSchedule = sTextList[1]
                self.SetContentTips(None)
            oTextDeft = self.GetObject('text_dft_000')
            oTextObj = wrapinterface.WrapRichTextWithLinkCursor(self, 120, interface.FontLT14_3, sActivityName, oTextDeft.GetColor())
            oTextDeft.SetText('')
            (x, y) = oTextDeft.GetPos()
            oTextObj.SetPos(x, y)
            self.m_oText = oTextObj
            self.GetObject('text_dft_002').SetText(sSchedule)
        



class CDoubleItem(combdialog.CAttachCombDialog):
    
    def __init__(self, parent):
        combdialog.CAttachCombDialog.__init__(self, parent, 'dialog/schedule/doubleitem2.dlg')
        (self.m_Width, self.m_Hight) = self.GetObject('frame_bg').GetSize()
        self.m_iCount = 0
        self.m_lItems = []

    
    def GetSize(self):
        return (self.m_Width, self.m_Hight)

    
    def GetCount(self):
        return self.m_iCount

    
    def AddItem(self, item):
        if self.m_iCount == 2:
            return None
        
        (x, y) = self.GetObject('loc_item%d' % self.m_iCount).GetPos()
        item.SetPos(x, y)
        self.m_lItems.append(item)
        self.m_iCount += 1

    
    def OnMouseWheelUp(self, p):
        combdialog.CAttachCombDialog.MouseWheelUp(self, p)

    
    def OnMouseWheelDown(self, p):
        combdialog.CAttachCombDialog.MouseWheelDown(self, p)



def Show(data):
    global g_ExitInfo
    g_ExitInfo = CExitInfoDialog()
    g_ExitInfo.Refresh(data)


def CalcFlag(myTime, textTime):
    (sTime, eTime) = textTime.split('~')
    if myTime <= myTime:
        pass
    elif myTime <= eTime:
        return 1
    
    if eTime < myTime:
        overFlag = 1
    else:
        overFlag = 0
    if overFlag:
        return 2
    else:
        return 0


def C2IMScreenShotPath():
    import pubdylogin
    import mgrscreenshot
    import imshare
    import os
    if not mgrscreenshot.g_ScreenShotPath:
        return None
    
    tmp = []
    for idx, path in enumerate(mgrscreenshot.g_ScreenShotPath):
        path = os.path.abspath(path)
        tmp.append(path)
    
    dct = {
        'picture_count': len(mgrscreenshot.g_ScreenShotPath),
        'upload_picture': tmp,
        'game_id': 1 }
    netobj = pubdylogin.GetHeader(imshare.GAME2IMAUDIOROOM.SCREENSHOTPATH)
    if not netobj:
        return None
    
    netobj.PackAddJsonS(dct)
    netobj.PacketSend()
    mgrscreenshot.RemoveAllPath()
    print '\xb5o\xb0e\xb9\xcf\xa4\xf9\xabH\xae\xa7\xb5\xb9\xbe\xd4\xb7\xf9', dct
