"""资源编辑器统一异常体系。

core 层只抛本模块的异常，GUI 层据此向用户展示中文错误信息。
"""


class ResourceEditorError(Exception):
    """所有资源编辑器异常的基类。"""


class ContainerError(ResourceEditorError):
    """资源包容器（0SLF / data.fls）解析或构建失败。"""


class CodecError(ResourceEditorError):
    """条目内容编解码失败。"""


class EncodeError(CodecError):
    """图片编码为精灵字节时失败（如行长超限、颜色数超限）。"""


class SaveError(ResourceEditorError):
    """保存流程（构建、校验、落盘）失败。"""
