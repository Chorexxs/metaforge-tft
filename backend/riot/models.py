from typing import Any

from pydantic import BaseModel


class Unit(BaseModel):
    name: str
    level: int = 1
    tier: int = 1
    items: list[Any] = []


class GameState(BaseModel):
    round: str = "1-1"
    phase: str = "planning"
    stage: int = 1

    gold: int = 0
    level: int = 1
    xp: int = 0

    hp: int = 100
    max_hp: int = 100

    board_units: list[Unit] = []
    bench_units: list[Unit] = []

    bench_items: list[Any] = []

    augments: list[str] = []

    win_streak: int = 0
    lose_streak: int = 0

    is_active: bool = False


class GameEvent(BaseModel):
    type: str
    data: dict[str, Any] = {}


class Recommendation(BaseModel):
    action: str
    priority: int
    reasoning: str
    target_comps: list[str] = []
