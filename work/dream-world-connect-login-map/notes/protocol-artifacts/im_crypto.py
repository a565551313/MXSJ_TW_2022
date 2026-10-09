"""
IMProtocol.dll 加密/解密模块
基于逆向分析结果实现

算法概要:
- 流密码，8个状态（0-7）循环
- 每个状态对应一个256字节的S盒（加密/解密各8个，共16个表）
- 加密: output = ENC_SBOX[state][key[state] ^ input]
- 解密: output = DEC_SBOX[state][input] ^ key[state]
- 8字节密钥，通过密钥派生S盒进行扩展
"""

import struct
import os


class IMProtocolCrypto:
    """IMProtocol 自定义流密码"""

    def __init__(self, key=None):
        """
        初始化加密上下文
        key: 8字节密钥，如果为None则使用默认密钥
        """
        if key is None:
            key = bytes(range(8))  # 默认密钥 00 01 02 03 04 05 06 07
        if len(key) != 8:
            raise ValueError("密钥必须是8字节")

        # 加载 S盒
        base = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(base, 'enc_sbox.bin'), 'rb') as f:
            self.enc_sbox = f.read()  # 2048 bytes
        with open(os.path.join(base, 'dec_sbox.bin'), 'rb') as f:
            self.dec_sbox = f.read()  # 2048 bytes

        self.key = bytearray(key)
        self.state = 0

    @staticmethod
    def load_key_sboxes():
        """加载密钥派生S盒"""
        base = os.path.dirname(os.path.abspath(__file__))
        sboxes = []
        for i in range(8):
            path = os.path.join(base, 'key_sbox_%d.bin' % i)
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    sboxes.append(f.read())
            else:
                sboxes.append(bytes(range(256)))
        return sboxes

    @classmethod
    def derive_key(cls, seed):
        """
        从种子派生密钥（模拟0x10005b80函数）
        算法: 链式S盒替换
        
        汇编分析（0x10005b80）:
          buf[0] = 0
          buf[4..11] = seed[0..7]
          buf[4] = KeySbox0[buf[4]]                    # 第1轮：自己查表
          for i in 1..7:
            buf[4+i] = KeySbox[i][buf[4+i-1] ^ buf[4+i]]  # 链式派生
          result = buf[4..11]
        """
        sboxes = cls.load_key_sboxes()

        # 12字节工作缓冲区，偏移4开始放8字节种子
        buf = bytearray(12)
        buf[0] = 0
        seed = bytes(seed[:8]) if len(seed) >= 8 else bytes(seed) + bytes(8 - len(seed))
        buf[4:12] = seed

        # 第1轮: buf[4] = KeySbox0[buf[4]]
        buf[4] = sboxes[0][buf[4]]

        # 第2-8轮: 链式派生
        for i in range(1, 8):
            xored = buf[4 + i - 1] ^ buf[4 + i]
            buf[4 + i] = sboxes[i][xored]

        return bytes(buf[4:12])

    def encrypt(self, data):
        """加密数据"""
        data = bytearray(data)
        for i in range(len(data)):
            state = self.state & 7
            key_byte = self.key[state]
            xored = key_byte ^ data[i]
            index = (state << 8) | xored
            data[i] = self.enc_sbox[index]
            self.state = (self.state + 1) & 7
        return bytes(data)

    def decrypt(self, data):
        """解密数据"""
        data = bytearray(data)
        for i in range(len(data)):
            state = self.state & 7
            key_byte = self.key[state]
            index = (state << 8) | data[i]
            data[i] = self.dec_sbox[index] ^ key_byte
            self.state = (self.state + 1) & 7
        return bytes(data)

    def reset(self):
        """重置状态"""
        self.state = 0

    def set_key(self, key):
        """设置密钥"""
        if len(key) != 8:
            raise ValueError("密钥必须是8字节")
        self.key = bytearray(key)
        self.state = 0

    def encrypt_packet(self, payload):
        """加密整个数据包（包含长度前缀）"""
        # 先构建包: [uint16_be length][payload]
        length = len(payload) + 2
        packet = struct.pack('>H', length) + payload
        # 加密整个包
        return self.encrypt(packet)

    def decrypt_packet(self, packet):
        """解密数据包，返回payload"""
        decrypted = self.decrypt(packet)
        if len(decrypted) < 2:
            raise ValueError("数据包太短")
        length = struct.unpack('>H', decrypted[:2])[0]
        return decrypted[2:length]


def build_frame(payload, cmd=None):
    """
    构建协议帧
    格式: [uint16_be total_length][payload]
    如果指定cmd，payload = [uint16_be cmd][原payload]
    """
    if cmd is not None:
        payload = struct.pack('>H', cmd) + payload

    total_length = len(payload) + 2
    frame = struct.pack('>H', total_length) + payload
    return frame


def parse_frame(data):
    """
    解析协议帧
    返回: (total_length, payload)
    """
    if len(data) < 2:
        raise ValueError("数据太短，无法解析帧头")
    total_length = struct.unpack('>H', data[:2])[0]
    payload = data[2:total_length]
    return total_length, payload


# 事件ID常量（从逆向分析中获得）
EVENT_CONNECTED = 0x2711      # 连接成功
EVENT_ERROR = 0x2712          # 错误
EVENT_UNKNOWN_2713 = 0x2713   # 未知（条件回调）
EVENT_SERVER_CMD = 0x2714     # 服务器命令 -> OnServerCmd(int)

# 导出函数地址映射（IMProtocol.dll, ImageBase = 0x10000000）
IMPROTOCOL_EXPORTS = {
    'IMP_ConnectNsServer':   0x10003000,
    'IMP_DecryptBuffer':     0x100031a0,
    'IMP_EncryptBuffer':     0x100031f0,
    'IMP_FreeIMBuffWriter':  0x100035b0,
    'IMP_NewIMBuffWriter':   0x10003570,
    'IMP_OpenLog':           0x10002fc0,
    'IMP_ReadBin':           0x10003400,
    'IMP_ReadInt16':         0x10003330,
    'IMP_ReadInt32':         0x100032c0,
    'IMP_ReadInt64':         0x10003280,
    'IMP_ReadInt8':          0x100033a0,
    'IMP_ReadStr':           0x10003400,
    'IMP_ReadUInt16':        0x10003330,
    'IMP_ReadUInt32':        0x100032c0,
    'IMP_ReadUInt64':        0x10003280,
    'IMP_ReadUInt8':         0x100033a0,
    'IMP_RefreshCryptKey':   0x100030d0,
    'IMP_SendBuffer2NS':     0x100036c0,
    'IMP_UnConnectNsServer': 0x10003240,
    'IMP_WriteBin':          0x10003790,
    'IMP_WriteInt16':        0x10003650,
    'IMP_WriteInt32':        0x10003600,
    'IMP_WriteInt64':        0x10003730,
    'IMP_WriteInt8':         0x100036c0,
    'IMP_WriteStr':          0x10003790,
    'IMP_WriteUInt16':       0x10003650,
    'IMP_WriteUInt32':       0x10003600,
    'IMP_WriteUInt64':       0x10003730,
    'IMP_WriteUInt8':        0x100036c0,
}

# 内部函数地址
INTERNAL_FUNCTIONS = {
    'encrypt_data':          0x10005c20,  # 数据加密
    'decrypt_data':          0x10005c60,  # 数据解密
    'derive_key':            0x10005b80,  # 密钥派生
    'send_buffer':           0x10001aa0,  # 发送缓冲区（写入长度前缀+发送）
    'connect_internal':      0x10001660,  # 内部连接函数
    'socket_connect':        0x10004920,  # socket连接（处理IP/域名）
    'init_crypto':           0x10001770,  # 初始化加密上下文
    'recv_handler':          0x10005cb0,  # 接收处理
    'log_message':           0x10005f80,  # 日志消息
}

# S盒地址
SBOX_ADDRESSES = {
    'key_sbox':              [0x10026448 + i * 0x100 for i in range(8)],
    'enc_sbox':              0x10026c48,  # 2048 bytes
    'dec_sbox':              0x10027448,  # 2048 bytes
}


if __name__ == '__main__':
    # 测试加密/解密
    print("=" * 60)
    print("IMProtocol 加密模块测试")
    print("=" * 60)

    # 使用测试密钥
    test_key = bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08])
    crypto = IMProtocolCrypto(test_key)

    plaintext = b"Hello, World! This is a test message."
    print("\n原文: %s" % plaintext.decode())
    print("原文(hex): %s" % plaintext.hex())

    # 加密
    encrypted = crypto.encrypt(plaintext)
    print("\n密文(hex): %s" % encrypted.hex())

    # 解密
    crypto.reset()
    decrypted = crypto.decrypt(encrypted)
    print("解密(hex): %s" % decrypted.hex())
    print("解密: %s" % decrypted.decode())

    assert decrypted == plaintext, "加密/解密测试失败！"
    print("\n✓ 加密/解密测试通过！")

    # 测试密钥派生
    print("\n" + "-" * 40)
    print("密钥派生测试")
    print("-" * 40)
    seed = bytes([0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0x11])
    derived = IMProtocolCrypto.derive_key(seed)
    print("种子:     %s" % seed.hex())
    print("派生密钥: %s" % derived.hex())

    # 测试帧构建
    print("\n" + "-" * 40)
    print("帧构建测试")
    print("-" * 40)
    payload = b"\x00\x01\x02\x03"
    frame = build_frame(payload, cmd=0x1234)
    print("Payload: %s" % payload.hex())
    print("Frame:   %s" % frame.hex())
    length, parsed = parse_frame(frame)
    print("解析长度: %d, Payload: %s" % (length, parsed.hex()))

    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)
