import asyncio
import random
from typing import Any

import httpx
from bs4 import BeautifulSoup

from scraper.validator import validate_composition_data
from shared.logger import get_logger

logger = get_logger(__name__)

TACTICS_URL = "https://tactics.tools/teamfight-tactics"
METATFT_URL = "https://metatft.com/tft-tier-list"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]


def get_random_headers() -> dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
    }


async def delay_random() -> None:
    await asyncio.sleep(random.uniform(2, 5))


async def fetch_tactics_comps() -> list[dict[str, Any]]:
    comps: list[dict[str, Any]] = []

    try:
        async with httpx.AsyncClient(timeout=30.0, headers=get_random_headers()) as client:
            await delay_random()

            response = await client.get(TACTICS_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            comp_elements = soup.select("[class*='comp'], [class*='build']")

            for elem in comp_elements[:20]:
                name = elem.select_one("h3, h4, [class*='name']")
                if not name:
                    continue

                winrate = elem.select("[class*='win'], [class*='wr']")
                top4 = elem.select("[class*='top4']")

                comp: dict[str, Any] = {
                    "name": name.get_text(strip=True),
                    "tier": "B",
                    "winrate": _parse_percentage(winrate[0].get_text() if winrate else "0%"),
                    "top4rate": _parse_percentage(top4[0].get_text() if top4 else "0%"),
                    "avg_placement": 4.5,
                    "traits": _extract_traits(elem),
                    "units": _extract_units(elem),
                    "items": [],
                }

                if validate_composition_data(comp):
                    comps.append(comp)

            logger.info("tactics_comps_scraped", count=len(comps))

    except httpx.HTTPError as e:
        logger.error("tactics_fetch_failed", error=str(e))
    except Exception as e:
        logger.error("tactics_parse_failed", error=str(e))

    return comps


async def fetch_metatft_comps() -> list[dict[str, Any]]:
    comps: list[dict[str, Any]] = []

    try:
        async with httpx.AsyncClient(timeout=30.0, headers=get_random_headers()) as client:
            await delay_random()

            response = await client.get(METATFT_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            tier_sections = soup.select("[class*='tier'], [class*='comp']")

            for tier_letter, section in enumerate(tier_sections[:4]):
                tier = ["S", "A", "B", "C"][tier_letter] if tier_letter < 4 else "B"

                for comp_card in section.select("[class*='card']")[:10]:
                    name = comp_card.select_one("h3, h4, [class*='name']")
                    if not name:
                        continue

                    comp = {
                        "name": name.get_text(strip=True),
                        "tier": tier,
                        "winrate": 45.0 if tier in ["S", "A"] else 40.0,
                        "top4rate": 70.0 if tier in ["S", "A"] else 60.0,
                        "avg_placement": 4.0 if tier == "S" else 5.0,
                        "traits": _extract_traits(comp_card),
                        "units": _extract_units(comp_card),
                        "items": [],
                    }

                    if validate_composition_data(comp):
                        comps.append(comp)

            logger.info("metatft_comps_scraped", count=len(comps))

    except httpx.HTTPError as e:
        logger.error("metatft_fetch_failed", error=str(e))
    except Exception as e:
        logger.error("metatft_parse_failed", error=str(e))

    return comps


def _parse_percentage(text: str) -> float:
    text = text.replace("%", "").replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return 0.0


def _extract_traits(element: BeautifulSoup) -> list[str]:
    traits: list[str] = []
    trait_elems = element.select("[class*='trait'], [class*='synergy']")
    for t in trait_elems[:6]:
        text = t.get_text(strip=True)
        if text:
            traits.append(text)
    return traits


def _extract_units(element: BeautifulSoup) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    unit_elems = element.select("[class*='champion'], [class*='unit']")
    for i, u in enumerate(unit_elems[:8]):
        text = u.get_text(strip=True) or f"Unit{i + 1}"
        units.append({"name": text, "role": "flex", "priority": "optional", "star": 1})
    return units


def merge_comps(
    comps_list: list[list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    comp_dict: dict[str, dict[str, Any]] = {}

    for comps in comps_list:
        for comp in comps:
            name = comp.get("name", "").lower()
            if name in comp_dict:
                existing = comp_dict[name]
                existing["winrate"] = (existing["winrate"] + comp["winrate"]) / 2
                existing["top4rate"] = (existing["top4rate"] + comp["top4rate"]) / 2
            else:
                comp_dict[name] = comp

    merged = list(comp_dict.values())
    merged.sort(key=lambda x: x["winrate"], reverse=True)

    for i, comp in enumerate(merged[:4]):
        comp["tier"] = "S"
    for i, comp in enumerate(merged[4:8], start=4):
        comp["tier"] = "A"
    for i, comp in enumerate(merged[8:14], start=8):
        comp["tier"] = "B"

    return merged


async def run_comps_scraper(patch_number: str) -> list[dict[str, Any]]:
    logger.info("comps_scraper_started", patch=patch_number)

    tactics_comps = await fetch_tactics_comps()
    metatft_comps = await fetch_metatft_comps()

    merged_comps = merge_comps([tactics_comps, metatft_comps])

    for comp in merged_comps:
        comp["patch_number"] = patch_number

    logger.info("comps_scraper_completed", patch=patch_number, count=len(merged_comps))
    return merged_comps


if __name__ == "__main__":
    import asyncio
    from shared.logger import setup_logging

    setup_logging()
    result = asyncio.run(run_comps_scraper("14.1"))
    print(f"Found {len(result)} compositions")
