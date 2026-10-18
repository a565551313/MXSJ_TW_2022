"""IP/CIDR access decisions and bounded, process-local rate limiting."""

from __future__ import annotations

import ipaddress
import time
from collections import OrderedDict


def in_networks(address, networks):
    return any(address in ipaddress.ip_network(n, strict=False) for n in networks)


def client_ip(peer, forwarded, trusted):
    address = ipaddress.ip_address(peer)
    if not in_networks(address, trusted) or not forwarded:
        return str(address)
    hops = forwarded.split(",")
    if len(hops) > 16:
        raise ValueError("代理链过长")
    chain = [ipaddress.ip_address(h.strip()) for h in hops]
    for previous in reversed(chain):
        if not in_networks(address, trusted):
            break
        address = previous
    return str(address)


def permitted(address, policy, now=None):
    if policy["mode"] == "allow":
        return True
    now = time.time() if now is None else now
    ip = ipaddress.ip_address(address)

    def matches(name):
        return any(
            (not r["expires"] or now < r["expires"])
            and ip in ipaddress.ip_network(r["cidr"], strict=False)
            for r in policy[name]
        )

    if matches("black"):
        return False
    return policy["mode"] != "white" or matches("white")


class Limiter:
    def __init__(self):
        self.entries = OrderedDict()

    def allow(self, key, limit, now=None):
        now = time.monotonic() if now is None else now
        start, count = self.entries.get(key, (now, 0))
        if now - start >= 60:
            start, count = now, 0
        self.entries[key] = (start, count + 1)
        self.entries.move_to_end(key)
        while len(self.entries) > 4096:
            self.entries.popitem(last=False)
        return count < limit
