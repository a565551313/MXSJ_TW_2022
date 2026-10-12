# MXSJ 资源编辑器

梦想世界（MXSJ / Duoyi）客户端 `data/*.fls` 资源包的浏览与编辑工具，
PySide6 GUI，核心解析与界面分离（设计见 [DESIGN.md](DESIGN.md)）。

## 功能

* 打开全部 7 个资源包：0SLF 容器（script/skill/skill2/passive/effect/
  magicres5.fls）与 data.fls（名目录式）。
* 条目浏览：类型过滤、名称/序号搜索、缩略图；按内容自动分类
  （精灵 / PNG / JSON / 文本 / 脚本数据 / 二进制）。
* **精灵动画预览**：I0/T0/I1 逐帧与画布锚点合成两种模式，
  播放/暂停、帧滑杆、帧率调节、锚点十字定位，调色板点选查色。
* 导出：单条目（精灵逐帧 PNG、原始文件）与整包精灵批量导出。
* 编辑：PNG 替换精灵帧（编码前给往返误差报告）、原始数据替换、
  条目新增/删除、单条目撤销/还原；保存时全量校验、原文件 `.bak`
  备份、原子替换，未改动条目逐字节原样保留。

## 运行

```bash
pip install PySide6 Pillow
PYTHONPATH=src python -m resource_editor ../data/skill.fls
```

或安装后使用入口脚本：`pip install -e .` 后执行 `mxsj-resource-editor`。

## 测试

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

合成夹具覆盖容器读写与编码器；真实包测试在 `data/` 存在时自动启用
（全量 807 精灵解码 + 样本像素级往返）。

## 约束

* script.fls 条目是 zlib+5 段 XOR 的 Python 2.7 字节码，只浏览不解码。
* effect.fls 的 41 个未破译二进制条目只提供 Hex 查看，
  背景见 `../tools/data-parser/I0_SPRITE_FORMAT.md`。
* 与原版客户端二进制的最终兼容性需 Windows 原生环境验证。
