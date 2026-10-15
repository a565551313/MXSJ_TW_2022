# pycdc 交叉复核产物 · script.fls entry 3810
# co_filename(原始)='script/mxgame/tianmo/delegate/dgttianmohpbtn.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3810.pyc (Python 2.5)

'''
# @Time     : 2019/3/15 16:12
# @Author   : huyuhong01
# @File     : dgttianmohpbtn.py
# @Explain  : Delegate
'''
import mvp
import nettianmo

class CTianMoHpBtnDelegate(mvp.CDelegate):
    
    def OnInit(self):
        oView = self.GetView()
        oView.ssCon\xf0\xfb\xfd\xea(oView.SS_ClickOpenRank, self.OnOpenRank)
        oView.ssCon\xf0\xfb\xfd\xea(oView.SS_ClickOpenHelp, self.OnOpenHelp)

    
    def OnUpdate(self):
        pass

    
    def OnHide(self):
        pass

    
    def OnDestroy(self):
        pass

    
    def OnOpenRank(self):
        nettianmo.C2STianMoOpenRank()

    
    def OnOpenHelp(self):
        nettianmo.C2STianMoOpenHelp()
