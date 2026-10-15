# pycdc 交叉复核产物 · script.fls entry 1077
# co_filename(原始)='script/mxgame/newgroup/delegate/delegategroupmaindlg.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1077.pyc (Python 2.5)

'''
================================================================================
\xd7\xf7\xd5\xdf: hufenlin
\tdelegategroupmaindlg\xa3\xba\xb0\xef\xc5\xc9 \xd6\xf7\xbd\xe7\xc3\xe6\xb4\xfa\xc0\xed
================================================================================
'''
import groupdefines
import groupdelegatebase
import grouppagefactory
import netgroup
import pagedgtbase
import groupsignal

class CDelegateGroupMainDlg(pagedgtbase.CMainPageDlgBase, groupdelegatebase.CDelegateBase):
    
    def __init__(\xb1\xa7lf, pView, pContext, sPageList):
        pagedgtbase.CMainPageDlgBase.__init__(\xb1\xa7lf, pView, sPageList)
        groupdelegatebase.CDelegateBase.__init__(\xb1\xa7lf, pView, pContext)
        \xb1\xa7lf.InitSignal()
        \xb1\xa7lf.InitC2SGet()

    
    def InitSignal(\xb1\xa7lf):
        '''\xb5\xf9\xa5U\xabH\xb8\xb9\xa6^\xbd\xd5 todo
\t\t:return:
\t\t'''
        groupsignal.Connect(groupsignal.SS_RedDotChanged, \xb1\xa7lf.OnRedDotChanged)

    
    def InitC2SGet(\xb1\xa7lf):
        '''
\t\t\xa5\xce\xa9\xf3\xbd\xd0\xa8D\xa4@\xa8\xc7\xa5\xb2\xadn\xaa\xba\xbc\xc6\xbe\xda
\t\t'''
        netgroup.C2SGetBuildData()

    
    def OnRedDotChanged(\xb1\xa7lf, sKey, bRed):
        pView = \xb1\xa7lf.GetView()
        pView.ShowRedPoint(bRed)

    
    def VGetBtnToPageDict(\xb1\xa7lf):
        return {
            'btn_orginfo': groupdefines.E_GROUPPAGE_INFO,
            'btn_apply': groupdefines.E_GROUPPAGE_APPLY,
            'btn_fuli': groupdefines.E_GROUPPAGE_WELFARE,
            'btn_huodong': groupdefines.E_GRPUPPAGE_PLAY }

    
    def VCreateSubPage(\xb1\xa7lf, nPage):
        '''\xb3\xd0\xab\xd8\xa4l\xad\xb6\xc3\xb1\xa1A\xa6\xdb\xa4v\xa9w\xa8\xee'''
        return grouppagefactory.CreateGroupPage(nPage, \xb1\xa7lf.GetView(), \xb1\xa7lf.GetView().GetContext())

    
    def OpenSubPage(\xb1\xa7lf, nPage, dExData = None):
        pagedgtbase.CMainPageDlgBase.OpenSubPage(\xb1\xa7lf, nPage, dExData)
        \xb1\xa7lf.GetView().SetLastOpenPage(nPage)

    
    def VClose(\xb1\xa7lf):
        pPage = \xb1\xa7lf.GetPageDlg().get(\xb1\xa7lf.GetNPage())
        if pPage:
            pPage.VClose()
        
        \xb1\xa7lf.GetView().SetShow(False)
        pContext = \xb1\xa7lf.GetContext()
        pContext.CloseGroupDlg(False)
