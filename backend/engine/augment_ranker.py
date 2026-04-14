from typing import Any

from shared.logger import get_logger

logger = get_logger(__name__)

AUGMENT_STAGES = {
    "2-1": "prismatic",
    "3-2": "gold",
    "4-2": "prismatic",
    "4-5": "gold",
}

TIER_WEIGHTS = {
    "prismatic": 3,
    "gold": 2,
    "silver": 1,
}


def get_available_augment_slots(round_: str) -> list[str]:
    if round_ == "2-1":
        return ["2-1"]
    if round_ == "3-2":
        return ["3-2"]
    if round_ == "4-2":
        return ["4-2"]
    return []


def rank_augments_for_comp(
    available_augments: list[dict[str, Any]],
    target_comp_traits: list[str],
) -> list[dict[str, Any]]:
    scored = []

    for aug in available_augments:
        aug_name = aug.get("name", "")
        aug_traits = aug.get("traits", [])

        synergy_count = sum(1 for t in target_comp_traits if t in aug_traits)

        tier = aug.get("tier", "silver")
        tier_score = TIER_WEIGHTS.get(tier, 1)

        score = (synergy_count * 10) + (tier_score * 5)

        scored.append(
            {
                "name": aug_name,
                "tier": tier,
                "score": score,
                "synergies": synergy_count,
            }
        )

    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    return scored


def get_best_augment(
    available: list[dict[str, Any]],
    target_traits: list[str],
) -> dict[str, Any] | None:
    ranked = rank_augments_for_comp(available, target_traits)
    return ranked[0] if ranked else None


def get_augment_recommendations(
    round_: str,
    augments_offered: list[dict[str, Any]],
    current_comp: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if round_ not in ["2-1", "3-2", "4-2"]:
        return []

    target_traits = current_comp.get("traits", []) if current_comp else []

    ranked = rank_augments_for_comp(augments_offered, target_traits)

    return [
        {
            "rank": i + 1,
            "name": aug.get("name"),
            "tier": aug.get("tier"),
            "score": aug.get("score"),
            "reasoning": f"Synergy with {aug.get('synergies')} traits"
            if aug.get("synergies")
            else f"High tier {aug.get('tier')}",
        }
        for i, aug in enumerate(ranked[:3])
    ]
