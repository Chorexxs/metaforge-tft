from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from shared.logger import get_logger
from shared.settings import get_settings

logger = get_logger(__name__)


class Base(DeclarativeBase):
    pass


class PatchVersionDB(Base):
    __tablename__ = "patch_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String(20), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ingestion_status: Mapped[str] = mapped_column(String(20), default="pending")

    def __repr__(self) -> str:
        return f"<PatchVersion {self.number}>"


class CompositionDB(Base):
    __tablename__ = "compositions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    patch_number: Mapped[str] = mapped_column(String(20), nullable=False)
    tier: Mapped[str] = mapped_column(String(1), nullable=False)
    winrate: Mapped[float] = mapped_column(nullable=False)
    top4rate: Mapped[float] = mapped_column(nullable=False)
    avg_placement: Mapped[float] = mapped_column(nullable=False)
    traits: Mapped[list[str]] = mapped_column(JSON, default=list)
    units: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    items: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    game_count: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<Composition {self.name} ({self.tier})>"


class ChampionDB(Base):
    __tablename__ = "champions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    traits: Mapped[list[str]] = mapped_column(JSON, default=list)


class ItemDB(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    image_path: Mapped[str] = mapped_column(String(200))


class AugmentDB(Base):
    __tablename__ = "augments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tier: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(String(500))


engine = None
async_session_maker: async_sessionmaker | None = None


async def init_db() -> None:
    global engine, async_session_maker

    settings = get_settings()
    engine = create_async_engine(settings.database__url, echo=False)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("database_initialized")


async def close_db() -> None:
    global engine

    if engine:
        await engine.dispose()
        logger.info("database_closed")


async def get_current_patch_from_db() -> str | None:
    if not async_session_maker:
        return None

    async with async_session_maker() as session:
        result = await session.execute(
            select(PatchVersionDB)
            .where(PatchVersionDB.ingestion_status == "completed")
            .order_by(PatchVersionDB.detected_at.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return row.number if row else None


async def save_patch_version(number: str, status: str = "pending") -> None:
    if not async_session_maker:
        return

    patch = PatchVersionDB(
        number=number,
        detected_at=datetime.utcnow(),
        ingestion_status=status,
    )

    async with async_session_maker() as session:
        session.add(patch)
        await session.commit()
        logger.info("patch_version_saved", number=number, status=status)


async def update_patch_status(number: str, status: str) -> None:
    if not async_session_maker:
        return

    async with async_session_maker() as session:
        result = await session.execute(
            select(PatchVersionDB).where(PatchVersionDB.number == number)
        )
        patch = result.scalar_one_or_none()
        if patch:
            patch.ingestion_status = status
            await session.commit()
            logger.info("patch_status_updated", number=number, status=status)


async def save_compositions(comps: list[dict[str, Any]], patch_number: str) -> None:
    if not async_session_maker:
        return

    async with async_session_maker() as session:
        for comp_data in comps:
            comp = CompositionDB(
                name=comp_data["name"],
                patch_number=patch_number,
                tier=comp_data.get("tier", "B"),
                winrate=comp_data.get("winrate", 0.0),
                top4rate=comp_data.get("top4rate", 0.0),
                avg_placement=comp_data.get("avg_placement", 8.0),
                traits=comp_data.get("traits", []),
                units=comp_data.get("units", []),
                items=comp_data.get("items", []),
                game_count=comp_data.get("game_count", 0),
            )
            session.add(comp)

        await session.commit()
        logger.info("compositions_saved", count=len(comps), patch=patch_number)
