import re
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from shared.logger import get_logger
from shared.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()

RIOT_PATCH_NOTES_URL = "https://www.leagueoflegends.com/en-us/news/tags/patch-notes/"


def extract_patch_number(text: str) -> str | None:
    match = re.search(r"14\.\d+", text)
    return match.group(0) if match else None


async def check_for_new_patch(current_patch: str | None = None) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(RIOT_PATCH_NOTES_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")

            title = soup.find("h1")
            if title:
                patch_number = extract_patch_number(title.get_text())
                if patch_number and patch_number != current_patch:
                    logger.info("new_patch_detected", patch=patch_number)
                    return patch_number

            logger.info("no_new_patch", current=current_patch)
            return None

    except httpx.HTTPError as e:
        logger.error("patch_check_failed", error=str(e))
        return None


async def get_latest_patch_from_web() -> str | None:
    return await check_for_new_patch()


async def detect_patch_change() -> tuple[str, datetime] | None:
    from scraper.database import get_current_patch_from_db

    stored_patch = await get_current_patch_from_db()
    latest_patch = await get_latest_patch_from_web()

    if latest_patch and latest_patch != stored_patch:
        return (latest_patch, datetime.utcnow())

    return None
