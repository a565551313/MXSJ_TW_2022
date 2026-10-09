#!/usr/bin/env python3
"""
模拟服务器框架 - 基于破解的加密算法，能接收连接并响应

功能:
1. 接收客户端 TCP 连接（端口 3134）
2. 使用破解的加密算法解密客户端数据包
3. 解析 loginhello 握手命令
4. 构造服务器响应（角色信息、登录成功等）
5. 加密并发送响应
6. 支持多种响应模式和调试输出

用法:
    # 基本模式（使用默认密钥）
    python mock_server.py

    # 指定密钥
    python mock_server.py --key 0102030405060708

    # 自动破解密钥后进入响应模式
    python mock_server.py --auto-crack

    # 详细调试模式
    python mock_server.py --verbose

    # 指定响应类型
    python mock_server.py --response-type login_success
"""

from __future__ import annotations

import argparse
import logging
import os
import socket
import struct
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

# 导入加密模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'notes', 'protocol-artifacts'))
from im_crypto import IMProtocolCrypto, build_frame, parse_frame

HOST = "0.0.0.0"  # 模拟服务器需要监听所有接口
DEFAULT_PORT = 3134
CHUNK_SIZE = 4096
MAX_FRAME = 0xFFFF

# 常见测试密钥
COMMON_KEYS = [
    bytes(range(8)),           # 00 01 02 03 04 05 06 07
    bytes([0x00] * 8),         # 全零
    bytes([0xFF] * 8),         # 全FF
    b'12345678',
    b'password',
    b'mxdw2022',
    b'DuoyiNet',
]

# 命令字定义（推测）
CMD_LOGIN_HELLO = 0x0001       # loginhello 握手
CMD_TEST_HELLO = 0x0002        # TEST_HELLO 测试握手
CMD_RESELECT_HELLO = 0x0003    # RESELECT_HELLO 重选握手
CMD_TRANSFER_SERVER = 0x0010   # C2STransferServer 转服
CMD_HEARTBEAT = 0x00FF         # 心跳

# 服务器响应命令（推测）
S2C_LOGIN_SUCCESS = 0x1001     # 登录成功
S2C_SERVER_ROLE_INFO = 0x1002  # 服务器角色信息
S2C_LOGIN_FAIL = 0x1003        # 登录失败
S2C_SERVER_LIST = 0x1004       # 服务器列表
S2C_HEARTBEAT_ACK = 0x10FF     # 心跳响应

# 响应类型
RESPONSE_TYPES = {
    'none': '不响应（仅捕获）',
    'login_success': '登录成功响应',
    'server_role_info': '服务器角色信息响应',
    'login_fail': '登录失败响应',
    'heartbeat': '心跳响应',
    'auto': '自动识别并响应',
}


def hex_dump(data: bytes, indent: str = "  ") -> str:
    """格式化hex转储"""
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02X}' for b in chunk)
        ascii_part = ''.join(chr(b) if 0x20 <= b <= 0x7E else '.' for b in chunk)
        lines.append(f"{indent}{i:04X}  {hex_part:<48}  |{ascii_part}|")
    return '\n'.join(lines)


def extract_frames(buffer: bytearray) -> list[bytes]:
    """从缓冲区提取完整的协议帧"""
    frames = []
    while len(buffer) >= 2:
        length = struct.unpack("!H", buffer[:2])[0]
        if length < 2 or length > MAX_FRAME:
            break
        if len(buffer) < length:
            break
        frames.append(bytes(buffer[:length]))
        del buffer[:length]
    return frames


class MockServer:
    """模拟服务器类"""
    
    def __init__(
        self,
        host: str = HOST,
        port: int = DEFAULT_PORT,
        key: bytes | None = None,
        auto_crack: bool = False,
        response_type: str = 'auto',
        verbose: bool = False,
        output_dir: Path = Path("./mock-server-logs"),
    ):
        self.host = host
        self.port = port
        self.key = key
        self.auto_crack = auto_crack
        self.response_type = response_type
        self.verbose = verbose
        self.output_dir = output_dir
        
        self.crypto: Optional[IMProtocolCrypto] = None
        if key:
            self.crypto = IMProtocolCrypto(key)
        
        self.logger = logging.getLogger("mock-server")
        self.connection_count = 0
        
        # 统计
        self.stats = {
            'connections': 0,
            'frames_received': 0,
            'frames_sent': 0,
            'bytes_received': 0,
            'bytes_sent': 0,
        }
    
    def setup_logging(self):
        """配置日志"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = self.output_dir / f"mock-server-{stamp}.log"
        
        handlers = [
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, mode="a", encoding="utf-8"),
        ]
        
        level = logging.DEBUG if self.verbose else logging.INFO
        
        logging.basicConfig(
            level=level,
            format="[%(asctime)s] %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=handlers,
            force=True,
        )
        
        self.logger.info(f"日志文件: {log_file.resolve()}")
    
    def try_decrypt(self, frame: bytes) -> tuple[bool, bytes, Optional[bytes]]:
        """
        尝试解密帧
        返回: (是否成功, 解密后的数据, 使用的密钥)
        """
        if self.crypto:
            # 使用已知密钥
            self.crypto.reset()
            try:
                # 尝试解密整个帧
                decrypted = self.crypto.decrypt(frame)
                if self._is_valid_frame(decrypted):
                    return True, decrypted, self.key
                
                # 尝试只解密payload
                self.crypto.reset()
                payload = self.crypto.decrypt(frame[2:])
                decrypted = frame[:2] + payload
                if self._is_valid_frame(decrypted):
                    return True, decrypted, self.key
            except Exception as e:
                self.logger.debug(f"解密失败: {e}")
        
        if self.auto_crack:
            # 尝试常见密钥
            for key in COMMON_KEYS:
                crypto = IMProtocolCrypto(key)
                crypto.reset()
                try:
                    decrypted = crypto.decrypt(frame)
                    if self._is_valid_frame(decrypted):
                        self.logger.info(f"🎉 自动破解成功! 密钥: {key.hex()}")
                        self.crypto = IMProtocolCrypto(key)
                        self.key = key
                        self.auto_crack = False  # 破解后切换到固定模式
                        return True, decrypted, key
                except Exception:
                    pass
        
        return False, frame, None
    
    def _is_valid_frame(self, data: bytes) -> bool:
        """检查解密后的数据是否是有效帧"""
        if len(data) < 2:
            return False
        length = struct.unpack("!H", data[:2])[0]
        if length < 2 or length > len(data):
            return False
        # 检查是否有合理的可打印字符比例
        payload = data[2:min(length, 34)]
        if not payload:
            return True
        printable = sum(1 for b in payload if 0x20 <= b <= 0x7E or b in (0x00, 0x0A, 0x0D, 0x09))
        return printable / len(payload) > 0.3
    
    def encrypt_response(self, payload: bytes) -> bytes:
        """加密响应数据"""
        if not self.crypto:
            return build_frame(payload)
        
        self.crypto.reset()
        frame = build_frame(payload)
        return self.crypto.encrypt(frame)
    
    def build_login_success_response(self, player_id: int = 12345) -> bytes:
        """
        构造登录成功响应
        格式推测: [cmd:uint16][result:uint16][player_id:uint32][...]
        """
        payload = struct.pack("!HHI", S2C_LOGIN_SUCCESS, 0, player_id)
        # 添加一些额外字段
        payload += struct.pack("!H", 1)  # 角色数量
        payload += b"\x00" * 16  # 保留字段
        return payload
    
    def build_server_role_info_response(self, server_id: int = 1, role_count: int = 1) -> bytes:
        """
        构造服务器角色信息响应
        格式推测: [cmd:uint16][server_id:uint32][role_count:uint16][roles...]
        """
        payload = struct.pack("!HIH", S2C_SERVER_ROLE_INFO, server_id, role_count)
        
        # 添加角色信息（推测格式）
        for i in range(role_count):
            role_id = 1000 + i
            role_name = f"Player{i+1}".encode('utf-8')
            role_level = 1
            role职业 = 1  # 职业ID
            
            payload += struct.pack("!I", role_id)
            payload += struct.pack("!H", len(role_name)) + role_name
            payload += struct.pack("!H", role_level)
            payload += struct.pack("!H", role职业)
            payload += struct.pack("!I", 2101)  # 默认地图ID
        
        return payload
    
    def build_login_fail_response(self, error_code: int = 1, error_msg: str = "Login failed") -> bytes:
        """构造登录失败响应"""
        msg_bytes = error_msg.encode('utf-8')
        payload = struct.pack("!HHH", S2C_LOGIN_FAIL, error_code, len(msg_bytes))
        payload += msg_bytes
        return payload
    
    def build_heartbeat_response(self) -> bytes:
        """构造心跳响应"""
        payload = struct.pack("!H", S2C_HEARTBEAT_ACK)
        return payload
    
    def handle_client_command(self, decrypted_frame: bytes) -> Optional[bytes]:
        """
        处理客户端命令，返回响应payload（未加密）
        """
        if len(decrypted_frame) < 4:
            return None
        
        # 解析命令字
        cmd = struct.unpack("!H", decrypted_frame[2:4])[0]
        self.logger.info(f"📋 客户端命令: 0x{cmd:04X} ({cmd})")
        
        # 提取命令字符串（如果有）
        payload = decrypted_frame[4:]
        if payload:
            # 尝试提取可打印字符串
            strings = []
            current = bytearray()
            for b in payload:
                if 0x20 <= b <= 0x7E:
                    current.append(b)
                else:
                    if len(current) >= 3:
                        strings.append(current.decode('ascii', errors='ignore'))
                    current = bytearray()
            if current:
                strings.append(current.decode('ascii', errors='ignore'))
            if strings:
                self.logger.info(f"   字符串: {strings}")
        
        # 根据响应类型和命令生成响应
        if self.response_type == 'none':
            return None
        
        if self.response_type == 'auto':
            # 自动模式：根据命令类型响应
            if cmd == CMD_LOGIN_HELLO or b'loginhello' in payload.lower():
                self.logger.info("   → 识别为 loginhello，发送角色信息响应")
                return self.build_server_role_info_response()
            elif cmd == CMD_TEST_HELLO or b'test_hello' in payload.lower():
                self.logger.info("   → 识别为 TEST_HELLO，发送心跳响应")
                return self.build_heartbeat_response()
            elif cmd == CMD_HEARTBEAT:
                return self.build_heartbeat_response()
            else:
                self.logger.info(f"   → 未知命令，发送心跳响应")
                return self.build_heartbeat_response()
        
        elif self.response_type == 'login_success':
            return self.build_login_success_response()
        
        elif self.response_type == 'server_role_info':
            return self.build_server_role_info_response()
        
        elif self.response_type == 'login_fail':
            return self.build_login_fail_response()
        
        elif self.response_type == 'heartbeat':
            return self.build_heartbeat_response()
        
        return None
    
    def handle_connection(self, client: socket.socket, peer: tuple):
        """处理单个客户端连接"""
        self.connection_count += 1
        conn_id = self.connection_count
        self.stats['connections'] += 1
        
        self.logger.info(f"\n{'#'*70}")
        self.logger.info(f"🔌 连接 #{conn_id} 来自 {peer}")
        self.logger.info(f"{'#'*70}")
        
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        client.settimeout(30)  # 30秒超时
        
        frame_buffer = bytearray()
        frame_count = 0
        
        # 保存捕获文件
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        capture_dir = self.output_dir / "captures"
        capture_dir.mkdir(parents=True, exist_ok=True)
        capture_path = capture_dir / f"conn{conn_id}-{stamp}.bin"
        
        try:
            with capture_path.open("wb") as capture_file:
                while True:
                    try:
                        data = client.recv(CHUNK_SIZE)
                    except socket.timeout:
                        self.logger.info("⏱️  接收超时")
                        break
                    except ConnectionResetError:
                        self.logger.info("🔌 连接被重置")
                        break
                    
                    if not data:
                        self.logger.info("👋 客户端关闭连接")
                        break
                    
                    self.stats['bytes_received'] += len(data)
                    capture_file.write(data)
                    capture_file.flush()
                    frame_buffer.extend(data)
                    
                    self.logger.info(f"\n📥 收到 {len(data)} 字节 (累计 {self.stats['bytes_received']} 字节)")
                    self.logger.debug(f"原始数据:\n{hex_dump(data, '  ')}")
                    
                    # 提取完整帧
                    frames = extract_frames(frame_buffer)
                    
                    for frame in frames:
                        frame_count += 1
                        self.stats['frames_received'] += 1
                        
                        self.logger.info(f"\n{'='*60}")
                        self.logger.info(f"📦 帧 #{frame_count} ({len(frame)} 字节)")
                        self.logger.info(f"{'='*60}")
                        self.logger.info(f"原始帧:\n{hex_dump(frame, '  ')}")
                        
                        # 尝试解密
                        success, decrypted, used_key = self.try_decrypt(frame)
                        
                        if success:
                            self.logger.info(f"\n🔓 解密成功!")
                            if used_key:
                                self.logger.info(f"   密钥: {used_key.hex()}")
                            self.logger.info(f"解密后:\n{hex_dump(decrypted, '  ')}")
                            
                            # 处理命令并生成响应
                            response_payload = self.handle_client_command(decrypted)
                            
                            if response_payload:
                                # 加密并发送响应
                                response_frame = self.encrypt_response(response_payload)
                                client.sendall(response_frame)
                                self.stats['frames_sent'] += 1
                                self.stats['bytes_sent'] += len(response_frame)
                                
                                self.logger.info(f"\n📤 发送响应 ({len(response_frame)} 字节):")
                                self.logger.info(f"   Payload: {response_payload.hex()}")
                                self.logger.info(f"   加密后:\n{hex_dump(response_frame, '  ')}")
                            else:
                                self.logger.info("   (不发送响应)")
                        else:
                            self.logger.info("\n🔒 无法解密（未知密钥或非加密数据）")
                            # 如果是捕获模式，仍然分析原始数据
                            if self.response_type == 'none':
                                self.logger.info(f"原始帧分析:\n{hex_dump(frame, '  ')}")
                    
                    if frame_buffer:
                        self.logger.debug(f"缓冲区剩余 {len(frame_buffer)} 字节（不完整帧）")
        
        except Exception as e:
            self.logger.error(f"处理连接时出错: {e}", exc_info=True)
        
        finally:
            self.logger.info(f"\n📊 连接 #{conn_id} 结束")
            self.logger.info(f"   接收帧: {frame_count} 个")
            self.logger.info(f"   捕获文件: {capture_path}")
    
    def start(self):
        """启动服务器"""
        self.setup_logging()
        
        self.logger.info("=" * 70)
        self.logger.info("🎮 梦想世界 模拟服务器框架")
        self.logger.info("=" * 70)
        self.logger.info(f"监听地址: {self.host}:{self.port}")
        self.logger.info(f"密钥: {self.key.hex() if self.key else '未设置'}")
        self.logger.info(f"响应模式: {RESPONSE_TYPES.get(self.response_type, self.response_type)}")
        self.logger.info(f"自动破解: {'是' if self.auto_crack else '否'}")
        self.logger.info(f"输出目录: {self.output_dir.resolve()}")
        self.logger.info("=" * 70)
        self.logger.info("⏳ 等待客户端连接... (Ctrl+C 停止)")
        
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            listener.bind((self.host, self.port))
            listener.listen(5)
            
            while True:
                try:
                    client, peer = listener.accept()
                    self.handle_connection(client, peer)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    self.logger.error(f"接受连接时出错: {e}")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            self.logger.info("\n\n🛑 服务器停止")
        
        finally:
            listener.close()
            self.logger.info("\n📈 统计信息:")
            self.logger.info(f"   连接数: {self.stats['connections']}")
            self.logger.info(f"   接收帧: {self.stats['frames_received']}")
            self.logger.info(f"   发送帧: {self.stats['frames_sent']}")
            self.logger.info(f"   接收字节: {self.stats['bytes_received']}")
            self.logger.info(f"   发送字节: {self.stats['bytes_sent']}")


def main():
    parser = argparse.ArgumentParser(
        description="梦想世界 模拟服务器框架 - 基于破解的加密算法",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本模式（不响应，仅捕获）
  python mock_server.py --response-type none

  # 自动模式（自动识别命令并响应）
  python mock_server.py --response-type auto --auto-crack

  # 使用固定密钥
  python mock_server.py --key 0102030405060708 --response-type auto

  # 登录成功响应模式
  python mock_server.py --response-type login_success

  # 详细调试
  python mock_server.py --verbose --response-type auto
        """
    )
    
    parser.add_argument("--host", default=HOST, help=f"监听地址 (默认: {HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"监听端口 (默认: {DEFAULT_PORT})")
    parser.add_argument("--key", type=str, default=None, help="加密密钥 (hex格式, 8字节)")
    parser.add_argument("--key-file", type=Path, default=None, help="密钥文件路径")
    parser.add_argument("--auto-crack", action="store_true", help="自动尝试破解密钥")
    parser.add_argument(
        "--response-type",
        choices=list(RESPONSE_TYPES.keys()),
        default='auto',
        help="响应类型 (默认: auto)"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="详细调试输出")
    parser.add_argument("--output", type=Path, default=Path("./mock-server-logs"), help="输出目录")
    
    args = parser.parse_args()
    
    # 解析密钥
    key = None
    if args.key_file:
        key = args.key_file.read_bytes()[:8]
    elif args.key:
        key_hex = args.key.replace(" ", "").replace("0x", "")
        key = bytes.fromhex(key_hex)
        if len(key) != 8:
            parser.error(f"密钥必须是8字节，当前 {len(key)} 字节")
    
    # 创建并启动服务器
    server = MockServer(
        host=args.host,
        port=args.port,
        key=key,
        auto_crack=args.auto_crack,
        response_type=args.response_type,
        verbose=args.verbose,
        output_dir=args.output,
    )
    
    server.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())
