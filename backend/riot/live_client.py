import asyncio
import time
from collections.abc import Callable

import httpx

from backend.riot.models import GameState, Unit
from shared.logger import get_logger
from shared.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()

LIVE_CLIENT_URL = settings.live_client__url
POLL_INTERVAL = settings.live_client__poll_interval_seconds


class LiveClient:
    def __init__(self):
        self._client = httpx.Client(
            verify=False,
            timeout=5.0,
        )
        self._last_state: GameState | None = None

    def close(self) -> None:
        self._client.close()

    def is_active(self) -> bool:
        try:
            logger.debug("riot_api_check", url=f"{LIVE_CLIENT_URL}allgamedata")
            response = self._client.get(f"{LIVE_CLIENT_URL}allgamedata")
            logger.debug("riot_api_response", status=response.status_code)
            return response.status_code == 200
        except Exception as e:
            logger.warning("riot_api_error", error=str(e))
            return False

    def fetch_state(self) -> GameState | None:
        try:
            response = self._client.get(f"{LIVE_CLIENT_URL}allgamedata")
            if response.status_code != 200:
                return GameState(is_active=False)

            data = response.json()

            game_data = data.get("gameData", {})
            player_data = game_data.get("player", {})

            board = []
            for u in player_data.get("boardUnits", []):
                raw_items = u.get("items", [])
                if isinstance(raw_items, list):
                    items = [i.get("item_id") if isinstance(i, dict) else str(i) for i in raw_items]
                else:
                    items = []
                unit = Unit(
                    name=u.get("character_name", "Unknown"),
                    level=u.get("tier", 1),
                    tier=u.get("star", 1),
                    items=items,
                )
                board.append(unit)

            bench = []
            for u in player_data.get("benchUnits", []):
                raw_items = u.get("items", [])
                if isinstance(raw_items, list):
                    items = [i.get("item_id") if isinstance(i, dict) else str(i) for i in raw_items]
                else:
                    items = []
                unit = Unit(
                    name=u.get("character_name", "Unknown"),
                    level=u.get("tier", 1),
                    tier=u.get("star", 1),
                    items=items,
                )
                bench.append(unit)

            state = GameState(
                round=game_data.get("round", "1-1"),
                phase=game_data.get("phase", "planning"),
                stage=game_data.get("stage", 1),
                gold=player_data.get("gold", 0),
                level=player_data.get("level", 1),
                xp=player_data.get("xp", 0),
                hp=player_data.get("hp", 100),
                max_hp=player_data.get("max_hp", 100),
                board_units=board,
                bench_units=bench,
                bench_items=player_data.get("itemNames", []),
                augments=player_data.get("augments", []),
                win_streak=player_data.get("win_streak", 0),
                lose_streak=player_data.get("lose_streak", 0),
                is_active=True,
            )

            self._last_state = state
            return state

        except httpx.HTTPStatusError as e:
            logger.warning("riot_api_unavailable", status=e.response.status_code)
            return GameState(is_active=False)
        except Exception as e:
            logger.error("riot_fetch_error", error=str(e))
            return GameState(is_active=False)

    def watch(
        self,
        callback: Callable[..., None],
        stop_event: asyncio.Event | None = None,
    ) -> None:
        logger.info("riot_watch_started")

        while True:
            if stop_event and stop_event.is_set():
                break

            state = self.fetch_state()
            callback(state)

            time.sleep(POLL_INTERVAL)

    def get_last_state(self) -> GameState | None:
        return self._last_state


def get_live_client() -> LiveClient:
    return LiveClient()


def check_game_active() -> bool:
    client = get_live_client()
    try:
        active = client.is_active()
        return active
    finally:
        client.close()


def get_current_game_state() -> GameState | None:
    client = get_live_client()
    try:
        return client.fetch_state()
    finally:
        client.close()
