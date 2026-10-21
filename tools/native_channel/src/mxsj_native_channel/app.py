"""Offline synthetic example: no socket, credentials or client modification."""

from __future__ import annotations

import argparse

from . import Channel, ClientHandshake, __version__, hello, hello_reply


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args(argv)
    seed = 0x12345678
    client = ClientHandshake()
    server = Channel(seed, "server")
    wire = hello(seed) + server.send(2, b"synthetic-server")
    received = []
    for byte in wire:
        received.extend(client.feed(bytes([byte])))
    assert client.take_reply() == hello_reply(seed)
    assert client.channel is not None
    response = server.feed(client.channel.send(3, b"synthetic-client"))
    client.finish()
    server.finish()
    print("Offline candidate codec demo (not native client acceptance)")
    print("Client received:", received)
    print("Server received:", response)
    return 0
