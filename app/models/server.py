from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Server:
    id: str
    name: str


SERVERS: tuple[Server, ...] = (
    Server("cain", "카인"),
    Server("diregie", "디레지에"),
    Server("siroco", "시로코"),
    Server("prey", "프레이"),
    Server("casillas", "카시야스"),
    Server("hilder", "힐더"),
    Server("anton", "안톤"),
    Server("bakal", "바칼"),
)
