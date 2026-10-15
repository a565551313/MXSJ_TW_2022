# pycdc 交叉复核产物 · script.fls entry 1273
# co_filename(原始)='script/mxgame/activity/piaoliuping/dlgseamailtaskitem.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1273.pyc (Python 2.5)

import interface
import combdialog
import ui

class CSeamailTaskItem(combdialog.CCombSubWnd):
    sUIName = 'dialog/activity/activity_return_item.dlg'
    
    def SetData(self, \xdf\xf2\xd5fo):
        self.GetObject('text_rewardnum').SetText('x%s' % \xdf\xf2\xd5fo['iReward'])
        self.GetObject('progress_activity').SetRate(\xdf\xf2\xd5fo['iCur'] * 1000 / \xdf\xf2\xd5fo['iMax'])
        self.GetObject('text_num').SetText('%s/%s' % (\xdf\xf2\xd5fo['iCur'], \xdf\xf2\xd5fo['iMax']))
        self.GetObject('text_target').SetText(\xdf\xf2\xd5fo['sDesc'])
        if \xdf\xf2\xd5fo['tIconPath']:
            self.m_oImg = ui.CImage(self.GetObject('loc_img'), \xdf\xf2\xd5fo['tIconPath'][0], \xdf\xf2\xd5fo['tIconPath'][1])
            interface.Center(self.m_oImg, \xdf\xf2\xd5fo['tIconOffset'][0], \xdf\xf2\xd5fo['tIconOffset'][1])
        else:
            self.m_oImg = None

    
    def LeftDown(self):
        pass

    
    def LeftUp(self):
        pass
