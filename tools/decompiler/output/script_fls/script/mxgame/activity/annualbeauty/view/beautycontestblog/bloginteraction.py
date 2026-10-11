# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\mxgame\activity\annualbeauty\view\beautycontestblog\bloginteraction.py
import bloginteractiondispatcher

class CBlogInteraction(object):

    def __init__(self, sDispatcherName):
        self.m_sServId = 0
        self.m_iPid = 0
        self.m_iWbId = 0
        self.m_sDispatcherName = sDispatcherName
        return

    def SetBlogInfo(self, sServId, iPid, iWbId):
        self.m_sServId = sServId
        self.m_iPid = iPid
        self.m_iWbId = iWbId
        return

    def OnClickZanBtn(self):
        r"""\xc2I\xc3٫\xf6\xb6s"""
        bloginteractiondispatcher.GetInstance(self.m_sDispatcherName).ssEmit(bloginteractiondispatcher.SS_ClickZanBtn, self.m_sServId, self.m_iPid, self.m_iWbId)
        return

    def OnClickReviewBtn(self):
        """\\xc2I\\xc0\\xbb\\xb5\\xfb\\xbd\u05eb\\xf6\\xb6s"""
        bloginteractiondispatcher.GetInstance(self.m_sDispatcherName).ssEmit(bloginteractiondispatcher.SS_ClickReviewBtn, self.m_sServId, self.m_iPid, self.m_iWbId)
        return

    def OnDeleteBlog(self):
        r"""\xc2I\xc0\xbb\xa7R\xb0\xa3\xb7L\xb3\xd5"""
        bloginteractiondispatcher.GetInstance(self.m_sDispatcherName).ssEmit(bloginteractiondispatcher.SS_ClickDelBlogBtn, self.m_sServId, self.m_iPid, self.m_iWbId)
        return

    def OnReportClick(self):
        r"""\xc2I\xc0\xbb\xc1|\xb3\xf8"""
        bloginteractiondispatcher.GetInstance(self.m_sDispatcherName).ssEmit(bloginteractiondispatcher.SS_ClickReportClick, self.m_sServId, self.m_iPid, self.m_iWbId)
        return


return
