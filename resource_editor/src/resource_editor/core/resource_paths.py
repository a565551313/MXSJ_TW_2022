"""游戏包内相对路径验证（零 Qt）。"""

from pathlib import PureWindowsPath


def validate_resource_path(value: str) -> str:
    value = value.strip().replace("/", "\\")
    if (
        not value
        or PureWindowsPath(value).drive
        or PureWindowsPath(value).is_absolute()
        or any(ord(char) < 32 or char in '<>:"|?*' for char in value)
        or any(part in ("", ".", "..") for part in value.split("\\"))
    ):
        raise ValueError("请填写包内相对路径，不是电脑文件地址；不能含空段或 . / ..。")
    value.encode("gbk")
    return value
