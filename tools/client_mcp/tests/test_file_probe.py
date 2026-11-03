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


def _request(backend, method="probe.get_report"):
    return Message(
        v=PROTOCOL_VERSION,
        kind="request",
        id="1",
        session=backend.latest_session(),
        method=method,
        params={},
    )


def test_file_probe_reads_cpython25_repr_report(tmp_path):
    path = tmp_path / "mxsj_probe_report.txt"
    path.write_text(
        "{'runtime': {'thread_count': None, 'main_loop_ticks': None, 'pid': None, "
        "'python_version': [2, 5, 0]}, 'modules': {'modules': ["
        "{'loaded': True, 'name': 'sys'}, {'loaded': True, 'name': 'time'}, "
        "{'loaded': True, 'name': 'os'}]}, 'native_api': {'status': 'unknown', "
        "'apis': []}, 'probe_version': '0.1.0'}",
        encoding="utf-8",
    )
    backend = FileProbeBackend(str(path))
    result = backend.handle_request(_request(backend))
    assert result.ok is True
    assert result.result["runtime"]["python_version"] == [2, 5, 0]
    assert result.result["runtime"]["pid"] is None
    assert result.result["modules"]["modules"][0]["loaded"] is True
    runtime = backend.handle_request(_request(backend, "probe.get_runtime"))
    assert runtime.ok is True
    assert runtime.result["python_version"] == [2, 5, 0]


def test_file_probe_rejects_code_and_non_object(tmp_path):
    path = tmp_path / "report.txt"
    backend = FileProbeBackend(str(path))
    for text in ("__import__('os').system('echo nope')", "[1, 2, 3]", "'text'"):
        path.write_text(text, encoding="utf-8")
        result = backend.handle_request(_request(backend))
        assert result.ok is False


def test_file_probe_rejects_oversized_report(tmp_path):
    path = tmp_path / "report.txt"
    path.write_text("{" + "'x': " + "1" * (256 * 1024) + "}", encoding="utf-8")
    backend = FileProbeBackend(str(path))
    result = backend.handle_request(_request(backend))
    assert result.ok is False


def test_heartbeat_tracks_report_freshness(tmp_path):
    import os

    path = tmp_path / "mxsj_probe_report.txt"
    path.write_text(
        repr({"runtime": {}, "modules": {}, "native_api": {}}), encoding="utf-8"
    )
    os.utime(path, (1_000.0, 1_000.0))
    fresh = FileProbeBackend(
        str(path), fresh_seconds=5.0, clock=lambda: 1_002.0
    ).heartbeat()
    assert fresh["alive"] is True
    assert fresh["mode"] == "report-file"
    assert fresh["heartbeat"] == "resident-timer"
    assert fresh["report_age_seconds"] == 2.0

    stale = FileProbeBackend(
        str(path), fresh_seconds=5.0, clock=lambda: 1_100.0
    ).heartbeat()
    assert stale["alive"] is False
    assert stale["heartbeat"] == "stale"
    assert stale["report_age_seconds"] >= 5.0


def test_heartbeat_reports_missing_file_as_dead(tmp_path):
    backend = FileProbeBackend(str(tmp_path / "missing.txt"))
    beat = backend.heartbeat()
    assert beat["alive"] is False
    assert beat["report_age_seconds"] is None


def test_ping_tool_returns_heartbeat_through_the_protocol(tmp_path):
    import time

    path = tmp_path / "report.txt"
    path.write_text(
        repr({"runtime": {}, "modules": {}, "native_api": {}}), encoding="utf-8"
    )
    backend = FileProbeBackend(str(path), fresh_seconds=30.0, clock=time.time)
    result = backend.handle_request(_request(backend, "probe.heartbeat"))
    assert result.ok is True
    assert result.result["alive"] is True


def test_fresh_seconds_must_be_positive(tmp_path):
    import pytest

    with pytest.raises(ValueError):
        FileProbeBackend(str(tmp_path / "x.txt"), fresh_seconds=0)
