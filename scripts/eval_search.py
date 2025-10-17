# scripts/eval_search.py
from __future__ import annotations

import argparse
import csv
import json
import time
from typing import List, Dict, Any
import requests


def _call(api_base: str, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{api_base.rstrip('/')}/{endpoint.lstrip('/')}"
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser(description="Evaluate /search relevance.")
    parser.add_argument("--api", default="http://127.0.0.1:8000", help="API base URL")
    parser.add_argument("--k", type=int, default=5, help="top-k results to fetch")
    parser.add_argument("--out", default="eval/search_eval.csv", help="CSV output path")
    parser.add_argument("--json", action="store_true", help="Also write JSON next to CSV")
    args = parser.parse_args()

    queries: List[str] = [
        "pricing pivot",
        "growth strategy for B2B SaaS",
        "bootstrap vs VC tradeoffs",
        "early user acquisition channels",
        "hiring first sales rep",
    ]

    rows = []
    json_dump = []
    for q in queries:
        try:
            payload = _call(args.api, "/search", {"q": q, "k": args.k})
            results = payload.get("results", [])
            for rank, item in enumerate(results, start=1):
                rows.append({
                    "query": q,
                    "rank": rank,
                    "title": item.get("title", ""),
                    "source": item.get("source", ""),
                    "score": item.get("score", ""),
                    "tags": ",".join(item.get("tags", [])) if isinstance(item.get("tags"), list) else item.get("tags", ""),
                    "stage": item.get("stage", ""),
                    "url": item.get("url", ""),
                })
            json_dump.append({"query": q, "results": results})
            time.sleep(0.2)
        except Exception as e:
            rows.append({"query": q, "rank": "", "title": f"ERROR: {e}", "source": "", "score": "", "tags": "", "stage": "", "url": ""})

    # write CSV
    fieldnames = ["query", "rank", "title", "source", "score", "tags", "stage", "url"]
    out_path = args.out
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    if args.json:
        jp = out_path.rsplit(".", 1)[0] + ".json"
        with open(jp, "w", encoding="utf-8") as jf:
            json.dump(json_dump, jf, ensure_ascii=False, indent=2)

    print(f"Wrote CSV → {out_path}")
    if args.json:
        print(f"Wrote JSON → {jp}")


if __name__ == "__main__":
    main()
