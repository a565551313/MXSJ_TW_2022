# tools 工具导航与生命周期

核对：2026-10-18，基线 `886915c`。这是第一阶段入口治理：**没有移动、删除或修改任何工具算法，也没有重建资源／索引**。
当前项目状态见 [STATUS](../docs/STATUS.md)，实际依赖见 [DEPENDENCIES](DEPENDENCIES.md)。
工具的历史年份、名字里的 Universal、测试通过或被其他程序调用，都不能单独证明原生兼容。

## 按任务选择入口

| 任务 | 优先入口 | 边界 |
|---|---|---|
| 浏览／替换／导出普通资源 | [资源编辑器](../resource_editor/README.md) | 新包保护；不是任意格式全覆盖 |
| 编辑 `.dlg` 布局 | [UI 编辑器](../ui_editor/README.md) | 不自动修改脚本接线；游戏渲染另验 |
| 恢复／修改／编译脚本 | [脚本编辑器](../script_editor/README.md) | 恢复候选不等于可信源码；原生验收另做 |
| 地图预览／导出 | [地图编辑器](../map_editor/README.md) | 未解碰撞不是可通行 |
| 静态数据异常复核 | [只读复核系统](../server/README.md) | 与旧 SQLite 数据集不完全等价 |
| 脚本说明与来源 | [脚本手册](../script_manual/README.md) | 完整登记不等于完整讲解 |
| 原生游戏 TCP 算法／离线复现 | [native_channel](native_channel/README.md) | 候选兼容层；目标保护包装器与真实客户端联网待验 |
| Windows 检查／共享核心同步 | [devkit](devkit/README.md) | 静态检查不替代实机 |
| PE 资源／专项逆向／历史复现 | 下表对应工具 | 先确认样本、输出和副作用 |

## 状态含义

- **现役**：当前维护入口或仍承担明确构建职责；不表示全部已验收。
- **研究专用**：有独立分析用途，只在已核输入／算法范围使用。
- **历史复现**：保留以重现旧证据，不推荐用于新的编辑交付。
- **停用**：已否决或暂停部署；保留文件不是恢复使用授权。

目录可混合多种状态；不以目录名或“v3”跨专题推断版本。

## 逐项索引

| 路径 | 状态／适用材料 | 输出与副作用 | 替代入口／保留理由 |
|---|---|---|---|
| [devkit/](devkit/README.md) | 现役；工具源码／共享核心 | check 只检查；`vendor_core --write` 会重写生成副本 | 当前无替代；改真源再分发 |
| [registration/](registration/README.md) | 现役原生注册专项，混有历史诊断；固定客户端与旧 VM | 构建／交付脚本产生布局、FLS 或 ZIP，逐命令检查 | 尚无真实注册服务；构建依赖旧 decompiler，不能删依赖 |
| [script_link/](script_link/README.md) | 现役索引职责，旧解码生成链待评估 | 默认可重写 UI 的静态索引 JSON | UI 运行读产物而非现场解码；不等于索引已自动升级到 dev7 |
| [decompiler/](decompiler/README.md) | 研究专用＋历史复现；双 VM／固定包参数 | 恢复文本、pyc、报告、新包；不执行候选源码 | 日常编辑走脚本编辑器；来源核验／构建仍有依赖 |
| [decompiler/output/](decompiler/output/) | 历史复现数据 | 非准确源码，禁止导入／执行；部分文件被探针读取 | 不是可随手清理的缓存；不是生产配置 |
| [data-parser/](data-parser/README.md) | 混合；逐文件见子表 | 解包、提取、改图、PE/FLS 输出各不相同 | 常规编辑走编辑器；PE 等专项未证明被替代 |
| [data_browser/](data_browser/README.md) | 历史复现；旧 SQLite 浏览器 | Web 入口启动监听，桌面入口创建 GUI/TUI | 新复核系统优先，但不承诺覆盖全部旧表 |
| [data-export/](data-export/README.md) | 历史导出材料 | CSV／JSON／SQLite；被旧浏览器读取 | 不是正式 game_data，不可无核对迁入 |
| [dis_v43/](dis_v43/README.md) | 历史复现；v4.3 映射及对应 marshal 样本 | 打印反汇编／候选对齐结果 | 当前双 VM 核心不等于此 CLI 的完全等价替代 |
| [fls_batch_decoder.py](fls_batch_decoder.py) | 历史复现／底层依赖；早期启发式分段与 marshal 读取 | 可写解码报告／产物 | 新写包不以旧猜段为真值；多处依赖 `MarshalReader` |
| [pymarshal_dis.py](pymarshal_dis.py) | 历史复现；旧 opcode 假设 | 反汇编输出，复用 `MarshalReader` | 不视为通用当前 VM 解释器 |
| [extract_co_signatures.py](extract_co_signatures.py) | 历史专项；旧 decoder 及指定条目 | 写 `co<idx>.json`；下游命令号推断含启发式 | 不是权威协议生成器；不能只因文件名“签名”就信任结果 |
| [ui_pack_write_probe.py](ui_pack_write_probe.py) | 历史复现；M1 固定 script 包探针 | 内存构建／逐条比较及临时 FLS 写入，调用旧补丁和 UI 核心 | 当前发布走编辑器；探针通过不等于实际引擎通过 |
| [client_patches/](client_patches/README.md) 注册 overlay／visual_assets | **停用**；注册 v3/v3.2/v3.3 已否决 | 历史构建可产生 FLS／PNG，但禁止据此分发 | 转原生 registration；不能推广为整个目录停用 |
| [native_uieditor_open_list/](client_patches/native_uieditor_open_list/README.md) | **停用（暂停部署）**；内置 UI 列表旧源码 v1/v2 | 候选源码与审计，无当前可部署保证 | 不能因为编辑器修复就重新启用旧候选 |
| [native_uieditor_open_list_v3/](client_patches/native_uieditor_open_list_v3/README.md) | **研究专用**；纠正属性名的源码参考 | 完整重编译离线参考，无可直接部署 FLS | 尚未 Windows／游戏验收；不要替换已验收原位包 |

## 操作前必读

1. “研究专用／历史复现”不代表可删除；先查运行、证据和说明三类依赖。
2. 不给摘要锁定的旧 `.py` 随手加注释；本轮只补旁路文档。
3. 旧解包／重包脚本没有因新文档而获得编辑器同等级输出保护。先审代码，输入只读，输出选仓库外新目录，不覆盖已有成果／源路径及别名。历史 ui_pack_write_probe 使用自己的临时文件写入路径，不因“探针”名称而例外。
4. 不执行反编译模块、不绕过敏感排除、不改原包与 key DB；批量恢复前读 [语料说明](../docs/DECOMPILE_CORPUS.md)。
5. 迁移先固定旧输入与输出，再独立对比新结果；原生游戏验收与工具自洽回读分开。第二阶段迁移和第三阶段清理尚未实施。
