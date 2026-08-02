import os
import re
import logging
import time
import numpy as np
from src.indexer import LegalIndexer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Simple in-memory cache for LLM-normalized queries (process lifetime)
_QUERY_NORM_CACHE = {}
_QUERY_NORM_CACHE_MAX = 500

# Out-of-domain signals (Only for subjects not yet ingested into our database, e.g. Divorce, Child Custody, Income Tax)
OUT_OF_DOMAIN_KEYWORDS = {"ডিভোর্স", "সন্তান", "অনুমতি", "পাসপোর্ট", "ভাতা", "ইনকাম ট্যাক্স", "ভ্যাট"}

# Banglish & Multilingual Phonetic Expansion Dictionary
# Police+assault terms must expand to hurt sections (323-325), NOT animal s.428.
BANGLISH_PHONETIC_MAP = {
    # --- Police assault / custodial violence ---
    "police": "পুলিশ police assault মারধর আঘাত ৩২৩ 323 ৩২৪ 324 ৩২৫ 325 torture নির্যাতন",
    "pulish": "পুলিশ police assault মারধর আঘাত ৩২৩ 323 ৩২৪ 324 ৩২৫ 325",
    "polise": "পুলিশ police assault মারধর আঘাত ৩২৩ 323",
    "ojotha": "অযথা অন্যায় বেআইনি police assault মারধর ৩২৩ 323",
    "ojatha": "অযথা অন্যায় বেআইনি police assault মারধর ৩২৩ 323",
    "amare": "আমাকে আঘাত মারধর hurt ৩২৩ 323",
    "amake": "আমাকে আঘাত মারধর hurt ৩২৩ 323",
    "marse": "মারধর আঘাত hurt assault ৩২৩ 323 beating",
    "marche": "মারধর আঘাত hurt assault ৩২৩ 323",
    "mara": "মারধর আঘাত hurt ৩২৩ 323",
    "pitse": "মারধর আঘাত hurt ৩২৩ 323",
    "piteche": "মারধর আঘাত hurt ৩২৩ 323",
    "beating": "মারধর আঘাত assault ৩২৩ 323 police",
    "assault": "মারধর আঘাত assault ৩২৩ 323 ৩২৪ 324",
    "torture": "নির্যাতন torture হেফাজত custodial ৩২৩ 323",
    "nirjaton": "নির্যাতন torture হেফাজত ৩২৩ 323",
    "hefazot": "হেফাজত custodial torture নির্যাতন",
    "custody": "হেফাজত custodial torture নির্যাতন",
    "lathi": "লাঠিচার্জ baton ৩২৪ 324 dangerous weapon",
    "baton": "লাঠিচার্জ baton ৩২৪ 324",

    # --- Animal (only when animal word is present) ---
    "biral": "পশু বিড়াল মারছে হত্যা ৪২৮ 428 animal",
    "cat": "পশু বিড়াল মারছে হত্যা ৪২৮ 428 animal",
    "kutta": "পশু কুকুর মারছে হত্যা ৪২৮ 428 animal",
    "dog": "পশু কুকুর মারছে হত্যা ৪২৮ 428 animal",
    "pet": "পশু পোষা প্রাণী ৪২৮ 428 animal",

    # --- Theft ---
    "churi": "চুরি ৩৭৯ 379",
    "chori": "চুরি ৩৭৯ 379",
    "stolen": "চুরি ৩৭৯ 379",

    # --- Murder / false implication ---
    "murdar": "মানুষ খুন হত্যা ৩০২ 302",
    "murder": "মানুষ খুন হত্যা ৩০২ 302",
    "khun": "মানুষ খুন হত্যা ৩০২ 302",
    "jogra": "ঝগড়া মারামারি ৩০২ 302",
    "jograr": "ঝগড়া মারামারি ৩০২ 302",
    "maramari": "ঝগড়া মারামারি আঘাত ৩২৩ 323 ৩০২ 302",
    "asami": "আসামি অভিযুক্ত ৩০২ 302",
    "banaise": "বানিয়েছে মামলা ৩০২ 302",

    # --- Fraud / money ---
    "taka": "টাকা অর্থ ৪২০ 420 406",
    "takabati": "টাকা অর্থ ৪২০ 420 406",
    "ferot": "ফেরত টাকা ৪২০ 420",
    "dicche": "দিচ্ছে না ৪২০ 420",

    # --- Cheque ---
    "cheque": "চেক বাউন্স ১৩৮ 138",
    "check": "চেক বাউন্স ১৩৮ 138",
    "bounce": "চেক বাউন্স ১৩৮ 138",

    # --- Labour ---
    "beton": "বেতন মজুরি শ্রম ১২০ 120",
    "salary": "বেতন মজুরি শ্রম ১২০ 120",

    # --- Land ---
    "jomi": "জমি বেদখল ৯ 9",
    "dokhol": "জমি বেদখল ৯ 9",
}

class HybridRetriever:
    def __init__(self, indexer: LegalIndexer = None):
        if indexer is None:
            indexer = LegalIndexer()
            indexer.build_all()
        self.indexer = indexer

    def _looks_like_banglish(self, text: str) -> bool:
        """Heuristic: Latin script with Bangla-phonetic patterns, or mixed."""
        if not text:
            return False
        # Already mostly Bengali script → no need to "translate"
        bengali_chars = sum(1 for c in text if "\u0980" <= c <= "\u09FF")
        if bengali_chars >= max(3, len(text) // 3):
            return False
        latin = sum(1 for c in text if c.isascii() and c.isalpha())
        if latin < 3:
            return False
        # Common Banglish markers
        markers = (
            "marse", "marche", "ojotha", "amare", "amake", "korte", "pari",
            "hoise", "hoiche", "churi", "chori", "taka", "biral", "pulish",
            "police", "kivabe", "ki korte", "hole", "korbo", "korben"
        )
        low = text.lower()
        return any(m in low for m in markers) or latin >= 8

    def _llm_normalize_banglish(self, query: str) -> str:
        """
        Use Groq LLM to rewrite Banglish / mixed queries into clear Bengali +
        English legal keywords suitable for BM25/vector search.
        Falls back to empty string on failure (caller uses phonetic map).
        """
        cache_key = query.strip().lower()
        if cache_key in _QUERY_NORM_CACHE:
            return _QUERY_NORM_CACHE[cache_key]

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return ""

        try:
            import requests
            system = (
                "You normalize Bangladesh citizen legal questions written in Banglish "
                "(Romanized Bengali) or mixed Bangla/English into a search-friendly form.\n"
                "Output ONLY one short line containing:\n"
                "1) Natural Bengali restatement of the question, and\n"
                "2) Key English/Bengali legal terms and likely Penal Code / Act section numbers if obvious.\n"
                "Do NOT answer the legal question. Do NOT invent case law. Keep under 40 words.\n"
                "Examples:\n"
                "Input: police amare ojotha marse ei jonno ami ki korte pari\n"
                "Output: পুলিশ আমাকে অযথা মারধর করেছে আঘাত police assault hurt voluntarily causing hurt ধারা ৩২৩ ৩২৪ ৩২৫ নির্যাতন\n"
                "Input: amar biral ke ekjon marse\n"
                "Output: আমার বিড়ালকে কেউ মেরেছে পশু নির্যাতন animal killing ধারা ৪২৮\n"
                "Input: cheque bounce hole ki korte pari\n"
                "Output: চেক বাউন্স ডিজঅনার negotiable instruments ধারা ১৩৮"
            )
            payload = {
                "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": query},
                ],
                "temperature": 0.1,
                "max_tokens": 120,
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=6,
            )
            if resp.status_code != 200:
                logger.warning(f"LLM Banglish normalize failed: HTTP {resp.status_code}")
                return ""
            text = resp.json()["choices"][0]["message"]["content"].strip()
            # Single line cleanup
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) < 5:
                return ""
            # Cache
            if len(_QUERY_NORM_CACHE) >= _QUERY_NORM_CACHE_MAX:
                _QUERY_NORM_CACHE.clear()
            _QUERY_NORM_CACHE[cache_key] = text
            logger.info(f"LLM Banglish normalize: '{query}' -> '{text}'")
            return text
        except Exception as e:
            logger.warning(f"LLM Banglish normalize error: {e}")
            return ""

    def _phonetic_expand(self, norm_q: str) -> str:
        """Offline Banglish phonetic map expansion (fast fallback)."""
        words = re.findall(r"\b\w+\b", norm_q)
        expanded_tokens = [norm_q]

        animal_words = {"biral", "cat", "kutta", "dog", "pet", "বিড়াল", "কুকুর", "পশু", "প্রাণী"}
        has_animal = any(w in animal_words for w in words) or any(
            a in norm_q for a in ("biral", "cat", "kutta", "dog", "pet", "বিড়াল", "কুকুর")
        )
        police_words = {"police", "pulish", "polise", "পুলিশ"}
        has_police = any(w in police_words for w in words) or "পুলিশ" in norm_q

        for w in words:
            if w not in BANGLISH_PHONETIC_MAP:
                continue
            expansion = BANGLISH_PHONETIC_MAP[w]
            if has_animal and not has_police and w in (
                "marse", "marche", "mara", "pitse", "piteche", "beating"
            ):
                expansion = "পশু প্রাণী আঘাত হত্যা ৪২৮ 428 animal"
            expanded_tokens.append(expansion)

        return " ".join(expanded_tokens)

    def _normalize_query(self, query):
        bengali_digits = "০১২৩৪৫৬৭৮৯"
        english_digits = "0123456789"
        trans_table = str.maketrans(bengali_digits, english_digits)
        norm_q = query.translate(trans_table).lower()

        # 1) Prefer LLM rewrite for Banglish / mixed queries when API key is set
        llm_part = ""
        if self._looks_like_banglish(query):
            llm_part = self._llm_normalize_banglish(query)

        # 2) Always apply offline phonetic expansion as safety net
        phonetic_part = self._phonetic_expand(norm_q)

        if llm_part:
            final_query = f"{norm_q} {llm_part} {phonetic_part}"
            logger.info(f"Query normalize (LLM+map): '{query}' -> '{final_query[:180]}...'")
        else:
            final_query = phonetic_part
            logger.info(f"Query normalize (map only): '{query}' -> '{final_query[:180]}'")

        return final_query

    def _keyword_overlap_bonus(self, query: str, doc: dict) -> float:
        """Extra score when query tokens appear in section keywords / title / number."""
        q = query.lower()
        kw_text = " ".join(doc.get("keywords") or []).lower()
        title = f"{doc.get('section_title_en', '')} {doc.get('section_title_bn', '')} {doc.get('section_number', '')}".lower()
        bonus = 0.0
        # Strong boost if section number itself is mentioned or heavily keyword-matched
        sec = str(doc.get("section_number", "")).lower()
        if sec and sec in q:
            bonus += 0.35
        # Count overlapping meaningful keywords
        q_tokens = set(re.findall(r"\b\w+\b", q))
        kw_tokens = set(re.findall(r"\b\w+\b", kw_text + " " + title))
        overlap = q_tokens & kw_tokens
        # Ignore very short / stop-like tokens
        overlap = {t for t in overlap if len(t) > 2}
        bonus += min(0.45, 0.06 * len(overlap))
        # Domain boost for police-assault intent
        police_signals = {"police", "pulish", "পুলিশ", "ojotha", "marse", "assault", "beating", "torture", "নির্যাতন", "মারধর"}
        hurt_secs = {"323", "324", "325", "323-325+torture"}
        if any(s in q for s in police_signals) and sec in hurt_secs:
            bonus += 0.5
        # Animal intent boost
        animal_signals = {"biral", "cat", "kutta", "dog", "pet", "বিড়াল", "কুকুর", "পশু", "প্রাণী", "animal"}
        if any(s in q for s in animal_signals) and sec == "428":
            bonus += 0.55
        # Penalize pure administrative Police Act sections when query is about assault
        admin_police_markers = {"inspector-general", "inspector general", "appoint", "2b", "2a", "2c", "2d"}
        if any(s in q for s in police_signals) and any(m in title or m in kw_text for m in admin_police_markers):
            bonus -= 0.6
        return bonus

    def retrieve(self, query: str, top_k: int = 5, rrf_k: int = 60):
        norm_query = self._normalize_query(query)

        # 1. BM25 Ranking
        query_tokens = self.indexer._tokenize(norm_query, remove_stopwords=True)
        bm25_scores = self.indexer.bm25.get_scores(query_tokens)
        max_bm25 = float(np.max(bm25_scores)) if len(bm25_scores) > 0 else 0.0
        bm25_ranking = np.argsort(bm25_scores)[::-1]

        # 2. Dense Vector Ranking (n-gram TF-IDF)
        q_vec = self.indexer.vectorizer.transform(norm_query)
        vector_sims = np.dot(self.indexer.doc_embeddings, q_vec.T).squeeze()
        if vector_sims.ndim == 0:
            vector_sims = np.array([float(vector_sims)])

        max_vector_sim = float(np.max(vector_sims)) if len(vector_sims) > 0 else 0.0
        vector_ranking = np.argsort(vector_sims)[::-1]

        # 3. Reciprocal Rank Fusion (RRF) + keyword overlap bonus
        rrf_scores = {}

        for rank, doc_idx in enumerate(bm25_ranking):
            if doc_idx not in rrf_scores:
                rrf_scores[doc_idx] = 0.0
            if bm25_scores[doc_idx] > 0.05:  # stricter than before
                rrf_scores[doc_idx] += 1.0 / (rrf_k + rank + 1)

        for rank, doc_idx in enumerate(vector_ranking):
            if doc_idx not in rrf_scores:
                rrf_scores[doc_idx] = 0.0
            if vector_sims[doc_idx] > 0.12:  # stricter threshold
                rrf_scores[doc_idx] += 1.0 / (rrf_k + rank + 1)

        # Apply keyword / intent bonus (and admin-section penalty)
        for doc_idx in list(rrf_scores.keys()):
            doc = self.indexer.documents[doc_idx]
            rrf_scores[doc_idx] += self._keyword_overlap_bonus(norm_query, doc)

        # Sort by final score
        sorted_doc_indices = sorted(rrf_scores.keys(), key=lambda idx: rrf_scores[idx], reverse=True)

        results = []
        for idx in sorted_doc_indices:
            doc = self.indexer.documents[idx]
            score = rrf_scores[idx]
            if score <= 0:
                continue
            results.append({
                "document": doc,
                "rrf_score": float(score),
                "bm25_score": float(bm25_scores[idx]),
                "vector_sim": float(vector_sims[idx])
            })

        top_results = results[:top_k]
        max_rrf = top_results[0]["rrf_score"] if top_results else 0.0

        # Stronger low-confidence rule
        has_out_of_domain_term = any(term in norm_query for term in OUT_OF_DOMAIN_KEYWORDS)
        known_secs = [
            "420", "415", "417", "406", "302", "379", "428", "138", "120", "154", "9",
            "323", "324", "325", "326", "319", "321",
            "৪২০", "৪০৬", "৩০২", "৩৭৯", "৪২৮", "১৩৮", "১২০", "৩২৩", "৩২৪", "৩২৫"
        ]
        has_explicit_section = any(sec in norm_query for sec in known_secs)

        # Require meaningful signal; also flag when top score is still weak
        is_low_confidence = (
            (has_out_of_domain_term and not has_explicit_section)
            or (max_bm25 < 0.15 and max_vector_sim < 0.15 and max_rrf < 0.25)
            or (not top_results)
        )

        # 4. Dependency expansion for related definitional sections
        doc_sec_numbers = {res["document"]["section_number"] for res in top_results}
        expanded_docs = list(top_results)

        if not is_low_confidence:
            for res in top_results:
                rel_secs = res["document"].get("related_sections", [])
                for rel_sec in rel_secs:
                    if rel_sec not in doc_sec_numbers and rel_sec in ["415", "405", "378", "429", "319", "321", "320"]:
                        for doc in self.indexer.documents:
                            if doc["section_number"] == rel_sec:
                                expanded_docs.append({
                                    "document": doc,
                                    "rrf_score": res["rrf_score"] * 0.9,
                                    "bm25_score": 0.0,
                                    "vector_sim": 0.0,
                                    "is_dependency": True,
                                    "dependent_on_section": res["document"]["section_number"]
                                })
                                doc_sec_numbers.add(rel_sec)
                                break

        return {
            "query": query,
            "top_matches": expanded_docs,
            "max_confidence_score": max_rrf,
            "max_bm25_score": max_bm25,
            "max_vector_sim": max_vector_sim,
            "is_low_confidence": is_low_confidence
        }

if __name__ == "__main__":
    retriever = HybridRetriever()
    res = retriever.retrieve("amar biral ke ekjon marse tar bepare ami ki korte pari?")
    print(f"Max RRF: {res['max_confidence_score']}, Low Conf: {res['is_low_confidence']}")
    print(f"Top Match: Section {res['top_matches'][0]['document']['section_number']} - {res['top_matches'][0]['document']['section_title_bn']}")
