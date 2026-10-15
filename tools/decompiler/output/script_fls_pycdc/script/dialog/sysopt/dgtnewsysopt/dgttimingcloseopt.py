# pycdc 交叉复核产物 · script.fls entry 216
# co_filename(原始)='script/dialog/sysopt/dgtnewsysopt/dgttimingcloseopt.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_216.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/2/20 17:28
\xd7\xf7\xd5\xdf: yb
\xce\xc4\xbc\xfe: dgttimingcloseopt
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import time
import commondialog
import delegatebase
import dlgnewsysopt
import dlgshutdown
import misc
import modeltimingcloseopt
import netstate
import timer
import usermacro

class CTimingCloseOptDgt(delegatebase.CDelegateBase):
    
    def Init(self):
        oView = self.GetView()
        self.EditInit()

    
    def EditInit(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_RefreshSelectShutDown, self.RefreshSelectShutdown)
        oView.ssConnect(oView.SS_OnSetTimeSelect, self.OnSetTimeSelect)
        oView.ssConnect(oView.SS_OnCountDownSelect, self.OnCountDownSelect)
        oView.ssConnect(oView.SS_OnSetShutDown, self.OnSetShutDown)
        oView.ssConnect(oView.SS_OnDelShutDown, self.DelShutdown)
        oView.ssConnect(oView.SS_PareantClose, self.CloseDlg)

    
    def RefreshSelectShutdown(self):
        oView = self.GetView()
        self.ResetShutDown()
        timer.Timer(0, misc.Functor(self.OpenShutDownTime), oRelayObj = self)
        if oView.GetTimeSelect():
            timer.Timer(0, misc.Functor(self.CloseTimeEdit), oRelayObj = self)
        
        if dlgshutdown.GetNoShutDown() and not oView.GetNoShutDown():
            oView.SetNoShutDown(dlgshutdown.GetNoShutDown())
        
        self.OnChangeShutdown()

    
    def OnChangeShutdown(self):
        oView = self.GetView()
        self.GetModel().SetShutDownList([
            oView.GetCountDownSelected(),
            oView.GetTimeSelect(),
            oView.GetNoShutDown()])

    
    def ResetShutDown(self):
        oView = self.GetView()
        oModel = self.GetModel()
        if len(oModel.GetShutDownList()) < 3:
            return None
        
        bShuwDownList = oModel.GetShutDownList()
        oView.SetCountDownSelect(bShuwDownList[0])
        oView.SetTimeSelect(bShuwDownList[1])
        oView.SetNoShutDown(bShuwDownList[2])

    
    def SetShutDownTime(self):
        oView = self.GetView()
        iSetTime = dlgshutdown.GetSetTime()
        iTime = time.time()
        if iSetTime:
            (iDay, iHour, iMinute) = time.localtime(iSetTime)[2:5]
        else:
            (iDay, iHour, iMinute) = time.localtime(iTime + 300)[2:5]
        sDayTxt = '\xa4\xb5\xa4\xd1'
        if iDay != time.localtime(iTime)[2]:
            sDayTxt = '\xa9\xfa\xa4\xd1'
        
        oView.SetHourEditText('%.2d' % iHour)
        oView.SetMinuteEditText('%.2d' % iMinute)
        oView.SetDayEditText(sDayTxt)

    
    def OnSetTimeSelect(self):
        oView = self.GetView()
        bShow = oView.GetTimeSelect()
        if not bShow:
            self.SetShutDownTime()
        
        bCountDown = oView.GetCountDownSelected()
        if bCountDown:
            oView.SetCountDownSelect(not bCountDown)
        

    
    def OnCountDownSelect(self):
        oView = self.GetView()
        bShow = oView.GetCountDownSelected()
        if not bShow:
            self.SetDelayTime()
        
        oView.SetTimeEditShow(not bShow)
        bSelect = oView.GetTimeSelect()
        if bSelect:
            None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, oView.SetTimeSelect, not bSelect)
        

    
    def OnSetShutDown(self):
        oView = self.GetView()
        if oView.GetCountDownSelected():
            self.SetCountShutdown()
        elif oView.GetTimeSelect():
            self.SetTimeShutdown()
        else:
            self.DelShutdown()
        self.OnChangeShutdown()

    
    def SetTimeShutdown(self):
        oView = self.GetView()
        bNoShutDown = oView.GetNoShutDown()
        sDayTxt = oView.GetDayText()
        if sDayTxt == '\xa4\xb5\xa4\xd1':
            iDay = 0
        else:
            iDay = 1
        sHour = oView.GetHourText()
        sMinute = oView.GetMinuteText()
        if not sHour or not sMinute:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xa6n\xae\xc9\xb6\xa1')
            return None
        
        iTime = time.time()
        iHour = int(sHour) + iDay * 24
        iMinute = int(sMinute)
        (iNowHour, iNowMinute) = time.localtime(iTime)[3:5]
        if iNowHour == iHour and iNowMinute == iMinute:
            usermacro.PROMPT_MSG('\xae\xc9\xb6\xa1\xa4\xa3\xaf\xe0\xb3]\xb8m\xb7\xed\xabe\xae\xc9\xb6\xa1')
            return None
        elif (iNowHour > iHour or iNowHour == iHour) and iNowMinute > iMinute:
            usermacro.PROMPT_MSG('\xbd\xd0\xb3]\xb8m\xbf\xf0\xa9\xf3\xb7\xed\xabe\xae\xc9\xa8\xe8\xaa\xba\xae\xc9\xb6\xa1')
            self.SetShutDownTime()
            oView.SetTimeSelect(oView.GetTimeSelect())
            return None
        
        iShutDownTime = iTime + (iHour - iNowHour) * 3600 + (iMinute - iNowMinute) * 60
        dlgshutdown.SetNoShutDown(bNoShutDown)
        dlgshutdown.StartSetTimeShutdown(iShutDownTime)
        usermacro.PROMPT_MSG('\xa9w\xae\xc9\xc3\xf6\xbe\xf7\xb3]\xb8m\xa6\xa8\xa5\\')

    
    def DelShutdown(self):
        oView = self.GetView()
        if dlgshutdown.HasSetTimeShutdown():
            usermacro.PROMPT_MSG('\xa9w\xae\xc9\xc3\xf6\xbe\xf7\xa4w\xa8\xfa\xae\xf8')
        
        oView.SetTimeSelect(False)
        oView.SetCountDownSelect(False)
        dlgshutdown.Clear()
        self.OnChangeShutdown()

    
    def SetCountShutdown(self):
        oView = self.GetView()
        
        try:
            iTime = int(oView.GetTimeEditText())
        except:
            usermacro.PROMPT_MSG('\xbf\xe9\xa4J\xaa\xba\xbc\xc6\xbe\xda\xa6\xb3\xbb~\xa1A\xbd\xd0\xad\xab\xb7s\xbf\xe9\xa4J')
            return None

        if iTime < 0 or iTime > 1440:
            usermacro.PROMPT_MSG('\xae\xc9\xb6\xa1\xa5\xb2\xb6\xb7\xa6b0~1440\xa4\xc0\xc4\xc1\xa4\xa7\xb6\xa1')
            return None
        
        bNoShutDown = oView.GetNoShutDown()
        dlgshutdown.SetNoShutDown(bNoShutDown)
        dlgshutdown.StartCountShutdown(iTime)
        if iTime > 0:
            usermacro.PROMPT_MSG('\xa9w\xae\xc9\xc3\xf6\xbe\xf7\xb3]\xb8m\xa6\xa8\xa5\\')
        elif iTime == 0:
            usermacro.PROMPT_MSG('\xa9w\xae\xc9\xc3\xf6\xbe\xf7\xa4w\xa8\xfa\xae\xf8')
        

    
    def SetDelayTime(self):
        oView = self.GetView()
        iDelayTime = dlgshutdown.GetDelayTime()
        if iDelayTime:
            oView.SetTimeEditText(str((iDelayTime + 59) / 60))
        elif netstate.IsState(111):
            sMinutes = '120'
        else:
            sMinutes = '60'
        oView.SetTimeEditText(sMinutes)
        oView.SetTimeEditSelect(0, len(oView.GetTimeEditText()))
        oView.SetTimeEditActive(True)

    
    def OpenShutDownTime(self):
        self.GetView().SetTimeEditShow(False)
        self.SetShutDownTime()

    
    def CloseTimeEdit(self):
        self.GetView().SetTimeEditShow(False)

    
    def GetModel(self):
        return modeltimingcloseopt.GetTimingCloseOptModel()

    
    def CloseDlg(self):
        if self.CheckShutdownModify():
            commondialog.ShowMessageBox('\x05\xe6\x0e\xf6\x02\xe6\x0f\xda\x1eD\x02\xcc\x0eZ\x0eF\x08\xe1', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (misc.Functor(self.SaveNowChange), misc.Functor(self.CloseOpt)))
        else:
            dlgnewsysopt.CloseNewSysOpt()

    
    def SaveNowChange(self, oDlg):
        self.OnSetShutDown()
        dlgnewsysopt.CloseNewSysOpt()

    
    def CloseOpt(self, oDlg):
        dlgnewsysopt.CloseNewSysOpt()

    
    def CheckShutdownModify(self):
        oView = self.GetView()
        bShutDownList = [
            oView.GetCountDownSelected(),
            oView.GetTimeSelect(),
            oView.GetNoShutDown()]
        return cmp(self.GetModel().GetShutDownList(), bShutDownList) != 0
