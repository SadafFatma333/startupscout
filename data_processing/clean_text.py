import json
import re
import html
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger("startupscout.clean_text")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "startupscout/data/processed/startup_posts.json"
OUTPUT_PATH = PROJECT_ROOT / "startupscout/data/processed/startup_posts_clean.json"

MIN_TEXT_LENGTH = 200


def clean_text_field(text: str) -> str:
    """Clean text for NLP/RAG use — remove HTML, links, symbols."""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9.,!?;:'\"()\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_and_deduplicate():
    """Clean merged dataset and remove low-quality or duplicate entries."""
    logger.info("Starting text cleaning and deduplication...")

    try:
        data = json.load(open(INPUT_PATH))
        if isinstance(data, dict):
            data = list(data.values())
    except Exception as e:
        logger.error(f"Error loading {INPUT_PATH}: {e}")
        return

    logger.info(f"Loaded {len(data)} records for cleaning.")

    cleaned = []
    seen_hashes = set()

    for i, rec in enumerate(data, start=1):
        title = rec.get("title", "").strip().lower()
        text = clean_text_field(rec.get("text", ""))

        # Skip if too short
        if len(text) < MIN_TEXT_LENGTH:
            continue

        # Simple fast deduplication: hash(title + first 50 chars)
        content_hash = hash(title + text[:50])
        if content_hash in seen_hashes:
            continue
        seen_hashes.add(content_hash)

        rec["title"] = title
        rec["text"] = text
        rec["summary"] = clean_text_field(rec.get("summary", ""))
        rec["content"] = clean_text_field(rec.get("content", ""))
        if "meta" in rec:
            rec["meta"]["length"] = len(text)
        cleaned.append(rec)

        if i % 500 == 0:
            logger.info(f"Processed {i}/{len(data)} records...")

    logger.info(f"Cleaned {len(cleaned)} records remaining after filtering.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved cleaned dataset → {OUTPUT_PATH}")
    return cleaned


if __name__ == "__main__":
    clean_and_deduplicate()
