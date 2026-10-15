# pycdc 交叉复核产物 · script.fls entry 178
# co_filename(原始)='script/mxgame/decorate/view/dlgdecoratemain.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_178.pyc (Python 2.5)

'''
# @Time     : 2019/1/8 10:25
# @Author   : huyuhong01
# @File     : dlgdecoratemain.py
# @Explain  : \xb8\xf6\xd0\xd4\xd7\xb0\xca\xce\xcf\xb5\xcd\xb3\xb5\xc4\xd6\xf7\xbd\xe7\xc3\xe6\xc8\xdd\xc6\xf7\xa3\xac\xd6\xf7\xd2\xaa\xb8\xba\xd4\xf0\xd7\xb0\xca\xce\xbd\xe7\xc3\xe6\xd3\xeb\xb6\xd3\xb1\xea\xbd\xe7\xc3\xe6\xb5\xc4\xc7\xd0\xbb\xbb
'''
import combdialog
import dlgdecorate
import mvp
import interface
import popupmgr
import popupdefine
import mdteammark
import dlgnewteammark
import commoncb

def Show():
    import main
    import misc
    import usermacro
    if main.InWar():
        usermacro.PROMPT_MSG('\xbe\xd4\xb0\xab\xa4\xa4\xa4\xa3\xaf\xe0\xa5\xb4\xb6}\xad\xd3\xa9\xca\xb8\xcb\xb9\xa2\xa8t\xb2\xce')
        return None
    
    if misc.IsNationFightServer():
        usermacro.PROMPT_MSG('\xbd\xd0\xa6^\xa8\xec\xad\xec\xaaA\xa8\xcf\xa5\xce\xb8\xd3\xa5\\\xaf\xe0')
        return None
    
    import popupmgr
    import popupdefine
    popupmgr.GetPopupMgr().OpenUI(popupdefine.CDecorateMainDlg, None, [
        0,
        0])


def Close():
    import popupmgr
    import popupdefine
    popupmgr.GetPopupMgr().CloseUI(popupdefine.CDecorateMainDlg)


class CDecorateMainDlg(combdialog.CCombDialog):
    
    def __init__(\x89elf, oParent, iPage, iSubPage):
        combdialog.CCombDialog.__init__(\x89elf, oParent, 'dialog/decorate/decorate_main.dlg')
        \x89elf.m_oDecorateView = None
        \x89elf.m_oTeamMarkView = None
        \x89elf.m_iSubPage = iSubPage
        \x89elf.GetObject('btn_zhuangshi').LeftUp()
        \x89elf.GetObject('btn_zhuangshi').SetShow(False)
        \x89elf.GetObject('btn_duibiao').SetShow(False)
        commoncb.RegistCB(commoncb.WAR_START, \x89elf, 'CloseWindow')

    
    def SwitchView(\x89elf, iViewType):
        if iViewType == 0:
            if \x89elf.m_oTeamMarkView:
                \x89elf.m_oTeamMarkView.SetShow(False)
            
        

    
    def ShowDecoreateView(\x89elf):
        if \x89elf.m_oTeamMarkView:
            \x89elf.m_oTeamMarkView.SetShow(False)
        
        if \x89elf.m_oDecorateView:
            \x89elf.m_oDecorateView.SetShow(True)
        else:
            \x89elf.m_oDecorateView = mvp.OpenView(dlgdecorate.CDecorateDlg, \x89elf, iAlign = interface.ALIGN_LEFT_TOP, iPage = \x89elf.m_iSubPage)

    
    def ShowTeamMarkView(\x89elf):
        if \x89elf.m_oDecorateView:
            \x89elf.m_oDecorateView.SetShow(False)
        
        if \x89elf.m_oTeamMarkView:
            \x89elf.m_oTeamMarkView.SetShow(True)
        else:
            oModel = mvp.GetModel(mdteammark.CTeamMarkModel, True)
            \x89elf.m_oTeamMarkView = dlgnewteammark.CTeamMark(\x89elf, oModel.GetCurrentUserMark(), oModel.GetMarkInfoDict(), oModel.GetUserMarkDayDict())

    
    def ClearSubView(\x89elf):
        if \x89elf.m_oDecorateView:
            \x89elf.m_oDecorateView = None
            mvp.CloseView(dlgdecorate.CDecorateDlg, bDestroyModel = False)
        
        if \x89elf.m_oTeamMarkView:
            \x89elf.m_oTeamMarkView = None
        

    
    def CloseWindow(\x89elf):
        \x89elf.ClearSubView()
        popupmgr.GetPopupMgr().CloseUI(popupdefine.CDecorateMainDlg)
        commoncb.RemoveCB(commoncb.WAR_START, \x89elf, 'CloseWindow')

    
    def OnMessage(\x89elf, iMsgID):
        if iMsgID == 1:
            \x89elf.CloseWindow()
        elif iMsgID == 2:
            pass
        elif iMsgID == 3:
            \x89elf.ShowDecoreateView()
        elif iMsgID == 4:
            \x89elf.ShowTeamMarkView()
