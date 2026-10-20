# 原生游戏 TCP 兼容候选模块 0.1.0

**已实现可独立调用的握手、双向密码流、非对称帧和下行 LZW 编解码。**
密钥派生、密钥流生成和解压已用目标 `mxmain.dll` 原生函数离线对照；
完整密码器 init/refill/process 用同包 `exe/render.dll` 对照。
**目标主程序的受保护密码器包装函数及 Windows 原生联网仍未验收。**
不能据此声称已登录、进图或完成整个原生信道验收。

研究细节、地址、输入摘要和不确定项见
[研究说明](../../notes/native_tcp_channel.md)。固定向量来自隔离 x86 指令模拟，
不是实际网络抓包。模块不启动监听、不改客户端、不依赖账号或业务服务。

## 快速运行

从仓库根目录：

```bash
python3 tools/native_channel/bootstrap.py --check-only
python3 tools/native_channel/run.py
python3 -m unittest discover -s tools/native_channel/tests -v
```

仅需 Python ≥3.10 标准库。复制整个 `tools/native_channel/` 目录后，上述工具
仍可独立运行普通测试和示例；原生 oracle / 脚本取证需要原仓库材料。
Windows 双击 `启动原生信道.bat` 运行离线示例。

安装为库（可选）：

```bash
python3 -m pip install ./tools/native_channel
python3 -m mxsj_native_channel
```

## 接口与示例

```python
from mxsj_native_channel import Channel, ClientHandshake, hello, hello_reply

# 固定假 seed；示例只交换内存字节，不连接网络。
seed = 0x12345678
server = Channel(seed, "server")
client = ClientHandshake()
packets = client.feed(hello(seed) + server.send(2, b"synthetic"))
assert packets[0].payload == b"synthetic"
reply = client.take_reply()
assert reply == hello_reply(seed)  # 25 字节，必须直接发送，不加密、不加帧
assert client.channel is not None
wire = client.channel.send(3, b"demo")
assert server.feed(wire)[0].payload == b"demo"
client.finish()
server.finish()
```

| API | 契约 |
|---|---|
| `derive(seed) -> Keys` | uint32 输入；返回客户端 `rx_key, tx_key, rx_skip, tx_skip` |
| `StreamCipher(key, skip)` | 初始化并丢弃 skip 字节；`crypt(bytes)` 对称异或并推进；`discard(n)` 只推进 |
| `hello(seed, server_number=1, certificate=0)` | 9 字节明文 HELLO |
| `hello_reply(seed)` | 25 字节裸应答；内部还原脚本的有符号种子语义 |
| `ClientHandshake.feed(chunk) -> list[Packet]` | 增量解析 HELLO；处理同一 chunk 中随后出现的密文 |
| `ClientHandshake.take_reply()` | 握手后取一次裸应答；后续返回空串 |
| `Channel(seed, role, length_bytes=3, max_frame=None, max_output=1048576)` | 已握手连接；`role` 为 `client/server`，方向自动映射；扩展长度支持 2/3 字节 |
| `Channel.send(command, payload=b'') -> bytes` | 构造并加密该方向完整包，推进发送密码流 |
| `Channel.feed(chunk) -> list[Packet]` | 解密并解析 0..N 包；保留未完成帧及 LZW 字典 |
| `finish()` | EOF 检查；残帧/握手未完成报 `ProtocolError` |

TCP 接入方负责：使用 `sendall` 或保存未发出的密文字节及偏移；
**部分写失败后不能重新调用 `send()` 加密同一个包**。裸应答必须排在后续
加密上行之前。服务端先收满并核验 25 字节裸应答，再把余下密文字节交给
`Channel.feed()`；不要把裸应答送入解密器。示例允许下行与 HELLO 粘包，
不表示真实服务端一定这样发送。

每次重连新建对象；单连接的读写顺序由调用方串行维护，实例不保证线程安全。
`ProtocolError` 后关闭连接并丢弃该实例。模块不承担超时、TLS、重试、登录、
认证业务、代理握手或上层字段序列化。`max_frame` 默认至多 1 MiB，并限制在
所选扩展长度可表达范围内；上行 payload 保守限制 247 字节。

## 原生 oracle 与证据复现

```bash
python3 -m venv /tmp/mxsj-channel-oracle
/tmp/mxsj-channel-oracle/bin/python -m pip install pefile==2024.8.26 unicorn==2.1.4
/tmp/mxsj-channel-oracle/bin/python tools/native_channel/tests/native_oracle.py
python3 tools/native_channel/tests/script_evidence.py
```

Windows venv 使用 `Scripts\python.exe`。oracle 校验两 DLL 的 SHA256，映射 PE
到 Unicorn，限定执行指令数和时间，不加载 Windows DLL，不调用入口点/系统导入。
解压函数唯一桩是 `/GS` cookie 检查返回；密码算法指令没有替换。
`--write` 重建 `evidence/vectors.json`，默认只核对；`--repo PATH` 指定原材料根目录。

- [vectors.json](evidence/vectors.json)：5 个假种子的双向派生、前 64 字节密文、
  9,000 字节 SHA256；4 个原生生成块；连续 LZW 帧及字典状态。
- [native-disassembly.txt](evidence/native-disassembly.txt)：带完整 objdump 命令的地址证据（清理行尾空白）。
- [script-bytecode.txt](evidence/script-bytecode.txt)：原始包中两个 code object 的操作数证据。
- 普通 unittest 不依赖 oracle 包，不读取客户端二进制，直接核验固定原生向量。

## 差异与验收边界

- 下行发送端采用合法的 literal-only LZW 编码，兼容原生解压测试，但无字典压缩收益；
  接收端完整处理字典引用、KwKwK、跨帧字典和延迟重置。
- 原生解码器会把输入耗尽当作结束，本模块严格要求 `0x7ff` 结束码；
  对不合法字典引用及过大输出也显式拒绝。若真实帧省略结束码，需有抓包证据后
  决定是否增加兼容选项，不能把这一限制当成目标已确认行为。
- 原生超长 C2S 的行为是弹错后继续，本模块在加密前拒绝总长 >250 字节。
- `SetSeed2`、代理/中转连接、加密前其他包和私有扩展参数不在此版本支持范围。
- 未连接官方服务、未使用真实账号。真实 Windows 客户端、EXE 构建和应用层认证待验。

## 质量与 Windows 构建

```bash
ruff check tools/native_channel
python3 tools/devkit/check_windows_compat.py tools/native_channel --strict
```

`build_exe.bat` 在 Windows 创建 venv、装开发依赖、跑普通测试并使用
PyInstaller 构建 `dist\MXSJNativeChannel\MXSJNativeChannel.exe`。
这是控制台离线示例，非游戏服务器。Linux 静态检查/打包配置干跑不等于 Windows
可执行文件验收。无 GUI、数据库、安装目录用户配置或后台服务。
