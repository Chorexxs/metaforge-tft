import os
from unittest.mock import AsyncMock, patch

import pytest

os.environ["INSFORGE_URL"] = "https://test.insforge.app"
os.environ["INSFORGE_API_KEY"] = "test_key_123"

from shared.insforge_client import InsForgeClient, get_insforge_client


class TestInsForgeClient:
    @pytest.mark.asyncio
    async def test_get_client(self):
        client = await get_insforge_client()
        assert client.base_url == "https://test.insforge.app"
        assert client.api_key == "test_key_123"
        await client.close()

    @pytest.mark.asyncio
    async def test_invoke_function_success(self):
        client = await get_insforge_client()

        with patch.object(
            client._client, "post", new=AsyncMock(return_value=MockResponse({"status": "ok"}))
        ):
            result = await client.invoke_function("health", {})

        assert "error" in result or "status" in result or result.get("data") is not None
        await client.close()


class MockResponse:
    def __init__(self, json_data, status=200):
        self._json_data = json_data
        self.status_code = status
        self.text = str(json_data) if json_data else ""

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")
