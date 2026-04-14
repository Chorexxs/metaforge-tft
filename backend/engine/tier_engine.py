from typing import Any

from shared.logger import get_logger

logger = get_logger(__name__)

WEIGHT_WINRATE = 0.4
WEIGHT_TOP4 = 0.35
WEIGHT_PLACEMENT = 0.25

MIN_GAMES_CONFIDENT = 100
MEDIUM_GAMES = 500
HIGH_GAMES = 1000


def calculate_placement_score(avg_placement: float) -> float:
    return max(0, (8 - avg_placement) / 7) * 100


def get_confidence_multiplier(game_count: int) -> float:
    if game_count < MIN_GAMES_CONFIDENT:
        return 0.5
    elif game_count < MEDIUM_GAMES:
        return 0.7
    elif game_count < HIGH_GAMES:
        return 0.85
    return 1.0


def calculate_tier_score(
    winrate: float,
    top4rate: float,
    avg_placement: float,
    game_count: int = 0,
) -> float:
    placement_score = calculate_placement_score(avg_placement)

    raw_score = (
        winrate * WEIGHT_WINRATE + top4rate * WEIGHT_TOP4 + placement_score * WEIGHT_PLACEMENT
    )

    confidence = get_confidence_multiplier(game_count)
    return raw_score * confidence


def assign_tier(score: float) -> str:
    if score >= 60:
        return "S"
    elif score >= 45:
        return "A"
    elif score >= 30:
        return "B"
    return "C"


def rank_compositions(
    compositions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    for comp in compositions:
        score = calculate_tier_score(
            winrate=comp.get("winrate", 0),
            top4rate=comp.get("top4rate", 0),
            avg_placement=comp.get("avg_placement", 8),
            game_count=comp.get("game_count", 0),
        )
        comp["score"] = score
        comp["tier"] = assign_tier(score)

    compositions.sort(key=lambda x: x.get("score", 0), reverse=True)
    return compositions


def filter_by_tier(
    compositions: list[dict[str, Any]],
    tiers: list[str],
) -> list[dict[str, Any]]:
    return [c for c in compositions if c.get("tier") in tiers]


def filter_by_patch(
    compositions: list[dict[str, Any]],
    patch: str,
) -> list[dict[str, Any]]:
    return [c for c in compositions if c.get("patch_number") == patch]


def get_top_compositions(
    compositions: list[dict[str, Any]],
    limit: int = 10,
) -> list[dict[str, Any]]:
    return compositions[:limit]


def merge_compositions(
    sources: list[list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    comp_dict: dict[str, dict[str, Any]] = {}

    for source_comps in sources:
        for comp in source_comps:
            name = comp.get("name", "").lower().strip()
            if not name:
                continue

            if name in comp_dict:
                existing = comp_dict[name]
                existing["winrate"] = (existing["winrate"] + comp.get("winrate", 0)) / 2
                existing["top4rate"] = (existing["top4rate"] + comp.get("top4rate", 0)) / 2
                existing["game_count"] = existing.get("game_count", 0) + comp.get("game_count", 0)
            else:
                comp_dict[name] = {
                    "name": comp.get("name"),
                    "winrate": comp.get("winrate", 0),
                    "top4rate": comp.get("top4rate", 0),
                    "avg_placement": comp.get("avg_placement", 8),
                    "traits": comp.get("traits", []),
                    "units": comp.get("units", []),
                    "game_count": comp.get("game_count", 0),
                    "patch_number": comp.get("patch_number"),
                }

    merged = list(comp_dict.values())
    return rank_compositions(merged)
