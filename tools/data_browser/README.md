# 旧 SQLite 数据浏览器

状态：**历史复现／旧数据查看**。当前静态数据复核优先 [Catalog/API/Web](../../server/README.md)。
不新增 tkinter 功能；保留旧浏览器不代表新的桌面工具规范允许 tkinter。

| 入口 | 输入／行为 | 边界 |
|---|---|---|
| `app.py` | 读取 `../data-export/game_data.sqlite`；HTTP/CLI 浏览，Web 默认端口 8080 | 启动 Web 会监听；本轮未运行或审计公网安全，不自动对外开放 |
| `desktop_app.py` | 同一 SQLite；tkinter GUI／终端 TUI | 旧交互，不是 PySide6 编辑器，也不是正式配置审核入口 |

旧数据库含装备、场景、对话等历史表；新系统使用 batch_001 的不同复核数据集。
**不能宣称新网页已逐表覆盖旧数据库**，也不能把同名行自动合并或当作规则正确。
旧浏览器读取数据库这一运行依赖仍存在，见 [DEPENDENCIES](../DEPENDENCIES.md)。
本轮没有迁移 SQLite、启动服务、删除浏览器或重写 GUI。
