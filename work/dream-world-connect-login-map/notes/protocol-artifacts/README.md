# protocol-artifacts 目录说明（2026-10-10 核对更新）

| 文件 | 状态 | 说明 |
|---|---|---|
| `im_crypto.py` | ✅ 可运行 | `IMProtocolCrypto`（`encrypt`/`decrypt`/`encrypt_packet`/`decrypt_packet`/`derive_key`/`set_key`/`reset`）、`build_frame`、`parse_frame`。往返自检通过。**注意：没有 `CryptContext`/`encrypt()`/`decrypt()` 模块级函数**（旧文档示例已废弃）。默认密钥为 `00..07`，仅为占位，不是游戏真实密钥。 |
| `enc_sbox.bin`、`dec_sbox.bin` | ✅ | 各 2048 B |
| `key_sbox_0.bin` ～ `key_sbox_7.bin` | ✅ | 各 256 B，密钥派生用 |
| `stream-0001.bin` ～ `stream-0022.bin` | ❌ **全部为 0 字节** | 回环捕获未收到任何客户端应用层数据（见 `evidence/E-LOOPBACK-001.md`、`E-LOOPBACK-002.md`）。**不能作为协议样本使用。** |
| `responsive-harness.log` | ✅ 记录 | 22 次连接均为 0 字节保存；2026-10-09 23:39:03 发送过 `00 02` 初始响应，随后客户端异常（见 `E-IDA-DYN-004`）。 |
| `responsive_loopback_harness.py` | 未在本次核对中运行 | 默认只捕获；只有显式给 `--response-hex` 才发送响应。 |

**结论**：目前本目录能证明的是“加密算法实现与 S 盒可复现”，不能证明“真实报文可解密”。真实密钥仍未获得（WI-010）。
