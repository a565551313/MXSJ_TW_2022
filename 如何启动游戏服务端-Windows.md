# Windows 双击启动说明

1. 在 GitHub 的 [PR #47](https://github.com/a565551313/MXSJ_TW_2022/pull/47) 中切换到 Files changed，找到仓库根目录的 `启动游戏服务端-Windows.bat`；或者先下载该分支的 ZIP 并解压。
2. 在 Windows 电脑上安装 Python 3.11 或更新版本：https://www.python.org/downloads/windows/ 。安装时勾选 **Add Python to PATH**。
3. 确认脚本文件位于仓库根目录，与 `server` 文件夹同级。
4. 双击 `启动游戏服务端-Windows.bat`。第一次启动会自动创建本地虚拟环境；不需要安装第三方服务端依赖。
5. 窗口显示 `development game-loop listening on 127.0.0.1:8765` 时，代表开发服务已开始监听。请保持窗口开启。
6. 停止服务时，在窗口按 Ctrl+C，或关闭窗口。

## 重要限制

- 这是本机开发原型，不是图形化游戏客户端，也不兼容原版客户端协议。
- 服务只监听本机 `127.0.0.1`，不能让其他电脑直接连接。
- 数据库文件保存在 `server/data/game-loop.sqlite3`。
- 如果提示找不到 Python，请先安装 Python 3.11+，并重新打开/双击脚本。
- 若 GitHub 仓库是私有的，需要先登录有访问权限的 GitHub 账号才能下载代码。
