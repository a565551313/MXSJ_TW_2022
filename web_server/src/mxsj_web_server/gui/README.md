# GUI 边界（未实现）

后续界面仅使用 PySide6，由 app.py 装配 QApplication。窗口／控件放本目录，
只调用 core 的公开接口，不在 Qt 回调中做文件 IO／解析，长任务交给 QThread／QThreadPool。

用户已要求本地 GUI、远程 Web 后台及本地控制后台开关；具体功能仍在讨论，
本轮仅整改工程标准，不实现窗口、远程后台或其鉴权，不安装无用途的 Qt 依赖。
