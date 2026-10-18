# PySide6 本地管理器

MainWindow 通过 Worker/QThreadPool 调用共享 Manager，耗时 I/O、密码哈希、服务启停不在 UI 线程运行。
菜单、工具栏、托盘复用 QAction；关闭确认默认取消，最小化时托盘不可用则正常留在任务栏。
本地保存带版本校验，不无提示覆盖远程修改；公开／管理监听相互独立，后台开关仅本地可控。

当前 UI 代码已实现，Windows 实机和系统托盘仍待验。沙盒缺 libGL.so.1，Qt offscreen 测试明确跳过，不能算通过。
