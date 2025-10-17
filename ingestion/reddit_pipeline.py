import time
import logging
from ingestion.reddit_ingestor import scrape_all
from ingestion.enrich_comments import enrich_comments
from utils.logger import setup_logger

logger = setup_logger("startupscout.reddit_pipeline")

COOLDOWN_BETWEEN_STAGES = 900  # 15 minutes (adjust as needed)


def run_pipeline():
    """Run full Reddit ingestion → cooldown → comment enrichment."""
    logger.info("=== Starting Reddit data pipeline ===")

    try:
        logger.info("Stage 1: Ingestion — fetching new posts...")
        scrape_all(total_limit=4000)
    except Exception as e:
        logger.error("Ingestion failed: %s", e)
        return

    logger.info("Stage 1 complete. Cooling down for %d seconds...", COOLDOWN_BETWEEN_STAGES)
    time.sleep(COOLDOWN_BETWEEN_STAGES)

    try:
        logger.info("Stage 2: Enrichment — fetching missing comments...")
        enrich_comments()
    except Exception as e:
        logger.error("Enrichment failed: %s", e)
        return

    logger.info("Reddit pipeline completed successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    run_pipeline()
