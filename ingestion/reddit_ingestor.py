import time
import logging
from pathlib import Path

from ingestion.utils.storage import load_existing_data, save_data
from ingestion.utils.reddit_api import fetch_comments_safe, fetch_subreddit_page
from utils.logger import setup_logger

# -----------------------------------------------------------
# Logger setup
# -----------------------------------------------------------
logger = setup_logger("startupscout.reddit")
logger.info("Starting Reddit ingestion...")

# -----------------------------------------------------------
# Config
# -----------------------------------------------------------
SUBREDDITS = [
    "startups", "Entrepreneur", "IndieHackers",
    "EntrepreneurRideAlong", "SideProject", "SaaS",
    "Startup_Ideas", "SmallBusiness"
]

# Always resolve data path relative to project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "startupscout/data/raw/reddit_posts.json"

# Rate-limiting settings
FETCH_DELAY = 1.5
COOLDOWN_AFTER_SUB = 900  # 15 minutes between subreddits


# -----------------------------------------------------------
# Core logic
# -----------------------------------------------------------
def fetch_subreddit(subreddit: str, limit: int = 500, existing=None) -> dict:
    """
    Fetch posts from a subreddit and enrich them with comments.
    Automatically resumes existing data and prevents duplicates.
    """
    records = existing or {}
    seen_urls = set(records.keys())

    logger.info(f"Fetching subreddit: r/{subreddit} (target: {limit} posts)")

    enriched_count = 0
    # --- Enrich existing posts missing comments ---
    for url, record in list(records.items()):
        if record.get("source") == "reddit" and ("comments" not in record or not record["comments"]):
            try:
                post_id = record["url"].split("/comments/")[1].split("/")[0]
                record["comments"] = fetch_comments_safe(post_id)
                enriched_count += 1
            except Exception as e:
                logger.warning(f"Failed to enrich comments for {url}: {e}")
    if enriched_count:
        logger.info(f"{subreddit}: enriched {enriched_count} existing posts with comments.")

    # --- Fetch new posts ---
    fetched_new = 0
    while len(records) < limit:
        try:
            data = fetch_subreddit_page(subreddit)
            if not data:
                logger.warning(f"{subreddit}: empty response, stopping.")
                break

            # When using PRAW directly, fetch_subreddit_page returns list not JSON
            posts = data if isinstance(data, list) else data.get("data", {}).get("children", [])
            if not posts:
                logger.warning(f"{subreddit}: no posts found.")
                break

            for post in posts:
                p = post.get("data", {}) if isinstance(post, dict) and "data" in post else post
                text = (p.get("selftext") or "").strip()
                if len(text) < 100:
                    continue

                permalink = p.get("permalink", "")
                full_url = f"https://www.reddit.com{permalink}"
                if full_url in seen_urls:
                    continue  # skip duplicates

                post_id = p.get("id")
                comments = fetch_comments_safe(post_id)

                record = {
                    "title": p.get("title", "").strip(),
                    "source": "reddit",
                    "subreddit": subreddit,
                    "decision": text,
                    "url": full_url,
                    "tags": [subreddit],
                    "stage": "",
                    "score": p.get("score", 0),
                    "comments": comments,
                    "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                records[full_url] = record
                fetched_new += 1

                if fetched_new % 50 == 0:
                    logger.info(f"{subreddit}: fetched {fetched_new} new posts...")
                if fetched_new % 100 == 0:
                    save_data(records, DATA_PATH)
                    logger.info(f"{subreddit}: autosaved after {fetched_new} new posts.")

                time.sleep(FETCH_DELAY)

            logger.info(f"{subreddit}: total {len(records)} unique posts so far.")
            break  # stop after one batch

        except Exception as e:
            logger.error(f"Error fetching subreddit {subreddit}: {e}")
            time.sleep(60)
            break

    logger.info(f"{subreddit}: finished with {len(records)} total records.")
    return records


# -----------------------------------------------------------
# Orchestrator
# -----------------------------------------------------------
def scrape_all(subreddits=SUBREDDITS, total_limit=4000):
    """Fetch all target subreddits, merging new and existing data."""
    existing = load_existing_data(DATA_PATH)
    records = existing
    per_sub = total_limit // len(subreddits)

    logger.info(f"Loaded {len(existing)} existing records from {DATA_PATH}")

    for sub in subreddits:
        logger.info(f"--- Processing {sub} ---")
        records = fetch_subreddit(sub, limit=per_sub, existing=records)
        save_data(records, DATA_PATH)
        logger.info(f"Saved {len(records)} total records after {sub}.")
        logger.info(f"Cooling down for {COOLDOWN_AFTER_SUB // 60} minutes...")
        time.sleep(COOLDOWN_AFTER_SUB)

    logger.info("✅ Reddit scraping completed successfully.")
    return records


# -----------------------------------------------------------
# Entry point
# -----------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    scrape_all(total_limit=4000)
