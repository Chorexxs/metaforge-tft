from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address

from shared.insforge_client import InsForgeClient, get_insforge_client
from shared.logger import get_logger, setup_logging
from shared.settings import get_settings

setup_logging()
logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address)

insforge_client: InsForgeClient | None = None


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("websocket_connected", total=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("websocket_disconnected", total=len(self.active_connections))

    async def send_personal(self, message: dict[str, Any], websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error("websocket_send_error", error=str(e))

    async def broadcast(self, message: dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    global insforge_client

    settings = get_settings()
    logger.info("application_starting", host=settings.app__host, port=settings.app__port)

    insforge_client = await get_insforge_client()
    logger.info("insforge_client_initialized")

    yield

    if insforge_client:
        await insforge_client.close()
    logger.info("application_shutting_down")


app = FastAPI(
    title="TFT HUD API",
    description="TFT HUD - Asistente de Draft en Tiempo Real",
    version="0.1.0",
    lifespan=lifespan,
)

state_limiter = limiter.limit("100/minute")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def add_request_id(request: Request):
    request.state.request_id = f"req_{id(request)}"
    return request.state.request_id


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "TFT HUD API", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/api/ping")
async def ping() -> dict[str, bool]:
    return {"pong": True}


@app.get("/api/comps")
async def get_compositions(
    patch: str | None = None,
    tier: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    if not insforge_client:
        return {"data": [], "error": "not_initialized", "count": 0}

    result = await insforge_client.invoke_function(
        "get-compositions",
        {"patch": patch, "tier": tier, "limit": limit},
    )

    if "error" in result:
        logger.error("get_compositions_failed", error=result.get("error"))
        return {"data": [], "error": result.get("error"), "count": 0}

    return {"data": result.get("data", []), "count": len(result.get("data", []))}


@app.get("/api/comps/{comp_id}")
async def get_composition(comp_id: str) -> dict[str, Any]:
    if not insforge_client:
        return {"data": None, "error": "not_initialized"}

    result = await insforge_client.invoke_function(
        "get-composition",
        {"id": comp_id},
    )

    if "error" in result:
        return {"data": None, "error": result.get("error")}

    return {"data": result.get("data")}


@app.get("/api/patch/current")
async def get_current_patch() -> dict[str, Any]:
    if not insforge_client:
        return {"data": None, "error": "not_initialized"}

    result = await insforge_client.invoke_function("get-current-patch", {})

    if "error" in result:
        return {"data": None, "error": result.get("error")}

    return {"data": result.get("data")}


@app.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type", "unknown")
            logger.info("websocket_event", type=event_type, data=data)

            if event_type == "game_state":
                from backend.engine import detect_phase, get_action as get_phase_action

                game_state = data.get("data", {})
                phase = detect_phase(
                    round_=game_state.get("round", "1-1"),
                    level=game_state.get("level", 1),
                )
                action = get_phase_action(
                    phase=phase,
                    gold=game_state.get("gold", 0),
                    level=game_state.get("level", 1),
                    round_=game_state.get("round", "1-1"),
                )
                await manager.send_personal(
                    {
                        "type": "recommendation",
                        "phase": phase,
                        "action": action,
                    },
                    websocket,
                )

            elif event_type == "ping":
                await manager.send_personal({"type": "pong"}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("websocket_error", error=str(e))
        manager.disconnect(websocket)


from backend.engine import (
    detect_phase,
    get_action as get_phase_action,
    recommend_board_units,
    get_transition_options,
)
from backend.engine.item_optimizer import optimize_item_inventory


@app.post("/api/game/action")
async def get_game_action(game_state: dict[str, Any]) -> dict[str, Any]:
    phase = detect_phase(
        round_=game_state.get("round", "1-1"),
        level=game_state.get("level", 1),
    )
    action = get_phase_action(
        phase=phase,
        gold=game_state.get("gold", 0),
        level=game_state.get("level", 1),
        round_=game_state.get("round", "1-1"),
    )
    return {"phase": phase, "action": action}


@app.post("/api/game/transition")
async def get_transition(current_units: list[str]) -> dict[str, Any]:
    comps_result = await insforge_client.invoke_function(
        "get-compositions",
        {"limit": 10},
    )

    if "error" in comps_result:
        return {"options": [], "error": comps_result.get("error")}

    compositions = comps_result.get("data", [])
    options = get_transition_options(current_units, compositions)

    return {"options": options[:5]}


@app.post("/api/items/optimizer")
async def optimize_items(body: dict[str, Any]) -> dict[str, Any]:
    components = body.get("components", [])
    target_comp = body.get("target_comp", {})

    result = optimize_item_inventory(components, target_comp)

    return result


@app.get("/api/augments")
async def get_augments(
    stage: str | None = None,
    comp_id: str | None = None,
) -> dict[str, Any]:
    if stage not in ["2-1", "3-2", "4-2"]:
        return {"data": [], "error": "invalid_stage"}

    mock_augments = [
        {"name": "Jeweled Lotus", "tier": "prismatic"},
        {"name": "Money Mgr", "tier": "gold"},
        {"name": "First Strike", "tier": "silver"},
    ]

    return {"data": mock_augments, "count": len(mock_augments)}


from backend.riot.live_client import check_game_active, get_current_game_state
from backend.riot.models import GameState


@app.get("/api/game/is-active")
async def is_game_active() -> dict[str, bool]:
    active = await check_game_active()
    return {"active": active}


@app.get("/api/game/live-state")
async def get_live_state() -> dict[str, Any]:
    state = await get_current_game_state()

    if not state or not state.is_active:
        return {
            "active": False,
            "data": None,
            "error": "no_active_game",
        }

    return {
        "active": True,
        "data": {
            "round": state.round,
            "phase": state.phase,
            "gold": state.gold,
            "level": state.level,
            "xp": state.xp,
            "hp": state.hp,
            "max_hp": state.max_hp,
            "board_units": [
                {
                    "name": u.name,
                    "tier": u.tier,
                    "items": u.items,
                }
                for u in state.board_units
            ],
            "bench_units": [
                {
                    "name": u.name,
                    "tier": u.tier,
                    "items": u.items,
                }
                for u in state.bench_units
            ],
            "augments": state.augments,
            "win_streak": state.win_streak,
            "lose_streak": state.lose_streak,
        },
    }
