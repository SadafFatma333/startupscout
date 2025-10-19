import time
import logging
from ingestion.medium_ingestor import ingest_medium
from ingestion.medium_enricher import enrich_medium
from utils.logger import setup_logger

logger = setup_logger("startupscout.medium_pipeline")
COOLDOWN_BETWEEN_STAGES = 600  # 10 minutes


def run_pipeline():
    logger.info("=== Starting Medium pipeline ===")

    try:
        ingest_medium()
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return

    logger.info(f"Cooldown for {COOLDOWN_BETWEEN_STAGES // 60} minutes before enrichment...")
    time.sleep(COOLDOWN_BETWEEN_STAGES)

    try:
        enrich_medium()
    except Exception as e:
        logger.error(f"Enrichment failed: {e}")
        return

    logger.info("Medium pipeline completed successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    run_pipeline()
