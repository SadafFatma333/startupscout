from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Dict, List
from utils.env_loader import load_environment
from utils.logger import setup_logger
from data_processing.utils.llm_client import call_llm, extract_json_or_empty

# ============================================================
# Environment & logging
# ============================================================
PROJECT_ROOT = load_environment()
logger = setup_logger("startupscout.llm_enricher")

INPUT_PATH = PROJECT_ROOT / "data/processed/startup_posts_clean.json"
OUTPUT_PATH = PROJECT_ROOT / "data/processed/startup_posts_enriched.json"

# ============================================================
# Runtime controls
# ============================================================
MAX_RECORDS = 250             # per batch run
BATCH_SAVE_EVERY = 50         # save frequency
DELAY_SECONDS = 1.0           # per request delay
COOLDOWN_BETWEEN_RUNS = 600   # 10 minutes between runs
MIN_CHARS = 300               # skip very short posts
MAX_TOTAL_COST = 1.50         # safety budget (approx)
MODEL_COST_PER_1K = 0.00075   # gpt-4o-mini price per 1K tokens (input+output)
EST_TOKENS_PER_RECORD = 500   # conservative estimate

PROVIDER_PRIORITY = ("openai", "local")
OPENAI_MODEL = "gpt-4o-mini"
LOCAL_MODEL = "llama3:8b"
TEMPERATURE = 0.3

PROMPT_TEMPLATE = """You are labeling startup-related content.

Return STRICT JSON with keys:
- "tags": an array of 3–6 short, meaningful tags (lowercase, hyphen separated, no emojis)
- "summary": a concise 2–3 sentence summary

Text:
{content}
"""

# ============================================================
# Helpers
# ============================================================
def _load_json_list(path: Path) -> List[dict]:
    if not path.exists():
        return []
    data = json.load(open(path))
    if isinstance(data, dict):
        data = list(data.values())
    return [r for r in data if isinstance(r, dict)]

def _index_by_url(records: List[dict]) -> Dict[str, dict]:
    return {r.get("url", f"idx:{i}"): r for i, r in enumerate(records)}

def _needs_enrichment(rec: dict) -> bool:
    return not (rec.get("auto_tags") and rec.get("auto_summary"))

def _build_prompt(rec: dict) -> str:
    content = (rec.get("text") or "")[:4000].strip()
    return PROMPT_TEMPLATE.format(content=content)

def _estimate_cost(n_records: int) -> float:
    tokens = n_records * EST_TOKENS_PER_RECORD
    return (tokens / 1000) * MODEL_COST_PER_1K

# ============================================================
# Main enrichment
# ============================================================
def enrich_dataset():
    est_cost = _estimate_cost(MAX_RECORDS)
    logger.info(
        f"Starting LLM enrichment (OpenAI only). caps: {MAX_RECORDS} records, "
        f"${est_cost:.4f} est cost, min {MIN_CHARS} chars"
    )

    base = _load_json_list(INPUT_PATH)
    logger.info("Loaded %d cleaned records from %s", len(base), INPUT_PATH)

    existing_out = _load_json_list(OUTPUT_PATH)
    out_index = _index_by_url(existing_out)
    base_index = _index_by_url(base)

    to_process = []
    for url, rec in base_index.items():
        if not _needs_enrichment(rec):
            out_index[url] = rec
            continue
        text = (rec.get("text") or "").strip()
        if len(text) >= MIN_CHARS and url not in out_index:
            to_process.append(url)

    pending = [u for u in to_process if u not in out_index or not out_index[u].get("auto_summary")]
    logger.info("Will process up to %d records this run.", min(len(pending), MAX_RECORDS))

    processed = 0
    for url in pending[:MAX_RECORDS]:
        rec = base_index[url]
        prompt = _build_prompt(rec)

        try:
            response_text = call_llm(
                prompt,
                provider_priority=PROVIDER_PRIORITY,
                openai_model=OPENAI_MODEL,
                local_model=LOCAL_MODEL,
                temperature=TEMPERATURE,
            )
            parsed = extract_json_or_empty(response_text)
            rec["auto_tags"] = parsed.get("tags", [])
            rec["auto_summary"] = parsed.get("summary", "")
        except Exception as e:
            logger.warning("Enrichment failed for %s: %s", url, e)
            rec.setdefault("auto_tags", [])
            rec.setdefault("auto_summary", "")

        out_index[url] = rec
        processed += 1

        if processed % BATCH_SAVE_EVERY == 0:
            merged = list(out_index.values())
            OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            json.dump(merged, open(OUTPUT_PATH, "w"), indent=2, ensure_ascii=False)
            logger.info("Checkpoint saved: %d/%d complete.", processed, len(pending))

        time.sleep(DELAY_SECONDS)

    merged = list(out_index.values())
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    json.dump(merged, open(OUTPUT_PATH, "w"), indent=2, ensure_ascii=False)
    logger.info("Run complete. Processed=%d, Est tokens=%d, Est cost=$%.4f → %s",
                processed, processed * EST_TOKENS_PER_RECORD, est_cost, OUTPUT_PATH)
    logger.info("Cooling down for %d seconds before next run...", COOLDOWN_BETWEEN_RUNS)
    time.sleep(COOLDOWN_BETWEEN_RUNS)

# ============================================================
# Entry point
# ============================================================
if __name__ == "__main__":
    enrich_dataset()
