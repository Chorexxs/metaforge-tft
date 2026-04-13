import asyncio
import random
from typing import Any

import httpx
from bs4 import BeautifulSoup

from scraper.database import init_db
from shared.logger import get_logger

logger = get_logger(__name__)

TFT_ITEMS_URL = "https://tactics.tools/items"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
]


def get_random_headers() -> dict[str, str]:
    return {"User-Agent": random.choice(USER_AGENTS)}


async def fetch_items() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    try:
        async with httpx.AsyncClient(timeout=30.0, headers=get_random_headers()) as client:
            await asyncio.sleep(random.uniform(2, 5))

            response = await client.get(TFT_ITEMS_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            item_elements = soup.select("[class*='item']")

            for elem in item_elements:
                name_elem = elem.select_one("[class*='name'], span")
                if not name_elem:
                    continue

                item: dict[str, Any] = {
                    "name": name_elem.get_text(strip=True),
                    "tier": "A",
                }
                items.append(item)

            logger.info("items_scraped", count=len(items))

    except httpx.HTTPError as e:
        logger.error("items_fetch_failed", error=str(e))
    except Exception as e:
        logger.error("items_parse_failed", error=str(e))

    return items


async def run_items_scraper(patch_number: str) -> None:
    logger.info("items_scraper_started", patch=patch_number)

    await init_db()

    items = await fetch_items()

    logger.info("items_scraper_completed", patch=patch_number, count=len(items))


if __name__ == "__main__":
    import asyncio

    from shared.logger import setup_logging

    setup_logging()
    asyncio.run(run_items_scraper("14.1"))
