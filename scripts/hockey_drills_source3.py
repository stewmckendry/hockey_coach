import requests
from bs4 import BeautifulSoup
import time
import json
import csv
import os
from tqdm import tqdm
from pathlib import Path

BASE_URL = "https://weisstechhockey.com/hockeydrills/"
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = SCRIPT_DIR.parent / "source_data" / "source3_drills_raw.json"

HEADERS = {"User-Agent": "Mozilla/5.0"}
session = requests.Session()

def fetch_soup(url):
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"⚠️ Failed to fetch {url}: {e}")
        return None

def extract_drill_details(drill_url):
    soup = fetch_soup(drill_url)
    if not soup:
        return {}

    content_block = soup.find("div", class_="entry-content")
    if not content_block:
        return {}

    # Try to extract YouTube video
    iframe = content_block.find("iframe")
    video_url = iframe["src"] if iframe and "youtube" in iframe["src"] else ""

    # Extract instructions
    paragraphs = content_block.find_all("p")
    instructions = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    return {
        "video_url": video_url,
        "instructions": instructions
    }

def load_existing():
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, "r") as f:
            return json.load(f)
    return []

def save_output_json(drills):
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(drills, f, indent=2)

def scrape_all_drills():
    soup = fetch_soup(BASE_URL)
    if not soup:
        return []

    existing = load_existing()
    existing_urls = set(d['url'] for d in existing)
    drills = existing.copy()

    category_blocks = soup.find_all("li", class_="drill-category")

    for cat in category_blocks:
        cat_header = cat.find("h4", class_="drill-category-title")
        if not cat_header:
            continue
        category = cat_header.get_text(strip=True).replace(cat_header.find("span").text, "").strip()

        drill_items = cat.find_all("li", class_="drill-item")
        for item in tqdm(drill_items, desc=f"📦 {category[:40]}"):
            try:
                a_tag = item.find("a")
                drill_url = a_tag["href"]

                if drill_url in existing_urls:
                    continue  # Skip already scraped

                title = a_tag.find("h5").get_text(strip=True)
                excerpt = a_tag.find("p", class_="drill-post-excerpt").get_text(strip=True)
                image_tag = a_tag.find("img")
                image_url = image_tag["src"] if image_tag else ""

                detail = extract_drill_details(drill_url)
                drill = {
                    "title": title,
                    "url": drill_url,
                    "image_url": image_url,
                    "video_url": detail.get("video_url", ""),
                    "instructions": detail.get("instructions", excerpt),
                    "teaching_points": "",
                    "category": category,
                    "source": "weisstechhockey"
                }

                drills.append(drill)
                existing_urls.add(drill_url)
                save_output_json(drills)  # Incremental save
                print(f"💾 Saved drill: {title}")

                time.sleep(0.5)

            except Exception as e:
                print(f"⚠️ Error scraping drill: {e}")

    return drills

if __name__ == "__main__":
    print("🔍 Starting full scrape from WeissTechHockey with resume support...")
    all_drills = scrape_all_drills()
    if all_drills:
        print(f"\n✅ Scraped and saved {len(all_drills)} drills total.")
    else:
        print("⚠️ No drills scraped.")
