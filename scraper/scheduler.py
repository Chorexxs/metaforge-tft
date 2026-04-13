from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from scraper.database import close_db, init_db
from scraper.patch_watcher import detect_patch_change
from shared.logger import get_logger, setup_logging
from shared.settings import get_settings

setup_logging()
logger = get_logger(__name__)
settings = get_settings()

scheduler = AsyncIOScheduler()


async def on_patch_detected(patch_number: str) -> None:
    logger.info("ingestion_triggered", patch=patch_number)
    from scraper.augments_scraper import run_augments_scraper
    from scraper.comps_scraper import run_comps_scraper
    from scraper.items_scraper import run_items_scraper

    try:
        await run_comps_scraper(patch_number)
        await run_items_scraper(patch_number)
        await run_augments_scraper(patch_number)
        logger.info("ingestion_completed", patch=patch_number)
    except Exception as e:
        logger.error("ingestion_failed", patch=patch_number, error=str(e))


async def check_for_updates() -> None:
    logger.debug("checking_for_patch_updates")
    result = await detect_patch_change()
    if result:
        patch_number, _ = result
        await on_patch_detected(patch_number)


async def start_scheduler() -> None:
    await init_db()

    interval_hours = settings.patch_check_interval_hours
    scheduler.add_job(
        check_for_updates,
        trigger=IntervalTrigger(hours=interval_hours),
        id="patch_checker",
        name="Check for TFT patch updates",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("scheduler_started", interval_hours=interval_hours)

    await check_for_updates()


async def stop_scheduler() -> None:
    scheduler.shutdown()
    await close_db()
    logger.info("scheduler_stopped")


if __name__ == "__main__":
    import asyncio

    asyncio.run(start_scheduler())
