#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Loopback login server: HELLO -> capture -> keystream harvest -> role list.

Additive to hello_server.py (that file is untouched).  This one goes further:
it tries to get the client from the account-login page to the role-select
screen, WITHOUT knowing the game-channel cipher.

WHY THIS IS POSSIBLE
--------------------
The cipher bodies live in the runtime-decrypted `_dyprot0/1` sections
(entropy 7.85 / 7.72 on disk), so we cannot compute the keystream ourselves.
But we do not have to:

1. `netlogin.C2SLoginIn` writes the account as a **fixed 32-byte** field and
   the password as a **fixed 20-byte** field, at body offsets 5..56
   (see notes/login-packets-20261011.md).  We know those 52 bytes.
2. Both directions are initialised from the same seed with the same key
   material, so keystream_send[i] == keystream_recv[i] == K[i].
3. Therefore  K[off+5 .. off+56] = ciphertext[5..56] XOR (name32 + pwd20),
   where `off` is the send-cipher position when the packet was sent.
4. The recv-cipher starts at the same position.  Sending `--pad` junk bytes
   first advances it into the region we know -- so we never need to learn the
   absolute skip value, only that both sides start equal.

WHAT IT DOES
------------
  * sends GS2C_HELLO exactly like hello_server.py
  * decodes client frames ([1B len], 0xFF escape) and logs them
  * on the 2nd frame (assumed C2GS_ACCOUNT_ENTER) harvests 52 keystream bytes
    and appends them to a keystream file keyed by absolute offset
  * if enough keystream is known, optionally sends LOGIN_ACCOUNT_INFO (15)
    and LOGIN_PLAYER_INFO (3) so the client reaches selectrole.Show(True)

Binds 127.0.0.1 only.  Never contacts any external address.

Usage:
    python3 login_server.py --account myacct --password mypass
    python3 login_server.py --account myacct --password mypass --send-login
"""

import argparse
import datetime
import json
import os
import socket
import struct
import threading

# ==========================================================================
# 在这里填账号密码
# --------------------------------------------------------------------------
# 必须和你在游戏登录框里敲的**完全一致**（含大小写）。这两个字符串会被编码成
# Big5、补零到 32 / 20 字节，再和收到的密文异或出密钥流。填错了收割出来的
# 52 字节就是垃圾，而且会写进 keystream.json 污染后续运行 —— 出错就删掉
# tools/keystream.json 重来。
#
# 第一次测建议**纯英文/数字**：ASCII 在 Big5 / GBK / UTF-8 下都一样，
# 不会因为编码问题对不上。中文账号也能用，但要先确认能正常存成 UTF-8。
# ==========================================================================
ACCOUNT = ""
PASSWORD = ""

HOST = "127.0.0.1"
GS2C_HELLO = 1
GS2C_LOGIN_ACCOUNT_INFO = 15
GS2C_LOGIN_PLAYER_INFO = 3

# netlogin.C2SLoginIn layout: cmd(1) + iScriptV1(1) + CV1(1) + CV2(2) = 5,
# then PacketAddS(name, 32) and PacketAddS(pwd, 20).
KNOWN_OFFSET = 5
NAME_LEN = 32
PWD_LEN = 20
KNOWN_LEN = NAME_LEN + PWD_LEN          # 52


# ------------------------------------------------------------------ frames
def build_frame(body: bytes) -> bytes:
    """Server->client framing: [1B len][body]; 0xFF escape for long bodies."""
    n = len(body)
    if n < 0xFF:
        return bytes([n]) + body
    return b"\xff" + struct.pack("<H", n) + body


class FrameReader:
    """Client->server framing. Length byte is NOT encrypted; body is."""

    def __init__(self):
        self.buf = bytearray()

    def feed(self, data):
        self.buf += data
        out = []
        while True:
            if not self.buf:
                break
            n = self.buf[0]
            need = 1 + n
            if n == 0xFF:
                if len(self.buf) < 3:
                    break
                n = struct.unpack_from("<H", self.buf, 1)[0]
                need = 3 + n
            if len(self.buf) < need:
                break
            out.append(bytes(self.buf[1:1 + n]) if self.buf[0] != 0xFF
                       else bytes(self.buf[3:3 + n]))
            del self.buf[:need]
        return out


# -------------------------------------------------------------- keystream
class KeyStream:
    """Sparse keystream table: absolute offset -> byte."""

    def __init__(self, path):
        self.path = path
        self.k = {}
        if path and os.path.exists(path):
            try:
                self.k = {int(a): int(b) for a, b in json.load(open(path)).items()}
            except Exception:
                self.k = {}

    def learn(self, off, plain, cipher):
        n = 0
        for i, p in enumerate(plain):
            self.k[off + i] = cipher[i] ^ p
            n += 1
        return n

    def covers(self, off, length):
        return all((off + i) in self.k for i in range(length))

    def crypt(self, off, body):
        return bytes(body[i] ^ self.k[off + i] for i in range(len(body)))

    def save(self):
        if self.path:
            tmp = self.path + ".tmp"
            json.dump({str(a): b for a, b in sorted(self.k.items())},
                      open(tmp, "w"))
            os.replace(tmp, self.path)

    def ranges(self):
        if not self.k:
            return "empty"
        xs = sorted(self.k)
        out, start, prev = [], xs[0], xs[0]
        for x in xs[1:]:
            if x == prev + 1:
                prev = x
                continue
            out.append((start, prev))
            start = prev = x
        out.append((start, prev))
        return ", ".join("0x%x-0x%x" % (a, b) if a != b else "0x%x" % a
                         for a, b in out)


# ---------------------------------------------------------------- packets
def build_hello(seed, server_num, cert):
    body = bytes([GS2C_HELLO]) + struct.pack("<IHB", seed & 0xFFFFFFFF,
                                             server_num & 0xFFFF, cert & 0xFF)
    return build_frame(body)


def build_account_info(count, curtime, vid):
    body = bytes([GS2C_LOGIN_ACCOUNT_INFO]) + struct.pack("<BIB", count, curtime, vid)
    return build_frame(body)


def build_player_info(role):
    b = bytearray([GS2C_LOGIN_PLAYER_INFO])
    b += struct.pack("<I", role["ID"])
    b += struct.pack("<I", role["time"])
    b += struct.pack("<B", role["Icon"])
    b += struct.pack("<H", role["Shape"])
    b += struct.pack("<H", role["Desc"])
    b += struct.pack("<B", role["Level"])
    b += struct.pack("<B", role["School"])
    b += struct.pack("<B", role["Race"])
    b += struct.pack("<B", role["iPrepareLoad"])
    b += struct.pack("<i", role["Point"])
    nm = role["Name"].encode("big5hkscs", "replace")[:16]
    b += nm + b"\x00" * (16 - len(nm))
    return build_frame(bytes(b))


def log(fp, msg):
    line = "%s %s" % (datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], msg)
    print(line, flush=True)
    fp.write(line + "\n")
    fp.flush()


# ----------------------------------------------------------------- session
def handle(conn, peer, args, fp, idx, ks):
    tag = "[conn%d]" % idx
    log(fp, "%s accepted from %s:%d" % (tag, peer[0], peer[1]))
    conn.settimeout(args.idle)

    hello = build_hello(args.seed, args.server_num, args.cert)
    conn.sendall(hello)
    log(fp, "%s sent GS2C_HELLO %d B: %s" % (tag, len(hello), hello.hex(" ")))

    # cipher positions.  Both start at the (unknown) skip; we only track
    # offsets relative to it, which is all we need.
    send_pos = 0        # bytes of *body* the client has sent
    recv_pos = 0        # bytes of *body* we have sent
    frames = 0
    fr = FrameReader()
    logged_harvest = False

    try:
        while True:
            try:
                data = conn.recv(65536)
            except socket.timeout:
                log(fp, "%s idle %ds, still connected" % (tag, args.idle))
                continue
            if not data:
                break
            log(fp, "%s recv %d B raw: %s" % (tag, len(data), data.hex(" ")))
            for body in fr.feed(data):
                frames += 1
                start = send_pos
                send_pos += len(body)
                log(fp, "%s   frame#%d body %d B (cipher 0x%x-0x%x): %s"
                    % (tag, frames, len(body), start, start + len(body) - 1,
                       body.hex(" ")))

                # ---- harvest: the login packet is the first non-empty frame
                # long enough to hold name+pwd.  Zero-length frames (e.g. the
                # trailing 0x00 length bytes after ANSWERHELLO) must not count
                # as a frame index.
                if not body:
                    continue
                if (args.account and
                        len(body) >= KNOWN_OFFSET + KNOWN_LEN and
                        not logged_harvest):
                    plain = (args.account.encode("big5hkscs", "replace")[:NAME_LEN]
                             .ljust(NAME_LEN, b"\x00") +
                             args.password.encode("big5hkscs", "replace")[:PWD_LEN]
                             .ljust(PWD_LEN, b"\x00"))
                    got = ks.learn(start + KNOWN_OFFSET, plain,
                                   body[KNOWN_OFFSET:KNOWN_OFFSET + KNOWN_LEN])
                    ks.save()
                    logged_harvest = True
                    log(fp, "%s   HARVEST %d keystream bytes at 0x%x-0x%x -> %s"
                        % (tag, got, start + KNOWN_OFFSET,
                           start + KNOWN_OFFSET + got - 1, ks.path))
                    log(fp, "%s   keystream now covers: %s" % (tag, ks.ranges()))

                    if args.send_login:
                        try:
                            send_login(conn, fp, tag, ks, recv_pos, args)
                        except Exception as e:
                            log(fp, "%s   send_login failed: %s" % (tag, e))
                    elif args.probe:
                        probe(conn, fp, tag, ks, recv_pos, args)
    except OSError as e:
        log(fp, "%s error: %s" % (tag, e))
    finally:
        conn.close()
        log(fp, "%s closed after %d frames" % (tag, frames))


def probe(conn, fp, tag, ks, recv_pos, args):
    """Advance the recv cipher into a region we know, using junk bytes.

    The decrypted junk will not match any cmd, so net.py should ignore it.
    """
    if recv_pos >= args.known_start:
        return 0
    n = args.known_start - recv_pos
    junk = bytes((i * 7 + 3) & 0xFF for i in range(n))
    conn.sendall(build_frame(junk))
    log(fp, "%s   PROBE sent %d junk body bytes (recv cipher now 0x%x)"
        % (tag, n, args.known_start))
    return n


def send_login(conn, fp, tag, ks, recv_pos, args):
    """Pad into the known region, then send the two login replies encrypted."""
    recv_pos += probe(conn, fp, tag, ks, recv_pos, args)

    info = build_account_info(args.count, args.curtime, args.vid)
    role = build_player_info(dict(ID=args.role_id, time=args.role_time,
                                  Icon=args.role_icon, Shape=args.role_shape,
                                  Desc=args.role_desc, Level=args.role_level,
                                  School=args.role_school, Race=args.role_race,
                                  iPrepareLoad=args.role_prepare,
                                  Point=args.role_point, Name=args.role_name))

    need = (len(info) - 1) + (len(role) - 1)
    if not ks.covers(recv_pos, need):
        log(fp, "%s   NOT ENOUGH KEYSTREAM: need %d B at 0x%x, have %s"
            % (tag, need, recv_pos, ks.ranges()))
        return
    if args.dry_run:
        log(fp, "%s   dry-run: would send %d B of login replies at 0x%x"
            % (tag, need, recv_pos))
        return

    out = b""
    pos = recv_pos
    for frame in (info, role):
        body = frame[1:]
        out += bytes([len(body)]) + ks.crypt(pos, body)
        pos += len(body)
    conn.sendall(out)
    log(fp, "%s   SENT login replies: LOGIN_ACCOUNT_INFO(%d) + LOGIN_PLAYER_INFO(%d)"
        % (tag, len(info) - 1, len(role) - 1))
    log(fp, "%s   cipher bytes: %s" % (tag, out.hex(" ")))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=3134)
    ap.add_argument("--seed", type=lambda s: int(s, 0), default=0x12345678)
    ap.add_argument("--server-num", type=int, default=1)
    ap.add_argument("--cert", type=int, default=0)
    ap.add_argument("--idle", type=int, default=30)

    ap.add_argument("--account", default=ACCOUNT,
                    help="exact account string you will type (default: the ACCOUNT "
                         "constant near the top of this file)")
    ap.add_argument("--password", default=PASSWORD,
                    help="exact password you will type (default: the PASSWORD "
                         "constant near the top of this file)")

    ap.add_argument("--send-login", action="store_true",
                    help="after harvesting, send LOGIN_ACCOUNT_INFO + LOGIN_PLAYER_INFO")
    ap.add_argument("--probe", action="store_true",
                    help="send the alignment junk packet and stop")
    ap.add_argument("--dry-run", action="store_true",
                    help="do everything except actually write the login replies")
    ap.add_argument("--known-start", type=lambda s: int(s, 0), default=0x1E,
                    help="recv-cipher offset to pad to before sending; default 0x1E "
                         "(5 + 25: the ANSWERHELLO body plus the 5 header bytes). "
                         "Use 0x5 if NakedSend turns out to be unencrypted.")

    ap.add_argument("--keystream", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "keystream.json"))

    ap.add_argument("--count", type=int, default=1, help="role count")
    ap.add_argument("--curtime", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--vid", type=int, default=1, help="1, 2 or 3 (else KeyError)")
    ap.add_argument("--role-id", type=lambda s: int(s, 0), default=1)
    ap.add_argument("--role-time", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--role-icon", type=int, default=1)
    ap.add_argument("--role-shape", type=int, default=0)
    ap.add_argument("--role-desc", type=int, default=0)
    ap.add_argument("--role-level", type=int, default=1)
    ap.add_argument("--role-school", type=int, default=0)
    ap.add_argument("--role-race", type=int, default=0)
    ap.add_argument("--role-prepare", type=int, default=0)
    ap.add_argument("--role-point", type=int, default=0)
    ap.add_argument("--role-name", default="Tester")

    ap.add_argument("--logdir", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "captures"))
    args = ap.parse_args()

    os.makedirs(args.logdir, exist_ok=True)
    path = os.path.join(args.logdir, "login-%s.log"
                        % datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    fp = open(path, "w", encoding="utf-8")
    ks = KeyStream(args.keystream)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, args.port))
    srv.listen(8)
    log(fp, "listening on %s:%d  hello=%s" % (HOST, args.port,
                                              build_hello(args.seed, args.server_num, args.cert).hex(" ")))
    log(fp, "keystream file: %s  (covers: %s)" % (ks.path, ks.ranges()))
    log(fp, "account=%r password=%r known_start=0x%x send_login=%s"
        % (args.account, args.password, args.known_start, args.send_login))
    if not args.account:
        log(fp, "WARNING: no account configured -> keystream harvesting will be "
                "skipped and --send-login will find no keystream. Edit the ACCOUNT "
                "/ PASSWORD constants near the top of this file, or pass --account.")
    idx = 0
    try:
        while True:
            conn, peer = srv.accept()
            idx += 1
            threading.Thread(target=handle, args=(conn, peer, args, fp, idx, ks),
                             daemon=True).start()
    except KeyboardInterrupt:
        log(fp, "stopped")


if __name__ == "__main__":
    main()
