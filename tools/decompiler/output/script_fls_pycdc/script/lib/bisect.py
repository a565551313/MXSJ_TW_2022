# pycdc 交叉复核产物 · script.fls entry 2958
# co_filename(原始)='script/lib/bisect.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2958.pyc (Python 2.5)

'''Bisection algorithms.'''

def insort_right(a, \xc4, lo = 0, hi = None):
    '''Insert item x in list a, and keep it sorted assuming a is sorted.

    If x is already in a, insert it to the right of the rightmost x.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    '''
    if lo < 0:
        raise ValueError('lo must be non-negative')
    
    if hi is None:
        hi = len(a)
    
    while lo < hi:
        mid = (lo + hi) // 2
        if \xc4 < a[mid]:
            hi = mid
            continue
        lo = mid + 1
    a.insert(lo, \xc4)

insort = insort_right

def bisect_right(a, \xc4, lo = 0, hi = None):
    '''Return the index where to insert item x in list a, assuming a is sorted.

    The return value i is such that all e in a[:i] have e <= x, and all e in
    a[i:] have e > x.  So if x already appears in the list, a.insert(x) will
    insert just after the rightmost x already there.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    '''
    if lo < 0:
        raise ValueError('lo must be non-negative')
    
    if hi is None:
        hi = len(a)
    
    while lo < hi:
        mid = (lo + hi) // 2
        if \xc4 < a[mid]:
            hi = mid
            continue
        lo = mid + 1
    return lo

bisect = bisect_right

def insort_left(a, \xc4, lo = 0, hi = None):
    '''Insert item x in list a, and keep it sorted assuming a is sorted.

    If x is already in a, insert it to the left of the leftmost x.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    '''
    if lo < 0:
        raise ValueError('lo must be non-negative')
    
    if hi is None:
        hi = len(a)
    
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < \xc4:
            lo = mid + 1
            continue
        hi = mid
    a.insert(lo, \xc4)


def bisect_left(a, \xc4, lo = 0, hi = None):
    '''Return the index where to insert item x in list a, assuming a is sorted.

    The return value i is such that all e in a[:i] have e < x, and all e in
    a[i:] have e >= x.  So if x already appears in the list, a.insert(x) will
    insert just before the leftmost x already there.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    '''
    if lo < 0:
        raise ValueError('lo must be non-negative')
    
    if hi is None:
        hi = len(a)
    
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < \xc4:
            lo = mid + 1
            continue
        hi = mid
    return lo


try:
    from _bisect import *
except ImportError:
    pass
