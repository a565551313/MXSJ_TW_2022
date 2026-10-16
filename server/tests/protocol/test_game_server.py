from __future__ import annotations

import asyncio
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER / "src"))

from mxsj_server.application.game_loop import GameLoopService
from mxsj_server.bootstrap.game_server import _serve_connection


class GameServerProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.service = GameLoopService(Path(self.tempdir.name) / "wire.sqlite3")
        self.server = await asyncio.start_server(
            lambda reader, writer: _serve_connection(reader, writer, self.service),
            "127.0.0.1",
            0,
            limit=16 * 1024 + 1,
        )
        self.port = self.server.sockets[0].getsockname()[1]
        self.reader, self.writer = await asyncio.open_connection("127.0.0.1", self.port)

    async def asyncTearDown(self) -> None:
        self.writer.close()
        await self.writer.wait_closed()
        self.server.close()
        await self.server.wait_closed()
        self.tempdir.cleanup()

    async def request(self, **payload: Any) -> dict[str, Any]:
        self.writer.write(json.dumps(payload, ensure_ascii=False).encode("utf-8") + b"\n")
        await self.writer.drain()
        return json.loads(await asyncio.wait_for(self.reader.readline(), timeout=5))

    async def test_wire_level_registration_to_map_closure(self) -> None:
        registered = await self.request(
            action="register", account_name="wire_player", password="correct-horse-battery"
        )
        self.assertTrue(registered["ok"])
        realms = await self.request(action="list_realms")
        self.assertEqual(realms["result"][0]["realm_id"], 1)
        selected_realm = await self.request(action="select_realm", realm_id=1)
        self.assertEqual(selected_realm["result"]["name"], "开发区")
        login = await self.request(
            action="login", account_name="wire_player", password="correct-horse-battery", realm_id=1
        )
        self.assertTrue(login["ok"])
        ticket = login["result"]["session_ticket"]
        created = await self.request(
            action="create_character", session_ticket=ticket, realm_id=1,
            operation_id="wire-create-1", name="网测角色",
        )
        character_id = created["result"]["character_id"]
        listed = await self.request(action="list_characters", session_ticket=ticket, realm_id=1)
        self.assertEqual([item["character_id"] for item in listed["result"]], [character_id])
        selected = await self.request(
            action="select_character", session_ticket=ticket, realm_id=1, character_id=character_id
        )
        self.assertEqual(selected["result"]["character_id"], character_id)
        entered = await self.request(action="enter_map", session_ticket=ticket, realm_id=1)
        self.assertEqual(entered["result"]["character_id"], character_id)
        self.assertEqual(entered["result"]["map_template_id"], 1)

    async def test_unknown_action_is_rejected_without_traceback(self) -> None:
        response = await self.request(action="eval", expression="__import__('os').system('id')")
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], "INVALID_ARGUMENT")
        self.assertNotIn("Traceback", json.dumps(response))


if __name__ == "__main__":
    unittest.main()
