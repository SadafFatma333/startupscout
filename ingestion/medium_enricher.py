import time
import random
import requests
from bs4 import BeautifulSoup
from pathlib import Path

from utils.env_loader import load_environment
from utils.logger import setup_logger
from ingestion.utils.storage import load_existing_data, save_data

logger = setup_logger("startupscout.medium_enricher")

PROJECT_ROOT = load_environment()
DATA_PATH = PROJECT_ROOT / "startupscout/data/raw/medium_posts.json"

MAX_ENRICH_PER_RUN = 50
ENRICH_DELAY_RANGE = (3, 6)


def clean_html(raw_html: str) -> str:
    """Remove scripts/styles and normalize whitespace."""
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.extract()
    return " ".join(soup.get_text(separator=" ").split())


def fetch_full_text(url: str) -> str:
    """Fetch and clean full article text from a Medium URL."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            return clean_html(resp.text)
        logger.warning(f"Failed {url} status={resp.status_code}")
        return ""
    except Exception as e:
        logger.warning(f"Error fetching {url}: {e}")
        return ""


def enrich_medium():
    """Enrich Medium posts missing full text content."""
    logger.info("Starting Medium enrichment job...")

    data = load_existing_data(DATA_PATH)
    if isinstance(data, list):
        data = {rec["url"]: rec for rec in data if "url" in rec}

    records = list(data.values())

    to_enrich = [
        r for r in records
        if r.get("source") == "medium"
        and (
            not r.get("content")
            or len(r["content"]) < 1000
            or r["content"].strip() == r.get("summary", "").strip()
        )
    ]

    if not to_enrich:
        logger.info("All posts already have sufficient content. Nothing to enrich.")
        return

    logger.info(f"Found {len(to_enrich)} posts missing content. Targeting first {MAX_ENRICH_PER_RUN}.")
    enriched = 0

    for rec in to_enrich[:MAX_ENRICH_PER_RUN]:
        url = rec["url"]
        rec["content"] = fetch_full_text(url)
        enriched += 1

        if enriched % 10 == 0:
            save_data({r["url"]: r for r in records if "url" in r}, DATA_PATH)
            logger.info(f"Saved checkpoint at {enriched}/{MAX_ENRICH_PER_RUN}.")

        time.sleep(random.uniform(*ENRICH_DELAY_RANGE))

    save_data({r["url"]: r for r in records if "url" in r}, DATA_PATH)
    logger.info(f"Enrichment complete. Added full text to {enriched} posts.")


if __name__ == "__main__":
    enrich_medium()
