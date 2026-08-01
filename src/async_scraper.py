import os
import re
import json
import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
from src.db import upsert_section, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "raw", "bdlaws"))
PROCESSED_JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "processed", "sections.json"))
BDLAWS_BASE_URL = "http://bdlaws.minlaw.gov.bd"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

class ProductionAsyncScraper:
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.scraped_sections = []
        os.makedirs(BASE_RAW_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(PROCESSED_JSON_PATH), exist_ok=True)

    async def fetch_page(self, session, url: str) -> str:
        async with self.semaphore:
            try:
                async with session.get(url, headers=HEADERS, timeout=12) as response:
                    if response.status == 200:
                        return await response.text()
            except Exception as e:
                logger.warning(f"Error fetching {url}: {e}")
            return ""

    def parse_act_index(self, html_content: str) -> list:
        acts = []
        soup = BeautifulSoup(html_content, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link['href']
            if "/act-" in href or "/volume-" in href:
                title = link.get_text(strip=True)
                match = re.search(r'act-(\d+)', href)
                act_id = int(match.group(1)) if match else len(acts) + 1
                
                full_url = href if href.startswith("http") else f"{BDLAWS_BASE_URL}/{href}"
                acts.append({
                    "act_id": act_id,
                    "title": title,
                    "url": full_url
                })
        return acts

    async def scrape_act_sections(self, session, act: dict):
        act_id = act["act_id"]
        act_url = act["url"]
        act_dir = os.path.join(BASE_RAW_DIR, f"act_{act_id}")
        os.makedirs(act_dir, exist_ok=True)

        logger.info(f"Scraping Act #{act_id}: {act['title']}...")
        html = await self.fetch_page(session, act_url)
        if not html:
            return

        soup = BeautifulSoup(html, "html.parser")
        sec_links = []
        for link in soup.find_all("a", href=True):
            href = link['href']
            if f"/act-{act_id}/section-" in href or "/section-" in href:
                full_sec_url = href if href.startswith("http") else f"{BDLAWS_BASE_URL}/{href}"
                match = re.search(r'section-(\d+)', href)
                sec_num = match.group(1) if match else "1"
                sec_links.append({"sec_num": sec_num, "url": full_sec_url})

        # Process each section
        for sec in sec_links:
            sec_num = sec["sec_num"]
            sec_url = sec["url"]
            sec_html = await self.fetch_page(session, sec_url)
            if not sec_html:
                continue

            # 1. Preserve Raw HTML file for auditability
            raw_file_path = os.path.join(act_dir, f"section_{sec_num}.html")
            with open(raw_file_path, "w", encoding="utf-8") as f:
                f.write(sec_html)

            # 2. Extract clean ground-truth text
            sec_soup = BeautifulSoup(sec_html, "html.parser")
            title_el = sec_soup.find("h4") or sec_soup.find("h3") or sec_soup.find("title")
            title_bn = title_el.get_text(strip=True) if title_el else f"ধারা {sec_num}"

            content_el = sec_soup.find("div", class_="section-details") or sec_soup.find("body")
            content_bn = content_el.get_text(separator="\n", strip=True) if content_el else ""

            easy_exp_bn = f"অফিশিয়াল bdlaws থেকে সরাসরি সংগৃহীত {act['title']}-এর {sec_num} ধারা।"

            sec_record = {
                "act_id": act_id,
                "act_name_en": act["title"],
                "act_name_bn": act["title"],
                "category": "Bangladesh Laws (বাংলাদেশ আইন)",
                "section_number": str(sec_num),
                "section_title_en": f"Section {sec_num}",
                "section_title_bn": title_bn,
                "content_en": content_bn,
                "content_bn": content_bn,
                "easy_explanation_bn": easy_exp_bn,
                "source_url": sec_url,
                "keywords": [str(sec_num), act["title"]],
                "past_court_cases": []
            }

            self.scraped_sections.append(sec_record)
            
            # Upsert into PostgreSQL if database is active
            upsert_section(
                act_id=act_id,
                act_name_en=act["title"],
                act_name_bn=act["title"],
                category="General Law",
                sec_num=str(sec_num),
                title_en=f"Section {sec_num}",
                title_bn=title_bn,
                content_en=content_bn,
                content_bn=content_bn,
                easy_exp_bn=easy_exp_bn,
                url=sec_url
            )

    async def run_full_pipeline(self, limit_acts: int = 5):
        logger.info("Initializing Live Async Scraper for bdlaws.minlaw.gov.bd...")
        init_db()

        async with aiohttp.ClientSession() as session:
            # Try multiple portal index URLs
            target_urls = [
                f"{BDLAWS_BASE_URL}/laws-of-bangladesh.html",
                f"{BDLAWS_BASE_URL}/act-list-all.html",
                "https://bdlaws.minlaw.gov.bd"
            ]

            acts = []
            for url in target_urls:
                main_html = await self.fetch_page(session, url)
                if main_html:
                    acts = self.parse_act_index(main_html)
                    if acts:
                        logger.info(f"Successfully scraped {len(acts)} Act links from {url}!")
                        break

            if not acts:
                logger.warning("Could not fetch live index directly. Initializing seed catalog index.")
                acts = [
                    {"act_id": 11, "title": "The Penal Code, 1860", "url": f"{BDLAWS_BASE_URL}/act-11.html"},
                    {"act_id": 26, "title": "The Negotiable Instruments Act, 1881", "url": f"{BDLAWS_BASE_URL}/act-26.html"},
                    {"act_id": 42, "title": "The Bangladesh Labour Act, 2006", "url": f"{BDLAWS_BASE_URL}/act-42.html"}
                ]

            target_acts = acts[:limit_acts] if limit_acts else acts
            tasks = [self.scrape_act_sections(session, act) for act in target_acts]
            await asyncio.gather(*tasks)

        # Write accumulated sections to JSON database
        if self.scraped_sections:
            with open(PROCESSED_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(self.scraped_sections, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.scraped_sections)} scraped sections to {PROCESSED_JSON_PATH}")

if __name__ == "__main__":
    scraper = ProductionAsyncScraper(max_concurrent=5)
    asyncio.run(scraper.run_full_pipeline(limit_acts=2))
