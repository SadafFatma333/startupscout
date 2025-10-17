import time
import random
from pathlib import Path

from ingestion.utils.storage import load_existing_data, save_data
from ingestion.utils.reddit_api import fetch_comments_safe
from utils.env_loader import load_environment
from utils.logger import setup_logger

logger = setup_logger("startupscout.reddit_enricher")

PROJECT_ROOT = load_environment()
DATA_PATH = PROJECT_ROOT / "startupscout/data/raw/reddit_posts.json"

MAX_TO_ENRICH = 200
SAVE_EVERY = 20
DELAY_RANGE = (1.5, 2.5)


def is_missing_comments(record: dict) -> bool:
    """Return True if a record has no comments or an empty list."""
    if "comments" not in record:
        return True
    comments = record["comments"]
    if comments is None:
        return True
    if isinstance(comments, list) and len(comments) == 0:
        return True
    return False


def is_reddit_record(record: dict) -> bool:
    """Return True if the record is a Reddit post."""
    src = record.get("source", "")
    url = record.get("url", "")
    sub = record.get("subreddit", "")
    # Accept common shapes: source like 'r/startups', presence of subreddit,
    # or a reddit.com URL. Do NOT require source == 'reddit'.
    return (
        (isinstance(src, str) and src.startswith("r/")) or
        (isinstance(sub, str) and len(sub) > 0) or
        ("reddit.com" in url)
    )


def enrich_comments():
    """Fetch and add comments for Reddit posts missing them."""
    data = load_existing_data(DATA_PATH)
    logger.info("Loaded %d posts from %s", len(data), DATA_PATH)

    # Normalize container to a dict keyed by URL (the rest of the pipeline expects that)
    if isinstance(data, list):
        data = {rec["url"]: rec for rec in data if "url" in rec}
        logger.info("Converted list dataset to dict keyed by URL (%d keys).", len(data))
    elif not isinstance(data, dict):
        logger.error("Unexpected data type: %s", type(data))
        return

    # Identify reddit posts with missing/empty comments
    targets = [
        (url, rec)
        for url, rec in data.items()
        if is_reddit_record(rec) and is_missing_comments(rec)
    ]

    logger.info("Posts missing comments detected: %d", len(targets))

    if not targets:
        logger.info("All posts already have comments. Nothing to enrich.")
        return

    logger.info(
        "Found %d posts missing comments. Targeting first %d.",
        len(targets),
        MAX_TO_ENRICH,
    )

    enriched = 0
    for url, rec in targets[:MAX_TO_ENRICH]:
        try:
            # Robust post_id extraction; supports urls with trailing slash or extra segments
            parts = rec["url"].split("/comments/")
            if len(parts) < 2:
                logger.warning("Could not parse post id from url: %s", url)
                continue
            post_id = parts[1].split("/")[0].strip()

            rec["comments"] = fetch_comments_safe(post_id)
            data[url] = rec
            enriched += 1

            if enriched % SAVE_EVERY == 0:
                save_data(data, DATA_PATH)
                logger.info("Checkpoint: %d/%d enriched.", enriched, MAX_TO_ENRICH)

            time.sleep(random.uniform(*DELAY_RANGE))

        except Exception as e:
            logger.warning("Failed to fetch comments for %s: %s", url, e)
            time.sleep(5)

    save_data(data, DATA_PATH)
    logger.info("Enrichment complete. Added comments to %d posts.", enriched)


if __name__ == "__main__":
    logger.info("Starting Reddit comments enrichment job...")
    enrich_comments()
