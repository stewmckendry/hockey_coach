import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
import json
import time
from tqdm import tqdm

BASE_URL = "https://www.icehockeysystems.com"
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = SCRIPT_DIR.parent / "source_data" / "source2_drills_raw.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def extract_text_list(section_soup):
    if not section_soup:
        return []
    return [li.get_text(strip=True) for li in section_soup.find_all("li")]

def find_section(soup, *keywords):
    for heading in soup.find_all("h2"):
        heading_text = heading.get_text(strip=True).lower()
        if any(kw.lower() in heading_text for kw in keywords):
            return heading.find_next("ul")
    return None

def find_main_image(soup):
    for img in soup.find_all("img", class_="img-responsive"):
        src = img.get("src", "")
        if "drill-maker" in src:
            return src
    return None

def scrape_drill_detail(drill_url):
    res = requests.get(drill_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    title = soup.select_one("h1.title").text.strip()
    video_url = soup.select_one(".vimeoURL")
    video_url = video_url.text.strip() if video_url else None

    image_url = find_main_image(soup)
    author_tag = soup.select_one(".author-display-name a")
    author = author_tag.text.strip() if author_tag else "IHS"

    summary = soup.find("p")
    summary_text = summary.get_text(strip=True) if summary else ""

    return {
        "title": title,
        "video_url": video_url,
        "image_url": image_url,
        "author": author,
        "summary": summary_text,
        "setup": extract_text_list(find_section(soup, "Setup")),
        "coaching_points": extract_text_list(find_section(soup, "Coaching Points")),
        "variations": extract_text_list(find_section(soup, "Variations", "Progressions")),
    }

def scrape_all_pages(max_pages=50):
    all_drills = []

    for page_num in range(max_pages):
        print(f"\n🔄 Scraping page {page_num + 1}/{max_pages}")
        listing_url = f"{BASE_URL}/hockey-drills?page={page_num}"
        res = requests.get(listing_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")
        drill_blocks = soup.select("div.views-row")

        for block in tqdm(drill_blocks, desc=f"Page {page_num + 1}", leave=False):
            if block.select_one(".members-only-overlay"):
                continue

            link_tag = block.select_one(".teaser-title a")
            if not link_tag:
                continue

            title = link_tag.text.strip()
            drill_url = urljoin(BASE_URL, link_tag["href"])

            tags = block.select_one(".type")
            tag_text = tags.get_text(strip=True) if tags else ""
            tag_list = [t.strip() for t in tag_text.split(",") if t.strip()]

            try:
                print(f"🔗 Fetching: {title}")
                detail = scrape_drill_detail(drill_url)
                detail.update({
                    "tags": tag_list,
                    "source": "IHS",
                    "members_only": False
                })
                all_drills.append(detail)
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Error on '{title}': {e}")
                continue

    return all_drills

if __name__ == "__main__":
    drills = scrape_all_pages()
    print(f"\n✅ Scraped {len(drills)} free drills total")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(drills, f, indent=2)

    print(f"💾 Saved to {OUTPUT_PATH}")
