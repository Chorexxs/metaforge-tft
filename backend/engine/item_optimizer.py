from typing import Any

from shared.logger import get_logger

logger = get_logger(__name__)

ITEM_COMPONENTS = {
    "BFSword": {"name": "Broadsword", "slot": "attack"},
    "BFDrake": {"name": "Broadsword", "slot": "attack"},
    "ChainVest": {"name": "Chain Vest", "slot": "defense"},
    "GiantBelt": {"name": "Giant's Belt", "slot": "health"},
    "Needlessly": {"name": "Needlessly Large Rod", "slot": "spell"},
    "Null": {"name": "Null Magic Mantle", "slot": "magic"},
    "PickAxe": {"name": "Pickaxe", "slot": "attack"},
    "Recurve": {"name": "Recurve Bow", "slot": "attack"},
    "Sparring": {"name": "Sparring Gloves", "slot": "crit"},
    "Spatula": {"name": "Spatula", "slot": "trait"},
    "Tear": {"name": "Tear of Silence", "slot": "mana"},
    "Warded": {"name": "Warding Talisman", "slot": "mana"},
}

COMPLETE_ITEMS = {
    "Deathblade": ["BFDrake", "BFDrake"],
    "Giant Slayer": ["BFDrake", "Recurve"],
    "Infinity Edge": ["BFDrake", "Tear"],
    "Jeweled Lotus": ["Tear", "Tear"],
    "Rabadon's": ["Needlessly", "Needlessly"],
    "Rabamortal": ["PickAxe", "Needlessly"],
    "Spear": ["PickAxe", "BFDrake"],
    "HoJ": ["Sparring", "Tear"],
    "BT": ["BFDrake", "ChainVest"],
    "GA": ["BFDrake", "Null"],
    "DB": ["ChainVest", "ChainVest"],
    "Zephyr": ["ChainVest", "GiantBelt"],
    "Warmog": ["GiantBelt", "GiantBelt"],
    "Gargoyle": ["ChainVest", "Null"],
    "Locket": ["Null", "Null"],
    "Frozen Heart": ["Tear", "ChainVest"],
    "Shroud": ["Null", "GiantBelt"],
    "Ionic": ["Needlessly", "Null"],
    "Gunblade": ["BFDrake", "Needlessly"],
}


def get_component(item_key: str) -> dict[str, Any]:
    return ITEM_COMPONENTS.get(item_key, {})


def get_completed_items(components: list[str]) -> list[str]:
    completed = []
    remaining = components.copy()

    for item_name, recipe in COMPLETE_ITEMS.items():
        recipe_parts = recipe.copy()
        can_make = True

        for part in recipe_parts:
            if part not in remaining:
                can_make = False
                break
            remaining.remove(part)

        if can_make:
            completed.append(item_name)

    return completed


def find_bis_items(
    target_comp: dict[str, Any],
    inventory: list[str],
) -> list[dict[str, Any]]:
    bis_items_comp = target_comp.get("bis_items", {})

    recommendations = []
    for slot, item_prefs in bis_items_comp.items():
        slot_type = ITEM_COMPONENTS.get(slot, {}).get("slot", "unknown")

        for pref in item_prefs:
            if pref in inventory:
                recommendations.append(
                    {
                        "slot": slot,
                        "item": pref,
                        "priority": "high",
                        "slot_type": slot_type,
                    }
                )

    return recommendations


def optimize_item_inventory(
    components: list[str],
    target_comp: dict[str, Any],
    bench_items: list[str] | None = None,
) -> dict[str, Any]:
    all_items = components.copy()
    if bench_items:
        all_items.extend(bench_items)

    completed = get_completed_items(all_items)

    bis_recs = find_bis_items(target_comp, all_items)

    upgradeable = []
    for slot, item_info in ITEM_COMPONENTS.items():
        if item_info["slot"] in ["attack", "defense", "spell"]:
            count = all_items.count(slot)
            if count >= 2:
                for check_item, recipe in COMPLETE_ITEMS.items():
                    if recipe.count(slot) >= 2:
                        upgradeable.append(
                            {
                                "slot": slot,
                                "result": check_item,
                                "components": [slot, slot],
                            }
                        )

    return {
        "completed_items": completed,
        "bis_recommendations": bis_recs,
        "upgradeable": upgradeable,
    }


def get_carries_items(champ_name: str, comp_data: dict[str, Any]) -> list[dict[str, Any]]:
    unit_items = comp_data.get("unit_items", [])
    return [ui for ui in unit_items if ui.get("champion") == champ_name]
