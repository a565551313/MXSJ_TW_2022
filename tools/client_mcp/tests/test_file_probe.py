import json

from mxsj_client_mcp.core.protocol import PROTOCOL_VERSION, Message
from mxsj_client_mcp.transports.ipc_probe import FileProbeBackend


def test_file_probe_reads_report(tmp_path):
    path = tmp_path / "report.json"
    payload = {
        "runtime": {"python_version": [2, 5, 6]},
        "modules": {},
        "native_api": {},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    backend = FileProbeBackend(str(path))
    req = Message(
        v=PROTOCOL_VERSION,
        kind="request",
        id="1",
        session=backend.latest_session(),
        method="probe.get_report",
        params={},
    )
    result = backend.handle_request(req)
    assert result.ok is True
    assert result.result["runtime"]["python_version"] == [2, 5, 6]
