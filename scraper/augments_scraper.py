import asyncio
import random
from typing import Any

import httpx
from bs4 import BeautifulSoup

from scraper.database import init_db
from shared.logger import get_logger

logger = get_logger(__name__)

TFT_AUGMENTS_URL = "https://tactics.tools/augments"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
]


def get_random_headers() -> dict[str, str]:
    return {"User-Agent": random.choice(USER_AGENTS)}


async def fetch_augments() -> list[dict[str, Any]]:
    augments: list[dict[str, Any]] = []

    try:
        async with httpx.AsyncClient(timeout=30.0, headers=get_random_headers()) as client:
            await asyncio.sleep(random.uniform(2, 5))

            response = await client.get(TFT_AUGMENTS_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            augment_elements = soup.select("[class*='augment']")

            for elem in augment_elements:
                name_elem = elem.select_one("h3, h4, [class*='name']")
                if not name_elem:
                    continue

                tier_elem = elem.select_one(
                    "[class*='prismatic'], [class*='gold'], [class*='silver']"
                )
                tier = "silver"
                if tier_elem:
                    tier_class = tier_elem.get("class", [])
                    if "prismatic" in tier_class:
                        tier = "prismatic"
                    elif "gold" in tier_class:
                        tier = "gold"

                description = ""
                desc_elem = elem.select_one("p, [class*='desc']")
                if desc_elem:
                    description = desc_elem.get_text(strip=True)

                augment: dict[str, Any] = {
                    "name": name_elem.get_text(strip=True),
                    "tier": tier,
                    "description": description,
                }
                augments.append(augment)

            logger.info("augments_scraped", count=len(augments))

    except httpx.HTTPError as e:
        logger.error("augments_fetch_failed", error=str(e))
    except Exception as e:
        logger.error("augments_parse_failed", error=str(e))

    return augments


async def run_augments_scraper(patch_number: str) -> None:
    logger.info("augments_scraper_started", patch=patch_number)

    await init_db()

    augments = await fetch_augments()

    logger.info("augments_scraper_completed", patch=patch_number, count=len(augments))


if __name__ == "__main__":
    import asyncio

    from shared.logger import setup_logging

    setup_logging()
    asyncio.run(run_augments_scraper("14.1"))
