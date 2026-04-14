import os
from typing import Any

import pytest

os.environ["INSFORGE_URL"] = "https://test.insforge.app"
os.environ["INSFORGE_API_KEY"] = "test_key_123"


@pytest.fixture
def sample_composition() -> dict[str, Any]:
    return {
        "name": "Test Comp",
        "patch_number": "14.1",
        "tier": "S",
        "winrate": 52.5,
        "top4rate": 78.0,
        "avg_placement": 3.8,
        "traits": ["Hellfire", "Enforcer"],
        "units": [
            {"name": "Jinx", "role": "carry", "priority": "core"},
            {"name": "Twitch", "role": "flex", "priority": "optional"},
        ],
        "items": [],
        "game_count": 1500,
    }


@pytest.fixture
def sample_patch_version() -> dict[str, Any]:
    return {
        "number": "14.1",
        "detected_at": "2026-01-01T00:00:00Z",
        "ingestion_status": "completed",
    }


@pytest.fixture
def sample_game_state() -> dict[str, Any]:
    return {
        "round": "2-1",
        "gold": 50,
        "level": 4,
        "xp": 0,
        "hp": 100,
        "win_streak": 2,
        "lose_streak": 0,
        "board_units": ["Kayle", "Lux"],
        "bench_units": ["Twitch", "Jinx"],
        "bench_items": [],
        "augments": [],
    }


@pytest.fixture
def mock_insforge_response() -> dict[str, Any]:
    return {"data": [{"id": "123", "name": "Test Comp"}], "count": 1}
