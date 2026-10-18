"""Validated network and access policy; changing settings never starts listeners."""

from __future__ import annotations

import copy
import ipaddress
import re
from urllib.parse import urlsplit


def defaults():
    policy = {
        "mode": "allow",
        "black": [],
        "white": [],
        "trusted_proxies": [],
        "requests_per_minute": 120,
    }
    return {
        "public": {
            "host": "127.0.0.1",
            "port": 8080,
            "origin": "http://127.0.0.1:8080",
            **copy.deepcopy(policy),
        },
        "admin": {
            "host": "127.0.0.1",
            "port": 8081,
            "origin": "http://127.0.0.1:8081",
            **copy.deepcopy(policy),
        },
    }


def validate(raw):
    if not isinstance(raw, dict) or set(raw) != {"public", "admin"}:
        raise ValueError("需要 public 和 admin 两组设置")
    raw = copy.deepcopy(raw)
    expected = set(defaults()["public"])
    for kind in ("public", "admin"):
        item = raw[kind]
        if not isinstance(item, dict) or set(item) != expected:
            raise ValueError("网络设置字段不正确")
        ipaddress.ip_address(item["host"])
        if type(item["port"]) is not int or not 1 <= item["port"] <= 65535:
            raise ValueError("端口必须为 1..65535")
        if (
            not isinstance(item["origin"], str)
            or len(item["origin"]) > 512
            or any(ch.isspace() or ord(ch) < 32 for ch in item["origin"])
        ):
            raise ValueError("对外地址无效")
        origin = urlsplit(item["origin"])
        if (
            origin.scheme not in {"http", "https"}
            or not origin.hostname
            or origin.username
            or origin.password
            or origin.path
            or origin.query
            or origin.fragment
        ):
            raise ValueError("对外地址仅包含协议、域名和可选端口，不含路径")
        if origin.port is not None and not 1 <= origin.port <= 65535:
            raise ValueError("对外端口无效")
        hostname = origin.hostname.lower()
        try:
            ip = ipaddress.ip_address(hostname)
            hostname = f"[{ip}]" if ip.version == 6 else str(ip)
        except ValueError:
            if not re.fullmatch(r"[a-z0-9]+(?:[a-z0-9.-]*[a-z0-9])?", hostname):
                raise ValueError("域名须为有效 ASCII／punycode 名称") from None
        port = origin.port
        port_text = (
            f":{port}"
            if port and port != (443 if origin.scheme == "https" else 80)
            else ""
        )
        item["origin"] = f"{origin.scheme}://{hostname}{port_text}"
        if kind == "admin" and origin.scheme != "https":
            if (
                origin.hostname not in {"localhost", "127.0.0.1", "::1"}
                or not ipaddress.ip_address(item["host"]).is_loopback
            ):
                raise ValueError("非本机管理后台必须配置 HTTPS 对外地址和 TLS 反向代理")
        if item["mode"] not in {"allow", "black", "white"}:
            raise ValueError("访问模式必须为 allow、black 或 white")
        for name in ("black", "white"):
            if not isinstance(item[name], list) or len(item[name]) > 256:
                raise ValueError("名单最多 256 项")
            for rule in item[name]:
                if not isinstance(rule, dict) or set(rule) != {
                    "cidr",
                    "note",
                    "expires",
                }:
                    raise ValueError("名单条目需要 cidr、note、expires")
                ipaddress.ip_network(rule["cidr"], strict=False)
                if not isinstance(rule["note"], str) or len(rule["note"]) > 128:
                    raise ValueError("备注过长")
                if type(rule["expires"]) is not int or rule["expires"] < 0:
                    raise ValueError("到期时间须为 Unix 秒，0 表示永久")
        if (
            not isinstance(item["trusted_proxies"], list)
            or len(item["trusted_proxies"]) > 32
        ):
            raise ValueError("可信代理最多 32 项")
        for network in item["trusted_proxies"]:
            ipaddress.ip_network(network, strict=False)
        limit = item["requests_per_minute"]
        if type(limit) is not int or not 10 <= limit <= 10000:
            raise ValueError("每来源每分钟请求上限须为 10..10000")
    a, b = raw["public"], raw["admin"]
    if a["port"] == b["port"]:
        raise ValueError("公开服务与后台必须使用不同端口")
    return copy.deepcopy(raw)
