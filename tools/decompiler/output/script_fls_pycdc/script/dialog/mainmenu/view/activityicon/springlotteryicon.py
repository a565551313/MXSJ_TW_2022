# pycdc 交叉复核产物 · script.fls entry 617
# co_filename(原始)='script/dialog/mainmenu/view/activityicon/springlotteryicon.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_617.pyc (Python 2.5)

import activityiconbase
import interface
import net2020springlottery
import netreddot
import ui

class CLotteryIcon(activityiconbase.CActivityIconBase):
    
    def __init__(self, *args):
        activityiconbase.CActivityIconBase.__init__(self, *args)
        self.m_oMyRedPoint = None

    
    def ShowRedPoint(self, bShow):
        if bShow:
            self.m_oMyRedPoint = ui.CImage(self, 'number/0.igs', 'misc')
            self.m_oMyRedPoint.SetZ(100)
            interface.TopRight(self.m_oMyRedPoint)
        else:
            self.m_oMyRedPoint = None

    
    def OnServData(self, extData):
        if extData:
            bRP = extData.get('bRP', None)
            if bRP == 1:
                self.ShowRedPoint(True)
            elif bRP == 0:
                self.ShowRedPoint(False)
            
        

    
    def OnClick(self):
        net2020springlottery.C2GSOpenLotteryDlg()
