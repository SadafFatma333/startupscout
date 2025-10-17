import time
import random
import feedparser
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from utils.logger import setup_logger
from utils.env_loader import load_environment
from ingestion.utils.storage import load_existing_data, save_data

logger = setup_logger("startupscout.medium_ingestor")

# Config
PROJECT_ROOT = load_environment()
DATA_PATH = PROJECT_ROOT / "startupscout/data/raw/medium_posts.json"

TAGS = [
    "startup", "entrepreneurship", "founder", "saas", "product-management",
    "fundraising", "bootstrapping", "growth", "marketing", "business",
    "startup-lessons", "lean-startup", "founder-stories", "product-launch",
    "side-projects", "business-ideas", "venture-capital", "startups-101",
    "tech-startups", "minimum-viable-product"
]

MAX_FULLTEXT_PER_RUN = 100
FULLTEXT_DELAY_RANGE = (3, 5)  # seconds between requests


def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.extract()
    return " ".join(soup.get_text(separator=" ").split())


def fetch_full_text(url):
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            return clean_html(resp.text)
        else:
            logger.warning(f"Failed {url} status={resp.status_code}")
            return ""
    except Exception as e:
        logger.warning(f"Error fetching {url}: {e}")
        return ""


def ingest_medium():
    logger.info("Starting Medium RSS ingestion...")
    existing = load_existing_data(DATA_PATH)
    seen_urls = set(existing.keys())
    new_records = 0
    fulltext_fetched = 0

    for tag in TAGS:
        feed_url = f"https://medium.com/feed/tag/{tag}"
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            logger.warning(f"No entries found for tag={tag}")
            continue

        for entry in feed.entries:
            url = entry.link
            if url in seen_urls:
                continue

            record = {
                "title": entry.title,
                "author": getattr(entry, "author", ""),
                "url": url,
                "published": getattr(entry, "published", ""),
                "summary": clean_html(getattr(entry, "summary", "")),
                "tags": [tag],
                "content": "",
                "source": "medium",
                "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Fetch limited number of full texts per run
            if fulltext_fetched < MAX_FULLTEXT_PER_RUN:
                record["content"] = fetch_full_text(url)
                fulltext_fetched += 1
                time.sleep(random.uniform(*FULLTEXT_DELAY_RANGE))

            existing[url] = record
            new_records += 1

        logger.info(f"Fetched {len(feed.entries)} entries for tag={tag}.")
        time.sleep(random.uniform(1, 2))  # light pause between feeds

    save_data(existing, DATA_PATH)
    logger.info(
        f"Completed Medium ingestion. Added {new_records} posts "
        f"({fulltext_fetched} with full text)."
    )
