#!/usr/bin/env python3
"""Loopback-only hello server: lets the client go from server selection to the account login page.

Basis (static analysis, see notes/hello-path-20261011.md):
  - Login happens in two steps. The client connects and **sends nothing first**; it waits for the server's GS2C_HELLO (cmd=1).
  - S2C frame (mx.exe CNetClient receive path 0x4AB540, before encryption is enabled):
        [1 byte length L] [L bytes body]      (if L==0xFF, the next 2 bytes are the real length, little-endian)
        body = [1 byte cmd] [payload]
  - netlogin.S2CHello reads: UnpackInt(4)=seed, UnpackInt(2)=g_ServerNum, UnpackInt(1)=isUseCertServer (little-endian)
    then: SetSeed -> m_Hello=True -> NakedSend(reply) -> selectserver.Show(False) -> loginin.ShowLogin()

Usage:
    python3 hello_server.py                 # listen on 127.0.0.1:3134 and send the hello immediately after accept
    python3 hello_server.py --no-hello      # control run: only record, send nothing
Binds only to 127.0.0.1. Does not connect to any external address.
"""
import argparse
import datetime
import os
import socket
import struct
import threading

HOST = "127.0.0.1"
GS2C_HELLO = 1


def build_hello(seed: int, server_num: int, cert: int) -> bytes:
    body = bytes([GS2C_HELLO]) + struct.pack("<IHB", seed & 0xFFFFFFFF, server_num & 0xFFFF, cert & 0xFF)
    assert len(body) < 0xFF
    return bytes([len(body)]) + body


def log(fp, msg):
    line = "%s %s" % (datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], msg)
    print(line, flush=True)
    fp.write(line + "\n")
    fp.flush()


def handle(conn, peer, args, fp, idx):
    tag = "[conn%d %s:%d]" % (idx, peer[0], peer[1])
    log(fp, "%s accepted" % tag)
    total = 0
    try:
        if not args.no_hello:
            pkt = build_hello(args.seed, args.server_num, args.cert)
            conn.sendall(pkt)
            log(fp, "%s sent GS2C_HELLO %d B: %s" % (tag, len(pkt), pkt.hex(" ")))
        conn.settimeout(args.idle)
        while True:
            try:
                data = conn.recv(65536)
            except socket.timeout:
                log(fp, "%s no data for %ds, still waiting (connection kept open)" % (tag, args.idle))
                continue
            if not data:
                break
            total += len(data)
            log(fp, "%s recv %d B: %s" % (tag, len(data), data.hex(" ")))
    except OSError as e:
        log(fp, "%s error: %s" % (tag, e))
    finally:
        conn.close()
        log(fp, "%s closed, received %d B total" % (tag, total))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=3134)
    ap.add_argument("--seed", type=lambda s: int(s, 0), default=0x12345678)
    ap.add_argument("--server-num", type=int, default=1)
    ap.add_argument("--cert", type=int, default=0, help="isUseCertServer, default 0 (no certificate login)")
    ap.add_argument("--no-hello", action="store_true", help="do not send the hello (control run)")
    ap.add_argument("--idle", type=int, default=30)
    ap.add_argument("--logdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "captures"))
    args = ap.parse_args()

    os.makedirs(args.logdir, exist_ok=True)
    path = os.path.join(args.logdir, "hello-%s.log" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    fp = open(path, "w", encoding="utf-8")
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, args.port))
    srv.listen(8)
    log(fp, "listening on %s:%d, hello=%s, log=%s" % (
        HOST, args.port, "OFF" if args.no_hello else build_hello(args.seed, args.server_num, args.cert).hex(" "), path))
    idx = 0
    try:
        while True:
            conn, peer = srv.accept()
            idx += 1
            threading.Thread(target=handle, args=(conn, peer, args, fp, idx), daemon=True).start()
    except KeyboardInterrupt:
        log(fp, "stopped")


if __name__ == "__main__":
    main()
