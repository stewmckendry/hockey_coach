#!/usr/bin/env python3
"""Crawl Maple Leafs Hot Stove and collect raw article HTML."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Set

import requests
from bs4 import BeautifulSoup

# Add repo root to PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.mlhs_article import MLHSArticle

BASE_URL = "https://mapleleafshotstove.com/leafs-news/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"
}


def _load_json_if_exists(path: Path) -> list[dict]:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def fetch_page(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


def parse_tiles(soup: BeautifulSoup) -> List[dict]:
    tiles: List[dict] = []
    for div in soup.select("div.td_module_2.td_module_wrap"):
        title_el = div.select_one("h3.entry-title.td-module-title a")
        if not title_el:
            continue
        url = title_el.get("href")
        title = title_el.get_text(strip=True)
        author_el = div.select_one("span.td-post-author-name")
        date_el = div.select_one("span.td-post-date")
        cat_el = div.select_one("a.td-post-category")
        excerpt_el = div.select_one("div.td-excerpt")
        author = author_el.get_text(strip=True) if author_el else None
        if author and author.endswith("-"):
            author = author[:-1].strip()
        tiles.append(
            {
                "title": title,
                "url": url,
                "author": author,
                "published_date": date_el.get_text(strip=True) if date_el else None,
                "category": cat_el.get_text(strip=True) if cat_el else None,
                "excerpt": excerpt_el.get_text(strip=True) if excerpt_el else None,
            }
        )
    return tiles


def fetch_article_html(url: str) -> str:
    soup = fetch_page(url)
    content_div = soup.select_one("div.td-post-content")
    return str(content_div) if content_div else ""


def crawl(num_pages: int, existing_urls: Set[str]) -> List[MLHSArticle]:
    articles: List[MLHSArticle] = []
    for page in range(1, num_pages + 1):
        page_url = BASE_URL if page == 1 else f"{BASE_URL}page/{page}/"
        print(f"🌐 Fetching {page_url}")
        soup = fetch_page(page_url)
        tiles = parse_tiles(soup)
        print(f"📝 Found {len(tiles)} articles on page {page}")
        for t in tiles:
            if t["url"] in existing_urls:
                print(f"⏭️ Skipping already fetched {t['url']}")
                continue
            html = fetch_article_html(t["url"])
            try:
                date_obj = (
                    datetime.strptime(t["published_date"], "%B %d, %Y").date()
                    if t.get("published_date")
                    else datetime.today().date()
                )
            except Exception:
                date_obj = datetime.today().date()
            author = t.get("author")
            if author and author.endswith("-"):
                author = author[:-1].strip()
            article = MLHSArticle(
                title=t["title"],
                url=t["url"],
                author=author,
                published_date=date_obj,
                category=t.get("category"),
                excerpt=t.get("excerpt"),
                html_content=html,
                page_number=page,
            )
            articles.append(article)
            existing_urls.add(t["url"])
    return articles


def write_output(articles: List[MLHSArticle], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = [json.loads(a.model_dump_json()) for a in articles]
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract Maple Leafs Hot Stove articles"
    )
    parser.add_argument(
        "--num-pages", type=int, default=1, help="Number of pages to crawl"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/raw/mlhs_articles.json"),
        help="Output JSON path",
    )
    args = parser.parse_args()

    existing_data = _load_json_if_exists(args.output)
    existing_urls = {a.get("url") for a in existing_data}
    articles = [MLHSArticle(**a) for a in existing_data]

    new_articles = crawl(args.num_pages, existing_urls)
    articles.extend(new_articles)
    write_output(articles, args.output)
    print(
        f"✅ Saved {len(new_articles)} new articles ({len(articles)} total) to {args.output}"
    )


if __name__ == "__main__":
    main()
