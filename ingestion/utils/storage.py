import json
import logging
from pathlib import Path

logger = logging.getLogger("startupscout.utils.storage")


def load_existing_data(path: str) -> dict:
    """Load previously fetched data from JSON into {url: record} dict."""
    p = Path(path)
    if not p.exists():
        return {}

    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} existing records from {path}")
        return {d["url"]: d for d in data}
    except Exception as e:
        logger.warning(f"Failed to load data from {path}: {e}")
        return {}


def save_data(data: dict, path: str):
    """Save dict of records back to JSON."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(list(data.values()), f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(data)} records → {path}")
