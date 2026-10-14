# 运行时尚未随包提供

目前`manifest.json`是**空清单**，内置编译器不可用。
不得拿游戏DLL、PATH中的Python或Python3代替标准编译器。
Linux开发时可以在GUI显式选经过版本/魔数校验的2.5.6/2.7.13可执行文件。

后续发行布局：

- `py25/win-x86/python.exe`及所需的标准库/DLL
- `py27/win-x86/python.exe`及所需的标准库/DLL
- `manifest.json`的compilers每项记录vm、platform（win32）、executable（相对此目录）、
  sha256及来源/许可证/完整文件清单。运行前先校验exe哈希，再检查版本、魔数、32bit。

当前只实现exe哈希，不具备完整DLL/标准库供应链审计；正式发行前还必须补齐整套文件校验。
构建脚本故意只复制空清单，不能据此声称完整随包编译器已交付。
