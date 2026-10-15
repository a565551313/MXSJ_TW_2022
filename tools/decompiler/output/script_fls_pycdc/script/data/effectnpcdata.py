# pycdc 交叉复核产物 · script.fls entry 4675
# co_filename(原始)='script/data/effectnpcdata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4675.pyc (Python 2.5)


def IsEffectNpc(iNpcID):
    return iNpcID in DATA


def GetNpcInfo(iNpcID):
    return DATA.get(iNpcID, None)


def GetEffectInfo(iEffectID):
    return EFFECT[iEffectID]

DATA = {
    10001: {
        'body': (0, 100, 0, 0),
        'efflist': [
            1] },
    10002: {
        'body': (100, 100, 0, 0),
        'efflist': [
            2] },
    10003: {
        'body': (0, 0, 0, 0),
        'efflist': [
            3] },
    10004: {
        'body': (100, 100, 0, 0),
        'efflist': [
            4] },
    10005: {
        'body': (100, 100, 0, 0),
        'efflist': [
            5] },
    10006: {
        'body': (100, 100, 0, 0),
        'efflist': [
            6] },
    10007: {
        'body': (100, 162, 0, 0),
        'efflist': [
            7] },
    10008: {
        'body': (0, 0, 0, 0),
        'efflist': [
            8] },
    10009: {
        'body': (0, 0, 0, 0),
        'efflist': [
            9] },
    10010: {
        'body': (100, 100, 0, 0),
        'efflist': [
            10] },
    10011: {
        'body': (100, 100, 0, 0),
        'efflist': [
            11] },
    10012: {
        'body': (100, 100, 0, 0),
        'efflist': [
            12] } }
EFFECT = {
    1: ('magicres/waddon/224.eff', 0, 0, 110),
    2: ('magicres/eff/story/19004.eff', 4, 0, 70),
    3: ('magicres/eff/\xbe\xe7\xc7\xe9\xcc\xd8\xd0\xa7/6002.eff', 0, 0, 0),
    4: ('magicres/eff/story/4138.eff', 0, 0, 0),
    5: ('magicres/eff/story/4139.eff', 0, 0, 0),
    6: ('magicres/eff/story/19009.eff', 4, 0, 70),
    7: ('magicres/eff/story/4818_a.eff', 0, 0, 0),
    8: ('magicres/eff/story/4510_u.eff', 0, 0, 0),
    9: ('magicres/eff/story/4137_u.eff', 0, 0, 0),
    10: ('magicres/eff/story/19010.eff', 4, 0, 70),
    11: ('magicres/eff/story/4510_c.eff', 0, 0, 110),
    12: ('magicres/waddon/225.eff', 0, 0, 10) }
continue
