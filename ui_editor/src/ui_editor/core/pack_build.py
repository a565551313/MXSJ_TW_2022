"""``0SLF`` 资源包的写回：替换指定条目的负载，重组整个归档。

读侧见 :mod:`.pack`。本模块在此之上提供三步能力（均不修改
原文件，产物是完整的归档字节）：

1. :func:`parse_archive` 把归档拆为头部、目录记录与各条目
   的存储字节（stored bytes，原样）；
2. :func:`build_archive` 以相同条目顺序重组归档，偏移重新
   紧凑排布，目录记录里的 r2/r3 按闭式变换重算（r1 与条目
   密钥的选择都沿用原条目，见下）；
3. :func:`replace_dlg_entry` 面向 UI 编辑器：定位路径对应
   条目，**沿用该条目原有的 4 字节 XOR 密钥**重新加密新
   明文并替换——引擎解密只依赖文件头反推（见 assets 的
   ``unpack_packed_text``），密钥不变则新旧条目在引擎眼中
   无区别，这是最保守的替换方式。

写后校验由调用方负责（用 FlsPack 重开、fetch_dlg 回读比对）。

**目录不变量（真实包实测，写回必须维持）**：6 个真实 0SLF 包
（script/effect/skill/skill2/passive/magicres5，共 6,056 条）一致
满足：目录记录按 ``entry_id`` 严格升序、目录区恰在文件尾、每条
记录的 ``r1`` 均非零。引擎按有序目录寻址（条目偏移的闭式变换
含目录下标），新增条目若只是把记录追加到目录尾并给 ``r1=0``，
自家线性解析读得到、引擎却查不到（甚至连累邻近条目），表现为
新条目丢失、重开计数变少、进游戏卡屏。故新增必须**按
entry_id 排序插入**（插入点之后记录的下标变化，r3 按新下标
重算），新记录的 r1 用 :func:`fresh_r1` 给出非零值；若待写源包
的目录已经乱序（旧版本写坏的包），保存时整包重组顺带修复。

大包快速路径（编辑器的保存入口用这组）：
:func:`patch_dlg_entry_in_file` 只改目标条目的负载与它那一条
16 字节目录记录——新负载变短/等长就原位替换（多出的旧字节
留在原地成间隙），变长且间隙不够时把新负载挪到目录原址、
目录整体顺移到其后，其余条目连偏移都不动；
:func:`patch_pack_copy` 在此之上做"复制整包 + 补丁"，或在
用户明确选原文件时直接补丁原文件。仅当包内负载交叠等病态
布局下才回退到整包重组。
"""

from __future__ import annotations

import bisect
import shutil
import struct
from pathlib import Path

from . import dlg_codec
from .errors import PackError
from .mxhash import mx_hash
from .pack import DIR_RECORD_SIZE, MAGIC, MASK32, decode_directory

_HEADER = struct.Struct("<4sII")
_RECORD = struct.Struct("<IIII")

__all__ = [
    "build_archive",
    "dump_archive",
    "entry_xor_key",
    "fresh_r1",
    "parse_archive",
    "patch_dlg_entry_in_file",
    "patch_pack_copy",
    "patch_raw_entry_in_file",
    "replace_dlg_entry",
    "replace_dlg_entry_to_file",
    "unpack_packed_text",
]


def fresh_r1(entry_id: int) -> int:
    """给新增条目定一个非零 r1（真实包 6,056 条无一为 0）。

    长度的闭式变换对任何 r1 都成立（写回时按选定 r1 反算 r2），
    故只需确定性地非零：黄金比例乘子散列 entry_id，为零取 1。
    """
    return ((entry_id * 0x9E3779B1) & MASK32) or 1

_KNOWN_HEADER = b"# -*- coding: gbk -*-"
_HEADER_PREFIX4 = b"# -*"


class RawEntry:
    """一条目录记录 + 其存储字节（解密前）。"""

    __slots__ = ("entry_id", "r1", "stored")

    def __init__(self, entry_id: int, r1: int, stored: bytes) -> None:
        self.entry_id = entry_id
        self.r1 = r1
        self.stored = stored


def parse_archive(data: bytes) -> list[RawEntry]:
    """把整个归档读入内存并拆解（大包慎用，写回场景条目数有限）。"""
    if len(data) < _HEADER.size or data[:4] != MAGIC:
        raise PackError("不是 0SLF 资源包（魔数不符）")
    _magic, count, dir_offset = _HEADER.unpack_from(data, 0)
    dir_end = dir_offset + count * DIR_RECORD_SIZE
    if dir_end > len(data):
        raise PackError("目录区越界，文件可能损坏")
    entries: list[RawEntry] = []
    for index in range(count):
        entry_id, r1, r2, r3 = _RECORD.unpack_from(
            data, dir_offset + index * DIR_RECORD_SIZE)
        clen, doff = decode_directory(index, (entry_id, r1, r2, r3))
        if doff + clen > len(data):
            raise PackError(f"条目 {index} 负载越界")
        entries.append(RawEntry(entry_id, r1, bytes(data[doff:doff + clen])))
    return entries


def build_archive(entries: list[RawEntry]) -> bytes:
    """重组归档：负载自 12 起紧凑排布，目录按 entry_id 升序置于尾。

    每条记录的 r1 沿用原值（为 0 的换 :func:`fresh_r1`，见模块
    文档的目录不变量）；r2/r3 由长度/偏移闭式重算，存储字节
    一概不动。排序使本函数同时成为乱序目录的修复路径。
    """
    import io

    ordered = sorted(entries, key=lambda e: e.entry_id)
    buffer = io.BytesIO()
    dump_archive(ordered, buffer)
    return buffer.getvalue()


def _effective_r1(entry: RawEntry) -> int:
    """写回时实际使用的 r1：原值非零沿用，为零换确定性非零值。"""
    return entry.r1 if entry.r1 else fresh_r1(entry.entry_id)


def dump_archive(entries: list[RawEntry], fh) -> int:
    """流式写出归档到二进制文件对象，返回总字节数（大包省内存）。

    按给定顺序写出（重组入口 build_archive 已排序）；r2/r3 闭式
    重算，r1 为零者以 :func:`fresh_r1` 代替。
    """
    offset = _HEADER.size
    r2_of = []
    for entry in entries:
        r2_of.append(((_effective_r1(entry) * entry.entry_id
                       + 0x0DF25E) & MASK32 ^ len(entry.stored)) & MASK32)
        offset += len(entry.stored)
    total = offset + len(entries) * DIR_RECORD_SIZE
    fh.write(_HEADER.pack(MAGIC, len(entries), offset))
    offset = _HEADER.size
    records = []
    for index, entry in enumerate(entries):
        r3 = (((r2_of[index] * index * 0x00F718FE + 0x0D59D16C) & MASK32)
              ^ offset) & MASK32
        records.append(_RECORD.pack(entry.entry_id,
                                    _effective_r1(entry),
                                    r2_of[index], r3))
        fh.write(entry.stored)
        offset += len(entry.stored)
    fh.write(b"".join(records))
    return total


def _xor4(data: bytes, key: bytes) -> bytes:
    """4 字节循环 XOR（整数整体异或，比逐字节快两个数量级）。"""
    if not data:
        return data
    repeated = (key * (len(data) // 4 + 1))[:len(data)]
    return (int.from_bytes(data, "little")
            ^ int.from_bytes(repeated, "little")).to_bytes(
                len(data), "little")


def unpack_packed_text(data: bytes) -> bytes:
    """把包内文本还原为明文字节：明文直接返回，XOR 加密则解开。

    先按已知文件头反推 4 字节密钥；不成再用列频率法恢复（明文
    本身列频率得全零密钥）；都不成时原样返回，交给上层报错。
    """
    if data.startswith(_KNOWN_HEADER[:5]) or data[:1] == b"[":
        return data  # .dlg 明文或 ui.lst（INI）
    key = bytes(a ^ b for a, b in
                zip(data[:4], _HEADER_PREFIX4, strict=False))
    decoded = _xor4(data, key)
    if decoded.startswith(_KNOWN_HEADER):
        return decoded
    return _xor4(data, _recover_key_by_frequency(data))


def _recover_key_by_frequency(data: bytes) -> bytes:
    favourites = set(
        b" etaoinshrdlu=(){}_#'\"0123456789.,:[]\n\t<>")
    key = bytearray(4)
    for r in range(4):
        column = data[r::4][:2048]
        best_score, best = -1, 0
        for cand in range(256):
            score = sum(1 for b in column if (b ^ cand) in favourites)
            if score > best_score:
                best_score, best = score, cand
        key[r] = best
    return bytes(key)


def entry_xor_key(stored: bytes) -> bytes:
    """从原条目存储字节反推其 4 字节 XOR 密钥（明文以 # -* 开头）。"""
    if len(stored) < 4:
        raise PackError("条目过短，无法反推 XOR 密钥")
    return bytes(a ^ b for a, b in zip(stored[:4], b"# -*", strict=True))


def replace_dlg_entry(archive: bytes, res_path: str,
                      new_plain: bytes) -> bytes:
    """把归档中 res_path 对应 .dlg 条目替换为 new_plain 的加密形。

    new_plain 必须是 .dlg 明文字节（以 ``# -*- coding: gbk -*-``
    开头）；加密沿用原条目密钥。找不到条目或明文不合式时抛
    PackError，绝不产生半成品归档。
    """
    from .errors import DlgError

    try:  # 结构闸门：能解才准写
        dlg_codec.parse_bytes(new_plain)
    except DlgError as exc:
        raise PackError(f"新布局无法解析，拒绝写回：{exc}") from exc
    entries = parse_archive(archive)
    entry_id = mx_hash(res_path.encode("gbk", "replace"))
    for entry in entries:
        if entry.entry_id == entry_id:
            plain_now = unpack_packed_text(entry.stored)
            if plain_now.startswith(b"["):
                raise PackError(f"{res_path} 不是 .dlg 条目，拒绝替换")
            key = entry_xor_key(entry.stored)
            entry.stored = _xor4(new_plain, key)
            return build_archive(entries)
    raise PackError(f"包中找不到条目：{res_path}")


class _RebuildNeeded(PackError):
    """负载交叠等病态布局，快速补丁不适用，调用方回退整包重组。"""


def _dir_record(entry_id: int, r1: int, index: int,
                length: int, offset: int) -> bytes:
    """按闭式变换生成一条目录记录（r1 沿用原值）。"""
    r2 = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ length) & MASK32
    r3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32)
          ^ offset) & MASK32
    return _RECORD.pack(entry_id, r1, r2, r3)


class _PatchPlan:
    """一次补丁的只读侦察结果：目标条目位置与新存储字节。"""

    __slots__ = ("count", "dir_offset", "dir_data", "spans",
                 "target", "doff", "clen", "limit", "new_stored")

    def __init__(self, **kw) -> None:
        for key, value in kw.items():
            setattr(self, key, value)


def _read_index(path: Path):
    """只读头部与目录：返回 (文件大小, 条数, 目录偏移, 目录字节,
    spans[(偏移,长度)], records[(entry_id,r1,r2,r3)])。"""
    with open(path, "rb") as fh:
        fh.seek(0, 2)
        file_size = fh.tell()
        fh.seek(0)
        head = fh.read(_HEADER.size)
        if len(head) < _HEADER.size or head[:4] != MAGIC:
            raise PackError("不是 0SLF 资源包（魔数不符）")
        _magic, count, dir_offset = _HEADER.unpack(head)
        dir_size = count * DIR_RECORD_SIZE
        if dir_offset + dir_size > file_size:
            raise PackError("目录区越界，文件可能损坏")
        fh.seek(dir_offset)
        dir_data = fh.read(dir_size)
        if len(dir_data) < dir_size:
            raise PackError("目录区读取不完整")
        spans: list[tuple[int, int]] = []
        records = []
        for index in range(count):
            raw = _RECORD.unpack_from(dir_data, index * DIR_RECORD_SIZE)
            clen, doff = decode_directory(index, raw)
            if doff + clen > file_size:
                raise PackError(f"条目 {index} 负载越界")
            spans.append((doff, clen))
            records.append(raw)
    return file_size, count, dir_offset, dir_data, spans, records


def _fit_limit(spans, doff: int, dir_offset: int, file_size: int) -> int:
    """条目之后第一个被占用的位置：新负载不超过它就能原位放下。"""
    limit = file_size
    if dir_offset > doff:
        limit = min(limit, dir_offset)
    for off, _ln in spans:
        if off > doff:
            limit = min(limit, off)
    return limit


def _plan_patch(path: Path, res_path: str,
                new_plain: bytes) -> _PatchPlan:
    """只读侦察：结构闸门 + 定位条目 + 算出新存储字节，不写文件。"""
    from .errors import DlgError

    try:  # 与 replace_dlg_entry 相同的结构闸门
        dlg_codec.parse_bytes(new_plain)
    except DlgError as exc:
        raise PackError(f"新布局无法解析，拒绝写回：{exc}") from exc
    entry_id = mx_hash(res_path.encode("gbk", "replace"))
    file_size, count, dir_offset, dir_data, spans, records = \
        _read_index(path)
    target = -1
    for index, raw in enumerate(records):
        if raw[0] == entry_id:
            target = index
            break
    if target < 0:
        raise PackError(f"包中找不到条目：{res_path}")
    doff, clen = spans[target]
    with open(path, "rb") as fh:
        fh.seek(doff)
        stored = fh.read(clen)
    if len(stored) != clen:
        raise PackError("目标条目读取不完整")
    if unpack_packed_text(stored).startswith(b"["):
        raise PackError(f"{res_path} 不是 .dlg 条目，拒绝替换")
    return _PatchPlan(
        count=count, dir_offset=dir_offset, dir_data=dir_data,
        spans=spans, target=target, doff=doff, clen=clen,
        limit=_fit_limit(spans, doff, dir_offset, file_size),
        new_stored=_xor4(new_plain, entry_xor_key(stored)))


def _write_located(path: Path, *, count: int, dir_offset: int,
                   dir_data: bytes, spans, target: int, entry_id: int,
                   r1: int, doff: int, limit: int,
                   new_stored: bytes) -> dict:
    """把已定位条目的负载换成 new_stored（原位放得下就原位，
    放不下挪到目录原址），返回 {"mode", "target_index", "bytes"}。"""
    with open(path, "r+b") as fh:
        if len(new_stored) <= limit - doff:
            fh.seek(doff)
            fh.write(new_stored)
            fh.seek(dir_offset + target * DIR_RECORD_SIZE)
            fh.write(_dir_record(entry_id, r1, target,
                                 len(new_stored), doff))
            mode = "inplace"
        else:
            new_doff = dir_offset
            new_end = new_doff + len(new_stored)
            for i, (off, ln) in enumerate(spans):
                if i != target and off < new_end \
                        and new_doff < off + ln:
                    raise _RebuildNeeded("包内负载与目录交叠")
            records = bytearray(dir_data)
            start = target * DIR_RECORD_SIZE
            records[start:start + DIR_RECORD_SIZE] = _dir_record(
                entry_id, r1, target, len(new_stored), new_doff)
            fh.seek(new_doff)
            fh.write(new_stored)
            fh.write(bytes(records))  # 紧接新负载之后就是新目录
            fh.seek(0)
            fh.write(_HEADER.pack(MAGIC, count,
                                  new_doff + len(new_stored)))
            mode = "relocated"
        fh.flush()
        fh.seek(0, 2)
        size = fh.tell()
    return {"mode": mode, "target_index": target, "bytes": size}


def patch_dlg_entry_in_file(pack_path, res_path: str,
                            new_plain: bytes) -> dict:
    """把 pack_path 里 res_path 条目换成 new_plain，只写补丁字节。

    - 新负载能放进原位置（含其后的间隙）：原位写入负载 + 该
      条目录记录（mode="inplace"，文件大小不变）；
    - 放不下：新负载写到目录原址、目录顺移到其后并更新头部
      目录偏移，其余条目偏移不变（mode="relocated"）；
    - 负载交叠的病态包抛 _RebuildNeeded，交调用方回退重组。

    返回 {"mode", "target_index", "bytes"}。文件须可写；原地
    修改的风险由调用方把控（编辑器侧默认先复制、选原文件时
    有强警告）。
    """
    path = Path(pack_path)
    plan = _plan_patch(path, res_path, new_plain)
    entry_id = mx_hash(res_path.encode("gbk", "replace"))
    raw = _RECORD.unpack_from(
        plan.dir_data, plan.target * DIR_RECORD_SIZE)
    return _write_located(
        path, count=plan.count, dir_offset=plan.dir_offset,
        dir_data=plan.dir_data, spans=plan.spans, target=plan.target,
        entry_id=entry_id, r1=raw[1], doff=plan.doff,
        limit=plan.limit, new_stored=plan.new_stored)


def patch_raw_entry_in_file(pack_path, entry_id: int,
                            new_stored: bytes) -> dict:
    """按 entry_id 写入任意条目的存储字节（图片/音频等原样数据）。

    条目已存在同 _write_located 的原位/迁移规则；不存在则新增：
    负载写在目录原址，目录按 entry_id 升序整表重写（新记录以
    :func:`fresh_r1` 插入有序位置，其后记录的下标变化，r3 按
    新下标重算——见模块文档的目录不变量；源目录若已乱序也因此
    顺带修复）。返回 {"mode", "target_index", "bytes"}，
    target_index 为新记录在有序目录中的位置。
    """
    path = Path(pack_path)
    file_size, count, dir_offset, dir_data, spans, records = \
        _read_index(path)
    for target, raw in enumerate(records):
        if raw[0] == entry_id:
            doff, _clen = spans[target]
            return _write_located(
                path, count=count, dir_offset=dir_offset,
                dir_data=dir_data, spans=spans, target=target,
                entry_id=entry_id, r1=raw[1], doff=doff,
                limit=_fit_limit(spans, doff, dir_offset, file_size),
                new_stored=new_stored)
    # 负载 + 新目录都写在目录原址起的连续区，与他条负载交叠则回退重组
    new_end = dir_offset + len(new_stored) + (count + 1) * DIR_RECORD_SIZE
    for off, ln in spans:
        if off < new_end and dir_offset < off + ln:
            raise _RebuildNeeded("新增条目与包内负载交叠")
    order = sorted(range(count), key=lambda i: records[i][0])
    sorted_ids = [records[i][0] for i in order]
    pos = bisect.bisect_left(sorted_ids, entry_id)
    rows = [(records[i][0], records[i][1] or fresh_r1(records[i][0]),
             spans[i][1], spans[i][0]) for i in order]
    rows.insert(pos, (entry_id, fresh_r1(entry_id),
                      len(new_stored), dir_offset))
    new_dir = b"".join(
        _dir_record(eid, r1, index, clen, doff)
        for index, (eid, r1, clen, doff) in enumerate(rows))
    with open(path, "r+b") as fh:
        fh.seek(dir_offset)
        fh.write(new_stored)
        fh.write(new_dir)
        fh.seek(0)
        fh.write(_HEADER.pack(MAGIC, count + 1,
                              dir_offset + len(new_stored)))
        fh.flush()
        fh.seek(0, 2)
        size = fh.tell()
    return {"mode": "added", "target_index": pos, "bytes": size}


def patch_pack_copy(archive_path, res_path: str, new_plain: bytes,
                    out_path, extra_entries: dict | None = None) -> dict:
    """把 res_path 条目的新内容落到 out_path，返回补丁报告。

    out 与源包不同：先整文件复制（系统级顺序拷贝）再在副本上
    打补丁，源包一字节不动；out 就是源包本身（用户明确覆盖
    时）：直接在原文件上打补丁，只写几 KB。校验由调用方完成。

    extra_entries 为 {资源路径: 存储字节}：随布局一并写入的
    附加条目（如本次编辑新加的图片），路径已存在则替换其内容，
    不存在则按路径哈希新增（排序插入，维持目录升序不变量）。
    源包目录若已乱序（旧版写坏的包）或负载交叠无法快速补丁，
    回退整包重组（build_archive 排序写目录，顺带修复）。

    报告以 images_added/images_replaced 汇报，并以 changed_ids
    给出允许内容不同的条目号集合（布局条目与被替换的附加
    条目；新增条目不在内，其下标会平移其后条目，故校验须按
    条目号而非序号比对）。
    """
    src, out = Path(archive_path), Path(out_path)
    extras = dict(extra_entries or {})
    try:
        same = src.resolve() == out.resolve()
    except OSError:
        same = str(src) == str(out)
    plan = _plan_patch(src, res_path, new_plain)  # 先只读侦察，失败不落盘
    src_ids = [_RECORD.unpack_from(plan.dir_data, i * DIR_RECORD_SIZE)[0]
               for i in range(plan.count)]
    need_rebuild = any(a > b for a, b in
                       zip(src_ids, src_ids[1:], strict=False))
    added: list[str] = []
    replaced: list[str] = []

    def apply_extras() -> None:
        added.clear()
        replaced.clear()
        for name in sorted(extras):
            result = patch_raw_entry_in_file(
                out, mx_hash(name.encode("gbk", "replace")),
                extras[name])
            (added if result["mode"] == "added"
             else replaced).append(name)

    info: dict | None = None
    if not need_rebuild:
        try:
            if not same:
                with open(src, "rb") as fin, open(out, "wb") as fout:
                    shutil.copyfileobj(fin, fout, 8 * 1024 * 1024)
            info = patch_dlg_entry_in_file(out, res_path, new_plain)
            apply_extras()
        except _RebuildNeeded:  # 病态包回退整包重组（慢，但正确）
            need_rebuild = True
    if need_rebuild:
        out.write_bytes(replace_dlg_entry(src.read_bytes(),
                                          res_path, new_plain))
        apply_extras()
        info = {"mode": "rebuild", "target_index": -1}
    layout_id = mx_hash(res_path.encode("gbk", "replace"))
    info["images_added"] = added
    info["images_replaced"] = replaced
    info["changed_ids"] = sorted(
        {layout_id} | {mx_hash(n.encode("gbk", "replace"))
                       for n in replaced})
    info["bytes"] = out.stat().st_size
    info["out"] = str(out)
    return info


def replace_dlg_entry_to_file(archive_path, res_path: str,
                              new_plain: bytes, out_path) -> int:
    """把源包中 res_path 条目换成 new_plain，写到 out_path。

    实现为 :func:`patch_pack_copy`（复制 + 原位补丁，不再整体
    重组）；返回写出的总字节数。校验由调用方完成。
    """
    return patch_pack_copy(archive_path, res_path,
                           new_plain, out_path)["bytes"]
