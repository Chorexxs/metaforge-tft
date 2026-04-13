import hashlib
import json
from pathlib import Path

import httpx

from shared.logger import get_logger
from shared.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()

DATA_DRAGON_BASE = "https://ddragon.leagueoflegends.com/cdn"
CACHE_DIR = Path(".cache/ddragon")


async def get_version_from_ddragon() -> str | None:
    versions_url = f"{DATA_DRAGON_BASE}/versions.json"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(versions_url)
            response.raise_for_status()
            versions = response.json()
            return versions.get("v")
    except httpx.HTTPError as e:
        logger.error("ddragon_version_fetch_failed", error=str(e))
        return None


def get_asset_url(asset_type: str, version: str, filename: str) -> str:
    return f"{DATA_DRAGON_BASE}/{version}/data/{asset_type}/{filename}"


async def download_champion_data(version: str) -> dict | None:
    url = get_asset_url("en_US", version, "champion.json")
    cache_file = CACHE_DIR / f"champion_{version}.json"

    if cache_file.exists():
        logger.info("champion_data_cache_hit", version=version)
        with open(cache_file) as f:
            return json.load(f)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with open(cache_file, "w") as f:
                json.dump(data, f)

            logger.info("champion_data_downloaded", version=version)
            return data

    except httpx.HTTPError as e:
        logger.error("champion_data_download_failed", error=str(e))
        return None


async def download_item_data(version: str) -> dict | None:
    url = get_asset_url("en_US", version, "item.json")
    cache_file = CACHE_DIR / f"item_{version}.json"

    if cache_file.exists():
        logger.info("item_data_cache_hit", version=version)
        with open(cache_file) as f:
            return json.load(f)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with open(cache_file, "w") as f:
                json.dump(data, f)

            logger.info("item_data_downloaded", version=version)
            return data

    except httpx.HTTPError as e:
        logger.error("item_data_download_failed", error=str(e))
        return None


async def download_set_data(set_version: int) -> dict | None:
    version = await get_version_from_ddragon()
    if not version:
        return None

    url = f"{DATA_DRAGON_BASE}/{version}/data/en_US/tft{set_version}.json"
    cache_file = CACHE_DIR / f"tft{set_version}_{version}.json"

    if cache_file.exists():
        logger.info("tft_set_data_cache_hit", set=set_version, version=version)
        with open(cache_file) as f:
            return json.load(f)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with open(cache_file, "w") as f:
                json.dump(data, f)

            logger.info("tft_set_data_downloaded", set=set_version, version=version)
            return data

    except httpx.HTTPError as e:
        logger.error("tft_set_data_download_failed", error=str(e))
        return None


def compute_file_hash(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
