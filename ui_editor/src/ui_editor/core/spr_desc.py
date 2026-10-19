"""`.spr` 界面特效描述符解码（纯逻辑、无 Qt）。

界面特效的 ``.spr`` **不是图像**：是 4 字节循环 XOR 加密的 INI 文本
帧时表（2026-10-19 对官服 interface.fls 56 个 .spr 实测：53 个首行
``[frames]``，每行「帧号 时长」；另有 ``[info]`` 类变体）。同目录
**同名 `.igs` 精灵**提供像素，``.spr`` 只定义播放节奏——故编辑器
旧逻辑把它当图片解码必然失败、画布只能占位。

解码顺序：候选段名前缀反推 4 字节密钥 → 列频率恢复 → 小文件可打印
前缀穷举。任一步得到「全可打印且形如 INI」的文本即接受。
"""

from __future__ import annotations

__all__ = ["decode_spr_text", "parse_frame_table", "frame_sources",
           "parse_images"]


def _xor4(data: bytes, key: bytes) -> bytes:
    """4 字节循环 XOR（整数整体异或，穷举时比逐字节快得多）。"""
    if not data:
        return data
    repeated = (key * (len(data) // 4 + 1))[:len(data)]
    return (int.from_bytes(data, "little")
            ^ int.from_bytes(repeated, "little")).to_bytes(len(data), "little")

#: 已知首段名（官服实测 [frames] 为主，其余为变体余量）
_SECTION_PREFIXES = (
    b"[frames]", b"[frame]", b"[info]", b"[information]",
    b"[sound]", b"[effect]", b"[anim]", b"[data]", b"[loop]",
)

_PRINTABLE = set(range(32, 127)) | {9, 10, 13}


def _looks_like_text(plain: bytes) -> bool:
    """INI 形态校验：``[段名]`` 首行 + 全可打印（段名限字母数字下划线）。"""
    if not plain or plain[0:1] != b"[":
        return False
    if not all(b in _PRINTABLE for b in plain):
        return False
    close = plain.find(b"]")
    if not 2 <= close <= 24:
        return False
    body = plain[1:close]
    return all(48 <= b <= 57 or 65 <= b <= 90 or 97 <= b <= 122 or b == 95
               for b in body)


def _freq_key(data: bytes) -> bytes:
    favourites = set(b" etaoinshrdlu=(){}_#'\"0123456789.,:[]\n\t<>")
    key = bytearray(4)
    for col in range(4):
        column = data[col::4][:512]
        best_score, best = -1, 0
        for cand in range(256):
            score = sum(1 for b in column if (b ^ cand) in favourites)
            if score > best_score:
                best_score, best = score, cand
        key[col] = best
    return bytes(key)


def _score(plain: bytes) -> int:
    """INI 结构分：帧行（`N D`）各 +2，形如 [section] 的行 +1；

    帧表从 0 号帧起（官服 56 例皆然）再 +3——短表被错误密钥改写
    成「同样干净但首帧非 0」的假解时靠它分出真伪。
    """
    text = plain.decode("ascii", "replace")
    score = 0
    first_pair: tuple[str, str] | None = None
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        parts = s.replace("\t", " ").split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            score += 2
            if first_pair is None:
                first_pair = (parts[0], parts[1])
        elif s.startswith("[") and s.endswith("]") and 2 <= len(s) <= 24:
            score += 1
    if first_pair is not None and first_pair[0] == "0":
        score += 3
    return score


def decode_spr_text(data: bytes) -> str | None:
    """XOR 密文 → INI 文本；不像 `.spr` 返回 None（不猜）。

    候选（段名前缀反推 → 频率恢复 → 小文件穷举）里可能撞出
    「可打印假阳性」，故收集全部通过形态校验的解，取帧表结构分最高。
    """
    if not data or len(data) < 8:
        return None
    candidates: list[bytes] = []
    for prefix in _SECTION_PREFIXES:
        key = bytes(a ^ b for a, b in zip(data[:4], prefix[:4], strict=False))
        plain = _xor4(data, key)
        if _looks_like_text(plain):
            candidates.append(plain)
    plain = _xor4(data, _freq_key(data))
    if _looks_like_text(plain):
        candidates.append(plain)
    best: bytes | None = max(candidates, key=_score) if candidates else None
    best_score = _score(best) if best is not None else 0
    # 前缀/频率没找到带帧行的解才穷举（假阳性不得挡住真解）；
    # 穷举解需结构分 ≥3 才能翻盘，纯 [info] 小表保留前缀解。
    if best_score < 2 and len(data) <= 512:
        head = data[:4]
        brute_plain: bytes | None = None
        brute_score = 0
        for a in range(32, 127):
            for b in range(32, 127):
                for c in range(32, 127):
                    key = bytes((head[0] ^ ord("["), head[1] ^ a,
                                 head[2] ^ b, head[3] ^ c))
                    plain = _xor4(data, key)
                    if _looks_like_text(plain):
                        score = _score(plain)
                        if score > brute_score:
                            brute_plain, brute_score = plain, score
        if brute_plain is not None and brute_score >= 3:
            best, best_score = brute_plain, brute_score
    if best is None:
        return None
    return best.decode("ascii", "strict")


def parse_frame_table(text: str) -> tuple[tuple[int, int], ...]:
    """INI 文本 → ((帧号, 时长), …)。

    ``[frames]`` 节内的数字按出现顺序两两成对（帧号, 时长）；
    分隔符任意（空格/制表/换行），非数字垃圾跳过。
    """
    nums: list[int] = []
    in_frames = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("["):
            in_frames = line.lower().startswith("[frames]")
            continue
        if not in_frames:
            continue
        for token in line.replace("\t", " ").split():
            if token.isdigit():
                nums.append(int(token))
    it = iter(nums)
    return tuple(zip(it, it, strict=False))  # 尾数落单丢弃


def frame_sources(name: str, text: str = "") -> tuple[str, ...]:
    """`X.spr` → 帧图像素候选（同名 `.igs` 优先，其次 `.png`）。

    `text` 给出解码后的描述符文本时，优先采用 `[images]` 节指明的
    ``FileName1..N``（与 .spr 同目录；``PackageName``/``BranchPath``
    指向外部 .fls 包，当前挂载查不到会自然落空）。
    """
    base = name[:-4] if name.lower().endswith(".spr") else name
    same_name = (f"{base}.igs", f"{base}.png")
    if not text:
        return same_name
    info = parse_images(text)
    if not info.get("files"):
        return same_name
    sep = "\\" if "\\" in base else ("/" if "/" in base else "")
    dir_prefix = base.rsplit(sep, 1)[0] + sep if sep else ""
    branch = str(info.get("branch", "") or "")
    branch = branch.replace("/", "\\")
    if branch and not branch.endswith("\\"):
        branch += "\\"
    package = str(info.get("package", "") or "")
    external = tuple(
        f"{package}:{branch}{f}" if package else f"{dir_prefix}{f}"
        for f in info["files"] if f
    )
    return external + same_name


def parse_images(text: str) -> dict:
    """`[images]` 外部指图节 → dict（无该节返回 {}）。

    官方 .spr 的另一形态（56 例中 2 例：combdialog\\特效\\及时雨/引天雷）：
    ``FileName1=magic0307.igs`` / ``PackageName=magic`` / ``BranchPath=
    res\\`` / ``PalPro=...``，像素在**别的 .fls 包**、不与 .spr 同名。
    返回 keys：files（FileName1..N 元组）、package、branch、palpro。
    """
    if not text:
        return {}
    files: list[str] = []
    package = branch = palpro = ""
    in_images = False
    seen = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("[") and line.endswith("]"):
            in_images = line[1:-1].strip().lower() == "images"
            seen = seen or in_images
            continue
        if not in_images or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip().lower(), val.strip()
        if key.startswith("filename"):
            if val:
                files.append(val)
        elif key.startswith("package"):
            package = val
        elif key.startswith("branch"):
            branch = val
        elif key.startswith("palpro"):
            palpro = val
    if not seen:
        return {}
    return {"files": tuple(files), "package": package,
            "branch": branch, "palpro": palpro}
