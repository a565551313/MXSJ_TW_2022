# 用户修改版 script.fls 交付与核对流程

> 状态：流程草案。日期：2026-11-02。  
> 背景：用户说明其客户端 `script.fls` 已做过很多修改，后续会提供修改版。仓库原始 `data/script.fls` 不能直接覆盖。

## 1. 当前锁定基线

```text
data/script.fls
SHA-256: 8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72

tools/decompiler/script_fls_keys.json
SHA-256: 43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb
```

在用户提供修改版之前，所有文档和骨架都基于原始锁定基线描述，不假设修改版内容。

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

未来构建探针测试包时：

```text
用户修改版 script.fls
  -> 只读输入
  -> 新增 / 替换最小白名单条目
  -> 生成新 script.fls
  -> 写到仓库外 builds/<timestamp>/
  -> 逐条校验未涉及条目不变
  -> 输出 build_report.json
```

禁止：

- 覆盖用户输入包；
- 覆盖仓库原始包；
- 放宽 key DB / 基线校验；
- 静默修复未知条目；
- 把生成包提交 Git。

## 8. 回退

每次生成测试包必须记录：

```text
输入包 SHA-256
输出包 SHA-256
修改条目列表
未修改条目校验结果
构建工具版本
构建时间
回退方法：恢复用户原始修改版或原始锁定基线
```

Windows 测试副本应保留用户原始修改版备份，避免探针测试包影响用户日常客户端。
