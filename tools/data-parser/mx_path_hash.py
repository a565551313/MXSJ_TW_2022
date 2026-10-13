#!/usr/bin/env python3
"""`0SLF` 资源包的路径哈希（多益 Mex 引擎资源寻址）复刻实现。

``0SLF`` 容器（interface.fls / misc.fls 等）内部不保存文件名：引擎把
资源路径哈希为 32 位整数存入目录的 ``entry_id`` 字段，运行时用同一
哈希查表。本模块是客户端本体 ``mxmain.dll`` 中哈希函数（VA
``0x48EF80``）的指令级复刻，结论与验证数据见
``notes/fls_path_hash_and_dlg.md``。

算法概要
--------
1. 路径规范化：逐字节处理，``\\`` 改为 ``/``，小写字母转大写；
2. 规范化字节流按小端打包成 u32 字数组（每字 4 字节，不足补 0），
   末尾追加两个魔数终止字 ``0x9BE74448`` 与 ``0x66F42C48``；
3. 状态 ``(A, X, Y)`` 初值 ``(0xF4FA8928, 0x37A8470E, 0x7758B42B)``，
   逐字迭代：``A = 2A + (A>>31)``；``U = A ^ 0x267B0B11``；当前字
   分别与 ``X``、``Y`` 异或；两轮「64 位乘积按 1 的补数折叠回
   32 位」混合（乘数由掩码 ``0xBDEB77DE|0x02040801`` 与
   ``0x7D7EBBDE|0x00804021`` 塑形）；
4. 返回 ``Y ^ X``。

最长支持 256 字节路径（64 字），与原函数一致。

已知测试向量（路径 → entry_id）::

    dialog/recommendfriend.dlg -> 0x04964CA7
    dialog/report_command.dlg  -> 0x38A57E9D
    ui.lst                     -> 0x8DA5E6EC
"""

from __future__ import annotations

MASK32 = 0xFFFFFFFF

__all__ = ["mx_hash"]


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
    """第二轮折叠：高 32 位先乘 2 再做带进位折叠（模 2^31-1 风格）。"""
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

    ``path`` 为原始字节串（ASCII 路径直接 encode；含中文路径传 GBK
    字节）。规范化（分隔符与大小写）在函数内部完成，与引擎一致。
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


_TEST_VECTORS = {
    b"dialog/recommendfriend.dlg": 0x04964CA7,
    b"dialog/report_command.dlg": 0x38A57E9D,
    b"ui.lst": 0x8DA5E6EC,
    b"dialog\\report_command.dlg": 0x38A57E9D,  # 分隔符规范化
}


def _self_test() -> int:
    failed = 0
    for path, expected in _TEST_VECTORS.items():
        got = mx_hash(path)
        status = "OK " if got == expected else "FAIL"
        if got != expected:
            failed += 1
        print(f"{status} {path!r}: 0x{got:08X} (期望 0x{expected:08X})")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_self_test())
