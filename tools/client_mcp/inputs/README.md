# inputs — 用户修改版 script.fls 隔离输入目录

> 状态：占位目录。当前没有输入包。

本目录用于临时存放用户提供的修改版 `script.fls`，方便在仓库工作区内做只读核对。

## 规则

1. 不要把文件命名为 `data/script.fls`，也不要覆盖仓库原始包。
2. 推荐子目录：

```text
inputs/<timestamp>/script.fls
inputs/<timestamp>/input_manifest.json
```

3. 本目录中的二进制包、日志、报告不提交 Git；`.gitignore` 已忽略除 README / .gitignore 外的内容。
4. 收到文件后先计算 SHA-256，再按 [SCRIPT_FLS_HANDOFF.md](../docs/SCRIPT_FLS_HANDOFF.md) 登记。
5. 如果文件很大或需要长期保存，优先放到仓库外：

```text
../mxsj-client-mcp-out/inputs/<timestamp>/script.fls
```

## Windows 计算 SHA-256 示例

```bat
certutil -hashfile script.fls SHA256
```

## 当前阻塞

等待用户提供已经修改过的 `script.fls`。在收到前，不假设探针挂点或条目编号。
