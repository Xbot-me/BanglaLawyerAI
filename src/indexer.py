import os
import json
import math
import logging
import numpy as np
from rank_bm25 import BM25Okapi
from src.db import get_all_sections_for_indexing

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "processed"))
EMBEDDINGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "embeddings"))

BENGALI_STOPWORDS = {
    "আইন", "কী", "কি", "বলে", "বলুন", "বলেন", "কোন", "ধারায়", "ধারায়", "ধারা", "মামলা", "হয়", "হয়", 
    "করা", "করায়", "করালে", "হলে", "হল", "যায়", "যায়", "জন্য", "থাকে", "থাকলে", "কোনটি", "কীভাবে",
    "কেমন", "এর", "এবং", "বা", "বাস্তব", "সম্পর্কে", "সম্পর্কিত", "বিবরণ", "অধীনে", "অধীন",
    "law", "section", "act", "under", "what", "which", "is", "are", "the", "for", "in", "of"
}


class PurePythonNgramVectorizer:
    def __init__(self, ngram_range=(2, 4)):
        self.ngram_range = ngram_range
        self.vocab = {}
        self.idf = {}
        self.doc_vectors = None

    def _get_ngrams(self, text):
        words = text.lower().split()
        ngrams = []
        for word in words:
            clean_word = word.strip(".,;:!?()[]{}'\"")
            if not clean_word or clean_word in BENGALI_STOPWORDS:
                continue
            ngrams.append(f"w_{clean_word}")
            padded = f"^{clean_word}$"
            for n in range(self.ngram_range[0], self.ngram_range[1] + 1):
                for i in range(len(padded) - n + 1):
                    ngrams.append(padded[i:i+n])
        return ngrams

    def fit_transform(self, corpus_texts):
        if not corpus_texts:
            self.vocab = {}
            self.idf = {}
            self.doc_vectors = np.zeros((0, 1), dtype=np.float32)
            return self.doc_vectors

        doc_ngrams_list = [self._get_ngrams(text) for text in corpus_texts]
        df = {}
        N = len(corpus_texts)

        for doc_ngrams in doc_ngrams_list:
            unique_ngrams = set(doc_ngrams)
            for ng in unique_ngrams:
                df[ng] = df.get(ng, 0) + 1

        self.vocab = {ng: idx for idx, ng in enumerate(sorted(df.keys()))}
        self.idf = {ng: math.log((N + 1) / (df[ng] + 1)) + 1.0 for ng in df}

        vocab_size = max(len(self.vocab), 1)
        vectors = np.zeros((N, vocab_size), dtype=np.float32)

        for d_idx, doc_ngrams in enumerate(doc_ngrams_list):
            counts = {}
            for ng in doc_ngrams:
                counts[ng] = counts.get(ng, 0) + 1
            for ng, count in counts.items():
                if ng in self.vocab:
                    v_idx = self.vocab[ng]
                    vectors[d_idx, v_idx] = count * self.idf[ng]

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.doc_vectors = vectors / norms
        return self.doc_vectors

    def transform(self, text):
        ngrams = self._get_ngrams(text)
        vocab_size = max(len(self.vocab), 1)
        vec = np.zeros((1, vocab_size), dtype=np.float32)
        if not self.vocab:
            return vec

        counts = {}
        for ng in ngrams:
            counts[ng] = counts.get(ng, 0) + 1
        for ng, count in counts.items():
            if ng in self.vocab:
                v_idx = self.vocab[ng]
                vec[0, v_idx] = count * self.idf[ng]

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec


class LegalIndexer:
    def __init__(self):
        self.bm25 = None
        self.documents = []
        self.doc_embeddings = None
        self.vectorizer = PurePythonNgramVectorizer(ngram_range=(2, 4))
        self.embedding_model = None

    def _load_seed_enrichment(self) -> dict:
        """
        Map (act_id, section_number) -> rich seed metadata (keywords, easy_explanation,
        procedure_steps, etc.). Used to enrich thin scraped rows from Postgres.
        """
        try:
            from src.scraper import SEEDED_SECTIONS
            enrich = {}
            for s in SEEDED_SECTIONS:
                key = (int(s.get("act_id") or 0), str(s.get("section_number") or ""))
                enrich[key] = s
                # Also index by section_number alone for acts where act_id may differ
                enrich[("any", str(s.get("section_number") or ""))] = s
            return enrich
        except Exception as e:
            logger.warning(f"Could not load seed enrichment: {e}")
            return {}

    def _enrich_documents(self, documents: list) -> list:
        """
        Merge curated keywords / explanations from SEEDED_SECTIONS into scraped
        Postgres rows so high-value sections (323, 379, 420, …) retrieve reliably
        even when the scraper only stored [section_number, act_title] as keywords.
        Seed-only sections that are missing from the DB are appended.
        """
        enrich = self._load_seed_enrichment()
        if not enrich:
            return documents

        seen_secs = set()
        for doc in documents:
            act_id = int(doc.get("act_id") or 0)
            sec = str(doc.get("section_number") or "")
            seen_secs.add(sec)
            seed = enrich.get((act_id, sec)) or enrich.get(("any", sec))
            if not seed:
                continue
            # Merge keywords (union, keep order)
            existing_kw = list(doc.get("keywords") or [])
            seed_kw = list(seed.get("keywords") or [])
            merged = list(dict.fromkeys(existing_kw + seed_kw))
            doc["keywords"] = merged
            # Prefer richer seed text when scraped fields are empty/generic
            if seed.get("easy_explanation_bn") and (
                not doc.get("easy_explanation_bn")
                or "অফিশিয়াল bdlaws থেকে সরাসরি" in (doc.get("easy_explanation_bn") or "")
            ):
                doc["easy_explanation_bn"] = seed["easy_explanation_bn"]
            if seed.get("section_title_bn") and (
                not doc.get("section_title_bn")
                or doc.get("section_title_bn", "").startswith("Section ")
                or doc.get("section_title_bn", "").startswith("ধারা ")
            ):
                doc["section_title_bn"] = seed["section_title_bn"]
            if seed.get("section_title_en") and (
                not doc.get("section_title_en")
                or doc.get("section_title_en", "").startswith("Section ")
            ):
                doc["section_title_en"] = seed["section_title_en"]
            if seed.get("content_bn") and len(seed["content_bn"]) > len(doc.get("content_bn") or ""):
                # Keep scraped official text if present; only fill if empty
                if not (doc.get("content_bn") or "").strip():
                    doc["content_bn"] = seed["content_bn"]
            if seed.get("related_sections"):
                doc["related_sections"] = seed["related_sections"]
            if seed.get("procedure_steps"):
                doc["procedure_steps"] = seed["procedure_steps"]
            if seed.get("evidence_matrix"):
                doc["evidence_matrix"] = seed["evidence_matrix"]

        # Append curated seed sections that are missing from DB (esp. composite entries)
        already_appended = set()
        for key, s in enrich.items():
            if key[0] == "any":
                continue  # skip duplicate "any" index entries
            sec = str(s.get("section_number") or "")
            if not sec or sec in seen_secs or sec in already_appended:
                continue
            already_appended.add(sec)
            seen_secs.add(sec)
            documents.append({
                "act_id": s.get("act_id", 11),
                "act_name_en": s.get("act_name_en", ""),
                "act_name_bn": s.get("act_name_bn", ""),
                "category": s.get("category", "General Law"),
                "chapter_number": s.get("chapter_number") or "",
                "chapter_title": s.get("chapter_title") or "",
                "section_number": sec,
                "section_title_en": s.get("section_title_en") or "",
                "section_title_bn": s.get("section_title_bn") or "",
                "content_en": s.get("content_en") or s.get("content_bn") or "",
                "content_bn": s.get("content_bn") or "",
                "easy_explanation_bn": s.get("easy_explanation_bn") or "",
                "keywords": s.get("keywords") or [],
                "related_sections": s.get("related_sections") or [],
                "source_url": s.get("source_url") or "",
                "procedure_steps": s.get("procedure_steps") or [],
                "evidence_matrix": s.get("evidence_matrix") or {},
                "past_court_cases": [],
            })
            logger.info(f"Appended curated seed section {sec} not found in Postgres.")

        return documents

    def load_documents(self, json_path=None):
        """
        Load documents for the search index. Tries Postgres first (the real,
        continuously-scraped dataset); enriches those rows with curated keywords
        from SEEDED_SECTIONS; falls back to the local JSON seed file only if the
        DB is empty or unreachable.
        """
        db_documents = get_all_sections_for_indexing()
        if db_documents:
            self.documents = self._enrich_documents(db_documents)
            logger.info(
                f"Loaded {len(self.documents)} documents from PostgreSQL "
                f"(enriched with curated seed keywords where available)."
            )
            return self.documents

        logger.warning("PostgreSQL returned no documents (empty or unreachable). Falling back to local JSON seed.")

        if json_path is None:
            json_path = os.path.join(PROCESSED_DIR, "sections.json")

        if not os.path.exists(json_path):
            logger.warning(f"File {json_path} not found either. Bootstrapping initial section seed dataset...")
            try:
                from src.scraper import fetch_and_preserve_raw
                from src.parser import parse_raw_documents
                fetch_and_preserve_raw()
                self.documents = parse_raw_documents()
                return self.documents
            except Exception as e:
                logger.error(f"Error bootstrapping section seed dataset: {e}")
                self.documents = []
                return self.documents

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
        except Exception as e:
            logger.error(f"Error loading {json_path}: {e}")
            self.documents = []

        logger.info(f"Loaded {len(self.documents)} documents from local JSON seed for indexing.")
        return self.documents

    def _tokenize(self, text, remove_stopwords=True):
        bengali_digits = "০১২৩৪৫৬৭৮৯"
        english_digits = "0123456789"
        trans_table = str.maketrans(bengali_digits, english_digits)

        normalized_text = text.translate(trans_table).lower()
        raw_tokens = [t.strip(".,;:!?()[]{}'\"") for t in normalized_text.split() if t.strip(".,;:!?()[]{}'\"")]

        if remove_stopwords:
            tokens = [t for t in raw_tokens if t not in BENGALI_STOPWORDS]
            return tokens if tokens else raw_tokens
        return raw_tokens

    def build_bm25_index(self):
        corpus_tokens = []
        if not self.documents:
            self.bm25 = BM25Okapi([["empty"]])
            return

        for doc in self.documents:
            text = f"{doc['section_number']} ধারা {doc['section_number']} {doc['section_title_bn']} {doc['section_title_en']} {doc['content_bn']} {doc['content_en']} {' '.join(doc.get('keywords', []))}"
            tokens = self._tokenize(text, remove_stopwords=True)
            corpus_tokens.append(tokens)

        self.bm25 = BM25Okapi(corpus_tokens)
        logger.info("BM25 keyword index constructed successfully.")

    def build_vector_index(self):
        os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
        if not self.documents:
            self.doc_embeddings = np.zeros((0, 1), dtype=np.float32)
            return

        raw_corpus = [f"{doc['section_number']} {doc['section_title_bn']} {doc['content_bn']} {doc['content_en']} {' '.join(doc.get('keywords', []))}" for doc in self.documents]
        self.doc_embeddings = self.vectorizer.fit_transform(raw_corpus)
        logger.info(f"Pure Python Multilingual Vector Index constructed. Matrix Shape: {self.doc_embeddings.shape}")

    def build_all(self, json_path=None):
        self.load_documents(json_path)
        self.build_bm25_index()
        self.build_vector_index()


if __name__ == "__main__":
    indexer = LegalIndexer()
    indexer.build_all()
    print("Indexing complete.")