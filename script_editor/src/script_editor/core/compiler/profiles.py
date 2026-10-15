from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Profile:
    key: str
    version: str
    magic: bytes
    label: str


PROFILES = {
    "py25": Profile("py25", "2.5.6", bytes.fromhex("b3f20d0a"), "script / VM2.5"),
    "py27": Profile("py27", "2.7.13", bytes.fromhex("03f30d0a"), "data / VM2.7"),
}
