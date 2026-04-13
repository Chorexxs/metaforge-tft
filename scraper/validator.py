from typing import Any

from shared.logger import get_logger

logger = get_logger(__name__)

VALID_CHAMPIONS = {
    "aatrox",
    "ahri",
    "akali",
    "akshan",
    "alistar",
    "amumu",
    "anivia",
    "annie",
    "aphelios",
    "ashe",
    "aurelion",
    "azir",
    "bard",
    "belveth",
    "blitzcrank",
    "brand",
    "braum",
    "briar",
    "caitlyn",
    "camille",
    "cassiopeia",
    "chogath",
    "corki",
    "darius",
    "diana",
    "draven",
    "ekko",
    "elise",
    "emily",
    "esports",
    "evelynn",
    "ezreal",
    "fiddlesticks",
    "fiora",
    "fizz",
    "galio",
    "gangplank",
    "garen",
    "gnar",
    "gragas",
    "graves",
    "gwen",
    "gz",
    "harden",
    "hecarim",
    "heimerdinger",
    "illaoi",
    "irelia",
    "ivern",
    "janna",
    "jarvaniv",
    "jax",
    "jayce",
    "jhin",
    "jinx",
    "js",
    "kaiisa",
    "kalista",
    "kamar",
    "kassadin",
    "katarina",
    "kayle",
    "kayn",
    "kennen",
    "khazix",
    "kindred",
    "kled",
    "kogmaw",
    "ksante",
    "leblanc",
    "lee sin",
    "leona",
    "leroy",
    "lillia",
    "lissandra",
    "lucian",
    "lulu",
    "lux",
    "malphite",
    "malzahar",
    "maokai",
    "masteryi",
    "milio",
    "miss fortune",
    "mordekaiser",
    "morgana",
    "nami",
    "nasus",
    "nautilus",
    "neeko",
    "nidalee",
    "nilah",
    "nocturne",
    "nunu",
    "olaf",
    "orianna",
    "ornn",
    "pantheon",
    "poppy",
    "pyke",
    "qiyana",
    "quinn",
    "rakan",
    "rammus",
    "reksai",
    "rell",
    "renata",
    "renekton",
    "rengar",
    "rhythm",
    "riven",
    "rumble",
    "ryze",
    "samira",
    "sejuani",
    "senada",
    "senna",
    "seraphine",
    "seraphine2",
    "sett",
    "shaco",
    "shen",
    "shyvana",
    "singed",
    "sion",
    "sivir",
    "skarner",
    "smolder",
    "sona",
    "soraka",
    "swain",
    "sylas",
    "syndra",
    "tahmkench",
    "taliyah",
    "talon",
    "tali",
    "taric",
    "teemo",
    "thresh",
    "tristana",
    "trundle",
    "tryndamere",
    "twisted fate",
    "twitch",
    "tyler1",
    "udyr",
    "urgot",
    "varus",
    "vayne",
    "veigar",
    "velkoz",
    "vex",
    "vi",
    "viego",
    "viktor",
    "vileman",
    "vladimir",
    "vlkn",
    "volibear",
    "warwick",
    "wukong",
    "xayah",
    "xerath",
    "xin zhao",
    "xinzhao",
    "yasuo",
    "yone",
    "yorick",
    "yuumi",
    "zac",
    "zed",
    "zeri",
    "ziggs",
    "zilean",
    "zoe",
    "zyra",
}

TIER_VALUES = {"S": 4, "A": 3, "B": 2, "C": 1}


def validate_composition_data(comp: dict[str, Any]) -> bool:
    if not comp.get("name"):
        logger.warning("composition_missing_name")
        return False

    if not comp.get("tier"):
        logger.warning("composition_missing_tier", name=comp.get("name"))
        return False

    tier = comp.get("tier", "").upper()
    if tier not in TIER_VALUES:
        logger.warning("invalid_tier", tier=tier, name=comp.get("name"))
        return False

    for key in ["winrate", "top4rate"]:
        value = comp.get(key, 0)
        if not isinstance(value, (int, float)) or value < 0 or value > 100:
            logger.warning(f"invalid_{key}", value=value, name=comp.get("name"))
            return False

    avg = comp.get("avg_placement", 8)
    if not isinstance(avg, (int, float)) or avg < 1 or avg > 8:
        logger.warning("invalid_avg_placement", avg=avg, name=comp.get("name"))
        return False

    return True


def validate_item_data(item: dict[str, Any]) -> bool:
    if not item.get("name"):
        logger.warning("item_missing_name")
        return False
    return True


def validate_augment_data(
    augment: dict[str, Any], valid_champions: set[str] | None = None
) -> bool:
    if not augment.get("name"):
        logger.warning("augment_missing_name")
        return False

    tier = augment.get("tier", "").lower()
    if tier not in ["prismatic", "gold", "silver"]:
        logger.warning("invalid_augment_tier", tier=tier)
        return False

    return True


def calculate_confidence_score(comp: dict[str, Any]) -> float:
    game_count = comp.get("game_count", 0)

    if game_count < 100:
        return 0.5
    elif game_count < 500:
        return 0.7
    elif game_count < 1000:
        return 0.85
    else:
        return 1.0
