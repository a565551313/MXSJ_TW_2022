# Windows源码测试包：先读这里

工具：**MXSJScriptManual / 客户端脚本开发手册 0.1.0.dev3**，本次交付编号 `windows-source-test1 / 2026-10-16`。

这是独立只读手册，**不是脚本编辑器，不运行游戏、不编辑/回编译游戏脚本、不改游戏包**。交付源码、启动、自检及Windows EXE构建脚本，不冒充已经构建/验收的Windows EXE。

## 一、解压后怎么用

1. 完整解压ZIP到可写目录，建议先试例如 `D:\工具测试\脚本手册 test1` 这样的中文/空格路径。**不要在压缩软件里直接运行，也不要覆盖游戏或旧工具目录。**
2. 安装官方 **64位Python 3.11或3.12**（最低3.10；支持Windows 10/11）。安装时勾选Add Python to PATH。包不含Python/Qt安装程序，第一次装依赖需要联网。
3. 进入 `MXSJScriptManual-source-0.1.0.dev3/script_manual/`，先双击 **`测试手册.bat`**。
   - 自动创建本目录 `.venv`，装开发/测试依赖；官方pip源失败才尝试清华/阿里镜像。
   - 跑依赖/结构预检、严格来源/full、手册GUI及core测试、N1独立测试、恢复工具合成测试、ruff及Windows静态。
   - **强制GUI测试，缺Qt不能跳过当通过**；失败会停住、保留退出码，不继续构建。
   - 完整日志在同目录 `windows_test_<随机号>_<随机号>.log`，每次新文件，不覆盖上次。
4. 自检后使用同一个环境启动：
   ```bat
   .venv\Scripts\python.exe bootstrap.py
   ```
   也可双击 `启动脚本手册.bat`；它选择系统 `py -3`/`python`，可能需在该解释器另装依赖。优先用上面命令复用自检venv。
5. 不需要把游戏目录、data/script.fls或完整反编译语料放进来。包里已带实际引用的小证据和目录元数据，可独立核对来源。

命令行复跑（工具所在目录）：

```bat
.venv\Scripts\python.exe check_manual.py --require-gui
```

六道闸门中的任一步非零都会整体失败；“自动检查通过”仍不等于下面的目视检查、Windows EXE或游戏验收。

## 二、请实测这些操作

- 窗口能打开、调整大小和关闭，标题/中文/路径没有乱码；启动/加载不一直卡住。
- 初始显示 **5135条目录登记、20篇说明、16篇有限审核通过、1条排除**。剩余四篇战斗稿待非A独审，不应显示全部20通过。
- 搜索 `script/login/mainpage.py`、`刷新公告`、`CreateCmdObject`、`右键使用`；检查路径、中文、函数搜索是否可定位。只有已写说明的模块才有功能词，不把未写模块冒充已解释。
- 切领域、审核状态；打开职责、类/函数、关联/修改、证据/来源四个页签；从hero关联跳到npc。
- 看登录稿是否明确 `A代审`及授权，战斗四篇是否仍待审；没有正文的目录项应明确尚未编写。
- “校验证据”选择**解压后的包根**（含script_manual、tools、server、work的那一层），不是游戏目录，也不是内层script_manual文件夹；应无缺来源/摘要不符/越界。
- 导出离线HTML到**包目录以外且尚不存在的新文件夹**。双击index.html检查搜索、筛选、导航；不要向已有目录或输入目录导出。
- 测试退出、重新打开；有异常时保留最小截图/报错和日志，不要提交真实账号、密码或游戏日志。

本次不启动游戏、不请求公告/注册业务URL、不验证服务端协议。手册中的反编译候选不是可执行源码，**不要运行tools/decompiler/output里的.py**。

## 三、需要EXE时你自己构建

在 `script_manual/` 双击 **`build_exe.bat`**：同目录venv→依赖→检查→强制Qt单测→PyInstaller。

- 默认：`dist\MXSJScriptManual\MXSJScriptManual.exe`，传给另一台机器时要整个目录，不能只拷exe。
- 单文件：先在cmd执行 `set MXSJ_MANUAL_ONEFILE=1` 再运行build_exe.bat，输出 `dist\MXSJScriptManual.exe`。
- 本包提供构建脚本，**我尚未在Windows构建/实测过EXE**。源码测试通过后再构建，以便区分Qt/环境问题与打包问题。
- 不需要安装Git，不需要原仓库、不需要编译器/game DLL。附带的共享解析器core源码只是供N1合成测试导入，不是另一份脚本编辑器交付。

## 四、包里有什么 / 没有什么

- `script_manual/`：完整本工具源码、5135目录、20注释/16有效review、来源摘录、schema、夹具、测试、自检和构建脚本。
- `tools/`、`script_editor/src/.../core/`：统一闸门需要的静态检查/合成测试/共享解析器源码；不会自动恢复或执行游戏模块。
- `server/docs/catalog/`、`work/.../protocol_table/`及`tools/decompiler/output/...`：**仅27个实际来源依赖的并集**，包含只读目录/协议元数据与少量被引用的候选文本，不是79MB全量语料。保留原相对路径和SHA方便校验。
- `docs/ARENA_SANDBOX_RECOVERY.md`、`AGENTS.md`和检查点模板：Arena环境变化的预防、判别、恢复规则；不是会自动改Git的恢复脚本。
- `PACKAGE_MANIFEST.json`：本包源码提交和逐文件大小/SHA256；`README_FIRST.md`为本说明的副本。
- **不含游戏FLS/EXE/DLL、原生编译器二进制、凭据、venv、node_modules或游戏安装包，不改Drive分享权限。**

## 五、给我回报什么

告诉我：Windows版本、Python版本、自检是否成功、哪一步失败；附本次 `windows_test_*.log` 和必要截图即可。日志可能含本机用户名/路径，发出前先脱敏，勿附真实账号/密码。我不会自动上传任何诊断信息。

当前Linux侧通过不代表Windows已通过；以你的这次结果为准。四战斗稿独立末审是另一个内容门槛，不能由Windows界面打开代替。
