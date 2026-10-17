# -*- coding: utf-8 -*-
import delegatebase, explorer, mduieditor, misc, os, widgetconfig, usermacro, commondialog, key, C_sys

class CUIEditorDgt(delegatebase.CDelegateBase):

    def GetView(self):
        '\n\t\t:rtype: dlguieditor.CUIEditorDlg\n\t\t'
        return delegatebase.CDelegateBase.GetView(self)

    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_OpenDlg, self.OnOpenDlg)
        oView.ssConnect(oView.SS_SaveDlg, self.OnSaveDlg)
        oView.ssConnect(oView.SS_NewDlg, self.OnNewDlg)
        oView.ssConnect(oView.SS_4To3, self.On4To3)
        oView.ssConnect(oView.SS_CloseWindow, self.OnCloseWindow)
        Is4To3 = mduieditor.GetUIEditorMgr().Is4To3()
        oView.Set4To3(Is4To3)
        key.RegisterHotKey(key.VK_UP, misc.Functor(self.OnDirChg, 1))
        key.RegisterHotKey(key.VK_DOWN, misc.Functor(self.OnDirChg, -1))
        key.RegisterHotKey(key.VK_LEFT, misc.Functor(self.OnDirChg, 2))
        key.RegisterHotKey(key.VK_RIGHT, misc.Functor(self.OnDirChg, -2))
        key.RegisterHotKey(key.VK_DELETE, misc.Functor(self.OnDelWidget))
        key.RegisterCtrlHotKey(key.VK_S, misc.Functor(self.OnSaveDlg))
        key.RegisterCtrlHotKey(key.VK_Z, misc.Functor(self.OnUndo))
        key.RegisterCtrlHotKey(key.VK_Y, misc.Functor(self.OnRedo))
        key.RegisterCtrlHotKey(key.VK_C, misc.Functor(self.OnCopy))
        key.RegisterCtrlHotKey(key.VK_V, misc.Functor(self.OnPaste))
        return

    def OnUndo(self):
        mduieditor.GetUIEditorMgr().Undo()
        return

    def OnRedo(self):
        mduieditor.GetUIEditorMgr().Redo()
        return

    def OnDirChg(self, iFlag):
        import interface
        oEdit = interface.GetActiveEdit()
        if oEdit and hasattr(oEdit, 'm_AttrEdit') and oEdit.m_AttrEdit:
            return
        oModel = mduieditor.GetUIEditorMgr()
        if not oModel.GetCurUIPath():
            return
        sSelectWidgetList = oModel.GetCurUISelectWidgetList()
        for sWidgetName in sSelectWidgetList:
            dChgInfo = {}
            dWidgetInfo = oModel.GetCurUIWidget(sWidgetName)
            if not dWidgetInfo:
                continue
            bCtrlDown = C_sys.IsKeyDown(key.VK_CTRL)
            if iFlag == 1:
                if bCtrlDown:
                    dChgInfo[widgetconfig.WIDGET_Y_KEY] = dWidgetInfo[widgetconfig.WIDGET_Y_KEY] - 10
                else:
                    dChgInfo[widgetconfig.WIDGET_Y_KEY] = dWidgetInfo[widgetconfig.WIDGET_Y_KEY] - 1
            elif iFlag == -1:
                if bCtrlDown:
                    dChgInfo[widgetconfig.WIDGET_Y_KEY] = dWidgetInfo[widgetconfig.WIDGET_Y_KEY] + 10
                else:
                    dChgInfo[widgetconfig.WIDGET_Y_KEY] = dWidgetInfo[widgetconfig.WIDGET_Y_KEY] + 1
            elif iFlag == 2:
                if bCtrlDown:
                    dChgInfo[widgetconfig.WIDGET_X_KEY] = dWidgetInfo[widgetconfig.WIDGET_X_KEY] - 10
                else:
                    dChgInfo[widgetconfig.WIDGET_X_KEY] = dWidgetInfo[widgetconfig.WIDGET_X_KEY] - 1
            elif iFlag == -2:
                if bCtrlDown:
                    dChgInfo[widgetconfig.WIDGET_X_KEY] = dWidgetInfo[widgetconfig.WIDGET_X_KEY] + 10
                else:
                    dChgInfo[widgetconfig.WIDGET_X_KEY] = dWidgetInfo[widgetconfig.WIDGET_X_KEY] + 1
            if dChgInfo:
                oModel.UpdateWidget(sWidgetName, dChgInfo)

        return

    def OnDelWidget(self):
        oModel = mduieditor.GetUIEditorMgr()
        if not oModel.GetCurUIPath():
            return
        import interface
        oEdit = interface.GetActiveEdit()
        if oEdit and hasattr(oEdit, 'm_AttrEdit') and oEdit.m_AttrEdit:
            return
        sSelectWidgetList = oModel.GetCurUISelectWidgetList()
        for sWidgetName in sSelectWidgetList:
            oModel.DelWidget(sWidgetName)

        return

    def OnOpenDlg(self):
        if self.IsCurUIChg():
            commondialog.ShowMessageBox('\xa5\xb4\xb6}\xac\xc9\xad\xb1\xb3Q\xad\xd7\xa7\xef\xa4F\xa1A\xacO\xa7_\xa9\xf1\xb1\xf3\xabO\xa6s\xa5\xb4\xb6}\xb7s\xac\xc9\xad\xb1', ('\xacO',
                                                                                                                                                                                '\xa7_'), (misc.Functor(self.OpenExplorer), None))
            return
        self.OpenExplorer()
        return

    def IsCurUIChg(self):
        oModel = mduieditor.GetUIEditorMgr()
        sCurUIPath = oModel.GetCurUIPath()
        if sCurUIPath:
            dWidgetList = oModel.ReadFromFile(sCurUIPath)
            return dWidgetList != oModel.GetCurUIWidgetList()
        return False

    def OpenExplorer(self, *args):
        oExplorer = explorer.ShowExplorer()
        oExplorer.Create(self.GetFileInfo(), misc.Functor(self.OnExporterCB), explorer.FILTER_TYPE_EXT, ['.dlg'], mduieditor.GetUIEditorMgr().GetLastSelectUIPath())
        return

    def OnExporterCB(self, sSelectPath):
        mduieditor.GetUIEditorMgr().CloseUI(mduieditor.GetUIEditorMgr().GetCurUIPath())
        sSelectPath = sSelectPath.replace('\\', '/')[2:]
        mduieditor.GetUIEditorMgr().SetsCurUIPath(sSelectPath)
        mduieditor.GetUIEditorMgr().SetLastSelectUIPath(sSelectPath)
        import editorcommand
        editorcommand.ResetCommandDataMgr()
        return

    def OnSaveDlg(self):
        (iFlag, sTips) = mduieditor.GetUIEditorMgr().SaveCurFile(mduieditor.GetUIEditorMgr().GetCurUIPath())
        if iFlag:
            usermacro.PROMPT_MSG('\xabO\xa6s\xa6\xa8\xa5\\')
        else:
            usermacro.PROMPT_MSG('\xabO\xa6s\xa5\xa2\xb1\xd1, %s' % sTips)
        return

    def OnNewDlg(self):
        sCwdPath = os.getcwd()
        sInterfacePath = os.path.join(sCwdPath, 'interface')
        if not os.path.exists(sInterfacePath):
            try:
                os.mkdir(sInterfacePath)
            except:
                return

        sInterfacePath = os.path.join(sInterfacePath, 'dialog4')
        if not os.path.exists(sInterfacePath):
            try:
                os.mkdir(sInterfacePath)
            except:
                return

        import time
        sPath = '%d.dlg' % int(time.time())
        sFullPath = os.path.join(sInterfacePath, sPath)
        try:
            f = open(sFullPath, 'w')
            f.write('# -*- coding: gbk -*-\n')
            f.write('# MD5: 12345678901234567890123456789012\n\n')
            f.write('UI_INFO = []')
            f.close()
        except:
            return

        usermacro.PROMPT_MSG('\xb7s\xab\xd8\xa4\xe5\xa5\xf3\xa6\xa8\xa5\\\xa1A\xa4\xe5\xa5\xf3\xabO\xa6s\xa6b:%s' % sFullPath)
        if self.IsCurUIChg():
            commondialog.ShowMessageBox('\xa5\xb4\xb6}\xac\xc9\xad\xb1\xb3Q\xad\xd7\xa7\xef\xa4F\xa1A\xacO\xa7_\xa9\xf1\xb1\xf3\xabO\xa6s\xa5\xb4\xb6}\xb7s\xac\xc9\xad\xb1', ('\xacO',
                                                                                                                                                                                '\xa7_'), (misc.Functor(self._OpenNewDlg, sPath), None))
        else:
            self._OpenNewDlg(sPath)
        return

    def On4To3(self, bSet):
        mduieditor.GetUIEditorMgr().Set4To3(bSet)
        return

    def OnCloseWindow(self):
        mduieditor.CloseUIEditor()
        return

    def _OpenNewDlg(self, sPath, *args):
        mduieditor.GetUIEditorMgr().CloseUI(mduieditor.GetUIEditorMgr().GetCurUIPath())
        mduieditor.GetUIEditorMgr().SetsCurUIPath(sPath.replace('\\', '/'))
        return

    def GetFileInfo(self):
        return self.GetTmpFileInfo()

    def GetTmpFileInfo(self):
        sPath = '.\\interface'
        dResult = {}
        for (sRoot, sDirList, sFileList) in os.walk(sPath):
            if sRoot == sPath:
                sCurPath = '.'
            else:
                sCurPath = '.\\' + sRoot[len(sPath) + 1:]
            dResult[sCurPath] = {}
            dResult[sCurPath]['sFileList'] = sFileList[:]
            dResult[sCurPath]['sDirList'] = sDirList[:]

        return dResult

    def CombineFileInfo(self, dFileInfo, dFileExInfo):
        for (sExPath, dExInfo) in dFileExInfo.items():
            if sExPath not in dFileInfo:
                dFileInfo[sExPath] = dExInfo
            else:
                for sFile in dExInfo['sFileList']:
                    if sFile not in dFileInfo[sExPath]['sFileList']:
                        dFileInfo[sExPath]['sFileList'].append(sFile)

                for sDIr in dExInfo['sDirList']:
                    if sDIr not in dFileInfo[sExPath]['sDirList']:
                        dFileInfo[sExPath]['sDirList'].append(sDIr)

        return dFileInfo

    def OnCopy(self):
        mduieditor.GetUIEditorMgr().CopyCurSelectWidget()
        return

    def OnPaste(self):
        oEditorMgr = mduieditor.GetUIEditorMgr()
        dCopyWidgetList = oEditorMgr.GetCopyWidgetList()
        while dCopyWidgetList:
            dCopyWidget = dCopyWidgetList.pop(0)
            dCurWidgetList = oEditorMgr.GetCurUIWidgetList()
            sWidgetName = oEditorMgr.FixWidget(dCurWidgetList, dCopyWidget)
            dCopyWidget[widgetconfig.WIDGET_NAME_KEY] = sWidgetName
            oEditorMgr.AddCopyWidget(dCopyWidget)

        return


class CPreviewDgt(delegatebase.CDelegateBase):

    def GetView(self):
        '\n\t\t:rtype: dlguieditor.CPreviewDlg\n\t\t'
        return delegatebase.CDelegateBase.GetView(self)

    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickItem, self.OnClickItem)
        oView.ssConnect(oView.SS_AlignHCenter, self.OnAlignHCenter)
        oView.ssConnect(oView.SS_AlignVCenter, self.OnAlignVCenter)
        oView.ssConnect(oView.SS_AlignLeft, self.OnAlignLeft)
        oView.ssConnect(oView.SS_AlignUp, self.OnAlignUp)
        oView.ssConnect(oView.SS_AlignRight, self.OnAlignRight)
        oView.ssConnect(oView.SS_AlignBotton, self.OnAlignBotton)
        oView.ssConnect(oView.SS_AlignHSpace, self.OnAlignHSpace)
        oView.ssConnect(oView.SS_AlignVSpace, self.OnAlignVSpace)
        oModel = mduieditor.GetUIEditorMgr()
        oModel.ssConnect(oModel.SS_ClickWidget, self.OnClickWidget)
        oModel.ssConnect(oModel.SS_UpdateWidget, self.OnUpdateWidget)
        oModel.ssConnect(oModel.SS_UpdateWidgetZ, self.OnUpdateWidgetZ)
        oModel.ssConnect(oModel.SS_AddWidget, self.OnAddWidget)
        oModel.ssConnect(oModel.SS_DelWidget, self.OnDelWidget)
        oModel.ssConnect(oModel.SS_CurUIChg, self.OnCurUIChg)
        return

    def GetAllSelectWidgetInfoList(self):
        oModel = mduieditor.GetUIEditorMgr()
        if not oModel.GetCurUIPath():
            return []
        sSelectWidgetList = oModel.GetCurUISelectWidgetList()
        dWidgetInfoList = []
        for sWidgetName in sSelectWidgetList:
            dWidgetInfoList.append(misc.DeepCopy(oModel.GetCurUIWidget(sWidgetName)))

        return dWidgetInfoList

    def OnAlignHCenter(self):
        oModel = mduieditor.GetUIEditorMgr()
        oView = self.GetView()
        dWidgetInfoList = self.GetAllSelectWidgetInfoList()
        if not dWidgetInfoList:
            return
        if len(dWidgetInfoList) == 1:
            dWidgetInfo = dWidgetInfoList[0]
            sWidgetName = dWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
            oWidget = oView.GetRealDlgObject(sWidgetName)
            oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_X_KEY): (400 - oWidget.GetSize()[0] / 2)})
        else:
            dWidgetInfo = dWidgetInfoList[0]
            sWidgetName = dWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
            oWidget = oView.GetRealDlgObject(sWidgetName)
            iCenterX = dWidgetInfo[widgetconfig.WIDGET_X_KEY] + oWidget.GetSize()[0] / 2
            for dOtherWidgetInfo in dWidgetInfoList[1:]:
                sWidgetName = dOtherWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
                oWidget = oView.GetRealDlgObject(sWidgetName)
                oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_X_KEY): (iCenterX - oWidget.GetSize()[0] / 2)})

        return

    def OnAlignVCenter(self):
        oModel = mduieditor.GetUIEditorMgr()
        oView = self.GetView()
        dWidgetInfoList = self.GetAllSelectWidgetInfoList()
        if not dWidgetInfoList:
            return
        if len(dWidgetInfoList) == 1:
            dWidgetInfo = dWidgetInfoList[0]
            sWidgetName = dWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
            oWidget = oView.GetRealDlgObject(sWidgetName)
            oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_Y_KEY): (300 - oWidget.GetSize()[1] / 2)})
        else:
            dWidgetInfo = dWidgetInfoList[0]
            sWidgetName = dWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
            oWidget = oView.GetRealDlgObject(sWidgetName)
            iCenterY = dWidgetInfo[widgetconfig.WIDGET_Y_KEY] + oWidget.GetSize()[1] / 2
            for dOtherWidgetInfo in dWidgetInfoList[1:]:
                sWidgetName = dOtherWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
                oWidget = oView.GetRealDlgObject(sWidgetName)
                oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_Y_KEY): (iCenterY - oWidget.GetSize()[1] / 2)})

        return

    def OnAlignLeft(self):
        oModel = mduieditor.GetUIEditorMgr()
        dWidgetInfoList = self.GetAllSelectWidgetInfoList()
        if not dWidgetInfoList:
            return
        if len(dWidgetInfoList) == 1:
            dWidgetInfo = dWidgetInfoList[0]
            sWidgetName = dWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
            oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_X_KEY): 0})
        else:
            dWidgetInfo = dWidgetInfoList[0]
            iX = dWidgetInfo[widgetconfig.WIDGET_X_KEY]
            for dOtherWidgetInfo in dWidgetInfoList[1:]:
                sWidgetName = dOtherWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
                oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_X_KEY): iX})

        return

    def OnAlignUp(self):
        oModel = mduieditor.GetUIEditorMgr()
        dWidgetInfoList = self.GetAllSelectWidgetInfoList()
        if not dWidgetInfoList:
            return
        if len(dWidgetInfoList) == 1:
            dWidgetInfo = dWidgetInfoList[0]
            sWidgetName = dWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
            oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_Y_KEY): 0})
        else:
            dWidgetInfo = dWidgetInfoList[0]
            iY = dWidgetInfo[widgetconfig.WIDGET_Y_KEY]
            for dOtherWidgetInfo in dWidgetInfoList[1:]:
                sWidgetName = dOtherWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
                oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_Y_KEY): iY})

        return

    def OnAlignRight(self):
        oModel = mduieditor.GetUIEditorMgr()
        oView = self.GetView()
        dWidgetInfoList = self.GetAllSelectWidgetInfoList()
        if not dWidgetInfoList:
            return
        if len(dWidgetInfoList) == 1:
            dWidgetInfo = dWidgetInfoList[0]
            sWidgetName = dWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
            oWidget = oView.GetRealDlgObject(sWidgetName)
            oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_X_KEY): (800 - oWidget.GetSize()[0])})
        else:
            dWidgetInfo = dWidgetInfoList[0]
            sWidgetName = dWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
            oWidget = oView.GetRealDlgObject(sWidgetName)
            iRightX = dWidgetInfo[widgetconfig.WIDGET_X_KEY] + oWidget.GetSize()[0]
            for dOtherWidgetInfo in dWidgetInfoList[1:]:
                sWidgetName = dOtherWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
                oWidget = oView.GetRealDlgObject(sWidgetName)
                oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_X_KEY): (iRightX - oWidget.GetSize()[0])})

        return

    def OnAlignBotton(self):
        oModel = mduieditor.GetUIEditorMgr()
        oView = self.GetView()
        dWidgetInfoList = self.GetAllSelectWidgetInfoList()
        if not dWidgetInfoList:
            return
        if len(dWidgetInfoList) == 1:
            dWidgetInfo = dWidgetInfoList[0]
            sWidgetName = dWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
            oWidget = oView.GetRealDlgObject(sWidgetName)
            oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_Y_KEY): (600 - oWidget.GetSize()[1])})
        else:
            dWidgetInfo = dWidgetInfoList[0]
            sWidgetName = dWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
            oWidget = oView.GetRealDlgObject(sWidgetName)
            iBottonY = dWidgetInfo[widgetconfig.WIDGET_Y_KEY] + oWidget.GetSize()[1]
            for dOtherWidgetInfo in dWidgetInfoList[1:]:
                sWidgetName = dOtherWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
                oWidget = oView.GetRealDlgObject(sWidgetName)
                oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_Y_KEY): (iBottonY - oWidget.GetSize()[1])})

        return

    def OnAlignHSpace(self):
        oModel = mduieditor.GetUIEditorMgr()
        dWidgetInfoList = self.GetAllSelectWidgetInfoList()
        if len(dWidgetInfoList) < 3:
            return
        dWidgetInfoLeft = dWidgetInfoList[0]
        dWidgetInfoRight = dWidgetInfoList[-1]
        iStartX = dWidgetInfoLeft[widgetconfig.WIDGET_X_KEY]
        iStepX = (dWidgetInfoRight[widgetconfig.WIDGET_X_KEY] - iStartX) / (len(dWidgetInfoList) - 1)
        for dOtherWidgetInfo in dWidgetInfoList[1:-1]:
            sWidgetName = dOtherWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
            oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_X_KEY): (iStartX + iStepX)})
            iStartX += iStepX

        return

    def OnAlignVSpace(self):
        oModel = mduieditor.GetUIEditorMgr()
        dWidgetInfoList = self.GetAllSelectWidgetInfoList()
        if len(dWidgetInfoList) < 3:
            return
        dWidgetInfoLeft = dWidgetInfoList[0]
        dWidgetInfoRight = dWidgetInfoList[-1]
        iStartY = dWidgetInfoLeft[widgetconfig.WIDGET_Y_KEY]
        iStepY = (dWidgetInfoRight[widgetconfig.WIDGET_Y_KEY] - iStartY) / (len(dWidgetInfoList) - 1)
        for dOtherWidgetInfo in dWidgetInfoList[1:-1]:
            sWidgetName = dOtherWidgetInfo[widgetconfig.WIDGET_NAME_KEY]
            oModel.UpdateWidget(sWidgetName, {(widgetconfig.WIDGET_Y_KEY): (iStartY + iStepY)})
            iStartY += iStepY

        return

    def OnClickItem(self, sWidgetName):
        mduieditor.GetUIEditorMgr().ClickWidget(sWidgetName)
        return

    def OnClickWidget(self, sWidgetName, bSelect):
        self.GetView().SetItemSelect(mduieditor.GetUIEditorMgr().GetCurUISelectWidgetList())
        return

    def OnUpdateWidget(self, sWidgetName, dWidgetInfo):
        if not dWidgetInfo:
            return
        oWidget = self.GetView().GetRealDlgObject(sWidgetName)
        if not oWidget:
            return
        iNotReCreateKeyList = [widgetconfig.WIDGET_Y_KEY, widgetconfig.WIDGET_X_KEY]
        for sAttrKey in dWidgetInfo.keys():
            if sAttrKey not in iNotReCreateKeyList:
                dWidgetList = mduieditor.GetUIEditorMgr().GetCurUIWidgetList()
                sSelectWidgetList = mduieditor.GetUIEditorMgr().GetCurUISelectWidgetList()
                self.GetView().RefreshDlg(dWidgetList, sSelectWidgetList)
                return

        tOrgPos = oWidget.GetPos()
        x = dWidgetInfo.get(widgetconfig.WIDGET_X_KEY, tOrgPos[0])
        y = dWidgetInfo.get(widgetconfig.WIDGET_Y_KEY, tOrgPos[1])
        oWidget.SetPos(x, y)
        return

    def OnUpdateWidgetZ(self, sWidgetName, z):
        self.RefreshAllWidgetZ()
        return

    def OnAddWidget(self, dWidgetInfo):
        self.GetView().AddWidget(dWidgetInfo)
        self.RefreshAllWidgetZ()
        return

    def OnDelWidget(self, sWidgetName):
        self.GetView().DelWidget(sWidgetName)
        self.RefreshAllWidgetZ()
        return

    def OnCurUIChg(self, sUIPath):
        dWidgetList = mduieditor.GetUIEditorMgr().GetCurUIWidgetList()
        sSelectWidgetList = mduieditor.GetUIEditorMgr().GetCurUISelectWidgetList()
        self.GetView().RefreshDlg(dWidgetList, sSelectWidgetList)
        return

    def RefreshAllWidgetZ(self):
        dWidgetList = mduieditor.GetUIEditorMgr().GetCurUIWidgetList()
        dZInfo = {}
        iTotalNum = len(dWidgetList)
        for dUIInfo in dWidgetList:
            self.CalculationZ(dUIInfo, dZInfo, -iTotalNum)
            iTotalNum -= 1

        self.GetView().RefreshAllWidgetZ(dZInfo)
        return

    def CalculationZ(self, dUIInfo, dZInfo, z):
        if not dUIInfo['bLoad']:
            return
        dZInfo[dUIInfo[widgetconfig.WIDGET_NAME_KEY]] = z
        dChildrenList = dUIInfo['lChildren']
        if dChildrenList:
            iTotalNum = len(dChildrenList)
            for dChildUIInfo in dChildrenList:
                self.CalculationZ(dChildUIInfo, dZInfo, -iTotalNum)
                iTotalNum -= 1

        return


class CWidgetListDgt(delegatebase.CDelegateBase):

    def GetView(self):
        '\n\t\t:rtype: dlguieditor.CWidgetListDlg\n\t\t'
        return delegatebase.CDelegateBase.GetView(self)

    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_AddWidget, self.OnAddWidget)
        oView.CreateWidgetList(widgetconfig.WIDGET_KEY_LIST)
        return

    def OnAddWidget(self, sWidgetType):
        mduieditor.GetUIEditorMgr().AddWidget(sWidgetType)
        return


class CAttrListDgt(delegatebase.CDelegateBase):

    def __init__(self, oView):
        delegatebase.CDelegateBase.__init__(self, oView)
        self.m_sWidgetName = ''
        self.JxCOrgWidgetInfo = None
        return

    def Init(self):
        oModel = mduieditor.GetUIEditorMgr()
        oModel.ssConnect(oModel.SS_ClickWidget, self.OnRefresh)
        oModel.ssConnect(oModel.SS_UpdateWidget, self.OnRefresh)
        oModel.ssConnect(oModel.SS_UpdateWidgetErr, self.OnUpdateWidgetErr)
        oModel.ssConnect(oModel.SS_DelWidget, self.OnRefresh)
        oModel.ssConnect(oModel.SS_CurUIChg, self.OnRefresh)
        oView = self.GetView()
        oView.ssConnect(oView.SS_ZChange, self.OnZChange)
        oView.ssConnect(oView.SS_AttrValueChange, self.OnAttrValueChange)
        return

    def OnUpdateWidgetErr(self, sWidgetName, iErrCode):
        if sWidgetName != self.m_sWidgetName:
            return
        sTips = ''
        if iErrCode & widgetconfig.WIDGET_UPDATE_ERR_NAME:
            sTips = '\xc4\xdd\xa9\xca\xa7\xf3\xb7s\xbf\xf9\xbb~\xa1G\xb1\xb1\xa5\xf3\xa6W\xad\xab\xbd\xc6'
        if not sTips:
            sTips = '\xc4\xdd\xa9\xca\xa7\xf3\xb7s\xbf\xf9\xbb~\xa1G\xbf\xf9\xbb~\xbdX%d' % iErrCode
        usermacro.PROMPT_MSG(sTips)
        self.OnRefresh()
        return

    def OnZChange(self, bUp):
        iZ = 1 if bUp else -1
        mduieditor.GetUIEditorMgr().UpdateWidgetZ(self.m_sWidgetName, iZ)
        return

    def OnAttrValueChange(self):
        oModel = mduieditor.GetUIEditorMgr()
        dCurWidgetInfo = self.GetView().GetCurWidgetInfo()
        dChangeInfo = {}
        for (sAttrKey, oValue) in dCurWidgetInfo.items():
            if oValue != self.JxCOrgWidgetInfo[sAttrKey]:
                dChangeInfo[sAttrKey] = oValue

        if self.JxCOrgWidgetInfo[widgetconfig.WIDGET_TYPE_KEY] in ('CTable', 'CPngTable'):
            if 'sTitles' in dChangeInfo or 'lSubWidth' in dChangeInfo:
                sTitles = dCurWidgetInfo['sTitles']
                if sTitles.endswith('\\n'):
                    sTitles = sTitles[:-2]
                sTitleList = sTitles.split('\\n')
                iSubWidth = dCurWidgetInfo['lSubWidth']
                if len(sTitleList) != len(iSubWidth):
                    usermacro.PROMPT_MSG('\xaa\xed\xc0Y\xbbP\xa6C\xbce\xaa\xba\xbc\xc6\xb6q\xadn\xa4@\xadP\xa1A\xbd\xd0\xc0\xcb\xacd')
                    return
                if 'lSubWidth' in dChangeInfo and 'iWidth' not in dChangeInfo:
                    dChangeInfo['iWidth'] = sum(dChangeInfo['lSubWidth']) + 15
        if self.JxCOrgWidgetInfo[widgetconfig.WIDGET_TYPE_KEY] in ('CButton', 'CTextButton',
                                                                   'CHPageButton',
                                                                   'CHPagePngButton',
                                                                   'CVPageButton',
                                                                   'CVPagePngButton'):
            if 'lRelationName' in dChangeInfo:
                dChangeInfo['iRelationNum'] = len(dChangeInfo['lRelationName'])
        LOG('\xc4\xdd\xa9\xca\xad\xd7\xa7\xef', dChangeInfo)
        oModel.UpdateWidget(self.m_sWidgetName, dChangeInfo)
        return

    def OnRefresh(self, *args):
        self.m_sWidgetName = ''
        self.GetView().ClearAttrPanel()
        sSelectWidgetList = mduieditor.GetUIEditorMgr().GetCurUISelectWidgetList()
        if len(sSelectWidgetList) == 1:
            self.m_sWidgetName = sSelectWidgetList[0]
            dWidgetInfo = mduieditor.GetUIEditorMgr().GetCurUIWidget(self.m_sWidgetName)
            self.JxCOrgWidgetInfo = misc.DeepCopy(dWidgetInfo)
            self.GetView().RefreshAttrPanel(dWidgetInfo, widgetconfig.GetWidgetAttrConfig(dWidgetInfo[widgetconfig.WIDGET_TYPE_KEY]))
        return


class CNodeListDgt(delegatebase.CDelegateBase):

    def GetView(self):
        '\n\t\t:rtype: dlguieditor.CNodeListDlg\n\t\t'
        return delegatebase.CDelegateBase.GetView(self)

    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickItem, self.OnClickItem)
        oModel = mduieditor.GetUIEditorMgr()
        oModel.ssConnect(oModel.SS_AddWidget, self.OnRefresh)
        oModel.ssConnect(oModel.SS_DelWidget, self.OnRefresh)
        oModel.ssConnect(oModel.SS_UpdateWidget, self.OnRefresh)
        oModel.ssConnect(oModel.SS_CurUIChg, self.OnRefresh)
        oModel.ssConnect(oModel.SS_UpdateWidgetZ, self.OnRefresh)
        oModel.ssConnect(oModel.SS_ClickWidget, self.OnClickWidget)
        return

    def OnClickItem(self, sWidgetName):
        mduieditor.GetUIEditorMgr().ClickWidget(sWidgetName)
        return

    def OnRefresh(self, *args):
        oModel = mduieditor.GetUIEditorMgr()
        dWidgetList = oModel.GetCurUIWidgetList()
        sWidgetSelectList = oModel.GetCurUISelectWidgetList()
        self.GetView().RefreshList(dWidgetList, sWidgetSelectList)
        return

    def OnClickWidget(self, sWidgetName, bSelect):
        sWidgetSelectList = mduieditor.GetUIEditorMgr().GetCurUISelectWidgetList()
        self.GetView().SetItemSelect(sWidgetSelectList)
        return
