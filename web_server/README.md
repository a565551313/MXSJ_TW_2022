# web_server — Web 服务管理器 0.3.0

独立 Python 3.10+ 项目，不依赖游戏服务端。已写入 PySide6 本地 GUI、浏览器管理后台与共享管理核心。
**当前是候选实现，不是已经完成 Windows／原生客户端／公网生产验收的发行版。**
原生文本格式边界见 [LEGACY_FORMATS](LEGACY_FORMATS.md)，部署与安全约束见 [管理设计](docs/MANAGEMENT.md)。

## 本地 GUI

Windows 双击 `启动Web服务.bat`，或：

```bash
python web_server/bootstrap.py
# 明确选择管理数据目录：
python web_server/run.py --gui --state-dir C:/private/MXSJWebServer
```

bootstrap 按项目标准检查／安装 PySide6，CLI/headless 核心不导入 Qt。
默认管理数据在 `%APPDATA%/MXSJWebServer/manager`；无 APPDATA 时用用户主目录下 MXSJWebServer/manager。
无参数启动打开 GUI，**两项监听默认均停止，且首次没有管理员密码、没有已发布内容**。
所有读写管理数据与 GUI 资源分开，不写安装包；同一管理目录只允许一个管理器进程。

页面：总览、新闻公告、客服公告、区服列表、发布管理、服务设置、日志／审计。
菜单：文件、编辑、内容、发布、服务、视图、帮助。
工具栏严格按以下顺序：

```text
公开服务：启动／暂停（继续）／重启／停止
→ 校验／预览
→ Web 后台：启动／暂停（继续）／重启／停止
→ 帮助／设置
```

- 两组服务独立监听、独立控制；公开服务默认 127.0.0.1:8080，后台 127.0.0.1:8081。
- 最小化进入托盘，双击恢复；托盘不可用则留在任务栏。托盘菜单复用同一 QAction。
- 关闭窗口／托盘退出均确认：隐藏到托盘、停止服务并退出、取消（默认）。没有自动开机启动或 Windows Service 安装。
- 桌面与浏览器共用 draft/settings revision，冲突必须重新加载合并，不静默覆盖。
- 先保存草稿→生成版本→查看差异→发布；可切换到旧版本回退。版本保存于独立 SQLite 管理库，最多 200 份。
- 校验／预览针对当前内容；预览为文本，不冒充游戏原生显示。更新包／未知清单明确未实现。
- 监听地址、端口、对外域名设置保存后需重启对应服务；IP 名单和限流即时生效。
- 编辑菜单作用于当前支持对应操作的文本控件；表格尚无全局撤销栈。未实现自定义布局持久化／最近配置列表。

## 浏览器后台

1. 在本地“服务 → 设置／重置管理员密码”初始化 12–256 字符密码。
2. 本地启动后台；浏览器打开设置中的管理对外地址，使用密码登录（当前单一 admin 身份）。
3. 登录后可编辑公告与区服、保存草稿、生成／预览／切换版本，查看导出日志，修改访问规则，控制公开服务。

后台监听开关、管理员密码重置及后台监听 IP／端口／域名只允许本地修改。
后台暂停时仍可登录查看、预览及退出，不允许保存、发布或控制公开服务；本地 GUI 仍可操作。
后台停止／重启会清除会话，但不会停止公开服务。单纯刷新浏览器不会自动覆盖未保存编辑。
浏览器设置页当前为经过严格服务端校验的 JSON 编辑器；本地设置页为表单／规则表格。

## 无界面运行

先通过本地 GUI 配置数据；远程 Linux 可用交互终端初始化管理员密码（不接受命令行明文密码）：

```bash
python web_server/run.py --state-dir /private/web-profile --set-admin-password
python web_server/run.py --headless --state-dir /private/web-profile
# 明确要求本次启动后台，默认不开：
python web_server/run.py --headless --state-dir /private/web-profile --enable-admin
```

管理配置持久化于 management.sqlite3，不与游戏数据库共用。无界面入口 Ctrl+C 会停止监听并清理。
GUI 与 headless 不能同时使用同一目录；不要额外启动另一份无访问控制的旧开发 runner 来冒充受管服务。

## 安全、黑白名单与日志

- 两项服务分别配置 allow／black／white。白名单模式仅允许白名单，黑名单拒绝优先；空白名单拒绝全部网络来源，本地 GUI 不受限。
- 支持 IPv4／IPv6 CIDR、备注、到期 Unix 秒（0 永久）；过期规则不参与匹配。
- 仅当真实 socket 来源在 trusted_proxies 内才解析 X-Forwarded-For，从右向左剥除可信代理；不信任任意客户端自报来源。
- 非本机后台要求 HTTPS 对外地址，TLS 在可信反向代理终止；应用本身没有 TLS 证书管理。HTTPS 后台只接受已配置可信代理的 socket 来源；还须用防火墙限制后端端口直连，不能仅填写 HTTPS 域名就宣称已加密。
- scrypt 随机盐存储管理员密码；会话随机、仅内存、30 分钟过期，最多 32 个；退出／停后台／重置密码失效。
- POST 要求精确 Origin、JSON 与会话 CSRF token；管理 Host 白名单、HttpOnly/SameSite=Strict Cookie，HTTPS 对外地址时加 Secure。无 CORS 放行，无任意 SQL／shell／脚本入口。
- 登录每 IP 每分钟 5 次、全局 30 次；普通请求限流可配置。每项监听最多 16 个并发连接，请求体最多 1 MiB、路径 2048 字符、socket 空闲超时 3 秒。
- 日志为受限字段 JSONL，5 MiB、5 份备份；不记录密码、Cookie、票据、CSRF、请求正文、query 或原始异常文本。陌生路径只记占位符。
- 诊断写失败不替换已提交业务结果，stderr 固定告警，GUI 状态显示累计故障；文件日志不是防篡改审计。
- 内容／设置／发布指针与审计同 SQLite 事务；诊断、登录及监听生命周期日志不具备事务审计保证。审计当前不自动清理，需离线备份维护。

## 原生格式与旧 CLI

已支持的正文：`/news.txt`、`/service.txt`、`/server.txt`（严格 Big5、CRLF、无 BOM）。
未配置的 `/httpupdate.txt`、`/filemd5.txt`、`/servernotice.txt` 等返回 404；未发布已知正文时返回 503。
`/healthz` 仅表示 Web 服务可响应，不代表游戏区服在线。
未知原生清单／补丁／列表附加段不猜测，完整格式依据仍见 LEGACY_FORMATS。

旧只读 CLI 保留用于独立文本托管测试，**它不具备管理器的 ACL／会话／生命周期功能**：

```bash
python web_server/run.py --init-example web_server/var/profile-001
python web_server/content.py --source web_server/var/profile-001/content.json --output web_server/var/releases/demo-001
python web_server/run.py --config web_server/var/releases/demo-001/config.json --check-only
python web_server/run.py --config web_server/var/releases/demo-001/config.json
```

生成只写新目录，不覆盖客户端或旧发布；不会访问官方地址或自动修改客户端 update.ini/server.ini。

## 工程结构与验证

```text
src/mxsj_web_server/
├─ app.py                    # GUI／headless／兼容 CLI 装配
├─ core/
│  ├─ content.py             # 原生文本生成
│  ├─ manager.py             # 共享用例协调
│  ├─ configuration/         # 设置和 SQLite 管理状态
│  ├─ publishing/            # 版本渲染与差异
│  ├─ runtime/               # 有界 HTTP 监听与停止
│  ├─ security/              # 密码／会话／ACL／限流
│  └─ observability/         # 脱敏轮替日志
├─ gui/                      # PySide6 菜单／工具栏／托盘／页面／Worker
├─ web/admin/                # API 和静态浏览器后台
├─ web/public/               # 玩家只读资源路由
├─ web/gateway.py            # 公开／管理边界
└─ data/                     # 只读假数据示例
```

```bash
pip install -r web_server/requirements-dev.txt
python web_server/bootstrap.py --check-only                 # 包含 Qt 原生库导入检查
python web_server/bootstrap.py --check-only --core-only     # 仅核心检查，不等于 GUI 可用
python -m unittest discover -s web_server/tests -v
ruff check web_server
python tools/devkit/check_windows_compat.py web_server --strict
```

Windows 双击 build_exe.bat：自检→ruff→测试→PyInstaller；默认 onedir，`WEB_SERVER_ONEFILE=1` 选择单文件。
GUI EXE console=False，不会运行时 pip 安装；冻结入口数据／网页资源随 spec 打包。
**当前沙盒缺 libGL.so.1，Qt offscreen 测试跳过；缺 libpython3.11.so.1.0，EXE 干跑不能完成。**
Windows 窗口、托盘、DPI、退出行为、BAT／EXE和真实浏览器视觉交互仍待实测，不以 HTTP 测试替代。
