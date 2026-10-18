"""共享内部契约 v0.1；不是客户端报文，尚无运行时校验实现。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CommandSource(str, Enum):  # noqa: UP042  # 保留原契约的 str(Enum) 行为。
    CLIENT = "client"
    INTERNAL = "internal"
    ADMIN = "admin"


@dataclass(frozen=True, slots=True, kw_only=True)
class RequestContext:
    """由已认证接入层/内部调度器构造，禁止从客户端参数直接反序列化。

    operation_id 是业务幂等键，不是每次网络重试新生成的随机值。
    character_id 可空，但角色命令必须在应用层要求它存在且验证归属。
    source 不是授权结果；每个接口仍需检查主体权限。
    """

    operation_id: str
    trace_id: str
    realm_id: int
    account_id: int | None
    character_id: int | None
    session_epoch: int | None
    source: CommandSource


@dataclass(frozen=True, slots=True, kw_only=True)
class CommandReceipt:
    """成功结果。持久化命令仅在提交后返回；瞬态命令仅保证状态拥有者已接受。

    哪些命令需持久化由接口文档规定；未包含响应数据的重试应返回相同回执。
    revision 属于本命令的主实体，不是全服版本号。
    """

    operation_id: str
    revision: int
    entity_id: int | None = None
    event_ids: tuple[str, ...] = ()


class DomainError(Exception):
    """稳定错误码由协议适配器翻译；message 不应包含密码、SQL或内部堆栈。"""

    def __init__(self, code: str, message: str = "") -> None:
        self.code = code
        super().__init__(message or code)


@dataclass(frozen=True, slots=True, kw_only=True)
class PageRequest:
    """实现必须校验 limit 的上下限，cursor 为服务端生成的不透明值。"""

    limit: int = 50
    cursor: str | None = None
