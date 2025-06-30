from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import os
import traceback

CHROME_DRIVER_PATH = "/opt/homebrew/bin/chromedriver"
OUTPUT_CSV = "source_data_drills_all.csv"
OUTPUT_JSON = "source_data_drills_all.json"

options = Options()
# Show the browser (headless often fails)
# options.add_argument("--headless=new")
options.add_argument("--window-size=1200,800")

driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)

all_drills = []

from selenium.common.exceptions import NoSuchElementException

page = 1
while True:
    print(f"\n🔄 Scraping page {page}...")
    try:
        if page == 1:
            print("🌐 Loading initial Drill Hub page")
            driver.get("https://www.hockeycanada.ca/en-ca/hockey-programs/drill-hub")
            time.sleep(3)

        print("🧩 STEP 1: Load and scroll page")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        print("🧩 STEP 2: Wait for drills to load")
        WebDriverWait(driver, 20).until(
            lambda d: len(d.find_elements(By.CLASS_NAME, "drillTitle")) >= 1
        )

        print("savingscreenshot for debugging")
        driver.save_screenshot(f"page_{page}_debug.png")

        print("🧩 STEP 3: Locate drill blocks")
        drill_blocks = driver.find_elements(By.CLASS_NAME, "drillInner")
        print(f"✅ Found {len(drill_blocks)} drills on page {page}")

        titles_on_page = []
        added_on_page = 0

        for block in drill_blocks:
            try:
                print("🔍 Extracting title")
                title = block.find_element(By.CLASS_NAME, "drillTitle").text.strip()
                titles_on_page.append(title)

                if title in [d['title'] for d in all_drills]:
                    continue

                print("🔍 Extracting image")
                img = block.find_element(By.CLASS_NAME, "drillDataImage").get_attribute("src")

                try:
                    print("🔍 Extracting video")
                    video = block.find_element(By.CLASS_NAME, "videoLink").get_attribute("href")
                except:
                    video = None

                try:
                    print("🔍 Extracting description")
                    desc_html = block.find_element(By.CLASS_NAME, "drillDescription").get_attribute("innerHTML")
                    soup = BeautifulSoup(desc_html, "html.parser")
                    uls = soup.find_all("ul")
                    instructions = "; ".join(li.get_text(strip=True) for li in uls[0].find_all("li")) if len(uls) > 0 else ""
                    teaching = "; ".join(li.get_text(strip=True) for li in uls[1].find_all("li")) if len(uls) > 1 else ""
                except Exception as e:
                    print("⚠️ Description parsing error:", e)
                    instructions = ""
                    teaching = ""

                all_drills.append({
                    "title": title,
                    "image_url": img,
                    "video_url": video,
                    "instructions": instructions,
                    "teaching_points": teaching
                })
                added_on_page += 1

            except Exception as e:
                print(f"⚠️ Drill block error: {e}")
                traceback.print_exc()

        print(f"➕ Added {added_on_page} drills (total: {len(all_drills)})")

        df = pd.DataFrame(all_drills)
        df.to_csv(OUTPUT_CSV, index=False)
        with open(OUTPUT_JSON, "w") as f:
            json.dump(all_drills, f, indent=2)

        print(f"💾 Saved after page {page} — total drills: {len(all_drills)}")

        print("🧩 STEP 4: Check for 'Next' button")
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "li.Next")
            if "Disabled" in next_button.get_attribute("class"):
                print("🏁 Last page reached. Stopping.")
                break
            else:
                print("➡️ Clicking 'Next'")
                driver.execute_script("arguments[0].click();", next_button)
                page += 1
                time.sleep(2)
        except NoSuchElementException:
            print("⚠️ No 'Next' button found at all. Stopping.")
            break
        except Exception as e:
            print(f"❌ Error clicking 'Next': {e}")
            break

    except Exception as e:
        print(f"❌ Failed on page {page}: {e}")
        traceback.print_exc()
        break

driver.quit()
print("\n✅ DONE! All drills saved.")
