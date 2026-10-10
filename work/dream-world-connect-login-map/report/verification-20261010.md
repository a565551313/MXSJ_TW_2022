# 项目真实情况核对报告（2026-10-10）

**核对人**: agent（session 分支 `arena/febc1561-mxsj-tw-2022`）
**核对方式**: 只读核对 + 在仓库外（`/tmp`）重跑解码/测试；未删除、移动、`git rm` 任何文件；未连接任何外部服务器；未运行原版客户端。
**仓库状态**: `HEAD` = `master` = `origin/master` = `ffec3d9`（Merge PR #5）。原 clone 为浅克隆（仅 1 个 commit），本次已执行 `git fetch --unshallow` 补全历史（本地现有 23 个 commit），不影响任何工作文件。
**配套证据**: `evidence/E-VERIFY-001.md`

---

## 0. 结论摘要

1. **项目主线可复核的部分是真实的**：FLS 全量解码统计、entry 516 反编译、映射表 v4.3、地图格式与 11 项地图测试、`IMProtocol.dll` 的 29 个导出、`IMProtocolCrypto` 的加解密往返，均经本次重跑确认。
2. **最关键的缺口没有被填上**：仓库里**没有任何一个真实捕获的应用层字节**。`notes/protocol-artifacts/stream-0001..0022.bin` 全部为 0 字节；通信密钥（`IMP_RefreshCryptKey`）仍未获得。因此“加密算法已完整破解”只能理解为“算法实现与 S 盒已还原，但无法对真实报文解密”。
3. **交接文档中多处“已确认”的结论没有证据支撑**：
   - “loginhello 明文包已确认（34 字节）”：对应文件 `tools/test-data/test_loginhello_plain.bin` **不存在**，字节串只出现在文档中，来源未记录。
   - C→S 命令字数值（0x0001/0x0002/0x0003/0x0010/0x00FF）：脚本中只有符号名（如 `LOAD_ATTR 'C2GS_SELECT_SERVER'`），数值来源在仓库中找不到证据。
   - 登录流程“已完成”（WI-009）：用户观察与运行日志都表明账号页未到达，无服务端响应。
4. **`server.ini` 已被修改**：当前提交（`1106434`）把原先指向 `203.70.8.205` 的两条记录改成了 `127.0.0.1`。文档中“lastserver 映射到 203.70.8.205”与当前文件不符。本次**未改动**该文件，仅记录事实，等待你决定是否恢复。
5. **文档中多处命令和代码示例不可运行**（加密示例、FLS 解码命令、pymarshal 用法、data_browser 参数），已在各文档中修正或标注。

---

## 1. 仓库与历史

| 项目 | 文档说法 | 核实结果 | 状态 |
|---|---|---|---|
| 工作分支 | `arena/6fbb3403-mxsj-tw-2022` | 本会话分支为 `arena/febc1561-mxsj-tw-2022`，指向 `ffec3d9`。`6fbb3403` 已经通过 PR #5 合入 master，远端已无该分支 | ❌ 过时 |
| 最新 commit | `711e6a7` | `711e6a7` 存在，且是 `HEAD` 的祖先；其后还有 `4e13085`（交接文档）、`51e1327`（清理 `__pycache__`）、`60b039c`（合并 master）、`ffec3d9`（PR #5） | ⚠️ 已过时（不是最新） |
| 历史可核对性 | — | 原 clone 为浅克隆，无法核对 `711e6a7`；已 unshallow，现可核对 | ✅ 已补全 |
| “不要合并 master” | 文档提醒 | 当前分支与 master 完全一致（同一 commit），该提醒已不适用 | ⚠️ 已过时 |
| 跟踪文件 | “master 有大量二进制不应入库” | 当前 `HEAD` 跟踪 577 个文件，`git ls-files` 体积合计约 478 MB（du 口径），包括 `libcef.dll`、`exe/render.dll`（24.5 MB）、`data/script.fls`、大量 `.ogg`。这些二进制是 PR #2（`8038b1e`）等提交引入的，**仍在仓库中** | ❌ 未解决（建议处理，但本次未移除） |

## 2. 游戏文件与二进制

| 项目 | 文档说法 | 核实结果 | 状态 |
|---|---|---|---|
| `IMProtocol.dll` 187 KB、29 个导出 | 同 | 187,216 B；导出 29；导入 `WS2_32.dll`、`KERNEL32.dll`、`USER32.dll`、`SHLWAPI.dll` | ✅ |
| `mx.exe` / `mxmain.dll` 9.7 MB 主程序 | 两者为不同主程序 | 两者 **字节完全相同**（MD5 `2609423f…`，9,698,712 B）。`mx.exe` 导入 `IMProtocol.dll`、`dgw.dll`、`libcef.dll` 等 | ⚠️ 需更正：二者为同一文件的两个名字 |
| “Themida 保护” | 文档 §1 | 样本节名为 `_dyprot0`、`_dyprot1`，未发现 Themida 特征串；根目录有 `DuoyiProtect.dll`。更像厂商自有保护 | ❌ 不成立（改为“疑似厂商自有保护”） |
| “内嵌 Python 2.7 解释器” | 文档 §1 | `mx.exe` 导入表中无 `python27.dll`；Python 2.7 运行时位于 `exe/python27.dll`、`exe/python27_dy.dll` | ⚠️ 位置需更正 |
| `render.dll`（24 MB） | 文档多处 | 根目录**无** `render.dll`；实际路径为 `exe/render.dll`（24,543,576 B）；根目录的是 `d2drender.dll`（27 KB） | ⚠️ 路径需更正 |
| `data/script.fls` 24 MB、5002 条目 | 同 | 24,454,082 B；SHA-256 `8b6e9266…` 与 `entry-result` 记录一致；记录的 `entry_count` 为 5002 | ✅ |
| `map/*.map` 5 个、约 1.1 MB | 同 | 5 个文件，合计 1,094,136 B；头部 `0.1M`，2000×1500 | ✅ |
| 客户端总大小 “约 703 MB” | 文档 §1 | 仓库中只包含部分文件，无法从仓库核实完整安装大小 | ❔ 未核实 |
| `server.ini` 的端点 | “203.70.8.198–207、3134” | 当前文件只含 4 个外网 IP（198、204、206、207）+ 2 条 `127.0.0.1`；`203.70.8.205` 只存在于历史版本（`caa7996`）。`203.70.8.198–207` 是推测范围，不是实测列表 | ❌ 需更正 |

### 2.1 `server.ini` 变更历史（重要）

| 提交 | 内容（GBK 解码后的服务器条目） |
|---|---|
| `caa7996` | 推荐区/免费区两条均为 `203.70.8.205`；另有 `207/206/204/198`。`[Login] lastserver=` 为空 |
| `1106434`（当前 HEAD） | 推荐区/免费区两条改为 `127.0.0.1`；其余不变 |

`E-001`（2026-10-09 10:37）记录的是原始文件，与 `caa7996` 一致。也就是说，**当前仓库中的 `server.ini` 不是游戏原始配置**，而是为本地回环测试修改过的版本。`mx.ini`、`mxbak.ini` 的 `lastserver=` 同样为空。

## 3. 脚本与解码

| 项目 | 文档说法 | 核实结果 | 状态 |
|---|---|---|---|
| FLS 全量解码 ok 4484 / suspect 246 / fail 272 | 同 | `decode-results-final.jsonl` 共 5002 行，统计与文档一致 | ✅ |
| `script-catalog.csv` “5007 行” | 文档 §3.6 | 实际 5003 行（含表头），即 5002 条数据 | ⚠️ 已更正 |
| `notes/decoder-artifacts/all_scripts_catalog.json` “全部 5002 条目” | 文档 §5 | 该文件**只有 11 条记录**（如 index 363、516） | ❌ 不成立（已在 `notes/decoder-artifacts/README.md` 中说明） |
| entry 516 `netserver.py`，59 个 code object | 同 | 在仓库外用 `fls_batch_decoder.py --archive data/script.fls --index 516` 重跑：59 个 code object，名称与文档一致；marshal 中包含 `loginhello`、`TEST_HELLO`、`RESELECT_HELLO`、`CMXNet`、`OnServerCmd`、`m_Pwd`、`m_PassPort` | ✅ |
| 映射表 v4.3 “43 + 5 个映射、16 个未知” | 同 | `mapping_table_v4.json`：version `4.3-taskB`，`table_a` 43、`table_b` 5、`unknown_hot` 16 组 | ✅（注意：`unknown_hot` 是 16 **组**，不是 16 个字节值） |
| “16 个未知 opcode”的列表 | 文档 §4.6 列出 24 个字节值 | 与映射表 `unknown_hot` 的 16 组口径不一致 | ⚠️ 口径需统一 |
| 协议命令目录 63 KB、1782 行 | 同 | 63,200 B、1782 行 | ✅ |
| 商城、战斗、任务/物品分析 | 同 | 文件存在 | ✅（未逐条复核内容） |

## 4. 加密与协议

| 项目 | 文档说法 | 核实结果 | 状态 |
|---|---|---|---|
| “8 状态流密码、S 盒全部提取” | 文档 §3.1 | `enc_sbox.bin`、`dec_sbox.bin`（各 2048 B）与 `key_sbox_0..7.bin`（各 256 B）齐全；`IMProtocolCrypto.encrypt/decrypt` 往返一致 | ✅ 算法实现可用 |
| “加密算法完整破解” | 多处 | 算法与 S 盒已还原，但**通信密钥未知**（`IMP_RefreshCryptKey` 运行时传入，WI-010 未完成）。密钥候选 4 个仍是“前期分析”，未验证。**无法解密真实报文** | ⚠️ 需更正为“算法已还原，密钥未获得” |
| `im_crypto.py` 示例 `CryptContext/encrypt/decrypt/derive_key` | 文档 §6.3、QUICK_START | 文件中**没有**这些名字；实际 API 为 `IMProtocolCrypto`（方法 `encrypt`、`decrypt`、`encrypt_packet`、`decrypt_packet`、`derive_key`、`set_key`、`reset`）、`build_frame`、`parse_frame` | ❌ 示例不可运行（已修正） |
| 帧格式 `uint16_be 总长度 + uint16_be 命令字 + payload` | 文档 §3.1、§3.5 | 与 `build_frame`/`parse_frame` 的实现一致；但**没有任何真实报文支持**，仅为推断 | ⚠️ 推断 |
| `loginhello` 明文包 34 B | “明文包已确认” | 文件 `tools/test-data/test_loginhello_plain.bin` **不存在**（`tools/test-data/` 目录也不存在）；字节串仅出现在文档中；生成方式未记录 | ❌ 无证据（已标注为“未经证实的构造样本”） |
| 命令字 0x0001（loginhello） | “明文包确认 ✅” | 无证据文件；脚本中只有符号名 | ❌ 未核实 |
| 命令字 0x0002、0x0003、0x0010、0x00FF | “前期分析 ✅” | 脚本只有符号名（`LOAD_ATTR`），数值来源未找到证据 | ❌ 未核实 |
| S→C 命令字 0x1001–0x10FF | 推测 | 与文档一致，明确为推测 | ✅（仍是推测） |
| “S2CServerRoleInfo 抓包” | 任务 ③ | 无任何抓包数据 | ❌ 未完成 |
| 回环捕获 `stream-0001..0022.bin` | 文档未明确说明为空 | **全部 0 字节**；`responsive-harness.log` 记录的 22 次连接均为 0 字节保存 | ❌ 关键缺口（已写入 `notes/protocol-artifacts/README.md`） |
| 回环 harness 发送 `00 02` 导致客户端异常 | 文档 §7.8 | `E-IDA-DYN-004`：IDA 在 `KernelBase.dll!RaiseException+0x62` 暂停 | ✅ 有动态证据 |
| 客户端已连接 `127.0.0.1:3134` | — | `E-LOOPBACK-002`：截图 + `Get-NetTCPConnection` 显示 Established；但客户端未发送应用层数据 | ✅ |

## 5. 地图

| 项目 | 文档说法 | 核实结果 | 状态 |
|---|---|---|---|
| `.map` 格式、5 张底图 | 同 | `work/dream-world-connect-login-map/tools/map-textures/` 下 2101/2111/2112/2122/2303 的 PNG 齐全（另有 `2303-sector-24.gepj.bin`）；`map-data/` 下 5 个 JSON 齐全 | ✅（路径需更正为 `work/…/tools/`） |
| `test_maps.py` 测试 | “11+7 项全部通过” | `notes/task-c-地图分析/artifacts/test_maps.py`：`Ran 11 tests … OK`；`test_map_gui.py` 未核实 | ✅ 部分 |
| `map_parser.py`、`map_viewer.py`、`gepj_decoder.py` 可用 | 同 | `--help` 正常 | ✅ |
| LLEC 可行走语义 | 未完成 | 证据 `E-MAP-003` 明确“尚未证明” | ✅ 仍未完成 |

## 6. 工具可用性

| 工具 | 文档中的用法 | 实际结果 | 状态 |
|---|---|---|---|
| `tools/fls_batch_decoder.py` | `--entry 516 --input … --output-dir …` | 参数不存在；真实参数为 `--archive`、`--index`、`--all`、`--output`、`--indices`、`--resume` 等。`--archive data/script.fls --index 516 --output DIR` 可用 | ❌ 文档用法错误（已修正） |
| `tools/pymarshal_dis.py` | `--mapping …`、`--help` | 不支持 `--help`（会被当作文件名报错）；不存在 `--mapping`，映射表会自动加载。真实参数：`--consts`、`--max-code N`、`--code-only NAME`、`--sizes` | ❌ 文档用法错误（已修正） |
| `work/…/tools/mock_server.py` | `tools/mock_server.py`（根目录） | 文件在 `work/dream-world-connect-login-map/tools/`；`--help` 正常；以 `--response-type auto --port 3999` 启动并绑定 `127.0.0.1` 正常，运行时会在 `tools/mock-server-logs/` 下生成日志 | ⚠️ 路径与副作用需说明 |
| `work/…/tools/packet_analyzer.py` | 同 | `--help` 正常；输入样本缺失，未能跑通样例 | ⚠️ |
| `work/…/tools/enhanced_capture_server.py` | 同 | `--help` 正常 | ✅ |
| `tools/data_browser/app.py` | `--cli` | `--help` 会直接启动 Web 服务（超时）；CLI 模式的真实用法是位置参数 `cli`（如 `app.py cli equipment 关键词`） | ⚠️ 用法需更正 |
| `tools/data-parser/universal_fls_tool.py` | 6 种归档 | `--help` 正常 | ✅ |

## 7. 证据与状态文件

| 项目 | 核实结果 | 状态 |
|---|---|---|
| workitems / timeline 引用的证据 ID | `E-IDA-001` 与 `E-IDA-DYN-002` 被引用但文件不存在 | ❌ 已在 `workitems.md` 中标注 |
| `E-LOOPBACK-001` | 记录“只到选服界面，捕获 0 字节” | ✅ 与核实一致 |
| WI-009 “done” | 与 E-LOOPBACK-001、WI-003 及 `handoff-20261009.md` 矛盾 | ❌ 已改回 `in_progress` |
| WI-011 “entry 516 已完整解码” | 已在仓库外重跑核实 | ✅ |
| WI-012 “模拟服务器已完成” | 框架存在并可启动，但未与真实客户端验证，无法模拟真实登录 | ⚠️ 已改为 partial |

## 8. 文档中的失效引用（抽样）

对所有 `.md` 中反引号包裹的文件名做了存在性检查（1175 处引用，83 个文档）。大部分“缺失”是游戏内部脚本路径（如 `script\login\netserver.py`）或历史绝对路径，属于正常引用。需要关注的、属于本项目文件的失效引用包括：

- `tools/test-data/test_loginhello_plain.bin`、`test_loginhello_v1/v2.bin`（`tools/README.md`、`protocol-commands-values.md`、`HANDOVER`、`INDEX`）
- `tools/mock_server_v2.py`、`notes/login-flow-complete.md`、`notes/server-list-format.md`、`evidence/E-MOCK-001.md`（`TASK-E`）
- `docs/MXSJ-Protocol-Specification.md`、`docs/packet-examples.md`、`docs/state-machine.md`、`tools/protocol_parser.py`、`evidence/E-DOC-001.md`（`TASK-G`、`TASK_DISPATCH`）
- `task-briefs/TASK-X-xxx.md`（模板占位符，`QUICK_START`、`DISPATCH_OVERVIEW`、`发给其他会话的指令.md`）
- `E-IDA-001`、`E-IDA-DYN-002`（被引用，不存在）
- `E-MAP-002`/`E-MAP-003` 中引用的 `artifacts/llec-pixel-correlation.json` 等（部分在 `notes/task-c-地图分析/artifacts/` 下，路径需写全）

以上失效引用**未删除**，已在相关文档中加注说明。

## 9. 本次核对产生的新文件（均为新增，未删除任何既有文件）

- `work/dream-world-connect-login-map/report/verification-20261010.md`（本文件）
- `work/dream-world-connect-login-map/evidence/E-VERIFY-001.md`
- `work/dream-world-connect-login-map/notes/protocol-artifacts/README.md`
- `work/dream-world-connect-login-map/notes/decoder-artifacts/README.md`
- ~~`work/dream-world-connect-login-map/tools/mock-server-logs/mock-server-20261010-094859.log`~~（`mock_server.py` 试运行产生的日志，经用户确认后已删除，目录一并移除）
- 仓库外临时文件：`/tmp/verify516/`、`/tmp/pevenv/`（不在仓库内）

## 10. 尚未解决、需要你决定的事项

1. **`server.ini` 保留回环配置（已决定，用户 2026-10-10 确认）**：`127.0.0.1` 是有意的本地回环配置，不恢复 `caa7996` 的 `203.70.8.205`。
2. **已处理（用户确认）**：试运行日志 `tools/mock-server-logs/` 已删除；各类 `__pycache__` 仍被 `.gitignore` 忽略，保留。
3. **游戏二进制与资源保留在 Git 中（已决定，2026-10-10 用户指示）**：不做移出、不做 `git rm --cached`、不迁移到外部存储。本次核对未改动任何此类文件。
4. **通信密钥（WI-010）仍是唯一的关键阻塞**。需要在 Windows 端、本地回环、测试副本中抓取真实握手数据后才能推进。
