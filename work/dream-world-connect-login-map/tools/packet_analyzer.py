#!/usr/bin/env python3
"""
数据包分析工具 - 解析 loginhello 的字段结构

功能:
1. 解析协议帧（uint16大端序长度前缀）
2. 自动识别和解密数据包
3. 详细分解 loginhello 握手包的字段结构
4. 分析其他已知命令的字段
5. 支持从文件或实时捕获分析
6. 生成详细的分析报告
7. 尝试暴力破解密钥（已知明文攻击）

用法:
    # 分析捕获的数据包文件
    python packet_analyzer.py capture.bin

    # 使用密钥解密分析
    python packet_analyzer.py capture.bin --key 0102030405060708

    # 分析目录下所有捕获文件
    python packet_analyzer.py ./captures/

    # 实时分析模式（配合捕获工具）
    python packet_analyzer.py --live --port 3134

    # 暴力破解密钥（已知明文攻击）
    python packet_analyzer.py capture.bin --crack --known-plaintext "loginhello"
"""

from __future__ import annotations

import argparse
import json
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

# 协议常量
CMD_NAMES = {
    0x0001: "LOGIN_HELLO (loginhello)",
    0x0002: "TEST_HELLO",
    0x0003: "RESELECT_HELLO",
    0x0010: "C2S_TRANSFER_SERVER",
    0x00FF: "HEARTBEAT",
    0x1001: "S2C_LOGIN_SUCCESS",
    0x1002: "S2C_SERVER_ROLE_INFO",
    0x1003: "S2C_LOGIN_FAIL",
    0x1004: "S2C_SERVER_LIST",
    0x10FF: "S2C_HEARTBEAT_ACK",
}

# 字段类型
FIELD_TYPES = {
    'uint8': ('!B', 1, '无符号8位整数'),
    'uint16': ('!H', 2, '无符号16位整数（大端序）'),
    'uint32': ('!I', 4, '无符号32位整数（大端序）'),
    'int16': ('!h', 2, '有符号16位整数（大端序）'),
    'int32': ('!i', 4, '有符号32位整数（大端序）'),
    'string': (None, None, '字符串（长度前缀）'),
    'bytes': (None, None, '原始字节'),
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
        if length < 2 or length > 0xFFFF:
            break
        if len(buffer) < length:
            break
        frames.append(bytes(buffer[:length]))
        del buffer[:length]
    return frames


class PacketAnalyzer:
    """数据包分析器"""
    
    def __init__(self, key: bytes | None = None, verbose: bool = False):
        self.key = key
        self.crypto = IMProtocolCrypto(key) if key else None
        self.verbose = verbose
        self.logger = logging.getLogger("packet-analyzer")
        
        # 分析统计
        self.stats = {
            'total_frames': 0,
            'decrypted_frames': 0,
            'commands_found': {},
            'strings_found': [],
        }
    
    def setup_logging(self, log_file: Path | None = None):
        """配置日志"""
        handlers = [logging.StreamHandler(sys.stdout)]
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(log_file, mode="a", encoding="utf-8"))
        
        level = logging.DEBUG if self.verbose else logging.INFO
        
        logging.basicConfig(
            level=level,
            format="[%(asctime)s] %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=handlers,
            force=True,
        )
    
    def decrypt_frame(self, frame: bytes) -> tuple[bool, bytes]:
        """尝试解密帧"""
        if not self.crypto:
            return False, frame
        
        try:
            # 尝试解密整个帧
            self.crypto.reset()
            decrypted = self.crypto.decrypt(frame)
            if self._is_valid_frame(decrypted):
                return True, decrypted
            
            # 尝试只解密payload
            self.crypto.reset()
            payload = self.crypto.decrypt(frame[2:])
            decrypted = frame[:2] + payload
            if self._is_valid_frame(decrypted):
                return True, decrypted
        except Exception as e:
            self.logger.debug(f"解密失败: {e}")
        
        return False, frame
    
    def _is_valid_frame(self, data: bytes) -> bool:
        """检查是否是有效帧"""
        if len(data) < 2:
            return False
        length = struct.unpack("!H", data[:2])[0]
        return 2 <= length <= len(data)
    
    def parse_field(self, data: bytes, offset: int, field_type: str) -> tuple[any, int, str]:
        """
        解析字段
        返回: (值, 新偏移, 描述)
        """
        if field_type == 'uint8':
            if offset + 1 > len(data):
                return None, offset, "数据不足"
            val = struct.unpack_from("!B", data, offset)[0]
            return val, offset + 1, f"uint8 = {val} (0x{val:02X})"
        
        elif field_type == 'uint16':
            if offset + 2 > len(data):
                return None, offset, "数据不足"
            val = struct.unpack_from("!H", data, offset)[0]
            cmd_name = CMD_NAMES.get(val, "")
            desc = f"uint16 = {val} (0x{val:04X})"
            if cmd_name:
                desc += f" [{cmd_name}]"
            return val, offset + 2, desc
        
        elif field_type == 'uint32':
            if offset + 4 > len(data):
                return None, offset, "数据不足"
            val = struct.unpack_from("!I", data, offset)[0]
            return val, offset + 4, f"uint32 = {val} (0x{val:08X})"
        
        elif field_type == 'int16':
            if offset + 2 > len(data):
                return None, offset, "数据不足"
            val = struct.unpack_from("!h", data, offset)[0]
            return val, offset + 2, f"int16 = {val}"
        
        elif field_type == 'int32':
            if offset + 4 > len(data):
                return None, offset, "数据不足"
            val = struct.unpack_from("!i", data, offset)[0]
            return val, offset + 4, f"int32 = {val}"
        
        elif field_type == 'string':
            # 长度前缀字符串（uint16长度 + 字节）
            if offset + 2 > len(data):
                return None, offset, "数据不足"
            length = struct.unpack_from("!H", data, offset)[0]
            offset += 2
            if offset + length > len(data):
                return None, offset, f"数据不足（需要{length}字节）"
            try:
                val = data[offset:offset+length].decode('utf-8', errors='replace')
            except:
                val = data[offset:offset+length].hex()
            return val, offset + length, f"string[{length}] = {repr(val)}"
        
        elif field_type == 'bytes':
            val = data[offset:]
            return val, len(data), f"bytes[{len(val)}] = {val.hex()}"
        
        return None, offset, f"未知类型: {field_type}"
    
    def analyze_login_hello(self, payload: bytes) -> dict:
        """
        分析 loginhello 握手包
        推测格式:
        [cmd:uint16][version:uint32][player_id:uint32][client_version:string]
        [timestamp:uint32][checksum:uint32][...]
        """
        result = {
            'type': 'LOGIN_HELLO',
            'fields': [],
            'raw_payload': payload.hex(),
            'raw_length': len(payload),
        }
        
        offset = 0
        
        # 字段1: 命令字（如果payload以命令字开头）
        if len(payload) >= 2:
            cmd, offset, desc = self.parse_field(payload, 0, 'uint16')
            result['fields'].append({'name': 'command', 'offset': 0, 'value': cmd, 'desc': desc})
            result['command'] = cmd
        
        # 尝试解析剩余字段
        remaining = payload[offset:]
        
        # 查找可打印字符串（如 "loginhello"）
        strings = self._extract_strings(remaining)
        if strings:
            result['strings'] = strings
            for s in strings:
                result['fields'].append({
                    'name': 'string',
                    'value': s,
                    'desc': f'可打印字符串: {repr(s)}'
                })
        
        # 尝试解析数字字段
        numeric_fields = []
        temp_offset = offset
        while temp_offset + 4 <= len(payload):
            val = struct.unpack_from("!I", payload, temp_offset)[0]
            # 只记录看起来合理的值
            if val < 0x10000000:  # 避免太大的随机数
                numeric_fields.append({
                    'offset': temp_offset,
                    'value': val,
                    'hex': f"0x{val:08X}",
                })
            temp_offset += 1  # 滑动窗口
        
        if numeric_fields:
            result['possible_uint32_fields'] = numeric_fields[:10]  # 只显示前10个
        
        # 分析版本号（常见位置）
        if len(remaining) >= 4:
            version = struct.unpack_from("!I", remaining, 0)[0]
            result['possible_version'] = {
                'value': version,
                'hex': f"0x{version:08X}",
                'bytes': f"{version & 0xFF}.{(version >> 8) & 0xFF}.{(version >> 16) & 0xFF}.{(version >> 24) & 0xFF}",
            }
        
        return result
    
    def analyze_server_role_info(self, payload: bytes) -> dict:
        """分析服务器角色信息响应"""
        result = {
            'type': 'S2C_SERVER_ROLE_INFO',
            'fields': [],
            'raw_payload': payload.hex(),
        }
        
        offset = 0
        
        # 命令字
        if len(payload) >= 2:
            cmd, offset, desc = self.parse_field(payload, 0, 'uint16')
            result['fields'].append({'name': 'command', 'offset': 0, 'value': cmd, 'desc': desc})
        
        # 服务器ID
        if offset + 4 <= len(payload):
            server_id, offset, desc = self.parse_field(payload, offset, 'uint32')
            result['fields'].append({'name': 'server_id', 'offset': offset-4, 'value': server_id, 'desc': desc})
        
        # 角色数量
        if offset + 2 <= len(payload):
            role_count, offset, desc = self.parse_field(payload, offset, 'uint16')
            result['fields'].append({'name': 'role_count', 'offset': offset-2, 'value': role_count, 'desc': desc})
            result['role_count'] = role_count
        
        # 解析角色列表
        roles = []
        for i in range(min(role_count if 'role_count' in result else 0, 10)):
            role = {}
            
            # 角色ID
            if offset + 4 <= len(payload):
                role_id, offset, desc = self.parse_field(payload, offset, 'uint32')
                role['id'] = role_id
            
            # 角色名（长度前缀字符串）
            if offset + 2 <= len(payload):
                name_len = struct.unpack_from("!H", payload, offset)[0]
                offset += 2
                if offset + name_len <= len(payload):
                    name = payload[offset:offset+name_len].decode('utf-8', errors='replace')
                    role['name'] = name
                    offset += name_len
            
            # 等级
            if offset + 2 <= len(payload):
                level, offset, desc = self.parse_field(payload, offset, 'uint16')
                role['level'] = level
            
            if role:
                roles.append(role)
        
        result['roles'] = roles
        return result
    
    def analyze_generic(self, payload: bytes, cmd: int = None) -> dict:
        """通用分析"""
        result = {
            'type': 'GENERIC',
            'fields': [],
            'raw_payload': payload.hex(),
            'raw_length': len(payload),
        }
        
        if cmd:
            result['command'] = cmd
            result['command_name'] = CMD_NAMES.get(cmd, 'UNKNOWN')
        
        # 提取字符串
        strings = self._extract_strings(payload)
        if strings:
            result['strings'] = strings
        
        # 十六进制转储
        result['hex_dump'] = hex_dump(payload)
        
        return result
    
    def _extract_strings(self, data: bytes, min_len: int = 3) -> list[str]:
        """提取可打印字符串"""
        strings = []
        current = bytearray()
        for b in data:
            if 0x20 <= b <= 0x7E:
                current.append(b)
            else:
                if len(current) >= min_len:
                    strings.append(current.decode('ascii', errors='ignore'))
                current = bytearray()
        if len(current) >= min_len:
            strings.append(current.decode('ascii', errors='ignore'))
        return strings
    
    def analyze_frame(self, frame: bytes, decrypt: bool = True) -> dict:
        """
        分析单个帧
        返回分析结果字典
        """
        self.stats['total_frames'] += 1
        
        result = {
            'frame_length': len(frame),
            'raw_frame': frame.hex(),
            'timestamp': datetime.now().isoformat(),
        }
        
        # 解析帧头
        if len(frame) >= 2:
            length = struct.unpack("!H", frame[:2])[0]
            result['frame_length_prefix'] = length
            result['payload_length'] = len(frame) - 2
        
        # 尝试解密
        decrypted = frame
        if decrypt and self.crypto:
            success, decrypted = self.decrypt_frame(frame)
            result['decrypted'] = success
            if success:
                self.stats['decrypted_frames'] += 1
                result['decrypted_frame'] = decrypted.hex()
        
        # 分析解密后的数据
        payload = decrypted[2:] if len(decrypted) > 2 else b''
        
        if len(payload) >= 2:
            cmd = struct.unpack("!H", payload[:2])[0]
            result['command'] = cmd
            result['command_name'] = CMD_NAMES.get(cmd, f'UNKNOWN(0x{cmd:04X})')
            
            # 更新统计
            cmd_name = CMD_NAMES.get(cmd, f'0x{cmd:04X}')
            self.stats['commands_found'][cmd_name] = self.stats['commands_found'].get(cmd_name, 0) + 1
            
            # 根据命令类型进行详细分析
            if cmd == 0x0001 or b'loginhello' in payload.lower():
                result['analysis'] = self.analyze_login_hello(payload)
            elif cmd == 0x1002:
                result['analysis'] = self.analyze_server_role_info(payload)
            else:
                result['analysis'] = self.analyze_generic(payload, cmd)
        else:
            result['analysis'] = self.analyze_generic(payload)
        
        return result
    
    def print_analysis(self, result: dict):
        """打印分析结果"""
        print("\n" + "=" * 70)
        print(f"📦 帧分析报告")
        print("=" * 70)
        print(f"帧长度: {result['frame_length']} 字节")
        print(f"长度前缀: {result.get('frame_length_prefix', 'N/A')}")
        print(f"Payload长度: {result.get('payload_length', 'N/A')}")
        
        if result.get('decrypted') is not None:
            status = "✅ 已解密" if result['decrypted'] else "🔒 未解密/加密"
            print(f"解密状态: {status}")
        
        if 'command' in result:
            print(f"命令字: 0x{result['command']:04X} ({result['command']})")
            print(f"命令名: {result.get('command_name', 'N/A')}")
        
        print(f"\n原始帧 (HEX):")
        print(hex_dump(bytes.fromhex(result['raw_frame'])))
        
        if 'decrypted_frame' in result:
            print(f"\n解密后帧 (HEX):")
            print(hex_dump(bytes.fromhex(result['decrypted_frame'])))
        
        analysis = result.get('analysis', {})
        if analysis:
            print(f"\n{'─'*70}")
            print(f"详细分析: {analysis.get('type', 'N/A')}")
            print(f"{'─'*70}")
            
            # 打印字段
            if 'fields' in analysis:
                print("\n字段分解:")
                for field in analysis['fields']:
                    offset = field.get('offset', '?')
                    name = field.get('name', '?')
                    value = field.get('value', '?')
                    desc = field.get('desc', '')
                    print(f"  [{offset:>4}] {name:<20} = {value}  ({desc})")
            
            # 打印字符串
            if 'strings' in analysis:
                print(f"\n发现的字符串:")
                for s in analysis['strings']:
                    print(f"  - {repr(s)}")
            
            # 打印角色信息
            if 'roles' in analysis:
                print(f"\n角色列表 ({len(analysis['roles'])} 个):")
                for role in analysis['roles']:
                    print(f"  - ID: {role.get('id', '?')}, 名: {role.get('name', '?')}, 等级: {role.get('level', '?')}")
            
            # 打印可能的数字字段
            if 'possible_uint32_fields' in analysis:
                print(f"\n可能的uint32字段:")
                for f in analysis['possible_uint32_fields']:
                    print(f"  [偏移 {f['offset']:>4}] = {f['value']} ({f['hex']})")
            
            # 打印版本信息
            if 'possible_version' in analysis:
                v = analysis['possible_version']
                print(f"\n可能的版本号: {v['bytes']} (0x{v['hex']})")
            
            # 打印原始payload
            if 'raw_payload' in analysis:
                print(f"\nPayload (HEX):")
                print(hex_dump(bytes.fromhex(analysis['raw_payload'])))
        
        print("=" * 70)
    
    def analyze_file(self, file_path: Path) -> list[dict]:
        """分析文件中的所有帧"""
        self.logger.info(f"分析文件: {file_path}")
        
        data = file_path.read_bytes()
        self.logger.info(f"文件大小: {len(data)} 字节")
        
        buffer = bytearray(data)
        frames = extract_frames(buffer)
        
        self.logger.info(f"提取到 {len(frames)} 个完整帧")
        if buffer:
            self.logger.info(f"剩余 {len(buffer)} 字节（不完整帧）")
        
        results = []
        for i, frame in enumerate(frames, 1):
            self.logger.info(f"\n分析帧 {i}/{len(frames)}...")
            result = self.analyze_frame(frame)
            result['frame_number'] = i
            result['source_file'] = str(file_path)
            results.append(result)
            self.print_analysis(result)
        
        return results
    
    def analyze_directory(self, dir_path: Path) -> list[dict]:
        """分析目录下所有捕获文件"""
        all_results = []
        
        # 查找所有捕获文件
        patterns = ['capture-*.bin', 'conn*.bin', 'stream-*.bin', '*.bin']
        files = set()
        for pattern in patterns:
            files.update(dir_path.glob(pattern))
        
        files = sorted(files)
        self.logger.info(f"找到 {len(files)} 个文件待分析")
        
        for file_path in files:
            if file_path.is_file():
                try:
                    results = self.analyze_file(file_path)
                    all_results.extend(results)
                except Exception as e:
                    self.logger.error(f"分析文件 {file_path} 失败: {e}")
        
        return all_results
    
    def generate_report(self, results: list[dict], output_path: Path | None = None) -> str:
        """生成分析报告"""
        report = []
        report.append("=" * 70)
        report.append("梦想世界 数据包分析报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 70)
        
        # 统计信息
        report.append("\n## 统计信息")
        report.append(f"- 总帧数: {self.stats['total_frames']}")
        report.append(f"- 成功解密: {self.stats['decrypted_frames']}")
        report.append(f"- 解密率: {self.stats['decrypted_frames']/max(self.stats['total_frames'],1)*100:.1f}%")
        
        # 命令统计
        report.append("\n## 命令分布")
        for cmd, count in sorted(self.stats['commands_found'].items(), key=lambda x: -x[1]):
            report.append(f"- {cmd}: {count} 次")
        
        # 详细分析
        report.append("\n## 详细分析")
        for i, result in enumerate(results, 1):
            report.append(f"\n### 帧 {i}")
            report.append(f"- 文件: {result.get('source_file', 'N/A')}")
            report.append(f"- 长度: {result['frame_length']} 字节")
            if 'command' in result:
                report.append(f"- 命令: 0x{result['command']:04X} ({result.get('command_name', 'N/A')})")
            
            analysis = result.get('analysis', {})
            if analysis.get('type') == 'LOGIN_HELLO':
                report.append("\n**Login Hello 握手包分析**:")
                if 'strings' in analysis:
                    report.append(f"- 字符串: {analysis['strings']}")
                if 'possible_version' in analysis:
                    v = analysis['possible_version']
                    report.append(f"- 可能版本: {v['bytes']}")
                if 'possible_uint32_fields' in analysis:
                    report.append("- 可能的数字字段:")
                    for f in analysis['possible_uint32_fields'][:5]:
                        report.append(f"  - [偏移 {f['offset']}] {f['value']} ({f['hex']})")
        
        # 密钥信息
        if self.key:
            report.append(f"\n## 密钥信息")
            report.append(f"- 密钥: {self.key.hex()}")
        
        report_text = '\n'.join(report)
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report_text, encoding='utf-8')
            self.logger.info(f"报告已保存: {output_path}")
        
        return report_text
    
    def crack_key_known_plaintext(self, frame: bytes, known_plaintext: bytes) -> Optional[bytes]:
        """
        已知明文攻击破解密钥
        
        原理: 流密码加密是 output = SBOX[state][key[state] ^ input]
        如果知道明文和密文，可以反推 key[state] = SBOX_inv[state][output] ^ input
        """
        self.logger.info(f"尝试已知明文攻击破解密钥...")
        self.logger.info(f"已知明文: {known_plaintext.hex()} ({known_plaintext})")
        
        # 需要至少8字节的已知明文（覆盖所有8个状态）
        if len(known_plaintext) < 8:
            self.logger.error("已知明文至少需要8字节（覆盖所有8个状态）")
            return None
        
        # 假设密文是解密后的payload部分
        # 需要知道密文对应的明文位置
        
        # 尝试在帧中找到已知明文的位置
        # 首先尝试解密整个帧
        for key_guess in self._generate_key_candidates(frame, known_plaintext):
            crypto = IMProtocolCrypto(key_guess)
            crypto.reset()
            decrypted = crypto.decrypt(frame)
            
            # 检查解密结果是否包含已知明文
            if known_plaintext in decrypted:
                self.logger.info(f"🎉 破解成功! 密钥: {key_guess.hex()}")
                return key_guess
        
        self.logger.info("❌ 破解失败")
        return None
    
    def _generate_key_candidates(self, frame: bytes, known_plaintext: bytes) -> list[bytes]:
        """生成可能的密钥候选"""
        candidates = []
        
        # 方法1: 从已知明文和密文直接计算
        # 假设我们知道明文在帧中的位置
        # 尝试不同的对齐方式
        for offset in range(min(len(frame), 32)):
            if offset + len(known_plaintext) > len(frame):
                break
            
            cipher_part = frame[offset:offset + len(known_plaintext)]
            
            # 对每个状态，尝试计算 key[state] = DEC_SBOX[state][cipher] ^ plain
            key = bytearray(8)
            valid = True
            
            for i in range(min(8, len(known_plaintext))):
                state = i % 8
                cipher_byte = cipher_part[i]
                plain_byte = known_plaintext[i]
                
                # 从加密公式反推:
                # cipher = ENC_SBOX[state][key ^ plain]
                # 需要找到 key 使得 ENC_SBOX[state][key ^ plain] == cipher
                # 即 key ^ plain = DEC_SBOX[state][cipher]
                # key = DEC_SBOX[state][cipher] ^ plain
                
                # 加载解密S盒
                base = os.path.join(os.path.dirname(__file__), '..', 'notes', 'protocol-artifacts')
                with open(os.path.join(base, 'dec_sbox.bin'), 'rb') as f:
                    dec_sbox = f.read()
                
                dec_val = dec_sbox[state * 256 + cipher_byte]
                key_byte = dec_val ^ plain_byte
                key[state] = key_byte
            
            candidates.append(bytes(key))
        
        # 方法2: 常见密钥
        common_keys = [
            bytes(range(8)),
            bytes([0x00] * 8),
            bytes([0xFF] * 8),
            b'12345678',
            b'password',
            b'mxdw2022',
            b'DuoyiNet',
        ]
        candidates.extend(common_keys)
        
        # 去重
        seen = set()
        unique = []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                unique.append(c)
        
        self.logger.info(f"生成了 {len(unique)} 个密钥候选")
        return unique


def main():
    parser = argparse.ArgumentParser(
        description="数据包分析工具 - 解析 loginhello 的字段结构",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析单个捕获文件
  python packet_analyzer.py capture-20261010-120000-1.bin

  # 使用密钥解密分析
  python packet_analyzer.py capture.bin --key 0102030405060708

  # 分析目录下所有文件
  python packet_analyzer.py ./captures/

  # 生成报告
  python packet_analyzer.py ./captures/ --report report.md

  # 暴力破解密钥
  python packet_analyzer.py capture.bin --crack --known-plaintext "loginhello"
        """
    )
    
    parser.add_argument("input", type=Path, nargs='?', help="输入文件或目录路径")
    parser.add_argument("--key", type=str, default=None, help="解密密钥 (hex格式, 8字节)")
    parser.add_argument("--key-file", type=Path, default=None, help="密钥文件路径")
    parser.add_argument("--report", type=Path, default=None, help="生成报告文件路径")
    parser.add_argument("--crack", action="store_true", help="尝试破解密钥")
    parser.add_argument("--known-plaintext", type=str, default=None, help="已知明文（用于破解）")
    parser.add_argument("--live", action="store_true", help="实时分析模式（监听端口）")
    parser.add_argument("--port", type=int, default=3134, help="实时模式监听端口")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    if not args.input and not args.live:
        parser.error("请指定输入文件/目录或使用 --live 模式")
    
    # 解析密钥
    key = None
    if args.key_file:
        key = args.key_file.read_bytes()[:8]
    elif args.key:
        key_hex = args.key.replace(" ", "").replace("0x", "")
        key = bytes.fromhex(key_hex)
        if len(key) != 8:
            parser.error(f"密钥必须是8字节，当前 {len(key)} 字节")
    
    # 创建分析器
    analyzer = PacketAnalyzer(key=key, verbose=args.verbose)
    analyzer.setup_logging()
    
    results = []
    
    if args.live:
        # 实时模式（简化版，实际应配合捕获工具）
        analyzer.logger.info(f"实时模式暂未完整实现，请使用 enhanced_capture_server.py")
        return 1
    
    elif args.input.is_file():
        # 分析单个文件
        results = analyzer.analyze_file(args.input)
        
        # 尝试破解
        if args.crack and args.known_plaintext:
            data = args.input.read_bytes()
            buffer = bytearray(data)
            frames = extract_frames(buffer)
            if frames:
                known = args.known_plaintext.encode('utf-8')
                cracked_key = analyzer.crack_key_known_plaintext(frames[0], known)
                if cracked_key:
                    analyzer.key = cracked_key
                    analyzer.crypto = IMProtocolCrypto(cracked_key)
                    analyzer.logger.info("使用破解的密钥重新分析...")
                    results = analyzer.analyze_file(args.input)
    
    elif args.input.is_dir():
        # 分析目录
        results = analyzer.analyze_directory(args.input)
    
    else:
        parser.error(f"输入路径不存在: {args.input}")
    
    # 生成报告
    if args.report and results:
        report = analyzer.generate_report(results, args.report)
        print("\n" + report)
    
    # 打印总结
    print("\n" + "=" * 70)
    print("分析总结")
    print("=" * 70)
    print(f"总帧数: {analyzer.stats['total_frames']}")
    print(f"解密成功: {analyzer.stats['decrypted_frames']}")
    if analyzer.stats['commands_found']:
        print("\n发现的命令:")
        for cmd, count in sorted(analyzer.stats['commands_found'].items(), key=lambda x: -x[1]):
            print(f"  - {cmd}: {count} 次")
    
    if analyzer.key:
        print(f"\n使用的密钥: {analyzer.key.hex()}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
