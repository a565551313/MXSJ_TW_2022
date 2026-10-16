# 脚本手册Windows源码测试包test1：实际交付回执

日期：2026-10-16。用户授权上传独立手册供Windows实测，并要求给后续Arena Agent写沙盒恢复指南。

## 已上传并读回核对

- 文件：[MXSJScriptManual_0.1.0.dev3_windows_source_test1_20261016.zip](https://drive.google.com/file/d/14s0nmb61CfMDFMerb23JpJkQioZHc6J6/view)
- 目录：[script_manual](https://drive.google.com/drive/folders/1mxu6gDe2qLywlGR17NgtSuCShgQZom85)，与既有script_editor同级；新文件夹继承原父目录设置，A未调用任何权限变更API。
- file ID：`14s0nmb61CfMDFMerb23JpJkQioZHc6J6`；父目录：`1mxu6gDe2qLywlGR17NgtSuCShgQZom85`。
- 大小：**3,140,276字节**。
- MD5：`94ab1107d8c4eacaee96111b5ab35d3a`。
- 本地SHA256：`261237f7212628b4574523466cd9805b329dfb2a57488d0226c97c0a5b8db0bc`。
- 源码固定提交：`84e0b9c53761e407d8089a92e17637804129aaab`，打包前已提交推送且干净；上传回执是后续提交，不为追新HEAD反复改包。
- 上传成功后单独get读回：文件名、父目录、size、MD5、mime=application/zip、trashed=false均符合。没有下载后重算远端SHA；本地SHA与远端MD5/大小校验明确区分。

## 内容与独立性

ZIP有264项：263份manifest登记载荷及manifest自身，逐项CRC/大小/SHA复核；包含本工具源码/内容/schema/测试、启动/测试/构建脚本、27个实际source的依赖并集、N1合成测试所需共享解析器core与BDF小收据、静态检查/恢复合成测试源码和沙盒恢复文档。没有把整个79MB语料/游戏目录混进去；不含FLS/EXE/DLL/PYC/PYO/WHL、原生编译器二进制、凭据、venv或node_modules，不是游戏包或另一份编辑器交付。

实际将上传的同一ZIP解压到仓库外`解压验证 中文 space`。验证解压根没有`.git`、没有`data/`原包目录，清除继承的PYTHONPATH/PYTHONHOME后，用该包自己的check_manual.py执行六闸门：

- strict evidence/full：5135登记/20说明/16有限通过/1排除，无stale；4battle仍待非A末审，不自批。
- 标准90项：79通过、11缺PySide6跳过、0失败；新增打包回归4项覆盖依赖/manifest/可重现ZIP、缺/错证据、禁止覆盖/仓库内输出、越界/符号链接。
- N1独立32/32通过，无BDF缺文件跳过；恢复合成27/27通过。
- ruff含spec通过；Windows静态walk172路径/34源全0（不是Windows运行）。
- 解压包再独立strict HTML build通过，覆盖数同上；不是只在原checkout上跑绿。
- Windows脚本ASCII/纯CRLF、控制字符检查通过，已有batch回归覆盖；没有执行cmd、Qt或PyInstaller冒充Windows实测。

## 用户操作

1. 完整解压到可写新目录；读顶层README_FIRST.md或script_manual/WINDOWS_TEST.md。
2. 安装64位Python3.11/3.12（最低3.10），进入script_manual双击`测试手册.bat`：本地venv、依赖镜像回退、预检/六闸门**强制GUI**、新日志、不覆盖旧日志、失败停住。
3. 用`.venv\Scripts\python.exe bootstrap.py`复用测试环境启动；按说明测中文/路径/函数搜索、四页签、筛选、跳转和导出。双击原启动bat会选择系统解释器，可能另装依赖。
4. 如需EXE自己双击build_exe.bat，支持onedir/onefile；本交付**不是已构建EXE**。
5. 回报Windows/Python版本、本次windows_test日志与必要截图，先脱敏个人路径，不附账号密码或游戏日志；不会自动上传诊断。

Linux通过不是Windows/Qt/EXE实测。目视/实机仍待用户；Windows使用正常也不代替四battle非A独立内容审核。不合master、不改游戏/编辑器/启动器、未改变Drive权限。

## 沙盒重置的长期入口

- `AGENTS.md`开工60秒：醒目必读入口。
- `docs/ARENA_SANDBOX_RECOVERY.md`：项目中已观测的临时环境失效、HEAD/index旧但新版文件仍在；只陈述观测，不诊断Arena内部根因或承诺本地持久。
- `docs/templates/AGENT_CHECKPOINT.md`：阶段推送核远端OID、输入/工具/环境指纹、真实测试和可重建配方。

恢复须先保工作差异和原创文件、核实际远端，区分真实缺失与元数据错位；禁止reset hard/clean、删.git、覆盖根目录或重复补交已有成果。高级update-ref/read-tree仅在全部路径核准、差异保护后手工；恢复后重验而非借用旧日志。这些文档已在Git远端和交付包内，不只留在聊天/临时路径。
