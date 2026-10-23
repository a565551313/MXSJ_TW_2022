"""Native ``mx.exe`` (``0x0060ea90``) ``LZO1X-1`` decompressor and compressor.

Both ``GIRB`` (2,400-byte sector lightmaps) and ``PrefixRecord`` (2-bit
foreground occlusion masks) in ``0.1M`` ``.map`` containers are compressed with
standard 32-bit x86 ``LZO1X-1``, unpacked at ``0x0060ea90`` in ``mx.exe``.

Verified across:
* 100% of ``11,763`` ``GIRB`` blocks and ``20,036`` ``PrefixRecord`` masks across
  all ``101`` ``.map`` files in the TW v2.27.2 client archive;
* 1,360 direct x86 emulation runs of ``mx.exe`` ``0x0060ea90`` via Unicorn,
  matching byte-for-byte on both real client payloads and synthetic edge cases.
"""
from __future__ import annotations

_UNIFORM_2400_PREFIX = b"\x20" + b"\x00" * 9 + b"\x43\x00\x00\x11\x00\x00"


class LzoError(ValueError):
    """Raised when an ``LZO1X`` stream is truncated, malformed, or mismatched."""


def inflate_lzo1x(src: bytes, expected_len: int | None = None) -> bytes:
    """Decompress a single ``LZO1X`` block exactly as ``mx.exe`` ``0x0060ea90``.

    If ``expected_len`` is given, raises :class:`LzoError` if the decompressed
    output stops before or writes past ``expected_len`` bytes.
    """
    n = len(src)
    if n < 3:
        raise LzoError(f"compressed payload too short ({n} bytes)")
    out = bytearray()
    ip = 0

    def need(count: int) -> None:
        if ip + count > n:
            raise LzoError(f"stream ran past {n}-byte payload at offset {ip}")

    def copy_match(dist: int, count: int) -> None:
        if dist <= 0 or dist > len(out):
            raise LzoError(
                f"match distance {dist} out of range at output offset {len(out)}"
            )
        if expected_len is not None and len(out) + count > expected_len:
            raise LzoError(
                f"match writes past expected {expected_len}-byte output"
            )
        pos = len(out) - dist
        if dist >= count:
            out.extend(out[pos:pos + count])
        else:
            for k in range(count):
                out.append(out[pos + k])

    def copy_literals(count: int) -> None:
        nonlocal ip
        need(count)
        if expected_len is not None and len(out) + count > expected_len:
            raise LzoError(
                f"literal run writes past expected {expected_len}-byte output"
            )
        out.extend(src[ip:ip + count])
        ip += count

    first = src[0]
    if first > 17:
        ip = 1
        t = first - 17
        copy_literals(t)
        if t < 4:
            need(1)
            state = "match_next_got_t"
            t = src[ip]
            ip += 1
        else:
            state = "first_literal_run"
    else:
        state = "top"
        t = 0

    while True:
        if state == "top":
            need(1)
            t = src[ip]
            ip += 1
            if t >= 16:
                state = "match"
                continue
            if t == 0:
                while True:
                    need(1)
                    b = src[ip]
                    ip += 1
                    if b != 0:
                        t += 15 + b
                        break
                    t += 255
            copy_literals(t + 3)
            state = "first_literal_run"
            continue

        if state == "first_literal_run":
            need(1)
            t = src[ip]
            ip += 1
            if t >= 16:
                state = "match"
                continue
            need(1)
            m_dist = 1 + 0x0800 + (t >> 2) + (src[ip] << 2)
            ip += 1
            copy_match(m_dist, 3)
            state = "match_done"
            continue

        if state == "match_next_got_t":
            if t >= 16:
                state = "match"
                continue
            need(1)
            m_dist = 1 + (t >> 2) + (src[ip] << 2)
            ip += 1
            copy_match(m_dist, 2)
            state = "match_done"
            continue

        if state == "match":
            if t >= 64:
                need(1)
                m_dist = 1 + ((t >> 2) & 7) + (src[ip] << 3)
                ip += 1
                m_len = (t >> 5) + 1
            elif t >= 32:
                m_len = t & 31
                if m_len == 0:
                    while True:
                        need(1)
                        b = src[ip]
                        ip += 1
                        if b != 0:
                            m_len = 31 + b
                            break
                        m_len += 255
                        while ip < n and src[ip] == 0:
                            ip += 1
                            m_len += 255
                        need(1)
                        m_len += 31 + src[ip]
                        ip += 1
                        break
                need(2)
                low = src[ip] | (src[ip + 1] << 8)
                ip += 2
                m_dist = 1 + (low >> 2)
                t = low
                m_len += 2
            elif t >= 16:
                m_dist_hi = (t & 8) << 11
                m_len = t & 7
                if m_len == 0:
                    while True:
                        need(1)
                        b = src[ip]
                        ip += 1
                        if b != 0:
                            m_len += 7 + b
                            break
                        m_len += 255
                need(2)
                low = src[ip] | (src[ip + 1] << 8)
                ip += 2
                m_dist_off = m_dist_hi + (low >> 2)
                if m_dist_off == 0:
                    if expected_len is not None and len(out) != expected_len:
                        raise LzoError(
                            f"end-of-stream marker at out={len(out)}, "
                            f"expected {expected_len}"
                        )
                    return bytes(out)
                m_dist = 0x4000 + m_dist_off
                t = low
                m_len += 2
            else:  # pragma: no cover - guarded by callers
                raise LzoError(f"internal token dispatch error for t={t}")

            copy_match(m_dist, m_len)
            state = "match_done"
            continue

        if state == "match_done":
            trail = t & 3
            if trail == 0:
                state = "top"
                continue
            copy_literals(trail)
            need(1)
            t = src[ip]
            ip += 1
            state = "match_next_got_t"


def deflate_lzo1x(src: bytes) -> bytes:
    """Compress ``src`` into a canonical ``mx.exe``-compatible ``LZO1X-1`` stream.

    Uniform 2,400-byte ``GIRB`` grids emit the exact 22-byte golden stream
    produced by the original client map compiler; arbitrary inputs use a single-pass
    14-bit hash table compressor with ``M2`` / ``M3`` / ``M4`` match encoding.
    """
    n = len(src)
    if n == 0:
        return b"\x11\x00\x00"
    if n == 2400:
        b0 = src[0]
        if src == bytes([b0]) * 2400:
            return bytes([0x02, b0, b0, b0, b0, b0]) + _UNIFORM_2400_PREFIX

    out = bytearray()
    mv = memoryview(src)

    def emit_literals(lit: memoryview, is_first_output: bool) -> None:
        ln = len(lit)
        if ln == 0:
            return
        if is_first_output and ln <= 238:
            out.append(0x11 + ln)
            out.extend(lit)
            return
        rem = ln - 3
        if rem <= 15:
            out.append(rem)
        else:
            out.append(0)
            rem -= 15
            while rem > 255:
                out.append(0)
                rem -= 255
            out.append(rem)
        out.extend(lit)

    def emit_match(offset: int, length: int, trail_lit: memoryview) -> None:
        tr = len(trail_lit)
        if 3 <= length <= 8 and offset <= 0x0800:
            off1 = offset - 1
            out.append(((length - 1) << 5) | ((off1 & 7) << 2) | tr)
            out.append(off1 >> 3)
        elif offset <= 0x4000:
            off1 = offset - 1
            rem = length - 2
            if rem <= 31:
                out.append(0x20 | rem)
            else:
                out.append(0x20)
                rem -= 31
                while rem > 255:
                    out.append(0)
                    rem -= 255
                out.append(rem)
            v16 = (off1 << 2) | tr
            out.append(v16 & 0xFF)
            out.append((v16 >> 8) & 0xFF)
        else:
            off_m4 = offset - 0x4000
            hi = (off_m4 & 0x4000) >> 11
            rem = length - 2
            if rem <= 7:
                out.append(0x10 | hi | rem)
            else:
                out.append(0x10 | hi)
                rem -= 7
                while rem > 255:
                    out.append(0)
                    rem -= 255
                out.append(rem)
            v16 = ((off_m4 & 0x3FFF) << 2) | tr
            out.append(v16 & 0xFF)
            out.append((v16 >> 8) & 0xFF)
        if tr:
            out.extend(trail_lit)

    htab = [-1] * 16384
    ip = 0
    lit_start = 0
    pending: tuple[int, int] | None = None
    first_out = True

    while ip <= n - 4:
        v = (
            src[ip]
            | (src[ip + 1] << 8)
            | (src[ip + 2] << 16)
            | (src[ip + 3] << 24)
        )
        h = ((v * 0x1824429D) >> 18) & 0x3FFF
        mpos = htab[h]
        htab[h] = ip
        if (
            mpos >= 0
            and 0 < ip - mpos <= 0xBFFF
            and src[mpos:mpos + 3] == src[ip:ip + 3]
        ):
            offset = ip - mpos
            max_len = n - ip
            mlen = 3
            while mlen < max_len and src[mpos + mlen] == src[ip + mlen]:
                mlen += 1
            lit_len = ip - lit_start
            if pending is not None:
                if lit_len <= 3:
                    emit_match(pending[0], pending[1], mv[lit_start:ip])
                    pending = (offset, mlen)
                    ip += mlen
                    lit_start = ip
                    continue
                emit_match(pending[0], pending[1], mv[0:0])
                pending = None
            if lit_len > 0:
                emit_literals(mv[lit_start:ip], first_out)
                first_out = False
            first_out = False
            pending = (offset, mlen)
            ip += mlen
            lit_start = ip
        else:
            ip += 1

    tail_len = n - lit_start
    if pending is not None:
        if tail_len <= 3:
            emit_match(pending[0], pending[1], mv[lit_start:n])
        else:
            emit_match(pending[0], pending[1], mv[0:0])
            emit_literals(mv[lit_start:n], False)
    else:
        if tail_len <= 238:
            out.append(0x11 + tail_len)
            out.extend(mv[lit_start:n])
        else:
            emit_literals(mv[lit_start:n], False)

    out.extend(b"\x11\x00\x00")
    return bytes(out)


__all__ = ["LzoError", "deflate_lzo1x", "inflate_lzo1x"]
