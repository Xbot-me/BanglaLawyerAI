import os
import re
import json
import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from src.db import upsert_section, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "raw", "bdlaws"))
PROCESSED_JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "processed", "sections.json"))
BDLAWS_BASE_URL = "http://bdlaws.minlaw.gov.bd"
CHRONOLOGICAL_INDEX_URL = "http://bdlaws.minlaw.gov.bd/laws-of-bangladesh-chronological-index.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

# Matches the real statutory section number embedded at the start of the section body text,
# e.g. "11. The word person includes..." or "420A. Cheating and dishonestly inducing..."
# NOTE: the URL's "section-XXXX" number is an internal row id, NOT the statutory section number.
SECTION_NUMBER_RE = re.compile(r'^\s*(\d+[A-Za-z]*)\.\s*(.*)', re.DOTALL)


class ProductionAsyncScraper:
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.scraped_sections = []
        os.makedirs(BASE_RAW_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(PROCESSED_JSON_PATH), exist_ok=True)

    async def fetch_page(self, session, url: str) -> str:
        async with self.semaphore:
            try:
                clean_url = urljoin(BDLAWS_BASE_URL, url)
                async with session.get(clean_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as response:
                    if response.status == 200:
                        raw_bytes = await response.read()
                        # bdlaws' HTTP header always claims charset=UTF-16, but that's not
                        # reliably true: some pages (large index/listing pages) really are
                        # UTF-16 with a BOM; others (individual section pages) are actually
                        # UTF-8 despite the header. Sniff the real encoding from the byte
                        # stream itself rather than trusting the header either way.
                        if raw_bytes.startswith(b'\xfe\xff') or raw_bytes.startswith(b'\xff\xfe'):
                            return raw_bytes.decode("utf-16", errors="replace")
                        elif raw_bytes.startswith(b'\xef\xbb\xbf'):
                            return raw_bytes.decode("utf-8-sig", errors="replace")
                        else:
                            try:
                                return raw_bytes.decode("utf-8")
                            except UnicodeDecodeError:
                                return raw_bytes.decode("utf-16", errors="replace")
            except Exception as e:
                logger.debug(f"Timeout/Error fetching {url}: {e}")
            return ""

    def parse_chronological_index(self, html_content: str) -> list:
        acts = []
        seen_act_ids = set()
        soup = BeautifulSoup(html_content, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link['href']
            # Real act section-index pages are served at /act-<id>.html
            # (confirmed directly from a live fetched page's own "[Section Index]" link)
            m = re.search(r'/act-(\d+)\.html', href)
            if m:
                act_id = int(m.group(1))
                title = link.get_text(strip=True)
                if not title or len(title) < 3 or act_id in seen_act_ids:
                    continue
                seen_act_ids.add(act_id)
                full_url = urljoin(BDLAWS_BASE_URL, href)
                acts.append({
                    "act_id": act_id,
                    "title": title,
                    "url": full_url
                })
        return acts

    async def scrape_act_sections(self, session, act: dict, idx: int, total: int):
        act_id = act["act_id"]
        act_url = act["url"]
        act_dir = os.path.join(BASE_RAW_DIR, f"act_{act_id}")
        os.makedirs(act_dir, exist_ok=True)

        html = await self.fetch_page(session, act_url)
        if not html:
            logger.warning(f"[{idx}/{total}] Act #{act_id} ({act['title'][:30]}) page unreachable, skipping.")
            return

        soup = BeautifulSoup(html, "html.parser")
        sec_links = []
        for link in soup.find_all("a", href=True):
            href = link['href']
            if "section-" in href:
                full_sec_url = urljoin(BDLAWS_BASE_URL, href)
                match = re.search(r'section-(\d+)', href)
                sec_id = match.group(1) if match else "1"
                sec_links.append({"sec_id": sec_id, "url": full_sec_url})

        # Remove duplicate section URLs
        unique_sec_links = list({sec["url"]: sec for sec in sec_links}.values())

        if not unique_sec_links:
            logger.info(f"[{idx}/{total}] Act #{act_id} ({act['title'][:30]}) has 0 section links.")
            return

        saved_count = 0
        for sec in unique_sec_links:
            sec_id = sec["sec_id"]
            sec_url = sec["url"]
            sec_html = await self.fetch_page(session, sec_url)
            if not sec_html:
                continue

            # 1. Preserve raw HTML for auditability (now correctly UTF-8 decoded)
            raw_file_path = os.path.join(act_dir, f"section_{sec_id}.html")
            with open(raw_file_path, "w", encoding="utf-8") as f:
                f.write(sec_html)

            # 2. Extract clean ground-truth text using the REAL page structure
            sec_soup = BeautifulSoup(sec_html, "html.parser")

            head_el = sec_soup.find("div", class_="txt-head")
            details_el = sec_soup.find("div", id="sec-dec") or sec_soup.find("div", class_="txt-details")

            title_bn = head_el.get_text(strip=True) if head_el else ""
            raw_content = details_el.get_text(separator=" ", strip=True) if details_el else ""

            if not raw_content:
                # No real section content found on this page (nav/junk/blank page) - skip it
                # rather than storing garbage.
                logger.debug(f"Skipping {sec_url}: no section content found (likely non-section page).")
                continue

            m = SECTION_NUMBER_RE.match(raw_content)
            if m:
                real_sec_num = m.group(1)
                content_bn = m.group(2).strip()
            else:
                real_sec_num = sec_id  # fallback only if the expected pattern isn't found
                content_bn = raw_content

            chapter_no_el = sec_soup.find("p", class_="act-chapter-no")
            chapter_title_el = sec_soup.find("p", class_="act-chapter-name")
            chapter_no = chapter_no_el.get_text(strip=True) if chapter_no_el else ""
            chapter_title = chapter_title_el.get_text(strip=True) if chapter_title_el else ""

            easy_exp_bn = f"অফিশিয়াল bdlaws থেকে সরাসরি সংগৃহীত {act['title']}-এর {real_sec_num} ধারা।"

            sec_record = {
                "act_id": act_id,
                "act_name_en": act["title"],
                "act_name_bn": act["title"],
                "category": "Bangladesh Laws (বাংলাদেশ আইন)",
                "chapter_number": chapter_no,
                "chapter_title": chapter_title,
                "section_number": str(real_sec_num),
                "section_title_en": f"Section {real_sec_num}",
                "section_title_bn": title_bn,
                "content_en": content_bn,
                "content_bn": content_bn,
                "easy_explanation_bn": easy_exp_bn,
                "source_url": sec_url,
                "keywords": [str(real_sec_num), act["title"]],
                "past_court_cases": []
            }

            self.scraped_sections.append(sec_record)
            saved_count += 1

            upsert_section(
                act_id=act_id,
                act_name_en=act["title"],
                act_name_bn=act["title"],
                category="General Law",
                sec_num=str(real_sec_num),
                title_en=f"Section {real_sec_num}",
                title_bn=title_bn,
                content_en=content_bn,
                content_bn=content_bn,
                easy_exp_bn=easy_exp_bn,
                url=sec_url
            )

        logger.info(f"[{idx}/{total}] Saved {saved_count} sections for Act #{act_id} ({act['title'][:30]}) -> Total in DB: {len(self.scraped_sections)}")

    async def run_full_pipeline(self, limit_acts: int = None, batch_size: int = 5):
        logger.info("Initializing Live Async Scraper for bdlaws.minlaw.gov.bd...")
        init_db()

        async with aiohttp.ClientSession() as session:
            logger.info(f"Fetching full Chronological Index from {CHRONOLOGICAL_INDEX_URL}...")
            main_html = await self.fetch_page(session, CHRONOLOGICAL_INDEX_URL)

            acts = []
            if main_html:
                acts = self.parse_chronological_index(main_html)
                logger.info(f"Successfully discovered {len(acts)} Acts on official bdlaws portal!")

            if not acts:
                logger.warning("Could not fetch live index directly. Initializing seed catalog index.")
                acts = [
                    {"act_id": 11, "title": "The Penal Code, 1860", "url": f"{BDLAWS_BASE_URL}/act-11.html"},
                    {"act_id": 26, "title": "The Negotiable Instruments Act, 1881", "url": f"{BDLAWS_BASE_URL}/act-26.html"},
                    {"act_id": 42, "title": "The Bangladesh Labour Act, 2006", "url": f"{BDLAWS_BASE_URL}/act-42.html"}
                ]

            target_acts = acts[:limit_acts] if limit_acts else acts
            total_acts = len(target_acts)

            for i in range(0, total_acts, batch_size):
                batch = target_acts[i:i+batch_size]
                tasks = [self.scrape_act_sections(session, act, i+j+1, total_acts) for j, act in enumerate(batch)]
                await asyncio.gather(*tasks)

        if self.scraped_sections:
            with open(PROCESSED_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(self.scraped_sections, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved total {len(self.scraped_sections)} scraped sections to {PROCESSED_JSON_PATH}")


if __name__ == "__main__":
    scraper = ProductionAsyncScraper(max_concurrent=5)
    asyncio.run(scraper.run_full_pipeline(limit_acts=2, batch_size=5))