# 只编译入口

实际随源码包/wheel/冻结包分发的唯一实现位于
`src/script_editor/data/compile_legacy.py`，避免维护两份入口。
该文件特意保持Python 2.5/2.7语法（没有future annotations），
只读取UTF-8源码、compile和marshal.dump，不import/exec目标代码。

M2新增同目录`audit_legacy.py`：在精确版本子进程中完整marshal读取已编译/已回读的自写pyc，
核对根CodeType与EOF，不import或exec模块。两个助手都随独立源码/wheel/冻结配置提供。
