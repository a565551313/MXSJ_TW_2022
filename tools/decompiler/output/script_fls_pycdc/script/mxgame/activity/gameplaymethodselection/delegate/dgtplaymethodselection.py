# pycdc 交叉复核产物 · script.fls entry 2164
# co_filename(原始)='script/mxgame/activity/gameplaymethodselection/delegate/dgtplaymethodselection.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2164.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/1/21 15:43
\xd7\xf7\xd5\xdf: yb
\xce\xc4\xbc\xfe: dgtplaymethodselection
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import delegatebase
import dialoguecommondata
import mdlplaymethodselection
import playmethodseldata
import usermacro
import netplayselection

class CPlayMethodSelDgt(delegatebase.CDelegateBase):
    
    def Init(self):
        self.RefreshQuestion()
        self.EditInit()
        self.GetView().SetNextBtnShow(True)

    
    def EditInit(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_OnSelectOption, self.SelectOption)
        oView.ssConnect(oView.SS_OnNextQuestion, self.NextQuestion)
        oView.ssConnect(oView.SS_OnLastQuestion, self.LastQuestion)

    
    def RefreshQuestion(self):
        oModel = self.GetModel()
        oView = self.GetView()
        iPage = oModel.GetPage()
        if iPage == 0:
            oView.SetLastPageBtn(False)
        else:
            oView.SetLastPageBtn(True)
        sQuestion = playmethodseldata.GetQuestionData(iPage)
        iPage += 1
        oView.SetQuestion('%d\xa1B' % iPage + sQuestion + '\xa1]\xbd\xd0\xbf\xef\xbe\xdc2\xb6\xb5\xa1^')
        self.RefreshOption()

    
    def RefreshOption(self):
        iPage = self.GetModel().GetPage()
        sQuestList = self.GetShowDataList(iPage)
        self.GetView().RefreshChooseTbView(sQuestList)

    
    def GetShowDataList(self, iPage):
        sQuestionList = []
        iSelectList = self.GetModel().GetSelectList()
        for iIdx, sOption in enumerate(playmethodseldata.GetOptionData(iPage + 153)):
            if sOption:
                sOptionDict = {
                    'sName': sOption,
                    'bSelect': iIdx in iSelectList,
                    'iOptionNum': iIdx }
                sQuestionList.append(sOptionDict)
                continue
        
        return sQuestionList

    
    def SelectOption(self, iOptionPage):
        oModel = self.GetModel()
        if iOptionPage not in oModel.GetNowSelectList():
            if oModel.GetSelectListLen() >= 2:
                usermacro.PROMPT_MSG(dialoguecommondata.GetDialogue('playmethodselect', 1004))
                return None
            
            if oModel.GetFirstSelect():
                oModel.SetFirstSelect(False)
                sName = playmethodseldata.GetOptionData(oModel.GetPage() + 1)[iOptionPage]
                usermacro.PROMPT_MSG(dialoguecommondata.GetDialogue('playmethodselect', 1003).replace('$name', sName))
            
            oModel.AddSelectListPage(iOptionPage)
        else:
            oModel.RemoveSelectListPage(iOptionPage)
        self.RefreshOption()

    
    def NextQuestion(self):
        oModel = self.GetModel()
        oView = self.GetView()
        iNextPage = oModel.GetPage() + 1
        if import GetSelectListLen() >= 2:
            oModel.SavePageSelect()
            if iNextPage >= playmethodseldata.GetQuestLen():
                netplayselection.C2GSendAllSelection(oModel.GetAllSelect())
                oView.CloseUI()
                return None
            else:
                iDict = oModel.GetAllSelect()
                oModel.SetPage(iNextPage)
                iSelectList = iDict.get(iNextPage, [])
                oModel.SetNowSelectList(iSelectList)
                if iNextPage + 1 >= playmethodseldata.GetQuestLen():
                    oView.SetNextBtnShow(False)
                
                self.RefreshQuestion()
        else:
            usermacro.PROMPT_MSG(dialoguecommondata.GetDialogue('playmethodselect', 1005))

    
    def LastQuestion(self):
        oModel = self.GetModel()
        iLastPage = oModel.GetPage() - 1
        if iLastPage < 0:
            return None
        
        iAllDict = oModel.GetAllSelect()
        oModel.SavePageSelect()
        oModel.SetPage(iLastPage)
        lLastSelect = iAllDict.get(iLastPage, [])
        oModel.SetNowSelectList(lLastSelect)
        self.RefreshQuestion()
        self.GetView().SetNextBtnShow(True)

    
    def GetModel(self):
        return mdlplaymethodselection.GetPlayMethodSelModel()
