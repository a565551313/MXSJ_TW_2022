#!/usr/bin/env python3
"""Fake mx.exe client for offline testing of tools/login_server.py.

We invent a keystream K, encrypt with it exactly like the real client would,
then check that the server's harvest + alignment + encrypted replies round-trip.
"""
import socket
import struct
import sys

HOST, PORT = "127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 3999
NAME, PWD = b"testacc", b"testpwd"
K = lambda i: (i * 37 + 11) & 0xFF          # invented keystream

# ---- C2GS_ACCOUNT_ENTER body, as netlogin.C2SLoginIn builds it
body = bytearray()
body += bytes([1])              # cmd
body += bytes([0x10, 0x20])     # iScriptV1, CLIENT_VERSION[1]
body += struct.pack("<H", 0x30)                     # CLIENT_VERSION[2]
body += NAME.ljust(32, b"\x00")
body += PWD.ljust(20, b"\x00")
body += bytes(81 - len(body))   # rest: version/localip/adsid/... (fixed part is 81)
assert len(body) == 81, len(body)

s = socket.create_connection((HOST, PORT), timeout=10)
hello = s.recv(64)
print("HELLO   :", hello.hex(" "))

# frame 1: ANSWERHELLO, 25 bytes, cipher offsets 0..24
f1 = bytes(K(i) ^ ((i * 5 + 1) & 0xFF) for i in range(25))
s.sendall(bytes([len(f1)]) + f1)

# frame 2: ACCOUNT_ENTER, cipher offsets 25..25+80
f2 = bytes(body[j] ^ K(25 + j) for j in range(len(body)))
s.sendall(bytes([len(f2)]) + f2)
print("sent 2 frames (25 + 81 body bytes)")

# ---- read everything the server sends back
data = b""
s.settimeout(5)
try:
    while True:
        c = s.recv(65536)
        if not c:
            break
        data += c
except socket.timeout:
    pass
print("server->client raw:", data.hex(" "))

# ---- decode frames; recv cipher starts at 0, server padded 30 bytes first
pos, off, frames = 0, 0, []
while pos < len(data):
    n = data[pos]
    if n == 0xFF:
        n = struct.unpack_from("<H", data, pos + 1)[0]
        raw, adv = data[pos + 3:pos + 3 + n], 3 + n
    else:
        raw, adv = data[pos + 1:pos + 1 + n], 1 + n
    frames.append(bytes(b ^ K(off + i) for i, b in enumerate(raw)))
    off += len(raw)
    pos += adv

print("\ndecoded %d frames:" % len(frames))
for i, f in enumerate(frames):
    if i == 0:
        print("  [pad  ] %d B (junk, expected)" % len(f))
    else:
        print("  [frame] cmd=%d  %s" % (f[0], f.hex(" ")))

ok = False
if len(frames) >= 3:
    a, p = frames[1], frames[2]
    if a[0] == 15 and len(a) == 7:
        cnt, tm, vid = struct.unpack_from("<BIB", a, 1)
        print("\nLOGIN_ACCOUNT_INFO -> Count=%d CurTime=%d vid=%d" % (cnt, tm, vid))
    if p[0] == 3 and len(p) == 38:
        (rid, rt, icon, shape, desc, lvl, sch, race, prep,
         point) = struct.unpack("<IIBHHBBBBi", p[1:22])
        nm = p[22:38].rstrip(b"\x00").decode("big5hkscs", "replace")
        print("LOGIN_PLAYER_INFO  -> ID=%d Level=%d School=%d Race=%d Point=%d Name=%r"
              % (rid, lvl, sch, race, point, nm))
        ok = True
print("\nRESULT:", "PASS" if ok else "FAIL")
s.close()
