---
name: mxsj-project
description: 在 MXSJ_TW_2022（夢想世界台服 v2.27.2）仓库中进行开发、逆向取证、原生 TCP 兼容研究或编辑器维护时，定位当前实现与证据，选择对应验证流程。用于本项目工作，不用于其他游戏或通用 Python 问题。
---

# MXSJ 项目开发与原生研究

## 找到仓库和当前事实

先定位 `a565551313/MXSJ_TW_2022` 的实际 checkout。优先使用会话提供的
source-repo-map、工作目录或 Git remote；不要写死某台沙箱的绝对路径。
以下路径均相对**仓库根目录**，不是相对安装后的 skill 目录。

读取根 `AGENTS.md`、`docs/ARENA_SANDBOX_RECOVERY.md`、`docs/STATUS.md`
及目标组件说明。仓库内当前规则和用户本轮授权优先；skill 不替代这些文件。
检查实际分支、完整 HEAD 和 dirty tree；STATUS 中旧会话的分支、授权及测试
数字是历史记录，不代表本轮授权或本轮结果。

用户提到 master 更新时，先 fetch 并比较 origin/master 与当前分支；有可保留的
本地工作先保存。允许且可 fast-forward 时在会话指定分支同步。出现分叉时先
检查差异，按当前授权处理集成；不覆盖工作树、不改用历史 STATUS 的分支名。
同步后重新读取相关规则和状态，不以本 skill 的创建日期推断项目现状。

按 [references/workflows.md](references/workflows.md) 选择入口，只读取与请求
有关的材料。若存在 `knowledge-base/index.md`，按地图检索本次涉及的决策。

## 决策时保留的项目边界

- 仓库根本身是游戏安装目录。`data/*.fls`、原 DLL、key DB 等是研究输入；
  包写回到新目标，不能覆盖原件。禁止执行恢复的游戏模块，以 code object、
  反汇编和受限数据解析取证。详见当前 AGENTS 的具体限制。
- `tools/decompiler/output/` 的文本是线索，不是可信可执行源码。
  查全量语料前读 `docs/DECOMPILE_CORPUS.md`；优先定点恢复。
- 原生控件、资源和脚本机制遵循 AGENTS 的原生优先规则；替代方案不能以
  旧 overlay 实验为授权先例。涉及例外时先核对本轮已有授权。
- `mx_common/` 是共享核心真源；先改真源再用 vendor 工具生成副本。
  新增工具/编辑器遵守 `docs/PYTHON_TOOL_CONVENTIONS.md` 的结构与交付约定。
- `local_server/`、`server/`、根目录 Mock 是不同实现。不能将 Mock 逻辑或候选
  CSV 的测试结果直接解释为正式服能力；从对应 README/STATUS 核验具体边界。

## 原生协议与证据判断

涉及握手、加密、封帧或客户端接入时，先读 `notes/native_tcp_channel.md` 和
`tools/native_channel/README.md`，再读实际调用方。已有独立 codec 不应被复制
出另一个算法版本。协议号、帧宽度和加密阶段必须绑定客户端构建与调用路径。

记录输入 SHA256、PE 地址/脚本 entry 和操作数位置、原始观察、复现命令及
未确定部分。PE VA 应注明首选基址；不要直接当作运行进程地址。

分别描述：静态指令证据、受限原生函数模拟、同族 DLL 对照、Python/Mock 回环、
用户实机反馈、我方实机复现。它们能支持的结论不同。阅读更新后的 STATUS：
已有 Windows 用户口述进图记录时应如实引用来源，也不能转称为我方已复现、
抓包验证或完整认证/事务保证。旧报告中的“尚无任何实机反馈”不能覆盖新记录。

Mock 启动前读 `docs/MOCK_SERVER.md` 并检查当前 main/参数/写入路径。
v1 的 SetSeed 绕过、v2 的原生加密及两者客户端准备行为不可混为一谈。
`--no-patch` 的存在不证明只读；不要为了文档或 skill 验证启动服务器。

## 验证与交付

按实际改动选择 references 中对应检查，并核对当前组件 README 的命令。
现有验证记录可用于相同输入；上游修改了哪些输入，就重新评估相关检查，
不要因同步 master 而把历史 pass 全部重算或全部丢弃。

算法验证优先使用独立原生向量；不能仅用自身编码器/解码器往返证明兼容。
不要改固定向量去迎合实现。Windows 静态检查、offscreen Qt 与 spec 干跑不
代表 Windows EXE 或真实客户端验收。对文档/skill 改动验证结构、路径和含义，
不为此启动会写客户端文件的流程。

更新 `docs/STATUS.md` 时写本次结果、来源和剩余边界，保留其他组件的有效记录。
提交/推送/PR 遵守本轮指定分支、当前权限和已有用户授权；skill 本身不授予
发布、改原包、启动公网监听或跨任务协调权限。
