#!/usr/bin/env python3
"""Process Maple Leafs Hot Stove articles with LLM to extract coaching insights."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Set
from uuid import uuid4

from openai import OpenAI

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.mlhs_article import MLHSArticle
from models.nhl_insight import NHLInsight

client = OpenAI()
PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / "prompts" / "nhl_insight_extraction.txt"
)
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    INSIGHT_PROMPT = f.read()


# ---------------------------------------------------------------------------
# Utils
# ---------------------------------------------------------------------------


def _parse_json(content: str):
    try:
        if content.startswith("```json"):
            content = content.split("```json", 1)[1].split("```", 1)[0]
        return json.loads(content)
    except Exception:
        return None


def _load_json_if_exists(path: Path) -> list[dict]:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def load_articles(path: Path) -> List[MLHSArticle]:
    data = _load_json_if_exists(path)
    return [MLHSArticle(**d) for d in data]


def load_existing_insights(path: Path) -> tuple[List[NHLInsight], Set[str]]:
    raw = _load_json_if_exists(path)
    insights: List[NHLInsight] = []
    urls: Set[str] = set()
    for d in raw:
        try:
            obj = NHLInsight(**d)
            insights.append(obj)
            urls.add(str(obj.source_url))
        except Exception:
            continue
    return insights, urls


def extract_insights_llm(article: MLHSArticle) -> List[NHLInsight]:
    user = f"ARTICLE HTML:\n{article.html_content}"
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[
            {"role": "system", "content": INSIGHT_PROMPT},
            {"role": "user", "content": user},
        ],
    )
    data = _parse_json(resp.choices[0].message.content)
    if not data:
        return []
    if isinstance(data, dict):
        data = [data]
    insights: List[NHLInsight] = []
    for d in data:
        d.setdefault("id", str(uuid4()))
        d.setdefault("source_url", str(article.url))
        d.setdefault("source_article", article.title)
        d.setdefault("source_type", "MLHS")
        d.setdefault("published_date", str(article.published_date))
        d.setdefault("author", article.author)
        try:
            insights.append(NHLInsight(**d))
        except Exception:
            continue
    return insights


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Process MLHS articles for NHL insights"
    )
    parser.add_argument(
        "--input", type=Path, default=Path("data/raw/mlhs_articles.json")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data/processed/mlhs_insights.json")
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=0,
        help="Limit number of articles to process",
    )
    args = parser.parse_args()

    articles = load_articles(args.input)
    existing, processed_urls = load_existing_insights(args.output)
    print(
        f"✅ Loaded {len(articles)} articles; {len(existing)} insights already processed"
    )

    to_process = [a for a in articles if str(a.url) not in processed_urls]
    if args.max_articles:
        to_process = to_process[: args.max_articles]

    new_insights: List[NHLInsight] = []
    for art in to_process:
        print(f"✨ Processing: {art.title}")
        new_insights.extend(extract_insights_llm(art))

    all_insights = [i.model_dump() for i in existing + new_insights]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_insights, f, indent=2)

    print(
        f"✅ Wrote {len(new_insights)} new insights ({len(all_insights)} total) to {args.output}"
    )


if __name__ == "__main__":
    main()
