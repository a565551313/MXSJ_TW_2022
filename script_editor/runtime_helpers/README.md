# 只编译入口

实际随源码包/wheel/冻结包分发的唯一实现位于
`src/script_editor/data/compile_legacy.py`，避免维护两份入口。
该文件特意保持Python 2.5/2.7语法（没有future annotations），
只读取UTF-8源码、compile和marshal.dump，不import/exec目标代码。
