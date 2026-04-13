from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Tier(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"


class IngestionStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class PatchVersion(BaseModel):
    id: Optional[int] = None
    number: str
    detected_at: datetime
    ingestion_status: IngestionStatus = IngestionStatus.pending


class Champion(BaseModel):
    id: Optional[int] = None
    key: str
    name: str
    cost: int
    traits: list[str] = []


class UnitRole(str, Enum):
    carry = "carry"
    tank = "tank"
    flex = "flex"


class UnitPriority(str, Enum):
    core = "core"
    optional = "optional"


class CompositionUnit(BaseModel):
    champion_id: int
    role: UnitRole
    priority: UnitPriority
    star_level: int = 1


class ItemSlot(BaseModel):
    item_id: str
    slot: int
    is_bis: bool = False
    is_flex: bool = False


class Composition(BaseModel):
    id: Optional[int] = None
    name: str
    patch_number: str
    tier: Tier
    winrate: float
    top4rate: float
    avg_placement: float
    traits: list[str] = []
    units: list[CompositionUnit] = []
    items: list[ItemSlot] = []
    game_count: Optional[int] = None


class AugmentTier(str, Enum):
    prismatic = "prismatic"
    gold = "gold"
    silver = "silver"


class AugmentStage(str, Enum):
    stage_2_1 = "2-1"
    stage_3_2 = "3-2"
    stage_4_2 = "4-2"


class Augment(BaseModel):
    id: Optional[int] = None
    name: str
    tier: AugmentTier
    description: str


class CompositionAugment(BaseModel):
    composition_id: int
    augment_id: int
    stage: AugmentStage
    rank: int
    notes: Optional[str] = None


class GamePhase(str, Enum):
    early = "early"
    mid = "mid"
    late = "late"


class EarlyGamePlan(BaseModel):
    composition_id: int
    phase: GamePhase
    units: list[str] = []
    econ_target: Optional[int] = None
    positioning_notes: Optional[str] = None


class GameState(BaseModel):
    round: str
    gold: int
    level: int
    xp: int
    hp: int
    win_streak: int = 0
    lose_streak: int = 0
    board_units: list[str] = []
    bench_units: list[str] = []
    bench_items: list[str] = []
    augments: list[str] = []


class Recommendation(BaseModel):
    action: str
    priority: int
    reasoning: str
    target_comps: list[str] = []
