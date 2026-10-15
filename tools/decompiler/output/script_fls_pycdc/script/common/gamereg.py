# pycdc 交叉复核产物 · script.fls entry 2964
# co_filename(原始)='script/common/gamereg.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2964.pyc (Python 2.5)

__all__ = [
    'OpenKey',
    'QueryInfoKey',
    'EnumKey',
    'QueryValueEx',
    'KEY_READ',
    'HKEY_LOCAL_MACHINE']
import types
import misc
from _wi
 import OpenKey
from _wi
 import HKEY_LOCAL_MACHINE
from _wi
 import KEY_READ
from _wi
 import QueryInfoKey
from _wi
 import EnumKey
from _wi
 import QueryValueEx

class Functor(misc.Functor):
    
    def __call__(self, *_arg\x97, **_kwArgs):
        
        try:
            ret = misc.Functor.__call__(self, *_arg\x97, **_kwArgs)
        except WindowsError:
            return False

        return (True, ret)



def Init():
    import _wi

    for name in dir(_wi
):
        obj = getattr(_wi
, name)
        if isinstance(obj, types.BuiltinFunctionType) or isinstance(obj, types.BuiltinMethodType):
            globals()[name] = Functor(obj)
            continue
    

Init()
