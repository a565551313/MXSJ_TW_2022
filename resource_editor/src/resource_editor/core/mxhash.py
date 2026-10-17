# 自动生成，请勿手改：由 tools/devkit/vendor_core.py 从
# mx_common/mxhash.py 复制（字节相同）。
# 改共享逻辑：改 mx_common/mxhash.py → --write；校验：--check
# 详细说明见 mx_common/README.md。
"""``0SLF`` 资源包的路径哈希（多益 Mex 引擎资源寻址）复刻实现。

引擎把资源路径哈希为 32 位整数存入目录的 ``entry_id`` 字段，运行
时用同一哈希查表。本模块是客户端本体 ``mxmain.dll`` 中哈希函数
（VA ``0x48EF80``）的指令级复刻，与仓库
``tools/data-parser/mx_path_hash.py`` 同源，结论见
``notes/fls_path_hash_and_dlg.md``。

**本文件是唯一真源**（``mx_common/``）；编辑器里运行的是
``tools/devkit/vendor_core.py`` 复制出来的同字节副本，改这里才是改
编辑器（见 ``mx_common/README.md``）。

算法概要：路径字节规范化（``\\`` 改 ``/``、小写转大写）后按小端
打包成 u32 字数组，追加终止字 ``0x9BE74448``/``0x66F42C48``，
状态 ``(A, X, Y)`` 逐字经两轮「64 位乘积按 1 的补数折叠」混合，
返回 ``Y ^ X``。最长 256 字节。
"""

from __future__ import annotations

MASK32 = 0xFFFFFFFF

__all__ = ["mx_hash", "path_hash"]


def _fold1(product: int) -> int:
    """64 位乘积按 1 的补数（end-around carry）折叠回 32 位（第一轮）。"""
    lo = product & MASK32
    hi = (product >> 32) & MASK32
    if hi:
        edx = (hi + 1) & MASK32
        carry_hi = 1 if hi == MASK32 else 0
    else:
        edx = hi
        carry_hi = 0
    total = lo + edx
    result = total & MASK32
    if (total >> 32) + carry_hi:
        result = (result + 1) & MASK32
    return result


def _fold2(product: int) -> int:
    """第二轮折叠：高 32 位先乘 2 再做带进位折叠。"""
    lo = product & MASK32
    hi = (product >> 32) & MASK32
    top_bit = hi >> 31
    doubled = (hi << 1) & MASK32
    if top_bit:
        doubled = (doubled + 1) & MASK32
        extra = 1 if doubled == 0 else 0
        total = lo + doubled
        high = extra + (total >> 32)
    else:
        total = lo + doubled
        high = total >> 32
    result = total & MASK32
    if high:
        result = (result + 2) & MASK32
    return result


def mx_hash(path: bytes) -> int:
    """计算资源路径的 32 位哈希（与 ``entry_id`` 比对的键）。

    ``path`` 为原始字节串：ASCII 路径直接 encode，含中文路径传
    GBK 字节。规范化（分隔符与大小写）在函数内部完成。
    """
    words = [0] * 66
    last_word = 0
    for pos, byte in enumerate(path):
        if byte == 0:
            break
        word_index = pos >> 2
        if word_index >= 0x40:  # 引擎上限：64 字（256 字节）
            break
        char = byte
        if char == 0x5C:  # '\\' -> '/'
            char = 0x2F
        elif 0x61 <= char <= 0x7A:  # 小写转大写
            char -= 0x20
        last_word = word_index
        words[word_index] = (
            words[word_index] + (char << ((pos & 3) * 8))
        ) & MASK32
    words[last_word + 1] = 0x9BE74448
    words[last_word + 2] = 0x66F42C48

    state_a = 0xF4FA8928
    state_x = 0x37A8470E
    state_y = 0x7758B42B
    for index in range(last_word + 3):
        state_a = (2 * state_a + (state_a >> 31)) & MASK32
        word = words[index]
        mix_u = state_a ^ 0x267B0B11
        state_y ^= word
        x_new = state_x ^ word
        mult1 = ((state_y + mix_u) & 0xBDEB77DE) | 0x02040801
        folded = _fold1((x_new * mult1) & 0xFFFFFFFFFFFFFFFF)
        mult2 = ((mix_u + x_new) & 0x7D7EBBDE) | 0x00804021
        state_y = _fold2((state_y * mult2) & 0xFFFFFFFFFFFFFFFF)
        state_x = folded
    return (state_y ^ state_x) & MASK32


def path_hash(path: str) -> int:
    """资源路径 → ``entry_id``：按 GBK **严格**编码，不可编码就抛错。

    存在的理由：``path.encode("gbk", "replace")`` 会把不可编码字符静默换成
    ``?``，于是**哈希的是另一个路径**——查不到也不报错（UI 编辑器分析
    P2-2）。引擎只认 GBK 字节，无法编码的路径在引擎侧同样寻址不到，
    所以这里宁可抛 :class:`ValueError` 让调用方决定：报诊断、跳过，
    还是拒绝写入。

    不做 `native_layout.path_bytes()` 的「包内相对路径」校验：本函数也用于
    查询（`contains("a/b.png")` 这类），校验由写入侧负责。
    """
    try:
        raw = path.encode("gbk")
    except UnicodeEncodeError as exc:
        raise ValueError(
            f"路径含 GBK 不可编码字符，引擎寻址不到：{path!r}") from exc
    return mx_hash(raw)
