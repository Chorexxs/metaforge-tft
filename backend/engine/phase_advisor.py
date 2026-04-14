from typing import Any

from shared.logger import get_logger

logger = get_logger(__name__)

ROUND_KRUGS = "2-1"
ROUND_WOLVES = "2-3"
ROUND_RIFTHORSE = "3-2"
ROUND_THREE_STAR = "4-3"
ROUND_FOUR_STAR = "4-5"

LEVEL_THRESHOLDS = {
    "early": 4,
    "mid": 6,
    "late": 8,
}

ECON_TARGETS = {
    "early": 50,
    "mid": 30,
    "late": 10,
}


def detect_phase(round_: str, level: int) -> str:
    if round_ in ["1-1", "1-2", "1-3", "1-4", "1-5", "1-6", "1-7"]:
        return "early"
    if round_ in ["2-1", "2-2", "2-3", "2-4", "2-5", "2-6", "2-7"]:
        if level <= 4:
            return "early"
        return "mid"
    if round_ in ["3-1", "3-2", "3-3", "3-4", "3-5", "3-6", "3-7"]:
        return "mid"
    return "late"


def get_econ_target(phase: str) -> int:
    return ECON_TARGETS.get(phase, 20)


def should_econ(phase: str, gold: int, round_: str) -> bool:
    target = get_econ_target(phase)

    if gold >= 50 and round_ != ROUND_KRUGS:
        return True

    if gold >= target:
        return True

    return False


def should_level_up(level: int, gold: int, phase: str) -> bool:
    if level >= 7 and gold >= 40:
        return True
    if level >= 6 and gold >= 30 and phase == "early":
        return True
    if level >= 5 and gold >= 50 and phase == "early":
        return True

    return False


def should_reroll(phase: str, gold: int, level: int) -> bool:
    if phase == "early":
        return False
    if gold >= 30 and level >= 8:
        return False
    if gold >= 40 and level >= 7:
        return True

    return gold >= 50


def get_action(phase: str, gold: int, level: int, round_: str) -> dict[str, Any]:
    action = {"action": "wait", "priority": 0, "reasoning": "default"}

    if should_econ(phase, gold, round_):
        return {
            "action": "econ",
            "priority": 5,
            "reasoning": f"Target {get_econ_target(phase)}g by this phase",
        }

    if should_level_up(level, gold, phase):
        return {
            "action": "level_up",
            "priority": 4,
            "reasoning": "Level up for better odds",
        }

    if should_reroll(phase, gold, level):
        return {
            "action": "reroll",
            "priority": 3,
            "reasoning": "Reroll for upgrades",
        }

    return action


def recommend_board_units(
    board_units: list[str],
    target_comp_units: list[dict[str, Any]],
) -> dict[str, Any]:
    core_units = [u for u in target_comp_units if u.get("priority") == "core"]
    flex_units = [u for u in target_comp_units if u.get("priority") == "flex"]

    on_board = set(board_units)
    core_on_board = [u for u in core_units if u.get("name") in on_board]
    core_missing = [u for u in core_units if u.get("name") not in on_board]

    flex_on_board = [u for u in flex_units if u.get("name") in on_board]

    return {
        "core_on_board": core_on_board,
        "core_missing": core_missing,
        "flex_on_board": flex_on_board,
        "completion_percent": len(core_on_board) / len(core_units) if core_units else 0,
    }


def get_transition_options(
    current_units: list[str],
    available_comps: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    options = []

    for comp in available_comps:
        comp_units = comp.get("units", [])
        core_names = [u.get("name") for u in comp_units if u.get("priority") == "core"]

        matches = sum(1 for name in core_names if name in current_units)
        if matches == 0:
            continue

        cost = len(core_names) - matches
        options.append(
            {
                "comp_name": comp.get("name"),
                "matches": matches,
                "total_needed": len(core_names),
                "cost_to_buy": cost,
                "tier": comp.get("tier"),
            }
        )

    options.sort(key=lambda x: (x["cost_to_buy"], -x["matches"]))
    return options
