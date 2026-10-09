#!/usr/bin/env python3
"""Loopback-only, length-aware TCP harness for protocol experiments.

The client-side static evidence indicates a two-byte network-order length
written at the start of a prepared buffer. This harness does not infer command
semantics. It records complete TCP streams and can optionally send an
explicitly supplied response frame after each complete inbound frame.
"""

from __future__ import annotations

import argparse
import binascii
import logging
import socket
import struct
from pathlib import Path

HOST = "127.0.0.1"
DEFAULT_PORT = 3134
MAX_FRAME = 0xFFFF


def hex_dump(data: bytes) -> str:
    return data.hex(" ").upper()


def parse_hex(value: str) -> bytes:
    compact = "".join(value.split())
    if compact.startswith("0x"):
        compact = compact[2:]
    if len(compact) % 2:
        raise ValueError("hex response must contain an even number of digits")
    try:
        return binascii.unhexlify(compact)
    except binascii.Error as exc:
        raise ValueError(f"invalid response hex: {exc}") from exc


def frame_length(prefix: bytes) -> int:
    """Decode the provisional big-endian uint16 transport length."""
    return struct.unpack("!H", prefix)[0]


def extract_frames(buffer: bytearray) -> list[bytes]:
    frames: list[bytes] = []
    while len(buffer) >= 2:
        length = frame_length(buffer[:2])
        if length < 2 or length > MAX_FRAME:
            raise ValueError(f"invalid provisional frame length {length}")
        if len(buffer) < length:
            break
        frames.append(bytes(buffer[:length]))
        del buffer[:length]
    return frames


def serve(
    port: int,
    output_dir: Path,
    response: bytes | None,
    initial_response: bytes | None,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "responsive-harness.log"
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, mode="a", encoding="utf-8"),
        ],
        force=True,
    )
    logger = logging.getLogger("responsive-harness")
    if response is None:
        logger.info("response mode: capture-only")
    else:
        logger.info("response mode: explicit fixed response, %d byte(s)", len(response))
    if initial_response is not None:
        logger.info(
            "initial response mode: send-on-accept, %d byte(s)",
            len(initial_response),
        )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((HOST, port))
        listener.listen()
        logger.info("listening only on %s:%d", HOST, port)
        while True:
            client, peer = listener.accept()
            logger.info("accepted %s", peer)
            with client:
                if initial_response is not None:
                    client.sendall(initial_response)
                    logger.info(
                        "sent initial response: %s",
                        hex_dump(initial_response),
                    )
                pending = bytearray()
                capture = bytearray()
                while True:
                    chunk = client.recv(4096)
                    if not chunk:
                        break
                    capture.extend(chunk)
                    pending.extend(chunk)
                    logger.info("received %d byte(s): %s", len(chunk), hex_dump(chunk))
                    try:
                        frames = extract_frames(pending)
                    except ValueError as exc:
                        logger.error("framing stopped: %s", exc)
                        break
                    for frame in frames:
                        declared = frame_length(frame[:2])
                        logger.info(
                            "complete frame declared_len=%d observed_len=%d hex=%s",
                            declared,
                            len(frame),
                            hex_dump(frame),
                        )
                        if response is not None:
                            client.sendall(response)
                            logger.info("sent explicit response: %s", hex_dump(response))
                stamp = len(list(output_dir.glob("stream-*.bin"))) + 1
                stream_path = output_dir / f"stream-{stamp:04d}.bin"
                stream_path.write_bytes(capture)
                logger.info("connection closed; saved %d byte(s) to %s", len(capture), stream_path)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Loopback-only responsive TCP harness")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument(
        "--response-hex",
        help="explicit response bytes; omitted means capture-only and no server bytes",
    )
    parser.add_argument(
        "--initial-response-hex",
        help="explicit response bytes sent immediately after accept",
    )
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    try:
        response = None if args.response_hex is None else parse_hex(args.response_hex)
        initial_response = (
            None
            if args.initial_response_hex is None
            else parse_hex(args.initial_response_hex)
        )
    except ValueError as exc:
        parser.error(str(exc))
    return serve(args.port, args.output_dir, response, initial_response)


if __name__ == "__main__":
    raise SystemExit(main())
