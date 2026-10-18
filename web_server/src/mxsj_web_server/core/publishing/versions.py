"""Immutable content versions rendered into exact legacy bytes."""

from __future__ import annotations

import difflib
import hashlib
import json

from mxsj_web_server.core.content import render
from mxsj_web_server.core.publication import Application, Asset


def application(raw):
    assets = {}
    for name, body in render(raw).items():
        assets["/" + name] = Asset(
            body,
            "text/plain",
            '"' + hashlib.sha256(body).hexdigest() + '"',
            "public, max-age=0, must-revalidate",
        )
    return Application(assets)


def preview(raw):
    return {name: body.decode("big5") for name, body in render(raw).items()}


def difference(old, new):
    def lines(value):
        return json.dumps(value, ensure_ascii=False, indent=2).splitlines()

    return "\n".join(
        difflib.unified_diff(
            lines(old), lines(new), fromfile="当前发布", tofile="目标内容", lineterm=""
        )
    )
