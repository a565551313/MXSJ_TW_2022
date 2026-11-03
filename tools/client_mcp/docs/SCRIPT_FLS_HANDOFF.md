# 用户修改版 script.fls 交付与核对流程

> 状态：现行口径。日期：2026-11-03。
> 背景：用户明确 `data/script.fls` **就地改原文件**（自己备份），不再有“仓库原始包不许覆盖”的老规矩，也不再走仓外交付。

## 1. 当前包身份

```text
data/script.fls（仓库内就地修改，2026-11-03）
SHA-256: 7ebcbac7a0fe5e0f7fa0a444e6069158df33dff045e4f876d2f76a4d767622dd
大小:    24,273,265 B
0SLF:    count=5003，目录 0 违规，5003 个 zlib 流全部可解、首尾相接
说明:    在无钩子版 1d6b2152…3074a 上给 mainpage 加了受保护钩子（try/except 包裹）；
         除 mainpage 外 5002 条载荷逐字节未变

tools/decompiler/script_fls_keys.json（未改动）
SHA-256: 43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb
```

历史基线 `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`（5002 条原始包）只作对照，不再要求工作区匹配。

## 2. 用户需要提供的最小材料

### 2.1 必须

1. 修改版 `script.fls` 文件本体；
2. 文件 SHA-256，如果用户方便计算；
3. 修改版对应客户端版本 / 构建说明；
4. 是否仍使用仓库原始 key DB；
5. 是否同时修改过 `interface.fls`、`data.fls`、`mx.exe`、`mxmain.dll` 或启动器。

### 2.2 强烈建议

1. 修改来源：自己编译、工具生成、第三方补丁、历史测试包等；
2. 已知修改条目或模块，例如注册、登录、UI、网络、GM 命令等；
3. 最近一次 Windows 实机运行结果；
4. 相关日志，需脱敏；
5. 如果由构建器生成，提供构建命令或构建报告。

### 2.3 不要提供

- 真实账号密码；
- 票据 / 密钥；
- 未脱敏聊天日志；
- 与测试无关的个人数据。

## 3. 推荐交付位置

不要把修改版直接覆盖到：

```text
data/script.fls
```

推荐放到隔离输入目录，例如：

```text
../mxsj-client-mcp-out/inputs/<timestamp>/script.fls
```

或在仓库内使用被忽略的输入目录：

```text
tools/client_mcp/inputs/<timestamp>/script.fls
```

`inputs/` 目录中的二进制包不得提交 Git。

## 4. 输入登记清单

收到修改版后，先写输入登记，不做修改：

```json
{
  "received_at": "2026-11-02T00:00:00+08:00",
  "file": "script.fls",
  "sha256": "<待计算>",
  "size_bytes": 0,
  "source": "user-provided modified client package",
  "claimed_client_version": "<待用户提供>",
  "key_db_assumed": "tools/decompiler/script_fls_keys.json",
  "other_modified_files": [],
  "windows_last_verified": "unknown",
  "status": "received-not-inspected"
}
```

## 5. 只读核对步骤

1. 计算 SHA-256 和文件大小。
2. 确认不是仓库原始包被意外覆盖。
3. 读取 FLS/0SLF 头和目录。
4. 尝试使用现有 key DB 做只读条目清点。
5. 如果 key DB 不匹配，停止并报告，不猜测密钥。
6. 输出条目清单：entry_id、自报名、VM、压缩长度、是否可解码。
7. 与原始基线做差异：新增、删除、替换、目录变化。
8. 对已知注册 / 登录 / 网络 / UI 入口做定点核对。
9. 输出差异报告，不执行任何恢复脚本。

## 6. 探针挂点选择原则

探针挂点必须基于用户修改版实际内容选择，不能直接照搬原始包假设。

候选挂点类型：

- 启动后脚本初始化点；
- 登录界面加载完成点；
- 主循环 / 定时回调点；
- 已存在的开发 / 诊断入口；
- 用户已有修改模块中的安全位置。

选择标准：

1. 不破坏用户已有修改；
2. 不影响正式逻辑；
3. 能在客户端主循环安全执行；
4. 可回退；
5. 可写后校验；
6. 不执行反编译恢复稿。

## 7. 测试包生成原则

**2026-11-03 用户指令（取代此前“仓库外新包”口径）**：直接在仓库内修改 `data/script.fls` 本身，用户自己备份；不再生成仓外修复包，也不再要求用户解压 / 替换文件。

修改流程：

```text
data/script.fls（仓库内唯一真身）
  -> 先在仓库内写可复现的修改工具与测试
  -> 只改必要条目（目录长度字 / 探针钩子）
  -> 原子写回 data/script.fls
  -> 逐条校验：目录结构、全部 zlib 流、未涉及条目逐字节不变
  -> 记录修改前后 SHA-256 与修改条目清单（提交信息 + build_report.json）
```

禁止：

- 放宽 key DB / 基线校验；
- 静默修复未知条目；
- 在没有逐条校验的情况下写回；
- 把修改工具之外的生成物（日志、临时包）提交 Git。

## 8. 回退

每次修改必须记录：

```text
输入包 SHA-256
输出包 SHA-256
修改条目列表
未修改条目校验结果
构建工具版本
构建时间
回退方法：用户自己的备份，或 git 历史里的上一个版本（`git show <commit>:data/script.fls`）
```

用户自行保留原始包备份；仓库内改动可通过 git 回退，不再需要仓外副本。
