"""Fixed JSON response boundary."""

from __future__ import annotations

import json


def reply(status, payload):
    return (
        status,
        {
            "Content-Type": "application/json; charset=utf-8",
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
        json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    )
