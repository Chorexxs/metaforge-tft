from typing import Any

import httpx
from pydantic import BaseModel

from shared.logger import get_logger
from shared.settings import get_settings

logger = get_logger(__name__)


def get_insforge_config():
    settings = get_settings()
    return {
        "url": settings.insforge__url,
        "api_key": settings.insforge__api_key,
    }


class Composition(BaseModel):
    id: str | None = None
    name: str
    patch_number: str
    tier: str
    winrate: float = 0.0
    top4rate: float = 0.0
    avg_placement: float = 8.0
    traits: list[str] = []
    units: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    game_count: int = 0


class PatchVersion(BaseModel):
    id: str | None = None
    number: str
    detected_at: str | None = None
    ingestion_status: str = "pending"


def get_api_key() -> str:
    settings = get_settings()
    api_key = settings.insforge__api_key
    if not api_key:
        logger.warning("insforge_api_key_empty")
    return api_key


def get_base_url() -> str:
    settings = get_settings()
    return settings.insforge__url


class InsForgeClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = base_url or get_base_url()
        self.api_key = api_key or get_api_key()
        self.functions_url = f"{self.base_url}/functions"
        self._client = httpx.AsyncClient(
            timeout=30.0,
        )

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def close(self) -> None:
        await self._client.aclose()

    async def invoke_function(
        self,
        slug: str,
        data: dict[str, Any] | None = None,
        method: str = "POST",
    ) -> dict[str, Any]:
        url = f"{self.functions_url}/{slug}"
        headers = self._get_headers()

        if not self.api_key:
            logger.error("insforge_api_key_missing", slug=slug)
            return {"error": "API key not configured"}

        if method == "GET":
            response = await self._client.get(url, headers=headers)
        else:
            response = await self._client.post(url, headers=headers, json=data or {})

        if response.status_code >= 400:
            logger.error(
                "function_invoke_error",
                slug=slug,
                status=response.status_code,
                text=response.text,
            )
            return {"error": response.text}

        try:
            return response.json()
        except Exception:
            return {"data": response.text}

    async def get_compositions(
        self,
        patch: str | None = None,
        tier: str | None = None,
        limit: int = 20,
    ) -> list[Composition]:
        data = {"patch": patch, "tier": tier, "limit": limit}
        result = await self.invoke_function("get-compositions", data)

        if "error" in result:
            logger.error("get_compositions_failed", error=result.get("error"))
            return []

        comps = result.get("data", [])
        return [Composition(**c) for c in comps]

    async def save_composition(self, comp: Composition) -> Composition:
        result = await self.invoke_function("save-composition", comp.model_dump())

        if "error" in result:
            logger.error("save_composition_failed", error=result.get("error"))
            return comp

        return Composition(**result.get("data", {}))

    async def get_current_patch(self) -> PatchVersion | None:
        result = await self.invoke_function("get-current-patch", {})

        if "error" in result or not result.get("data"):
            return None

        return PatchVersion(**result["data"])

    async def save_patch(self, number: str) -> PatchVersion:
        result = await self.invoke_function("save-patch", {"number": number})

        if "error" in result:
            logger.error("save_patch_failed", error=result.get("error"))
            return PatchVersion(number=number)

        return PatchVersion(**result.get("data", {}))


async def get_insforge_client() -> InsForgeClient:
    return InsForgeClient()


async def test_connection() -> bool:
    client = await get_insforge_client()
    try:
        result = await client.invoke_function("health", {})
        logger.info("insforge_connection_ok", result=result)
        return True
    except Exception as e:
        logger.error("insforge_connection_failed", error=str(e))
        return False
    finally:
        await client.close()
