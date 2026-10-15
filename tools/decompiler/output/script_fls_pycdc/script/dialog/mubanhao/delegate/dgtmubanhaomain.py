# pycdc 交叉复核产物 · script.fls entry 4606
# co_filename(原始)='script/dialog/mubanhao/delegate/dgtmubanhaomain.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4606.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/4/12 15:01
\xd7\xf7\xd5\xdf: lzj
\xce\xc4\xbc\xfe: dgtmubanhaomain
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import delegatebase
import mgrmubanhao
import misc
import mubanhaodefines
import mubanhaodata

class CMubanhaoMainDgt(delegatebase.CDelegateBase):
    
    def Init(self):
        self.RefreshTbView()
        self.InitSubDialog()
        self.EditInit()
        self.RefreshFirstPage()

    
    def EditInit(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_MainBtnSelect, self.MainBtnSelect)
        oView.ssConnect(oView.SS_ChildBtnSelect, self.ChildBtnSelect)
        oView.ssConnect(oView.SS_MainSpecialBtn, self.OnSpecialBtnSelect)

    
    def RefreshFirstPage(self):
        iLastPage = self.GetModel().GetLastPage()
        self.OnPageMsg(iLastPage)

    
    def MainBtnSelect(self, sBtnName):
        oModel = self.GetModel()
        if oModel.GetMainBtnName() == sBtnName:
            oModel.SetMainBtnName('')
        else:
            oModel.SetMainBtnName(sBtnName)
        self.RefreshTbView()

    
    def ChildBtnSelect(self, iMsg):
        oModel = self.GetModel()
        oModel.SetSelPage(iMsg)
        oModel.SetLastPage(iMsg)
        self.RefreshTbView()
        self.OnPageMsg(iMsg)

    
    def OnSpecialBtnSelect(self, sBtnName):
        oModel = self.GetModel()
        if oModel.GetMainBtnName() == sBtnName:
            return None
        
        oModel.SetMainBtnName(sBtnName)
        self.ChildBtnSelect(mubanhaodata.GetFirstBtnMsg(sBtnName))
        self.RefreshTbView()

    
    def RefreshTbView(self):
        sBtnList = []
        oModel = self.GetModel()
        for sName in mubanhaodata.GetNameData():
            bSpecial = mubanhaodata.IsSpecialMainBtn(sName)
            if sName != self.GetModel().GetMainBtnName():
                sBtnList.append({
                    'sName': sName,
                    'bMainBtn': True,
                    'bSelect': False,
                    'bSpecial': bSpecial })
                continue
            else:
                sBtnList.append({
                    'sName': sName,
                    'bMainBtn': True,
                    'bSelect': True,
                    'bSpecial': bSpecial })
                if bSpecial:
                    continue
                
            for dData in mubanhaodata.GetData()[sName]:
                dCopyData = misc.DeepCopy(dData)
                dCopyData['bMainBtn'] = False
                if dData['iMsg'] == oModel.GetSelPage():
                    dCopyData['bSelect'] = False
                else:
                    dCopyData['bSelect'] = True
                sBtnList.append(dCopyData)
            
        
        self.GetView().RefreshChooseTbView(sBtnList)

    
    def InitSubDialog(self):
        import dlgshuxingpage
        import dlgskillpage
        import dlgtrickpage
        import dlgequippage
        self.m_BuildFunc = {
            mubanhaodefines.PAGE_SHUXING: dlgshuxingpage.BuildSubWnd,
            mubanhaodefines.PAGE_SKILL: dlgskillpage.BuildSubWnd,
            mubanhaodefines.PAGE_XINFA: dlgtrickpage.BuildSubWnd,
            mubanhaodefines.PAGE_EQUIP: dlgequippage.BuildSubWnd }
        self.m_SubDialogs = { }

    
    def OnPageMsg(self, iMsg, dExData = None):
        for oDialog in self.m_SubDialogs.values():
            oDialog.SetActive(False)
        
        if iMsg not in self.m_SubDialogs:
            if iMsg not in self.m_BuildFunc:
                return None
            
            self.m_SubDialogs[iMsg] = self.m_BuildFunc[iMsg](self.GetView().GetSubLoc())
            if self.m_SubDialogs[iMsg]:
                \xc4\xe7\xc4\xc8 = self.GetView().GetSubLoc()
                self.m_SubDialogs[iMsg].SetZ(\xc4\xe7\xc4\xc8.GetZ())
                self.m_SubDialogs[iMsg].SetPos(0, 0)
            
        else:
            self.m_SubDialogs[iMsg].SetActive(True)

    
    def GetModel(self):
        return mgrmubanhao.GetMubanhaoMgr()
