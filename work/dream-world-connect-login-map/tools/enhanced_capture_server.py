#!/usr/bin/env python3
"""
增强版回环捕获工具 - 自动解密捕获的数据包

功能:
1. 捕获客户端发送的原始 TCP 数据
2. 自动解析协议帧（uint16大端序长度前缀）
3. 使用破解的加密算法自动解密数据包
4. 显示明文内容和字段分析
5. 保存原始数据和解密后的数据

用法:
    # 仅捕获（不解密）
    python enhanced_capture_server.py

    # 使用指定密钥自动解密
    python enhanced_capture_server.py --key 0102030405060708

    # 从文件加载密钥
    python enhanced_capture_server.py --key-file key.bin

    # 尝试多个常见密钥自动破解
    python enhanced_capture_server.py --auto-crack
"""

from __future__ import annotations

import argparse
import logging
import os
import socket
import struct
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 导入加密模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'notes', 'protocol-artifacts'))
from im_crypto import IMProtocolCrypto, build_frame, parse_frame

HOST = "127.0.0.1"
DEFAULT_PORT = 3134
CHUNK_SIZE = 4096
MAX_FRAME = 0xFFFF

# 常见测试密钥（用于自动破解）
COMMON_KEYS = [
    bytes(range(8)),                          # 00 01 02 03 04 05 06 07
    bytes([0x00] * 8),                        # 全零
    bytes([0xFF] * 8),                        # 全FF
    bytes([0x01] * 8),                        # 全01
    b'12345678',                              # ASCII "12345678"
    b'password',                              # ASCII "password"
    b'mxdw2022',                              # 游戏相关
    b'DuoyiNet',                              # 公司名
    b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A',      # PNG头（某些游戏用魔数）
]


def hex_dump(data: bytes, indent: str = "  ") -> str:
    """格式化hex转储"""
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02X}' for b in chunk)
        ascii_part = ''.join(chr(b) if 0x20 <= b <= 0x7E else '.' for b in chunk)
        lines.append(f"{indent}{i:04X}  {hex_part:<48}  |{ascii_part}|")
    return '\n'.join(lines)


def format_ascii(data: bytes) -> str:
    return "".join(chr(byte) if 0x20 <= byte <= 0x7E else "." for byte in data)


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


def try_decrypt(frame: bytes, crypto: IMProtocolCrypto) -> tuple[bool, bytes]:
    """
    尝试解密帧
    返回: (是否成功, 解密后的数据)
    """
    if len(frame) < 2:
        return False, frame
    
    try:
        # 先尝试直接解密（假设整个帧都是加密的）
        crypto.reset()
        decrypted = crypto.decrypt(frame)
        
        # 检查解密后的帧是否有合理的长度前缀
        if len(decrypted) >= 2:
            length = struct.unpack("!H", decrypted[:2])[0]
            if 2 <= length <= len(decrypted):
                return True, decrypted
        
        # 如果长度前缀不合理，尝试只解密payload（跳过长度前缀）
        crypto.reset()
        payload = crypto.decrypt(frame[2:])
        decrypted = frame[:2] + payload
        return True, decrypted
        
    except Exception:
        return False, frame


def auto_crack_key(frame: bytes) -> Optional[tuple[bytes, bytes]]:
    """
    尝试用常见密钥破解帧
    返回: (密钥, 解密后的数据) 或 None
    """
    for key in COMMON_KEYS:
        crypto = IMProtocolCrypto(key)
        success, decrypted = try_decrypt(frame, crypto)
        if success:
            # 进一步验证：解密后的数据应该包含可打印字符或合理结构
            payload = decrypted[2:] if len(decrypted) > 2 else b''
            printable_ratio = sum(1 for b in payload[:32] if 0x20 <= b <= 0x7E or b in (0x00, 0x0A, 0x0D)) / max(len(payload[:32]), 1)
            if printable_ratio > 0.5:  # 超过50%可打印字符
                return key, decrypted
    return None


def analyze_packet(data: bytes, direction: str = "C→S") -> str:
    """分析数据包内容"""
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"数据包分析 [{direction}]")
    lines.append(f"{'='*60}")
    lines.append(f"总长度: {len(data)} 字节")
    
    if len(data) >= 2:
        length = struct.unpack("!H", data[:2])[0]
        lines.append(f"帧长度前缀: {length} (0x{length:04X})")
        lines.append(f"Payload长度: {len(data)-2} 字节")
    
    lines.append(f"\n原始数据 (HEX):")
    lines.append(hex_dump(data))
    
    # 尝试提取可打印字符串
    strings = []
    current = bytearray()
    for b in data:
        if 0x20 <= b <= 0x7E:
            current.append(b)
        else:
            if len(current) >= 3:
                strings.append(current.decode('ascii', errors='ignore'))
            current = bytearray()
    if len(current) >= 3:
        strings.append(current.decode('ascii', errors='ignore'))
    
    if strings:
        lines.append(f"\n可打印字符串 ({len(strings)}个):")
        for s in strings[:20]:
            lines.append(f"  - {repr(s)}")
    
    # 尝试解析为已知命令
    if len(data) >= 4:
        cmd = struct.unpack("!H", data[2:4])[0]
        lines.append(f"\n可能的命令字: 0x{cmd:04X} ({cmd})")
    
    return '\n'.join(lines)


def configure_logging(output_dir: Path, log_file: Path | None) -> Path:
    if log_file is None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = output_dir / f"enhanced-capture-{stamp}.log"
    else:
        log_file.parent.mkdir(parents=True, exist_ok=True)
    
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, mode="a", encoding="utf-8"),
    ]
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )
    return log_file


def serve(
    port: int,
    output_dir: Path,
    key: bytes | None,
    key_file: Path | None,
    auto_crack: bool,
    decrypt_mode: str,
) -> int:
    """
    启动增强版捕获服务器
    
    decrypt_mode:
        - 'none': 不解密
        - 'auto': 自动尝试破解密钥
        - 'fixed': 使用固定密钥
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file = configure_logging(output_dir, None)
    logger = logging.getLogger("enhanced-capture")
    
    # 初始化加密模块
    crypto = None
    if key_file:
        key = key_file.read_bytes()[:8]
        logger.info(f"从文件加载密钥: {key.hex()}")
    
    if key:
        crypto = IMProtocolCrypto(key)
        logger.info(f"使用固定密钥: {key.hex()}")
        decrypt_mode = 'fixed'
    elif auto_crack:
        logger.info("启用自动破解模式（尝试常见密钥）")
        decrypt_mode = 'auto'
    else:
        logger.info("捕获模式: 仅捕获原始数据，不解密")
        decrypt_mode = 'none'
    
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        listener.bind((HOST, port))
        listener.listen()
        logger.info(f"🎧 增强版捕获服务器启动: {HOST}:{port}")
        logger.info(f"📁 输出目录: {output_dir.resolve()}")
        logger.info(f"🔐 解密模式: {decrypt_mode}")
        logger.info("⏳ 等待客户端连接... (Ctrl+C 停止)")
        
        connection_number = 0
        while True:
            client, peer = listener.accept()
            connection_number += 1
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            capture_path = output_dir / f"capture-{stamp}-{connection_number}.bin"
            decrypted_path = output_dir / f"decrypted-{stamp}-{connection_number}.bin"
            
            logger.info(f"\n{'#'*60}")
            logger.info(f"🔌 连接 #{connection_number} 来自 {peer}")
            logger.info(f"📄 原始数据保存: {capture_path.name}")
            logger.info(f"{'#'*60}")
            
            received_total = 0
            frame_buffer = bytearray()
            frame_number = 0
            
            with client, capture_path.open("wb") as capture:
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                
                while True:
                    try:
                        data = client.recv(CHUNK_SIZE)
                    except ConnectionResetError:
                        logger.info("连接被重置")
                        break
                    
                    if not data:
                        logger.info("客户端关闭连接")
                        break
                    
                    received_total += len(data)
                    capture.write(data)
                    capture.flush()
                    frame_buffer.extend(data)
                    
                    logger.info(f"\n📥 收到 {len(data)} 字节 (累计 {received_total} 字节)")
                    logger.info(f"原始数据:\n{hex_dump(data, '  ')}")
                    
                    # 提取完整帧
                    frames = extract_frames(frame_buffer)
                    
                    for frame in frames:
                        frame_number += 1
                        logger.info(f"\n{'='*60}")
                        logger.info(f"📦 帧 #{frame_number} (完整帧, {len(frame)} 字节)")
                        logger.info(f"{'='*60}")
                        logger.info(f"帧数据:\n{hex_dump(frame, '  ')}")
                        
                        # 尝试解密
                        if decrypt_mode == 'fixed' and crypto:
                            success, decrypted = try_decrypt(frame, crypto)
                            if success:
                                logger.info(f"\n🔓 解密成功 (密钥: {key.hex() if key else 'unknown'})")
                                logger.info(f"解密后数据:\n{hex_dump(decrypted, '  ')}")
                                
                                # 保存解密后的数据
                                with decrypted_path.open("ab") as f:
                                    f.write(decrypted)
                                
                                # 分析解密后的数据包
                                analysis = analyze_packet(decrypted, "C→S (解密后)")
                                logger.info(analysis)
                            else:
                                logger.info("解密失败或数据格式不匹配")
                        
                        elif decrypt_mode == 'auto':
                            logger.info("🔍 尝试自动破解密钥...")
                            result = auto_crack_key(frame)
                            if result:
                                cracked_key, decrypted = result
                                logger.info(f"🎉 破解成功! 密钥: {cracked_key.hex()}")
                                logger.info(f"解密后数据:\n{hex_dump(decrypted, '  ')}")
                                
                                # 保存
                                with decrypted_path.open("ab") as f:
                                    f.write(decrypted)
                                
                                # 分析
                                analysis = analyze_packet(decrypted, "C→S (破解后)")
                                logger.info(analysis)
                                
                                # 更新全局密钥供后续帧使用
                                crypto = IMProtocolCrypto(cracked_key)
                                key = cracked_key
                                decrypt_mode = 'fixed'
                                logger.info(f"✅ 已切换到固定密钥模式: {cracked_key.hex()}")
                            else:
                                logger.info("❌ 未能破解（尝试了所有常见密钥）")
                        
                        # 分析原始帧
                        if decrypt_mode == 'none':
                            analysis = analyze_packet(frame, "C→S (原始)")
                            logger.info(analysis)
                    
                    if frame_buffer:
                        logger.info(f"\n⏳ 缓冲区剩余 {len(frame_buffer)} 字节（不完整帧）")
            
            logger.info(f"\n📊 连接 #{connection_number} 结束")
            logger.info(f"   总接收: {received_total} 字节")
            logger.info(f"   完整帧: {frame_number} 个")
            logger.info(f"   原始数据: {capture_path}")
            if decrypt_mode != 'none' and decrypted_path.exists():
                logger.info(f"   解密数据: {decrypted_path}")
            
    except KeyboardInterrupt:
        logger.info("\n\n🛑 服务器停止")
    finally:
        listener.close()
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="增强版回环捕获工具 - 自动解密捕获的数据包",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本捕获（不解密）
  python enhanced_capture_server.py

  # 使用固定密钥解密
  python enhanced_capture_server.py --key 0102030405060708

  # 从文件加载密钥
  python enhanced_capture_server.py --key-file mykey.bin

  # 自动尝试破解密钥
  python enhanced_capture_server.py --auto-crack

  # 指定端口和输出目录
  python enhanced_capture_server.py --port 3134 --output ./my-captures
        """
    )
    
    parser.add_argument("--host", default=HOST, help=f"监听地址 (默认: {HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"监听端口 (默认: {DEFAULT_PORT})")
    parser.add_argument("--output", type=Path, default=Path("./captures"), help="输出目录 (默认: ./captures)")
    parser.add_argument("--key", type=str, default=None, help="固定密钥 (hex格式, 如: 0102030405060708)")
    parser.add_argument("--key-file", type=Path, default=None, help="密钥文件路径 (8字节二进制)")
    parser.add_argument("--auto-crack", action="store_true", help="自动尝试破解密钥（尝试常见密钥）")
    
    args = parser.parse_args()
    
    # 解析密钥
    key = None
    if args.key:
        key_hex = args.key.replace(" ", "").replace("0x", "")
        if len(key_hex) % 2:
            parser.error("密钥hex长度必须为偶数")
        key = bytes.fromhex(key_hex)
        if len(key) != 8:
            parser.error(f"密钥必须是8字节，当前 {len(key)} 字节")
    
    serve(
        port=args.port,
        output_dir=args.output,
        key=key,
        key_file=args.key_file,
        auto_crack=args.auto_crack,
        decrypt_mode='none',
    )


if __name__ == "__main__":
    sys.exit(main())
