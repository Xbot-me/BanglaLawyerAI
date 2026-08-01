import os
import json
import logging
from bs4 import BeautifulSoup
from src.scraper import BASE_RAW_DIR, SEEDED_SECTIONS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "processed"))
OUTPUT_JSON_PATH = os.path.join(PROCESSED_DIR, "sections.json")

def parse_raw_documents(act_slug="act_11_penal_code_1860"):
    act_dir = os.path.join(BASE_RAW_DIR, act_slug)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    sections = []
    seeded_map = {sec["section_number"]: sec for sec in SEEDED_SECTIONS}
    
    # Extract all seeded sections cleanly
    for meta_item in SEEDED_SECTIONS:
        sec_num = meta_item["section_number"]
        record = {
            "act_id": meta_item.get("act_id", 11),
            "act_name_en": meta_item.get("act_name_en"),
            "act_name_bn": meta_item.get("act_name_bn"),
            "category": meta_item.get("category", "General Law"),
            "chapter_number": meta_item.get("chapter_number"),
            "chapter_title": meta_item.get("chapter_title"),
            "section_number": sec_num,
            "section_title_en": meta_item.get("section_title_en"),
            "section_title_bn": meta_item.get("section_title_bn"),
            "domain": meta_item.get("domain", "Criminal Law"),
            "content_en": meta_item.get("content_en"),
            "content_bn": meta_item.get("content_bn"),
            "easy_explanation_bn": meta_item.get("easy_explanation_bn"),
            "keywords": meta_item.get("keywords", []),
            "related_sections": meta_item.get("related_sections", []),
            "source_url": meta_item.get("source_url"),
            "elements_of_offence": meta_item.get("elements_of_offence", []),
            "evidence_matrix": meta_item.get("evidence_matrix", {}),
            "police_questions": meta_item.get("police_questions", []),
            "procedure_steps": meta_item.get("procedure_steps", []),
            "past_court_cases": meta_item.get("past_court_cases", []),
            "case_strength": meta_item.get("case_strength", {})
        }
        sections.append(record)
    
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(sections, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Processed {len(sections)} sections saved to {OUTPUT_JSON_PATH}")
    return sections

if __name__ == "__main__":
    records = parse_raw_documents()
    print(f"Parsed {len(records)} legal records.")
