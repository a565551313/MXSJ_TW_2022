# pycdc 交叉复核产物 · script.fls entry 4906
# co_filename(原始)='script/dialog/dlgquiz.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4906.pyc (Python 2.5)

import interface
import combdialog
import combmacro
import wrapinterface
g_QuizDialog = None

def ModuleReset():
    global g_QuizDialog
    g_QuizDialog = None


def C2SSendQuiz(sQuestion, sAnswer, iMoneynum):
    import net
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_OPEN_UI)
    netobj.PacketAddI(17, 1)
    netobj.PacketAddI(iMoneynum, 4)
    netobj.PacketAddS(sQuestion, 140)
    netobj.PacketAddS(sAnswer, 92)
    netobj.PacketSend()


def Hz2AscEx(sStr):
    import chatinput
    sStr = chatinput.Hz2Asc(sStr)
    
    try:
        flag = 0
        s = ''
        for c in sStr:
            n = ord(c)
            if flag == 0:
                if n == 161:
                    flag = 1
                else:
                    s += c
            n == 161
            if n == 163:
                s += '.'
            elif n == 171:
                s += '~'
            elif n == 190:
                s += '['
            elif n == 191:
                s += ']'
            else:
                s = s + chr(161) + c
            flag = 0
    except:
        s = ''

    return s


class CQuizDialog(combdialog.CCombDialog):
    
    def __init__(self, iPrize):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/quiz.dlg')
        interface.Center(self)
        self.m_iPrize = 0
        self.m_text_totalmoney = None
        self.m_edit_question = combmacro.CMLEDIT(interface.CMultilineEdit, 'edit_question', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_edit_answer1 = combmacro.CEDIT(interface.CEdit, 'edit_answer1', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_edit_answer2 = combmacro.CEDIT(interface.CEdit, 'edit_answer2', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_edit_answer3 = combmacro.CEDIT(interface.CEdit, 'edit_answer3', self, interface.COLOR_5, interface.FontLT14_3)
        (x, y, w, h) = combmacro.GetIFObjectData(self, 'edit_prize', 0, 0)
        self.m_text_prize = combmacro.CIFTEXT(interface.CTextObject, 'edit_prize', self, 0, 0, '', interface.FontLT14EG_1, interface.COLOR_11)
        self.m_text_totalmoney = combmacro.CIFTEXT(interface.CTextObject, 'edit_prize', self, 1, 0, '', interface.FontLT14EG_1, interface.COLOR_11)
        self.SetTotalMoney(iPrize)
        self.m_edit_question.SetLimit(140)
        self.m_edit_answer1.SetLimit(30)
        self.m_edit_answer2.SetLimit(30)
        self.m_edit_answer3.SetLimit(30)
        self.m_edit_question.Active(True)
        self.m_edit_question.SetNextEdit(self.m_edit_answer1)
        self.m_edit_answer1.SetNextEdit(self.m_edit_answer2)
        self.m_edit_answer2.SetNextEdit(self.m_edit_answer3)
        self.m_edit_answer3.SetNextEdit(self.m_edit_question)

    
    def SetTotalMoney(self, iPrize):
        import hero
        self.m_text_totalmoney.SetText(str(hero.g_Prop.m_Cash))
        self.m_text_prize.SetText(str(iPrize))
        self.m_iPrize = iPrize

    
    def CloseWindow(self):
        global g_QuizDialog, g_QuizDialog
        self.m_edit_question.Active(False)
        self.m_edit_answer1.Active(False)
        self.m_edit_answer2.Active(False)
        self.m_edit_answer3.Active(False)
        del g_QuizDialog
        g_QuizDialog = None

    
    def _CheckEmptyString(self, sStr):
        if sStr is not None:
            sStr = sStr.strip()
        
        if sStr is None or len(sStr) == 0:
            return ''
        
        return sStr

    
    def _CheckAnswerForbiddenWords(self, sStr):
        forbidden_words = ('"', "'", '\\', '=', '+', '|', ';', ':', '<', '>', '[', ']', '{', '}', '?', '*', ',', '(', ')', '^', '%', '$', '#', '!', '~', '`', '@', '&', '_', '\xa1C', '\xa1A', '\xa1B', '\xa1F', '\xa1G', '\xa1H', '\xa1I', '\xa1K', '\xa1X', '\xa1P', '\xa3\xbc', '\xa3\xbe', '\xa1\xa1', '\xa1y', '\xa1z', '\xa1u', '\xa1v', '\xa1\xa1', '\xa1\xaa', '\xa1\xa1', '\xfd\x85', '\xa1\xb2', '\xa1e', '\xa1f', '\xa1q', '\xa1r', '\xa1m', '\xa1n', '\xa1D', '\xa1u', '\xa1v', '\xa1y', '\xa1z', '\xa1\xa1', '\xa1\xa1', '\xa1i', '\xa1j', '\xa1]', '\xa1^', '\xa1e', '\xa1f', '\xa1a', '\xa1b', '\xa1@', '\xa1\xe3', '\xa1U', '\xa1\xa1')
        
        try:
            flag = 0
            word = ''
            for c in sStr:
                if flag == 0:
                    word = c
                    if ord(c) >= 128:
                        flag = 1
                    
                else:
                    word += c
                    flag = 0
                if flag == 0:
                    if word in forbidden_words:
                        msg = '\xb1z\xaa\xba\xb5\xaa\xae\xd7\xa4\xa4\xa5]\xa7t\xa4F\xbc\xd0\xc2I\xb2\xc5\xb8\xb9\xa1A\xbd\xd0\xad\xab\xb7s\xbf\xe9\xa4J'
                        import usermacro
                        usermacro.PROMPT_MSG(msg)
                        return False
                    
                    word = ''
                    continue
        except:
            return False

        return True

    
    def _CheckInvalidWords(self, sStr):
        invalid_words = ('fuck', '\xa4\xbb\xa5|', '64\xb0\xca\xb6\xc3', '64\xbc\xc9\xb6\xc3', '89\xa6~', '89\xbe\xc7', '89\xb9B\xb0\xca', '89\xad\xb7\xaai', '\xbe\xc7\xbc\xe9', '\xaak\xbd\xfc', '\xbd\xfc\xa5\\', '\xa5~\xb1\xbe', '\xa8p\xaaA', '\xa6\xbf\xae\xd6\xa4\xdf', '\xa4j\xac\xf6\xa4\xb8', '\xa4j\xa5@\xac\xf6', '\xa6\xdb\xb5I', '\xb9C\xa6\xe6', '\xa6h\xd0\xde', '\xbe\xde\xa7A', '\xaf\xf3\xa7A', '\xa4\xe9\xa7A', '\xa4\xea\xa7A', '\xb4\xa1\xa7A', 'x\xa7A', '\xbau\xa7A\xb6\xfd', '\xa7A\xb6\xfdb', '\xa7A\xb6\xfdB', '\xa7A\xb6\xfd\xaa\xbab', '\xa7A\xb6\xfd\xaa\xbaB', '\xa4\xd1\xa6w', '\xa6@\xb2\xa3', '\xa6@\xd0\xde', '\xb0\xea\xa5\xc1\xd0\xde', '\xa5\xec\xb4\xb5\xc4\xf5', '\xbfp\xb4\xb5\xaaL', '\xa6^\xb1\xd0', '\xa4\xe4\xa8\xba', '\xa4\xe9\xa5\xbb', '\xa4\xea\xa5\xbb', '\xa4\xe9\xb3f', '\xa4\xea\xb3f', '\xa4k\xa4z', '\xa4\xa4\xa4\xe9\xa4\xcd\xa6n', '\xa4\xa4\xa4\xea\xa4\xcd\xa6n', '\xb0\xe2mb', '\xb0\xe2rmb', '\xb1a\xbdm', '\xb1a\xb3s', '\xa5N\xbdm', '\xa5N\xb3s', '\xb4\xc0\xbdm', '\xb4\xc0\xb3s', ' ', '\xa1@', '.cn', '.com', '.info', '.net', '\xa6h\xaa\xb1', '5173', '\xbd\xe6', '\xb6R', '\xb2^\xc4_', 'duowan', 'taobao', '\xa5\xb4\xbf\xfa', '\xa4u\xa7@\xab\xc7', '\xac\xf5\xb3\xbb\xb0\xd3\xa4H', '\xb0\xe2', '\xc2\xb2\xb3\xe6\xb4\xe5', '\xbdu\xa4U\xa5\xe6\xa9\xf6', '\xa5\xad\xa5x', '\xa6\xb9\xb8\xb9', '\xa5~\xb1\xbe')
        for word in invalid_words:
            if word in sStr:
                import usermacro
                usermacro.PROMPT_MSG('\xb1z\xbf\xe9\xa4J\xaa\xba\xa4\xba\xaee\xa4\xa4\xa7t\xa6\xb3\xb9H\xb8T\xb5\xfc\xbby\xa1A\xbd\xd0\xa5J\xb2\xd3\xad\xd7\xa7\xef\xab\xe1\xad\xab\xb7s\xb6\xf1\xbcg\xa1C')
                return False
                continue
        
        return True

    
    def OnMessage(self, msgid):
        if msgid == 2:
            self.CloseWindow()
        elif msgid == 1:
            import usermacro
            txt = self.m_edit_question.GetText()
            import usermacro
            import banword
            if not banword.IsValidChat(txt)[0]:
                usermacro.PROMPT_MSG('\xa7A\xaa\xba\xb5o\xa8\xa5\xa4\xa4\xa5]\xa7t\xb9H\xb8T\xb5\xfc\xbby\xa1I')
                return None
            
            self.m_question = self._CheckEmptyString(self.m_edit_question.GetText())
            if self.m_question is None or len(self.m_question) == 0:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xb0\xdd\xc3D')
                return None
            
            answer1 = self._CheckEmptyString(self.m_edit_answer1.GetText())
            answer2 = self._CheckEmptyString(self.m_edit_answer2.GetText())
            answer3 = self._CheckEmptyString(self.m_edit_answer3.GetText())
            import usermacro
            import banword
            if not banword.IsValidChat(answer1)[0]:
                usermacro.PROMPT_MSG('\xa7A\xaa\xba\xb5o\xa8\xa5\xa4\xa4\xa5]\xa7t\xb9H\xb8T\xb5\xfc\xbby\xa1I')
                return None
            
            import usermacro
            import banword
            if not banword.IsValidChat(answer2)[0]:
                usermacro.PROMPT_MSG('\xa7A\xaa\xba\xb5o\xa8\xa5\xa4\xa4\xa5]\xa7t\xb9H\xb8T\xb5\xfc\xbby\xa1I')
                return None
            
            import usermacro
            import banword
            if not banword.IsValidChat(answer3)[0]:
                usermacro.PROMPT_MSG('\xa7A\xaa\xba\xb5o\xa8\xa5\xa4\xa4\xa5]\xa7t\xb9H\xb8T\xb5\xfc\xbby\xa1I')
                return None
            
            if len(answer1) == 0:
                if len(answer2) == 0 or len(answer3) == 0:
                    usermacro.PROMPT_MSG('\xbd\xd0\xa6\xdc\xa4\xd6\xbf\xe9\xa4J\xb0\xdd\xc3D\xaa\xba\xa4@\xad\xd3\xb5\xaa\xae\xd7')
                    return None
                
            answer1 = Hz2AscEx(answer1)
            answer2 = Hz2AscEx(answer2)
            answer3 = Hz2AscEx(answer3)
            if not self._CheckInvalidWords(self.m_question) and not self._CheckInvalidWords(answer1) and not self._CheckInvalidWords(answer2) and not self._CheckInvalidWords(answer3) and not self._CheckAnswerForbiddenWords(answer1) and not self._CheckAnswerForbiddenWords(answer2) or not self._CheckAnswerForbiddenWords(answer3):
                return None
            
            self.m_answer = answer1 + '|' + answer2 + '|' + answer3
            
            def DoSendQuiz(dlg):
                C2SSendQuiz(self.m_question, self.m_answer, self.m_iPrize)
                self.CloseWindow()

            import commondialog
            commondialog.ShowMessageBox('\xb1z\xacO\xa7_\xa7\xc6\xb1\xe6\xaa\xe1\xb6O#R%d\xa8\xe2#n\xa8\xd3\xb5o\xa7G\xc4a\xbd\xe0\xb0\xdd\xc3D\xa1H' % self.m_iPrize, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (DoSendQuiz, None))
        



def Show(iPrize):
    global g_QuizDialog
    if g_QuizDialog:
        g_QuizDialog.SetTotalMoney(iPrize)
        g_QuizDialog.SetShow(True)
    else:
        g_QuizDialog = CQuizDialog(iPrize)
