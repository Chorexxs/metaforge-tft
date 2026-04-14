from typing import Any

import httpx
from pydantic import BaseModel

from shared.logger import get_logger

logger = get_logger(__name__)

INSFORGE_CONFIG = {
    "url": "https://36b6whsc.eu-central.insforge.app",
    "api_key": "ik_a6b927fccf5a123ec0a4f0b5b2ccebe9",
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


class InsForgeClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = base_url or INSFORGE_CONFIG["url"]
        self.api_key = api_key or INSFORGE_CONFIG["api_key"]
        self.functions_url = f"{self.base_url}/functions"
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def invoke_function(
        self,
        slug: str,
        data: dict[str, Any] | None = None,
        method: str = "POST",
    ) -> dict[str, Any]:
        url = f"{self.functions_url}/{slug}"

        if method == "GET":
            response = await self._client.get(url)
        else:
            response = await self._client.post(url, json=data or {})

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
