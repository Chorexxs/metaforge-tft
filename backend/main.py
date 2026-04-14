from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.insforge_client import InsForgeClient, get_insforge_client
from shared.logger import get_logger, setup_logging
from shared.settings import get_settings

setup_logging()
logger = get_logger(__name__)
insforge_client: InsForgeClient | None = None


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
