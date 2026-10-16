# Windows 一键验证

1. 下载并解压本开发分支 ZIP。
2. 确保安装了 Python 3.11 或更新版本。
3. 在解压后的项目根目录双击 **一键验证游戏闭环-Windows.bat**。
4. 等待脚本自动启动本地开发服务器、测试 TCP 实际流程，并运行全部标准库自动化测试。
5. 看到 `SUCCESS: registration -> realm -> login -> character -> map loop verified.` 和 `RESULT: SUCCESS` 表示本次闭环与自动化测试均通过。
6. 如果显示 `FAILED`，保留窗口，将报错文字或截图发给开发者。窗口最后按任意键关闭。

无需 pip 安装第三方包。脚本会创建独立验证数据库 `server/data/verify-game-loop.sqlite3`，不覆盖常规开发数据库。

注意：验证对象是本分支的本地 JSON-lines 开发协议，不是原版客户端协议；成功不代表原版客户端已经兼容。服务仅绑定本机回环地址，不要暴露到公网。
