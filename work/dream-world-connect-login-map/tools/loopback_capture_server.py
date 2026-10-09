#!/usr/bin/env python3
"""Loopback-only TCP capture listener for the local client connection test.

Binds only to 127.0.0.1, writes a timestamped text log and saves each raw TCP
stream under ./captures/ by default. It never sends application-protocol bytes
and never connects to an external host.
"""

from __future__ import annotations

import argparse
import logging
import socket
import sys
from datetime import datetime
from pathlib import Path

HOST = "127.0.0.1"
DEFAULT_PORT = 3134
CHUNK_SIZE = 4096


def format_ascii(data: bytes) -> str:
    return "".join(chr(byte) if 0x20 <= byte <= 0x7E else "." for byte in data)


def configure_logging(output_dir: Path, log_file: Path | None) -> Path:
    if log_file is None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = output_dir / f"server-{stamp}.log"
    else:
        log_file.parent.mkdir(parents=True, exist_ok=True)

    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, mode="a", encoding="utf-8"),
    ]
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )
    return log_file


def serve(port: int, output_dir: Path, log_file: Path | None) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    actual_log_file = configure_logging(output_dir, log_file)
    logger = logging.getLogger("loopback_capture")

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        listener.bind((HOST, port))
        listener.listen()
        logger.info("Listening only on %s:%d", HOST, port)
        logger.info("Waiting for a client; press Ctrl+C to stop")
        logger.info("Received bytes are logged and saved; no protocol response is sent")
        logger.info("Text log: %s", actual_log_file.resolve())

        connection_number = 0
        while True:
            client, peer = listener.accept()
            connection_number += 1
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            capture_path = output_dir / f"capture-{stamp}-{connection_number}.bin"
            logger.info("Accepted TCP connection from %s", peer)
            logger.info("Saving raw stream to %s", capture_path.resolve())

            received_total = 0
            with client, capture_path.open("wb") as capture:
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                while True:
                    data = client.recv(CHUNK_SIZE)
                    if not data:
                        logger.info("Client closed the connection")
                        break

                    capture.write(data)
                    capture.flush()
                    received_total += len(data)
                    hex_text = data.hex(" ").upper()
                    ascii_text = format_ascii(data)
                    logger.info("Received %d byte(s); total %d", len(data), received_total)
                    logger.info("HEX   %s", hex_text)
                    logger.info("ASCII %s", ascii_text)

            logger.info("Capture finished: %d byte(s) saved to %s", received_total, capture_path.resolve())
    except KeyboardInterrupt:
        logger.info("Stopping listener")
    except OSError as exc:
        logger.error("Could not listen on %s:%d: %s", HOST, port, exc)
        return 1
    finally:
        listener.close()

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture a local client's TCP bytes on loopback only.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"TCP port to listen on (default: {DEFAULT_PORT})")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "captures",
        help="directory for raw captures and default text log (default: tools/captures)",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="optional text-log path (default: timestamped .log in the capture directory)",
    )
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    return serve(args.port, args.output_dir, args.log_file)


if __name__ == "__main__":
    raise SystemExit(main())
