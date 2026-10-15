# pycdc 交叉复核产物 · script.fls entry 3896
# co_filename(原始)='script/mxgame/newgroup/delegate/delegateapply/delegategrouprecommendfriend.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3896.pyc (Python 2.5)

'''
delegategrouprecommendfriend.py
create by xian90 2019/5/21 17:35
\xc4\xa3\xbf\xe9\xb9\xa6\xc4\xdc\xcb\xb5\xc3\xf7:
'''
import groupdelegatebase
import interface
import friend

class CDelegateGroupRecommendFriend(groupdelegatebase.CDelegateBase):
    
    def __init__(self, pView, pContext):
        groupdelegatebase.CDelegateBase.__init__(self, pView, pContext)
        self.InitSignal()

    
    def InitSignal(self):
        '''\xb5\xf9\xa5U\xabH\xb8\xb9\xa6^\xbd\xd5
\t\t:return:
\t\t'''
        oView = self.GetView()
        oView.ssConnect(oView.SS_DialogOpenFinish, self.OnDialogOpenFinish)
        oView.ssConnect(oView.SS_ClickCloseBtn, self.OnDialogClose)
        oView.ssConnect(oView.SS_UpdateTJFriendName, self.OnUpdateTJFriendName)

    
    def OnDialogOpenFinish(self):
        LOG_DEBUG('--------\xb1M"\x7f)\xc7M=\xa12b3Q+\xe3)@!D <(9;\xf0*4+%--------')
        vList = friend.GetFrdMgr().GetList()
        vList.sort(key = (lambda iFriendId: None if friend.IsOnline(iFriendId) else 1))
        vData = []
        for iFriendId in vList:
            sName = friend.GetAttrValue(iFriendId, 'm_Name', '%d' % iFriendId)
            bOnLine = friend.IsOnline(iFriendId)
            vData.append((iFriendId, sName, bOnLine))
        
        oView = self.GetView()
        oView.InitFriendLst(vData)

    
    def OnUpdateTJFriendName(self, iFriendId, sName):
        
        try:
            None(LOG_DEBUG, '--------\xb1\xc0\xaf\xf2\xa4J\xc0\xb0\xa1A\xbf\xef\xbe\xdc\xa6n\xa4\xcd\xac\xc9\xad\xb1\xbf\xef\xbe\xdc\xa4F\xacY\xad\xd3\xa6n\xa4\xcd--------', iFriendId)
            import groupsignal
            groupsignal.Emit(groupsignal.SS_UpdateTjMemberName, iFriendId, sName)
            return None


    
    def OnDialogClose(self):
        LOG_DEBUG('--------\xb1\xc0\xaf\xf2\xa4J\xc0\xb0\xa1A\xbf\xef\xbe\xdc\xa6n\xa4\xcd\xac\xc9\xad\xb1\xc3\xf6\xb3\xac--------')
        self.GetContext().CloseGroupRecommendFriendDlg()
