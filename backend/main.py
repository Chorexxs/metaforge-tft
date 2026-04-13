from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.logger import get_logger, setup_logging
from shared.settings import get_settings

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    settings = get_settings()
    logger.info("application_starting", host=settings.app__host, port=settings.app__port)
    yield
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
