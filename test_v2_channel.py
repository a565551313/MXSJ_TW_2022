#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 mock_server_v2.py 的原生加密通道集成
"""

import socket
import struct
import sys
import threading
import time
from pathlib import Path

# 添加 native channel 到路径
sys.path.insert(0, str(Path(__file__).parent / "tools" / "native_channel" / "src"))
from mxsj_native_channel.core.channel import ClientHandshake, Channel

# 导入 mock_server_v2 的关键函数
sys.path.insert(0, str(Path(__file__).parent))
import mock_server_v2 as mock_v2


def test_unframe_function():
    """测试 _unframe 函数"""
    print("\n" + "=" * 60)
    print("测试 1: _unframe 函数")
    print("=" * 60)

    # 测试短包
    opcode = 69
    payload = b"test"
    framed = mock_v2.frame_gs2c(opcode, payload)
    print(f"原始: opcode={opcode}, payload={payload.hex()}")
    print(f"封帧: {framed.hex()}")

    opcode2, payload2 = mock_v2._unframe(framed)
    print(f"解帧: opcode={opcode2}, payload={payload2.hex()}")

    assert opcode2 == opcode, f"短包 opcode 不匹配: 期望 {opcode}, 实际 {opcode2}"
    assert payload2 == payload, f"短包 payload 不匹配: 期望 {payload.hex()}, 实际 {payload2.hex()}"
    print("✓ 短包测试通过")

    # 测试长包（>255 字节）
    opcode = 16
    payload = bytes(range(256)) * 2  # 512 字节
    framed = mock_v2.frame_gs2c(opcode, payload)
    print(f"\n长包: opcode={opcode}, payload={len(payload)}B")
    print(f"封帧: {len(framed)}B, 前 10 字节: {framed[:10].hex()}")

    opcode2, payload2 = mock_v2._unframe(framed)
    print(f"解帧: opcode={opcode2}, payload={len(payload2)}B")

    assert opcode2 == opcode, f"长包 opcode 不匹配: 期望 {opcode}, 实际 {opcode2}"
    assert payload2 == payload, f"长包 payload 不匹配: 长度期望 {len(payload)}, 实际 {len(payload2)}"
    print("✓ 长包测试通过")

    print("=" * 60)


def test_handshake_and_encrypted_communication():
    """测试握手和加密通信"""
    print("=" * 60)
    print("测试 2: 原生加密通道握手")
    print("=" * 60)

    seed = 0x12345678
    server_num = 3

    # 创建服务器 socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("127.0.0.1", 0))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]
    print(f"服务器监听端口: {port}")

    errors = []

    def server_thread():
        try:
            # Set timeout so we don't hang forever if client fails
            server_sock.settimeout(5.0)
            conn, addr = server_sock.accept()
            print(f"[服务器] 接受连接: {addr}")
            # Set timeout on the connection socket too
            conn.settimeout(5.0)

            # 发送 HELLO（明文）
            from mxsj_native_channel.core.channel import hello
            hello_bytes = hello(seed, server_num, 0)
            conn.sendall(hello_bytes)
            print(f"[服务器] 发送 HELLO: {hello_bytes.hex()}")

            # 接收 25 字节裸回复
            reply = conn.recv(25)
            if len(reply) != 25:
                errors.append(f"裸回复长度错误: {len(reply)}")
                return
            print(f"[服务器] 收到裸回复: {reply.hex()}")

            # 创建加密通道
            server_channel = Channel(seed, "server")
            print("[服务器] 加密通道已建立")

            # 发送一个测试包
            test_opcode = 69  # GS2C_HEART_BEAT
            test_payload = b""
            wire = server_channel.send(test_opcode, test_payload)
            conn.sendall(wire)
            print(f"[服务器] 发送加密包: opcode={test_opcode}, {len(wire)}B")

            # 接收客户端的测试包
            chunk = conn.recv(4096)
            packets = server_channel.feed(chunk)
            if not packets:
                errors.append("未收到客户端的包")
                return
            pkt = packets[0]
            print(f"[服务器] 收到加密包: opcode={pkt.command}, payload={pkt.payload.hex()}")

            if pkt.command != 109:  # C2GS_HEART_BEAT
                errors.append(f"opcode 错误: 期望 109, 实际 {pkt.command}")

            conn.close()
            print("[服务器] 测试完成 ✓")
        except Exception as e:
            errors.append(f"服务器异常: {e}")
            import traceback
            traceback.print_exc()

    def client_thread():
        try:
            time.sleep(0.1)  # 等待服务器启动
            client_sock = socket.create_connection(("127.0.0.1", port), timeout=5)
            print(f"[客户端] 连接到端口 {port}")

            # 使用 ClientHandshake 处理握手
            handshake = ClientHandshake()

            # 接收 HELLO
            hello_data = client_sock.recv(9)
            packets = handshake.feed(hello_data)
            print(f"[客户端] 收到 HELLO: {hello_data.hex()}")

            # 发送裸回复
            reply = handshake.take_reply()
            client_sock.sendall(reply)
            print(f"[客户端] 发送裸回复: {reply.hex()}")

            # 获取加密通道
            client_channel = handshake.channel
            if client_channel is None:
                errors.append("客户端通道未建立")
                return
            print("[客户端] 加密通道已建立")

            # 接收服务器的测试包
            chunk = client_sock.recv(4096)
            packets = client_channel.feed(chunk)
            if not packets:
                errors.append("客户端未收到服务器的包")
                return
            pkt = packets[0]
            print(f"[客户端] 收到加密包: opcode={pkt.command}, payload={pkt.payload.hex()}")

            if pkt.command != 69:
                errors.append(f"opcode 错误: 期望 69, 实际 {pkt.command}")

            # 发送测试包给服务器
            test_opcode = 109  # C2GS_HEART_BEAT
            test_payload = b""
            wire = client_channel.send(test_opcode, test_payload)
            client_sock.sendall(wire)
            print(f"[客户端] 发送加密包: opcode={test_opcode}, {len(wire)}B")

            client_sock.close()
            print("[客户端] 测试完成 ✓")
        except Exception as e:
            errors.append(f"客户端异常: {e}")
            import traceback
            traceback.print_exc()

    # 启动线程
    t1 = threading.Thread(target=server_thread)
    t2 = threading.Thread(target=client_thread)

    t1.start()
    t2.start()

    t1.join(timeout=5)
    t2.join(timeout=5)

    server_sock.close()

    # 检查线程是否正常结束
    assert not t1.is_alive(), "服务器线程未正常结束（超时）"
    assert not t2.is_alive(), "客户端线程未正常结束（超时）"
    assert not errors, f"测试失败: {errors}"

    print("\n" + "=" * 60)
    print("测试 2 通过 ✓")
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("mock_server_v2.py 集成测试")
    print("=" * 60)

    try:
        test_unframe_function()
        test_handshake_and_encrypted_communication()
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 60)
    print("所有测试通过 ✓✓✓")
    print("=" * 60)
