import json
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger("startupscout.merge_sources")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REDDIT_PATH = PROJECT_ROOT / "startupscout/data/raw/reddit_posts.json"
MEDIUM_PATH = PROJECT_ROOT / "startupscout/data/raw/medium_posts.json"
OUTPUT_PATH = PROJECT_ROOT / "startupscout/data/processed/startup_posts.json"


def load_json(path: Path):
    """Load JSON safely as list of dicts."""
    if not path.exists():
        logger.warning(f"{path} not found. Skipping.")
        return []
    try:
        with open(path, "r") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = list(data.values())
        return [r for r in data if isinstance(r, dict)]
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        return []


def normalize_record(record, source):
    """Normalize and unify fields across all content sources."""
    summary = record.get("summary", "")
    content = record.get("content", "")
    decision = record.get("decision", "")

    # canonical unified text field
    text = (
        decision
        or (content if len(content) > len(summary) else summary)
        or ""
    )

    comments = record.get("comments") if source == "reddit" else []

    return {
        "id": record.get("url", ""),
        "source": source,
        "title": record.get("title", "").strip(),
        "text": text.strip(),
        "summary": summary.strip(),
        "content": content.strip(),
        "tags": record.get("tags", []),
        "url": record.get("url", ""),
        "comments": comments,
        "score": record.get("score", 0),
        "fetched_at": record.get("fetched_at"),
        "meta": {
            "length": len(text.strip()),
            "source_type": "discussion" if source == "reddit" else "article",
        },
    }


def merge_sources():
    """Combine Medium and Reddit posts into one unified dataset."""
    reddit_data = load_json(REDDIT_PATH)
    medium_data = load_json(MEDIUM_PATH)

    logger.info(f"Loaded {len(reddit_data)} Reddit and {len(medium_data)} Medium posts.")

    merged = []
    for r in reddit_data:
        merged.append(normalize_record(r, "reddit"))
    for r in medium_data:
        merged.append(normalize_record(r, "medium"))

    # Deduplicate by URL
    unique = {rec["url"]: rec for rec in merged if rec.get("url")}
    merged_list = list(unique.values())

    logger.info(f"Merged {len(merged_list)} unique records total.")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(merged_list, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved merged dataset → {OUTPUT_PATH}")
    return merged_list


if __name__ == "__main__":
    merge_sources()
