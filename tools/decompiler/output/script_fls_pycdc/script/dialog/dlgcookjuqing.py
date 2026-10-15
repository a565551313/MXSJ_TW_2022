# pycdc 交叉复核产物 · script.fls entry 4280
# co_filename(原始)='script/dialog/dlgcookjuqing.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4280.pyc (Python 2.5)

import combdialog
import interface
import ui
import timer
import C_sys
g_CookDlg = None

def ModuleReset():
    global g_CookDlg
    g_CookDlg = None


def Show(iNpcID):
    global g_CookDlg
    g_CookDlg = CCookJuQingDlg(iNpcID)


def ShowPintu(iNpcID):
    global g_CookDlg
    g_CookDlg = CPintuDlg(iNpcID)


class CCookJuQingDlg(combdialog.CCombDialog):
    PATH = 'combdialog\\\xd4\xd3\xcd\xbc\\\xca\xb1\xbc\xe4\xcc\xf5.igs'
    RED_PATH = 'combdialog4/\xd4\xd3\xcd\xbc/\xc5\xeb\xe2\xbf/red.png'
    ORI_PATH = 'combdialog4/\xd4\xd3\xcd\xbc/\xc5\xeb\xe2\xbf/ori.png'
    YEL_PATH = 'combdialog4/\xd4\xd3\xcd\xbc/\xc5\xeb\xe2\xbf/yellow.png'
    ALL_NUM = 18
    DELTY = 9
    PERADD = 3
    PERTIME = 10
    
    def __init__(self, iNpcID):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/cook_juqing.dlg')
        interface.Center(self)
        self.InitPlay()
        self.m_iID = iNpcID
        self.m_iLastFrame = 2
        self.m_iFireCount = 0
        self.m_oTxt = self.GetObject('txt_fire')
        self.InitDlg()

    
    def InitDlg(self):
        import dlgguidetips
        self.m_ProgressBar = self.GetObject('img_bar')
        oPar = self.GetObject('loc_tips')
        (w, h) = oPar.GetSize()
        self.m_oGuideTips = dlgguidetips.CGuideTips(oPar, '\xbd\xd0\xc2I\xc0\xbb\xa1u\xc2I\xa4\xf5\xa1v \xb6}\xa9l\xb2i\xb6\xb9\xa7a\xa1I', 4, 0, 0, w, h)
        self.m_oChangeFrameTimer = timer.Timer(0.28, self.ChangeFrame, 1000)

    
    def ChangeFrame(self):
        oBtn = self.GetObject('btn_pack')
        oBtn.SetFrame(self.m_iLastFrame)
        if self.m_iLastFrame == 2:
            self.m_iLastFrame = 1
        else:
            self.m_iLastFrame = 2

    
    def InitPlay(self):
        self.m_iFire = 0
        self.m_oTimer = None
        self.m_oCloseTimer = None
        self.m_iStartTime1 = 0
        self.m_iStartTime2 = 0
        self.m_iPerfectTime1 = 0
        self.m_iFireNum = 0
        self.m_iGameState = 0
        self.m_bFail = False
        self.m_bClickPlay = False
        self.m_oNormalFireList = []
        self.m_oBigFireList = []
        self.m_oBgBarList = []
        self.m_iFireCount = 0
        self.m_oUpFire = None
        self.m_oDownFire = None

    
    def OnPlayGame(self):
        '''
\t\t\xb6}\xa9l\xaa\xb1\xb9C\xc0\xb8
\t\t'''
        self.m_iFire = 3
        self.AddFire(2)
        self.AddBar(3)
        self.m_iGameState = 1
        self.m_oTimer = self.CreatePyCommand(self.PERTIME, self.CheckFire)
        self.m_iStartTime1 = C_sys.GetTime()
        self.CheckFire()

    
    def Play(self):
        '''
\t\t\xa5[\xa4@\xa6\xb8\xa4\xf5
\t\t'''
        oBtn = self.GetObject('btn_pack')
        oBtn.SetFrame(1)
        self.m_iFireCount += 1
        if self.m_iGameState == 0:
            self.m_oTxt.SetText('#67\xa5[\xa8\xec\xa4\xa4\xa4\xf5\xb2i\xb6\xb9!')
            self.GetObject('btn_pack').SetText('\xa5[\xa4\xf5')
            self.OnPlayGame()
        elif self.m_iGameState == 1:
            self.m_bClickPlay = True
            self.m_iFire += 2
            self.AddBar(2)
        

    
    def RePlay(self):
        '''
\t\t\xad\xab\xaa\xb1\xb9C\xc0\xb8
\t\t'''
        if self.m_oTimer:
            self.m_oTimer.Release()
        
        self.InitPlay()
        self.InitDlg()
        self.m_oTxt.SetText('\xa5\xcd\xb0_\xaa\xa4\xa4\xf5~')

    
    def OnFinishLevelOne(self):
        '''
\t\t\xa7\xb9\xa6\xa8\xb6\xa5\xacq1
\t\t'''
        if self.m_oTimer:
            self.m_oTimer.Release()
        
        self.m_oTimer = None
        self.AddFire(3)
        self.m_iStartTime2 = C_sys.GetTime()
        self.m_oTimer = self.CreatePyCommand(self.PERTIME, self.KeepFire)

    
    def OnFinish(self):
        '''
\t\t\xa7\xb9\xa6\xa8\xb9C\xc0\xb8
\t\t'''
        import usermacro
        usermacro.PROMPT_MSG('\xa6n\xa4F\xa1I#G\xac\xc3\xaf]\xa4Y\xa4l#n\xa4w\xb8g\xb7s\xc2A\xa5X\xc4l\xa1I ')
        self.m_oTxt.SetText('\xb2i\xb6\xb9\xa7\xb9\xa6\xa8\xa1I')
        self.GetObject('btn_pack').SetShow(False)
        if self.m_oTimer:
            self.m_oTimer.Release()
        
        self.m_oTimer = None
        self.m_iGameState = 2
        if self.m_iFire > 32:
            iType = 1
        elif self.m_iFire in xrange(17, 33):
            iType = 2
        else:
            iType = 3
        import netcommon
        netcommon.C2SJuqingCook(iType, self.m_iID)
        self.m_oCloseTimer = self.CreatePyCommand(60, self.OnCloseWindow)

    
    def OnFail(self):
        '''
\t\t\xb9C\xc0\xb8\xa5\xa2\xb1\xd1
\t\t'''
        import usermacro
        usermacro.PROMPT_MSG('\xaet\xa4@\xc2I\xb4N\xa7\xb9\xac\xfc\xa7\xb9\xa6\xa8\xa5\xf4\xb0\xc8\xa4F\xa9O~')
        self.m_bFail = True
        self.m_iGameState = 2
        self.m_bClickPlay = True
        if self.m_oTimer:
            self.m_oTimer.Release()
        
        self.m_oTimer = None

    
    def AddFire(self, iNum):
        self.m_iFireNum = iNum
        self.m_oBigFireList = []
        oUpBg = self.GetObject('loc_smallfire')
        oDownBg = self.GetObject('loc_fire')
        if iNum == 1:
            sUpPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc5\xeb\xe2\xbf/\xd2\xbb\xbc\xb6\xbb\xf0_up_.igs'
            sDownPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc5\xeb\xe2\xbf/\xd2\xbb\xbc\xb6\xbb\xf0_down_.igs'
        else:
            sUpPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc5\xeb\xe2\xbf/\xb6\xfe\xbc\xb6\xbb\xf0_up_.igs'
            sDownPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc5\xeb\xe2\xbf/\xb6\xfe\xbc\xb6\xbb\xf0_down_.igs'
        self.m_oUpFire = ui.\x91\x9bmage(oUpBg, sUpPath, interface.UIPath)
        self.m_oUpFire.CreateCommand(2, 'animation')
        self.m_oDownFire = ui.\x91\x9bmage(oDownBg, sDownPath, interface.UIPath)
        self.m_oDownFire.CreateCommand(2, 'animation')

    
    def KeepFire(self, bDel = True, a = 1):
        iTmpTime = C_sys.GetTime()
        if iTmpTime - self.m_iStartTime1 > 160000 or self.m_iFire == 0:
            self.OnFail()
            return None
        
        if self.m_iStartTime1 and iTmpTime - self.m_iStartTime1 > 25000:
            self.OnFinish()
            return None
        
        if bDel:
            if self.m_iFire > 1:
                self.m_iFire -= 1
                self.DelBar(1)
            
        
        if self.m_iFire * 1 / self.ALL_NUM < 0.37:
            self.AddFire(1)
        elif self.m_iFire * 1 / self.ALL_NUM < 0.75:
            self.AddFire(2)
        else:
            self.CreateBigFire()
        return (0,)

    
    def CheckFire(self, bDel = True, a = 1):
        iTmpTime = C_sys.GetTime()
        if bDel:
            if self.m_iFire > 20 or iTmpTime - self.m_iStartTime1 >= 50000:
                if self.m_oTimer:
                    self.m_oTimer.Release()
                
                self.m_oTimer = None
                self.OnFinishLevelOne()
            
            if iTmpTime - self.m_iStartTime1 > 80000:
                self.OnFail()
                return None
            
            if self.m_iFire == self.ALL_NUM:
                self.OnFinish()
                if self.m_oTimer:
                    self.m_oTimer.Release()
                
                self.m_oTimer = None
                return None
            
            if self.m_iFire > 1:
                self.m_iFire -= 1
                self.DelBar(1)
            
        
        if self.m_iFire * 1 / self.ALL_NUM < 0.25:
            if self.m_iFireNum != 1:
                self.AddFire(1)
            
        elif self.m_iFire * 1 / self.ALL_NUM < 0.5:
            if self.m_iFireNum != 2:
                self.AddFire(2)
            
        elif self.m_iFire * 1 / self.ALL_NUM < 0.75:
            if self.m_iFireNum != 3:
                self.AddFire(3)
            
        else:
            self.CreateBigFire()
        return (0,)

    
    def CreateBigFire(self):
        self.m_oNormalFireList = []
        self.m_oBigFireList = []
        oUpBg = self.GetObject('loc_smallfire')
        oDownBg = self.GetObject('loc_fire')
        sUpPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc5\xeb\xe2\xbf/\xc8\xfd\xbc\xb6\xbb\xf0_up_.igs'
        sDownPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc5\xeb\xe2\xbf/\xc8\xfd\xbc\xb6\xbb\xf0_down_.igs'
        self.m_oUpFire = ui.\x91\x9bmage(oUpBg, sUpPath, interface.UIPath)
        self.m_oUpFire.CreateCommand(2, 'animation')
        self.m_oDownFire = ui.\x91\x9bmage(oDownBg, sDownPath, interface.UIPath)
        self.m_oDownFire.CreateCommand(2, 'animation')

    
    def AddBar(self, iNum):
        sPath = ''
        for i in xrange(iNum):
            if len(self.m_oBgBarList) < self.ALL_NUM * 7 / 18:
                sPath = self.YEL_PATH
            elif len(self.m_oBgBarList) < self.ALL_NUM * 7 / 9:
                sPath = self.ORI_PATH
            elif len(self.m_oBgBarList) < self.ALL_NUM:
                sPath = self.RED_PATH
            else:
                return None
            obj = ui.\x91\x9bmage(self.m_ProgressBar, sPath, interface.UIPath)
            (_, h) = self.m_ProgressBar.GetSize()
            obj.SetPos(2, h - 9 - len(self.m_oBgBarList) * (self.DELTY + 1))
            obj.SetZ(2)
            self.m_oBgBarList.append(obj)
        

    
    def DelBar(self, iNum):
        if self.m_iFire * 1 / self.ALL_NUM < 0.25:
            self.m_oTxt.SetText('\xa5[\xa8\xec\xa4\xa4\xa4\xf5\xb2i\xb6\xb9')
        elif self.m_iFire * 1 / self.ALL_NUM < 0.75:
            self.m_oTxt.SetText('\xa6A\xabO\xab\xf9\xa4@\xb7|\xa8\xe0')
        else:
            self.m_oTxt.SetText('\xb4w\xa4r\xbd_\xb8X\xbe\xcf\xb4\xa9\xb1\xec\xa4\xa4\xa4\xf5')
        print 'DelBarDelBarDelBarDelBarDelBarDelBar'
        self.m_oBgBarList = self.m_oBgBarList[:-iNum]

    
    def OnCloseWindow(self, dlg = None):
        global g_CookDlg
        g_CookDlg = None
        if self.m_oCloseTimer:
            self.m_oCloseTimer.Release()
        
        if self.m_oChangeFrameTimer:
            self.m_oChangeFrameTimer.Release()
        
        self.m_oCloseTimer = None
        self.m_oChangeFrameTimer = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 2:
            self.OnCloseWindow()
        elif iMsgID == 5:
            self.Play()
        



class CPintuDlg(combdialog.CCombDialog):
    
    def __init__(self, iNpcID):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/xinrenpintu.dlg')
        interface.Center(self)
        self.m_oIconList = []
        self.m_iStateList = []
        self.m_bFinish = False
        self.m_iNpcID = iNpcID
        self.InitIcon()

    
    def InitIcon(self):
        self.GetObject('txt_left').SetShow(False)
        self.GetObject('txt_right').SetShow(False)
        self.GetObject('img_color').SetShow(False)
        for i in xrange(1, 4):
            oBg = self.GetObject('loc_icon%d' % i)
            (x, y) = oBg.GetPos()
            oIcon = CHold(self, i)
            oIcon.SetPos(x, y)
            self.m_oIconList.append(oIcon)
        

    
    def OnCheckIcon(self, iIndex):
        oIcon = self.m_oIconList[iIndex - 1]
        (x, y) = oIcon.GetPos()
        (hx, hy, hw, h) = self.GetLocData('hotbox_%d' % iIndex)
        if x in xrange(hx, hx + hw) and y in xrange(hy, hy + h):
            oIcon.SetHold(False)
            (x, y) = self.GetObject('loc_correct%d' % iIndex).GetPos()
            oIcon.SetPos(x, y)
            self.m_iStateList.append(1)
        else:
            oBg = self.GetObject('loc_icon%d' % iIndex)
            (x, y) = oBg.GetPos()
            oIcon.SetPos(x, y)
            import usermacro
            usermacro.PROMPT_MSG('\xac\xdd\xb0_\xa8\xd3\xa4\xa3\xacO\xb3o\xbc\xcb\xaa\xba\xae@\xa1A\xa6A\xa5J\xb2\xd3\xc1@\xa4@\xc1@')
        if len(self.m_iStateList) == 3:
            self.OnFinish()
        

    
    def OnFinish(self):
        if len(self.m_iStateList) == 3:
            self.m_oIconList = []
            self.GetObject('text_dft_000').SetShow(False)
            self.GetObject('btn_del').SetShow(False)
            self.GetObject('txt_left').SetShow(True)
            self.GetObject('txt_right').SetShow(True)
            self.GetObject('img_color').SetShow(True)
            self.GetObject('img_grey').SetShow(False)
            self.m_bFinish = True
            import netcommon
            netcommon.C2SJuqingPintu(self.m_iNpcID)
        else:
            import usermacro
            usermacro.PROMPT_MSG('\xab\xf7\xb9\xcf\xc1\xd9\xa6\xb3\xb4\xdd\xaf\xca\xae@')

    
    def OnCloseWindow(self, dlg = None):
        global g_CookDlg
        g_CookDlg = None

    
    def CheckFinish(self):
        import commondialog
        if not self.m_bFinish:
            box = commondialog.ShowMessageBox('\xbdT\xbb{\xa9\xf1\xb1\xf3\xab\xf7\xb9\xcf\xbb\xf2?', ('\xbdT\xbb{', '\xa8\xfa\xae\xf8'), (self.OnCloseWindow, None))
        else:
            self.OnCloseWindow()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            if not self.m_bFinish:
                self.OnFinish()
            else:
                self.OnCloseWindow()
        elif iMsgID == 2:
            self.CheckFinish()
        



class CHold(ui.\x91\x9bmage, interface.CHoldObject):
    
    def __init__(self, oParent, iIndex):
        ui.\x91\x9bmage.__init__(self, oParent, 'combdialog3/\xd4\xd3\xcd\xbc/\xd0\xc2\xca\xd6\xc6\xb4\xcd\xbc/%d.png' % iIndex, interface.UIPath)
        self.MessageProcess()
        self.m_iIndex = iIndex
        self.m_bHold = True

    
    def LeftDown(self):
        if not self.m_bHold:
            return None
        
        interface.CHoldObject.LeftDown(self)

    
    def LeftUp(self):
        if not self.m_bHold:
            return None
        
        interface.CHoldObject.LeftUp(self)
        self.GetParent().OnCheckIcon(self.m_iIndex)

    
    def SetHold(self, bHold):
        self.m_bHold = bHold

    
    def Hold(self):
        if not self.m_bHold:
            return None
        
        import cursor
        (mx, my) = cursor.GetPos()
        x = mx - interface.HoldX
        y = my - interface.HoldY
        self.SetPos(x, y)
