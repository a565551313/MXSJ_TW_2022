# pycdc 交叉复核产物 · script.fls entry 4853
# co_filename(原始)='script/mxgame/activity/keju/kejutest.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4853.pyc (Python 2.5)

import kejudefines

def TestOpenHuishi():
    '''
\timport kejutest
\tkejutest.TestOpenHuishi()
\t'''
    dInfo = { }
    dInfo['iNid'] = 1
    dInfo['iNumQuest'] = 1
    dInfo['iQuestionAmount'] = 1
    dct = { }
    dct['answerDct'] = ansDict = { }
    dct['sQuestion'] = '\xa7A\xacO\xad\xfe\xb8\xcc\xa4H\xa1H'
    dct['jn'] = jnDict = { }
    for i, s in enumerate(('\xbcs\xaaF', '\xa5_\xa8\xca', '\xa4W\xae\xfc', '\xb4\xf2\xabn')):
        numAns = i
        ansDict[numAns] = s
    
    for i in range(4):
        jnRemain = 2
        jnDict[i] = jnRemain
    
    dInfo['dContent'] = dct
    dct['iTrueIdx'] = 1
    dInfo['iTrueNum'] = 1
    dInfo['iExp'] = 100
    dInfo['iUsedTime'] = 200
    dInfo['iScore'] = 10
    import dlgkeju
    dlgkeju.ShowProvinceExamDlg(kejudefines.TYPE_QUESTION, dInfo)


def TestOpenTown():
    '''
\timport kejutest
\tkejutest.TestOpenTown()
\t'''
    dInfo = { }
    dInfo['iType'] = 1
    dInfo['iIdx'] = 1
    dInfo['iQuestionAmount'] = 1
    dInfo['iNid'] = 1
    dct = { }
    dct['sQuestion'] = '\xa7A\xacO\xad\xfe\xb8\xcc\xa4H\xa1H'
    dct['answerLst'] = lst = []
    for i, sAnswer in enumerate(('\xbcs\xaaF', '\xa5_\xa8\xca', '\xa4W\xae\xfc')):
        lst.append(sAnswer)
    
    dInfo['dContent'] = dct
    dInfo['iExp'] = 100
    dInfo['iFinishTime'] = 0
    dInfo['iScore'] = 100
    import dlgkeju
    dlgkeju.ShowTwonExamDlg(kejudefines.TYPE_QUESTION, dInfo)


def TestOpenTownPeotry():
    '''
\timport kejutest
\tkejutest.TestOpenTownPeotry()
\t'''
    dInfo = { }
    dInfo['iType'] = 1
    dInfo['iIdx'] = 1
    dInfo['iQuestionAmount'] = 1
    dInfo['iNid'] = 1
    dct = { }
    None = 'iPeotryID'
    dct['tQuestionList'] = [
        ('\xa7\xc9', '\xabe', '\xa9\xfa', '', '\xa5\xfa', '\xa5\xfa', '\xa5\xfa'),
        ('\xba\xc3', '\xacO', '\xa6a', '\xa4W', '', '\xa5\xfa', '\xa5\xfa')]
    dct['sAnswerList'] = [
        '\xa4\xe9',
        '\xa4\xeb',
        '\xb3\xb7',
        '\xc1\xf7',
        '\xacO',
        '\xad\xb7',
        '\xae\xe6',
        '\xaa\xba',
        '\xb7j',
        '\xaf\xc1']
    dInfo['dContent'] = dct
    dInfo['iExp'] = 100
    dInfo['iFinishTime'] = 0
    dInfo['iScore'] = 100
    dInfo['bIsHuishi'] = False
    import dlgkeju
    dlgkeju.ShowTwonExamDlg(kejudefines.TYPE_POETRY, dInfo)


def TestOpenHuishiPeotry():
    '''
\timport kejutest
\tkejutest.TestOpenHuishiPeotry()
\t'''
    dInfo = { }
    dInfo['bIsHuishi'] = True
    dInfo['iNid'] = 1
    dInfo['iNumQuest'] = 1
    dInfo['iQuestionAmount'] = 1
    dct = { }
    dct['iPeotryID'] = 1
    dct['tQuestionList'] = [
        ('\xa7\xc9', '\xabe', '\xa9\xfa', '', '\xa5\xfa', '\xa5\xfa', '\xa5\xfa'),
        ('\xba\xc3', '\xacO', '\xa6a', '\xa4W', '', '\xa5\xfa', '\xa5\xfa')]
    dct['sAnswerList'] = [
        '\xa4\xe9',
        '\xa4\xeb',
        '\xb3\xb7',
        '\xc1\xf7',
        '\xacO',
        '\xad\xb7',
        '\xae\xe6',
        '\xaa\xba',
        '\xb7j',
        '\xaf\xc1']
    dct['jn'] = {
        0: 1,
        1: 1,
        2: 1,
        3: 1 }
    dInfo['dContent'] = dct
    dct['iTrueIdx'] = 1
    dInfo['iTrueNum'] = 1
    dInfo['iExp'] = 100
    dInfo['iUsedTime'] = 200
    dInfo['iScore'] = 10
    import dlgkeju
    dlgkeju.ShowProvinceExamDlg(kejudefines.TYPE_POETRY, dInfo)


def TestShootGame():
    '''
\timport kejutest
\tkejutest.TestShootGame()
\t'''
    import dlgkeju
    dInfo = { }
    dInfo['dContent'] = { }
    dInfo['iNid'] = 1
    dInfo['bIsHuishi'] = True
    dInfo['dContent']['iTimes'] = 10
    dlgkeju.ShowFlySwordDlg(dInfo)
