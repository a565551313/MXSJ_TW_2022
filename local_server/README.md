# 独立本地服务端 0.2.0

**目标：与正式服业务行为一致，唯一允许的功能性差异是使用 SQLite 存储；工程、运行和数据相互独立。**

本目录现在自带源码、配置、测试和构建入口，不再导入正式服包或读取兄弟项目源码。可以单独复制本目录运行；本次没有修改已恢复的正式服目录。

## 当前能做什么

- 账号：操作员显式建号、scrypt 随机盐密码校验；不自动注册、不免认证。
- 会话：票据摘要、过期、撤销、同区服接管与旧会话失效。
- 角色基础：创建／查询、名称与数量及外观／门派组合校验、幂等回执。
- SQLite：显式初始化、版本与迁移摘要检查、外键、事务与回滚；损坏库不自动重建。
- 日志：结构化事件、操作追踪、轮替、脱敏和失败诊断。
- 独立 CLI、自检、源码与安装包入口、项目内测试及 Windows 构建配置。

**尚无游戏 TCP 监听、原生认证协议接入、选角进图、完整玩法或 GUI。** 其余模块目前只有契约／目录边界，不是已实现功能；不能称为已达到完整正式服等价验收。GUI 目录已预留，后续使用 PySide6。

## 目录（均在本项目内）

```text
local_server/
  pyproject.toml                    项目元数据、安装入口、lint 配置
  README.md
  bootstrap.py                     自检与源码启动
  run.py                           薄入口，仅加入本目录 src
  config.example.json              SQLite 与日志配置示例
  requirements.txt
  requirements-dev.txt
  启动本地测试服.bat
  build_exe.bat
  local_server.spec                 只收集本项目源码；当前为 CLI EXE
  src/mxsj_local_server/
    __init__.py                    版本
    __main__.py                    python -m 入口
    app.py                         应用入口
    cli.py                         操作员控制台
    core/
      configuration/               配置读取与校验
      bootstrap/                   本项目内的服务组装
      contracts/                   内部数据契约
      modules/
        account/                   账号规则与服务
        character/                 角色基础规则与服务
        activity/ administration/ appearance/ battle/
        children/ crafting/ economy/ guild/ housing/
        inventory/ mail/ npc/ party/ pet/ quest/
        skill/ social/ trade/ world/  契约与边界，玩法尚未实现
      runtime/                     会话与票据
      persistence/
        ports.py                   存储接口
        sqlite/                    SQLite 仓储、表结构与事务
      observability/               日志与操作追踪
      protocol/legacy/             原生协议边界，待实现
      protocol/modern/             现代协议边界，待实现
      transport/                   网络传输边界，待实现
    gui/
      pages/                       页面预留
      dialogs/                     对话框预留
  tests/
    local_runtime/                 SQLite／账号／会话／角色回归
    observability/                 日志／追踪回归
    test_project.py                独立目录与导入边界测试
  docs/
    ARCHITECTURE.md               独立边界与代码来源
  var/                             按配置显式创建，已忽略
    local.sqlite3
    logs/
```

## 运行（在本目录下）

Python **3.11+**，SQLite **3.24+**；当前核心只需标准库。

1. 复制 `config.example.json` 为 `config.json`。
2. 自检、显式初始化，再建测试账号：

```bash
python bootstrap.py --check-only
python run.py --config config.json init-db
python run.py --config config.json check
python run.py --config config.json provision --account player_one
python run.py --config config.json console
```

建号交互输入并确认密码，使用假测试密码；不接受明文密码命令行参数。控制台支持 `login`、`list`、`create`、`logout`、`quit`，这是操作员基础验证入口，不是玩家网络接口。

数据库和日志的相对路径按**配置文件所在目录**解析。自检不初始化数据库；只操作明确配置的本地路径，不启动正式服或修改客户端。请将配置和数据保存在用户私有目录，勿指向正式服数据或共享网络盘。

安装包入口（也只安装本项目）：

```bash
python -m pip install .
mxsj-local-server --version
python -m mxsj_local_server --config config.json check
```

## 检查与构建

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -t . -v
ruff check .
```

Windows 双击入口仍是操作员 CLI，首次使用需先按上述步骤配置和初始化。`build_exe.bat` 创建虚拟环境、检查本项目测试并调用 PyInstaller；不引用兄弟项目。**Windows BAT／EXE 尚未实机验收，不宣称已产出可交付 EXE。**

本轮 Linux：68 项测试通过，包括单独复制本目录至含中文和空格的临时目录，在隔离 Python 进程中自检、初始化、重开数据库与写入日志；ruff 与 Windows 静态检查通过。测试证明基础独立性与既有功能回归，不证明完整玩法等价、原生客户端兼容或 Windows GUI 可用。

## 数据和日志限制

不自动迁移旧 Mock 数据，不读取客户端资源，不伪造未实现功能成功。日志脱敏及轮替不等于防篡改审计；日志失败不会把已经提交的业务伪报为失败。默认数据／日志目录不入 Git。

独立代码来源和后续边界见 [架构说明](docs/ARCHITECTURE.md)。
