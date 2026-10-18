# web_server — 独立客户端 Web 分发服务

Python 3.10+ 独立子项目，可将本目录复制到另一台服务器运行。无需游戏服务端源码、数据库或 TCP 网关。
版本：**0.2.1 工程规范整改版**。现已实现显式资源白名单的只读 WSGI 应用；并非已经通过原生启动器验收的更新平台。

## 职责与边界

目标：公告、区服发现、版本／文件清单及后续补丁分发。与游戏 TCP、GM 发布端和只读 review_api 分离。

| 内容 | 当前状态 |
|---|---|
| GET／HEAD、ETag／304、可配置缓存 | 已实现；按文件原始字节响应，不转编码 |
| `/healthz` | 仅表示 Web 应用存活，不代表区服在线或更新发布完整 |
| 公告／列表／清单托管 | 已支持 Big5／CRLF 公告和五字段基础区服列表生成；不生成更新清单 |
| 客户端 `server.txt`、`httpupdate.txt`、`filemd5.txt` 格式 | 待核验；不等同于已有本地 server.ini 格式 |
| 大补丁、Range／断点续传、签名发布／回滚 | 未实现；应独立交给下载源／CDN，后续另验收 |
| 发布后台、鉴权、上传、数据库 | 未实现，也不开放匿名写接口 |
| Windows 原生启动器／客户端验收 | 未执行 |

**示例发布 `/news.txt`、`/service.txt`、`/server.txt` 和 `/example.txt`，均为假测试内容，不是官方公告或已上线区服。不会返回虚假的“已是最新版本”，也不会读取或改写根目录客户端配置。**
未知路径（包括未配置的原生更新 URL）返回 404，不回退到首页或假成功。

## 运行与自检

运行所需只有 Python 标准库，无第三方依赖。在仓库根目录：

```bash
python web_server/bootstrap.py --check-only
python web_server/run.py --version
python web_server/run.py --init-example web_server/var/profile-001
python web_server/run.py --config web_server/var/profile-001/config.json
python -m unittest discover -s web_server/tests -v
```

本地开发地址：`http://127.0.0.1:8080/news.txt`；健康检查 `/healthz`。
Windows 同样使用上述 Python 命令（可用 `py -3` 替换 `python`）。没有本轮已构建或验收的 EXE。
预览容器中需显式 `--host 0.0.0.0`；对外部署不使用这个开发 runner。

示例资源位于 `src/mxsj_web_server/data/`；用 `--init-example` 复制到独立的新目录后编辑，
不要修改包内样本。将实际发布内容放入专用目录（例如忽略入库的 `var/releases/v001`），
配置 `content_root` 及 `resources`。content_root 相对配置文件定位，不依赖 shell 当前目录。
资源条目示意（文件须事先准备好）：

```json
{
  "url": "/news.txt",
  "file": "news.txt",
  "content_type": "text/plain",
  "max_age": 0
}
```

不隐式附加 charset、不转换字节；原始 Big5 等编码须由发布者根据客户端证据确认。
每个文件最大 8 MiB，总快照最大 32 MiB，最多 128 项；超过限制必须转独立下载源，不为了大包无限扩大内存。
路径不自动映射磁盘目录，禁止目录浏览、越界路径、符号链接和硬链接资源。文件名 URL 为有限 ASCII 格式。
HTML 默认设置限制性 CSP，无脚本／外部资源；旧内嵌浏览器能否支持须实测，不把它当新管理前端。

## 发布与部署

- 开发 runner 是标准库单进程同步 WSGI 服务器，**不是生产 HTTP 服务器**；没有公网防护、容量或 TLS 验收。
- 生产使用经过部署验证的 WSGI server＋反向代理。应用工厂为 `mxsj_web_server.core.publication.create_app(config_path)`；源码部署设置 `PYTHONPATH=src`，也可安装本项目 wheel。
  WSGI server、TLS／证书、超时、请求／连接限制和依赖锁定由后续部署方案选定，当前不声称已具备生产安装包。
- Python 应用在启动时读取完整资源快照，请求期间不读取发布目录。更新文件后必须重新加载应用／重启。
- 发布到新的、不可变的 release 目录，验证后再切换配置并重新加载；不要在线覆盖正在加载的文件。
  目录须由可信发布者独占管理；不抵御恶意并发文件替换。
- 多 worker／多副本发布期间仍可能新旧并存；本实现不保证集群原子发布。先上传补丁，再发布清单，保留旧版本下载路径。
- 可独立放到任意满足客户端网络兼容性的主机；公告／列表短缓存，带版本号补丁可由独立 CDN 长缓存。
- 旧客户端的 TLS、重定向、压缩、Range 和缓存兼容性需要逐项验证，不能默认现代浏览器可用就等于启动器可用。
- ETag 是传输缓存标识，不是数字签名；原生 MD5 清单也不是来源可信证明。更新源安全、签名／信任链另行设计。
- 发布权限必须与公开读取分离；不让此服务直连游戏数据库，也不在此服务发放游戏票据。

## 日志

开发 runner 的请求日志仅输出固定事件和状态码，不记录 URL、query、请求头或文件内容；启动失败仅固定错误提示。
`bootstrap.py` 的启动异常按项目约定写入同目录 `启动日志.txt`，包含 UTC 时间、Python 版本及完整 traceback；仅供本地排错，分享前须审查脱敏。配置／网络请求不得放入真实凭据。
当前没有访问日志持久化轮替、发布审计或生产异常诊断系统；不依赖另一个项目的 logger。
生产 WSGI／代理访问日志也需单独配置脱敏、保留和权限，不能误以为应用不记录就代表代理不会记录。

## 下一步

1. 固定原生启动器／客户端实际请求及响应格式、编码、错误处理证据。
2. 使用独立假数据验证公告、刷新区服列表，不访问历史官方地址。
3. 定义版本清单、不可变下载路径、校验与发布／回滚流程。
4. 选定生产部署方式，补独立结构化日志、资源限制与网络集成测试。
5. Windows 原生启动器验证后，才更新兼容性结论；不提前修改原客户端 update.ini/server.ini。

## 生成公告与基础区服列表

编辑 UTF-8 的 profile 中 `content.json`，填写 news、service 和 groups。reserve/type 是不透明字段，示例采用已有样本的 `3`／`&`；不推断其意义。
生成到**不存在的新目录**（再次执行须换 release 名称，不自动覆盖）：

```bash
python web_server/content.py --source web_server/var/profile-001/content.json --output web_server/var/releases/demo-001
python web_server/run.py --config web_server/var/releases/demo-001/config.json --check-only
python web_server/run.py --config web_server/var/releases/demo-001/config.json
```

输出 news.txt、service.txt、server.txt 和仅发布这三份文件的 config.json；文件为严格 Big5、CRLF，无 BOM。
不可编码文字、字段注入、重复分组、无效 IP／端口会拒绝；完整发布前验证，不静默替换字符。
不支持可选 serverid 或列表附加段，基础列表并未经过客户端界面验收；当前不支持更新包生成。
具体字段证据、未知项及后续核验入口见 [原生格式记录](LEGACY_FORMATS.md)。

## 标准目录与启动入口

```text
web_server/
├─ pyproject.toml                  # 元数据、版本、console-scripts、ruff
├─ requirements.txt               # 当前运行核心仅标准库
├─ requirements-dev.txt           # ruff／PyInstaller／build
├─ bootstrap.py                   # 自检、按需安装依赖、启动诊断
├─ 启动Web服务.bat                 # CRLF／ASCII，双击启动当前 CLI
├─ build_exe.bat                   # 测试通过才构建
├─ web_server.spec                # onedir／onefile；当前 console=True
├─ run.py                         # 无 pip 安装的轻量入口
├─ content.py                     # 兼容旧生成命令的薄入口
├─ src/mxsj_web_server/
│  ├─ __init__.py                 # __version__
│  ├─ __main__.py                 # python -m mxsj_web_server
│  ├─ app.py                      # 应用装配；当前 CLI，非 Qt 窗口
│  ├─ core/                       # HTTP／生成／路径逻辑，不依赖 Qt
│  ├─ gui/                        # 待实现的 PySide6 边界，现仅说明
│  └─ data/                       # 只读示例 JSON 与 Big5／CRLF 文件
└─ tests/                         # unittest，无 Qt 依赖
```

源码运行不要求 pip 安装本包：双击 BAT 或 `python bootstrap.py` 即可。
无参数启动会在 `%APPDATA%\MXSJWebServer\` 初始化假数据配置并启动本地开发服务；
未设置 APPDATA 时使用用户主目录下的 MXSJWebServer，不写安装目录。
配置已存在则读取，不覆盖；目录存在但初始化不完整时明确报错，操作员检查后选择新的目录。
`--check-only` 无参数时只校验包内示例，不创建用户目录、不启动监听。
显式 `--config` 使用指定路径；资源路径相对于该配置，不相对于当前工作目录。
冻结只读资源来自 `_MEIPASS/mxsj_web_server/data`，和可写用户配置分离。

`bootstrap.py` 支持透传参数，检查 Python >=3.10；当前无需安装第三方运行依赖。
以后确需依赖时，按导入名／pip 名表检查，官方源→清华→阿里镜像尝试并复检；
自检失败返回 2，成功返回 0；BAT 失败保留窗口，不闪退。

**GUI 和远程后台仍待需求讨论，并未实现。** 因此当前注册 console-scripts，而不是虚假的 gui-scripts；
EXE 保留控制台，双击不会凭空打开管理窗口。后续真实 GUI 必须用 PySide6，补 QApplication／gui-scripts，
任务线程、布局／DPI 和退出清理验收，然后改 GUI EXE 为 console=False。

## 测试与 Windows 构建

```bash
python -m unittest discover -s web_server/tests -v
python web_server/bootstrap.py --check-only
ruff check web_server
python tools/devkit/check_windows_compat.py web_server --strict
```

Windows 双击 `build_exe.bat`：创建 venv → 开发依赖 → 自检 → ruff → unittest → PyInstaller。
默认产物 `dist\MXSJWebServer\MXSJWebServer.exe`；设置 `WEB_SERVER_ONEFILE=1` 后运行同一 BAT 可构建单文件版本。
两个版本都以 run.py 为入口，运行时不会 pip 安装依赖；使用示例：

```text
MXSJWebServer.exe --version
MXSJWebServer.exe --check-only
MXSJWebServer.exe --config C:\private\profile\config.json
MXSJWebServer.exe content --source C:\private\content.json --output C:\private\release-002
```

版本号以 pyproject.toml、__version__、README 和 `--version` 保持一致。
Linux 只能干跑 spec、检查资源收集与 Linux 产物入口；**不能交付或宣称 Windows EXE 已通过**。
Windows 待验：中文／空格路径、首次双击自检、关闭后无残留进程、两种 EXE、用户目录写入及客户端读取。
当前整改单元测试不包含 GUI；未执行不算通过。独立管理后台鉴权、生产 HTTP 部署仍未实现。

### 本轮检查记录（0.2.1）

- Linux／Python 3.11.2：35 项 unittest、ruff、自检、Windows 静态检查通过；wheel 独立安装入口验证通过。
- onedir／onefile spec 均尝试干跑，但沙盒缺少 `libpython3.11.so.1.0`，构建失败，无 EXE 产物。
- spec 结构测试使用替身验证装配参数，不替代真实构建；没有使用桩库冒充可运行产物。
- Windows／Python 3.10 实机、GUI 均未验。具体记录见仓库 STATUS 及证据文件。
