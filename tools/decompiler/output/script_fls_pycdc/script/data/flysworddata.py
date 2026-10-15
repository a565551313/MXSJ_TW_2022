# pycdc 交叉复核产物 · script.fls entry 1910
# co_filename(原始)='script/data/flysworddata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1910.pyc (Python 2.5)


def GetMonsterData(iMonsterID):
    if iMonsterID not in MONSTER or iMonsterID == 1:
        return MONSTER[1]
    
    if 'bInited' not in MONSTER[iMonsterID]:
        dTmpData = { }
        dTmpData.update(MONSTER[1])
        dTmpData.update(MONSTER[iMonsterID])
        dTmpData['bInited'] = True
        MONSTER[iMonsterID] = dTmpData
    
    return MONSTER[iMonsterID]


def GetGameData(iGameID):
    if iGameID not in DATA or iGameID == 1:
        return DATA[1]
    
    if 'bInited' not in DATA[iGameID]:
        dTmpData = { }
        dTmpData.update(DATA[1])
        dTmpData.update(DATA[iGameID])
        dTmpData['bInited'] = True
        DATA[iGameID] = dTmpData
    
    return DATA[iGameID]

DATA = {
    1: {
        'iBigNumLeft': 1,
        'iBigNumRight': 1,
        'iMonsterList': 1,
        'iSwordAngle': 90,
        'iSwordDam': 320,
        'iSwordDeltTime': 2,
        'iSwordFlyTime': 10,
        'iSwordH': 100,
        'iSwordSpeed': 60,
        'iSwordStartX': 300,
        'iSwordStartY': 450,
        'iSwordW': 20,
        'sMonsterName': '\xc5]\xafT',
        'sSwordVoice': 'weapon/07.wav',
        'tShakeList': ((5, 5), (2, 3), (-4, -6), (-10, 3), (0, 0)) },
    2: {
        'iMonsterList': (2, 3, 4),
        'sMonsterName': '\xafP\xa4\xf5\xb3\xbe',
        'sSwordVoice': 'weapon/07.wav' },
    3: {
        'iMonsterList': (5, 6, 7),
        'sMonsterName': '\xc5]\xc3~',
        'sSwordVoice': 'weapon/07.wav' } }
MONSTER = {
    1: {
        'dMonsterDesc': {
            'color': [
                1,
                0,
                0],
            'weapon': [
                0,
                0],
            'weapon2': [
                0,
                0],
            'weapon3': [
                0,
                0] },
        'iMonsterDeltX': 50,
        'iMonsterEndX': 500,
        'iMonsterEndY': 200,
        'iMonsterH': 120,
        'iMonsterHP': 900,
        'iMonsterShape': 2490,
        'iMonsterSpeed': 4,
        'iMonsterStartHurt': 10,
        'iMonsterStartX': 150,
        'iMonsterStartY': 200,
        'iMonsterStopTime': 0.3,
        'iMonsterW': 120,
        'sMonsterAni': 'war/shit/eff.spr',
        'sMonsterVoice': 'char/2490/hit.snd' },
    2: {
        'dMonsterDesc': {
            'color': [
                3,
                0,
                0],
            'weapon': [
                0,
                1],
            'weapon2': [
                0,
                0],
            'weapon3': [
                0,
                0] },
        'iMonsterEndX': 500,
        'iMonsterEndY': 200,
        'iMonsterHP': 300,
        'iMonsterShape': 2380,
        'iMonsterSpeed': 4,
        'iMonsterStartX': 150,
        'iMonsterStartY': 200,
        'sMonsterVoice': 'char/2380/hit.snd' },
    3: {
        'dMonsterDesc': {
            'color': [
                3,
                0,
                0],
            'weapon': [
                0,
                1],
            'weapon2': [
                0,
                0],
            'weapon3': [
                0,
                0] },
        'iMonsterEndX': 200,
        'iMonsterEndY': 200,
        'iMonsterHP': 300,
        'iMonsterShape': 2380,
        'iMonsterStartX': 600,
        'iMonsterStartY': 200,
        'sMonsterVoice': 'char/2380/hit.snd' },
    4: {
        'dMonsterDesc': {
            'color': [
                3,
                0,
                0],
            'weapon': [
                0,
                1],
            'weapon2': [
                0,
                0],
            'weapon3': [
                0,
                0] },
        'iMonsterEndX': 450,
        'iMonsterEndY': 200,
        'iMonsterHP': 300,
        'iMonsterShape': 2380,
        'iMonsterStartX': 50,
        'iMonsterStartY': 200,
        'sMonsterVoice': 'char/2380/hit.snd' },
    5: {
        'dMonsterDesc': {
            'color': [
                0,
                1,
                0],
            'weapon': [
                5,
                1],
            'weapon2': [
                0,
                0],
            'weapon3': [
                0,
                0] },
        'iMonsterEndX': 450,
        'iMonsterEndY': 200,
        'iMonsterHP': 300,
        'iMonsterShape': 2390,
        'iMonsterStartX': 50,
        'iMonsterStartY': 200,
        'sMonsterVoice': 'char/2390/hit.snd' },
    6: {
        'bIsGood': 1,
        'dMonsterDesc': {
            'color': [
                0,
                0,
                0],
            'weapon': [
                0,
                0],
            'weapon2': [
                0,
                0],
            'weapon3': [
                0,
                0] },
        'iMonsterEndX': 300,
        'iMonsterEndY': 200,
        'iMonsterHP': 600,
        'iMonsterShape': 4005,
        'iMonsterStartX': 100,
        'iMonsterStartY': 200,
        'sMonsterVoice': 'char/4005/hit.snd' },
    7: {
        'dMonsterDesc': {
            'color': [
                0,
                1,
                0],
            'weapon': [
                5,
                1],
            'weapon2': [
                0,
                0],
            'weapon3': [
                0,
                0] },
        'iMonsterEndX': 50,
        'iMonsterEndY': 200,
        'iMonsterHP': 300,
        'iMonsterShape': 2390,
        'iMonsterStartX': 450,
        'iMonsterStartY': 200,
        'sMonsterVoice': 'char/2390/hit.snd' } }
