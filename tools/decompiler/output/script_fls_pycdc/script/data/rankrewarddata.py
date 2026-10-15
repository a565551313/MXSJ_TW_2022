# pycdc 交叉复核产物 · script.fls entry 694
# co_filename(原始)='script/data/rankrewarddata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_694.pyc (Python 2.5)

import rankitemrewarddata
RANK_ID_OFFSET = 2015

def GetRewardData(iRank):
    iID = iRank + RANK_ID_OFFSET
    lResult = []
    if iID in DATA:
        for iItemRewardID in DATA[iID]['lReward']:
            for tReward in rankitemrewarddata.GetRewardDataByID(iItemRewardID):
                lResult.append(tReward)
            
        
        lResult.append((23013, DATA[iID]['iFightCash']))
    
    return lResult

None['lReward'] = [
    None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, {
        2001: {
            'iFightCash': 0,
            'lReward': [
                2001] },
        2002: {
            'iFightCash': 0,
            'lReward': [
                2002] },
        2003: {
            'iFightCash': 0,
            'lReward': [
                2003] },
        2004: {
            'iFightCash': 0,
            'lReward': [
                2004] },
        2005: {
            'iFightCash': 0,
            'lReward': [
                2005] },
        2006: {
            'iFightCash': 0,
            'lReward': [
                2006] },
        2007: {
            'iFightCash': 0,
            'lReward': [
                2007] },
        2008: {
            'iFightCash': 0,
            'lReward': [
                2008] },
        2009: {
            'iFightCash': 0,
            'lReward': [
                2009] },
        2010: {
            'iFightCash': 0,
            'lReward': [
                2010] },
        2011: {
            'iFightCash': 0,
            'lReward': [
                2011] },
        2012: {
            'iFightCash': 0,
            'lReward': [
                2012] },
        2013: {
            'iFightCash': 0,
            'lReward': [
                2013] },
        2014: {
            'iFightCash': 0,
            'lReward': [
                2014] },
        2015: {
            'iFightCash': 500000,
            'lReward': [
                2015,
                2016] } }, {
        2001: {
            'iFightCash': 0,
            'lReward': [
                2001] },
        2002: {
            'iFightCash': 0,
            'lReward': [
                2002] },
        2003: {
            'iFightCash': 0,
            'lReward': [
                2003] },
        2004: {
            'iFightCash': 0,
            'lReward': [
                2004] },
        2005: {
            'iFightCash': 0,
            'lReward': [
                2005] },
        2006: {
            'iFightCash': 0,
            'lReward': [
                2006] },
        2007: {
            'iFightCash': 0,
            'lReward': [
                2007] },
        2008: {
            'iFightCash': 0,
            'lReward': [
                2008] },
        2009: {
            'iFightCash': 0,
            'lReward': [
                2009] },
        2010: {
            'iFightCash': 0,
            'lReward': [
                2010] },
        2011: {
            'iFightCash': 0,
            'lReward': [
                2011] },
        2012: {
            'iFightCash': 0,
            'lReward': [
                2012] },
        2013: {
            'iFightCash': 0,
            'lReward': [
                2013] },
        2014: {
            'iFightCash': 0,
            'lReward': [
                2014] },
        2015: {
            'iFightCash': 500000,
            'lReward': [
                2015,
                2016] } }, {
        'iFightCash': 800000 }, {
        'iFightCash': 800000 }, **{
        'iFightCash': 800000 }),
    2018]
None[2016] = None
None[2017] = {
    'iFightCash': 1000000,
    'lReward': [
        2019,
        2020,
        2021] }
None[2018] = {
    'iFightCash': 1500000,
    'lReward': [
        2022,
        1933,
        2024] }
None[2019] = {
    'iFightCash': 2000000,
    'lReward': [
        2025,
        2026,
        2027] }
None[2020] = {
    'iFightCash': 2500000,
    'lReward': [
        2028,
        2029,
        2030] }
None[2021] = {
    'iFightCash': 3000000,
    'lReward': [
        2031,
        2032,
        2033] }
None[2022] = {
    'iFightCash': 3500000,
    'lReward': [
        2034,
        2035,
        2036] }
None[1933] = {
    'iFightCash': 4000000,
    'lReward': [
        2037,
        2038,
        2039] }
None[2024] = {
    'iFightCash': 4500000,
    'lReward': [
        2040,
        2041,
        2042] }
None[2025] = {
    'iFightCash': 5000000,
    'lReward': [
        2043,
        2044,
        2045] }
None[2026] = {
    'iFightCash': 5500000,
    'lReward': [
        2046,
        2047,
        2048] }
None[2027] = {
    'iFightCash': 6000000,
    'lReward': [
        2049,
        2050,
        2051,
        2052] }
DATA = None
