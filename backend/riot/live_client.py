import asyncio
import time
from collections.abc import Callable

import httpx

from backend.ocr.screen_reader import get_screen_reader
from backend.riot.models import GameState, Unit
from shared.logger import get_logger
from shared.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()

LIVE_CLIENT_URL = settings.live_client__url
POLL_INTERVAL = settings.live_client__poll_interval_seconds

_ocr_reader = None


def _get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        try:
            _ocr_reader = get_screen_reader()
        except Exception as e:
            logger.warning("ocr_init_failed", error=str(e))
    return _ocr_reader


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
        ocr_gold = 0
        ocr_hp = 100
        ocr_level = 1

        try:
            ocr_reader = _get_ocr_reader()
            if ocr_reader:
                ocr_stats = ocr_reader.get_game_stats()
                ocr_gold = ocr_stats.get("gold", 0)
                ocr_hp = ocr_stats.get("hp", 100)
                ocr_level = ocr_stats.get("level", 1)
                logger.debug("ocr_stats", gold=ocr_gold, hp=ocr_hp, level=ocr_level)
        except Exception as e:
            logger.debug("ocr_fetch_skipped", error=str(e))

        try:
            response = self._client.get(f"{LIVE_CLIENT_URL}allgamedata")
            if response.status_code != 200:
                return GameState(is_active=False)

            data = response.json()

            game_data = data.get("gameData", {})
            player_data = game_data.get("player", {})
            active_player = data.get("activePlayer", {})

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

            api_level = active_player.get("level", ocr_level) if active_player else ocr_level
            if api_level == 1 and ocr_level > 1:
                api_level = ocr_level

            state = GameState(
                round=game_data.get("round", "1-1"),
                phase=game_data.get("phase", "planning"),
                stage=game_data.get("stage", 1),
                gold=ocr_gold if ocr_gold > 0 else player_data.get("gold", 0),
                level=api_level,
                xp=player_data.get("xp", 0),
                hp=ocr_hp if ocr_hp > 0 else player_data.get("hp", 100),
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
