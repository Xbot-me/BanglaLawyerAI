import os
import re
import logging
import numpy as np
from src.indexer import LegalIndexer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Out-of-domain signals (Only for subjects not yet ingested into our database, e.g. Divorce, Child Custody, Income Tax)
OUT_OF_DOMAIN_KEYWORDS = {"ডিভোর্স", "সন্তান", "অনুমতি", "পাসপোর্ট", "ভাতা", "ইনকাম ট্যাক্স", "ভ্যাট"}

# Banglish & Multilingual Phonetic Expansion Dictionary
BANGLISH_PHONETIC_MAP = {
    "biral": "পশু বিড়াল মারছে হত্যা ৪২৮ 428",
    "cat": "পশু বিড়াল মারছে হত্যা ৪২৮ 428",
    "kutta": "পশু কুকুর মারছে হত্যা ৪২৮ 428",
    "dog": "পশু কুকুর মারছে হত্যা ৪২৮ 428",
    "pet": "পশু পোষা প্রাণী ৪২৮ 428",
    "churi": "চুরি ৩৭৯ 379",
    "chori": "চুরি ৩৭৯ 379",
    "stolen": "চুরি ৩৭৯ 379",
    "murdar": "মানুষ খুন হত্যা ৩০২ 302",
    "murder": "মানুষ খুন হত্যা ৩০২ 302",
    "khun": "মানুষ খুন হত্যা ৩০২ 302",
    "jogra": "ঝগড়া মারামারি ৩০২ 302",
    "jograr": "ঝগড়া মারামারি ৩০২ 302",
    "maramari": "ঝগড়া মারামারি ৩০২ 302",
    "asami": "আসামি অভিযুক্ত ৩০২ 302",
    "banaise": "বানিয়েছে মামলা ৩০২ 302",
    "taka": "টাকা অর্থ ৪২০ 420 406",
    "takabati": "টাকা অর্থ ৪২০ 420 406",
    "ferot": "ফেরত টাকা ৪২০ 420",
    "dicche": "দিচ্ছে না ৪২০ 420",
    "cheque": "চেক বাউন্স ১৩৮ 138",
    "check": "চেক বাউন্স ১৩৮ 138",
    "bounce": "চেক বাউন্স ১৩৮ 138",
    "beton": "বেতন মজুরি শ্রম ১২০ 120",
    "salary": "বেতন মজুরি শ্রম ১২০ 120",
    "jomi": "জমি বেদখল ৯ 9",
    "dokhol": "জমি বেদখল ৯ 9"
}

class HybridRetriever:
    def __init__(self, indexer: LegalIndexer = None):
        if indexer is None:
            indexer = LegalIndexer()
            indexer.build_all()
        self.indexer = indexer

    def _normalize_query(self, query):
        bengali_digits = "০১২৩৪৫৬৭৮৯"
        english_digits = "0123456789"
        trans_table = str.maketrans(bengali_digits, english_digits)
        norm_q = query.translate(trans_table).lower()

        # Tokenize query into words to match exact Banglish keywords
        words = re.findall(r'\b\w+\b', norm_q)
        expanded_tokens = [norm_q]

        for w in words:
            if w in BANGLISH_PHONETIC_MAP:
                expanded_tokens.append(BANGLISH_PHONETIC_MAP[w])

        final_query = " ".join(expanded_tokens)
        logger.info(f"Banglish Phonetic Expansion: '{query}' -> '{final_query}'")
        return final_query

    def retrieve(self, query: str, top_k: int = 2, rrf_k: int = 60):
        norm_query = self._normalize_query(query)

        # 1. BM25 Ranking
        query_tokens = self.indexer._tokenize(norm_query, remove_stopwords=True)
        bm25_scores = self.indexer.bm25.get_scores(query_tokens)
        max_bm25 = float(np.max(bm25_scores)) if len(bm25_scores) > 0 else 0.0
        bm25_ranking = np.argsort(bm25_scores)[::-1]

        # 2. Dense Vector Ranking
        q_vec = self.indexer.vectorizer.transform(norm_query)
        vector_sims = np.dot(self.indexer.doc_embeddings, q_vec.T).squeeze()
        if vector_sims.ndim == 0:
            vector_sims = np.array([float(vector_sims)])

        max_vector_sim = float(np.max(vector_sims)) if len(vector_sims) > 0 else 0.0
        vector_ranking = np.argsort(vector_sims)[::-1]

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores = {}

        for rank, doc_idx in enumerate(bm25_ranking):
            if doc_idx not in rrf_scores:
                rrf_scores[doc_idx] = 0.0
            if bm25_scores[doc_idx] > 0.01:
                rrf_scores[doc_idx] += 1.0 / (rrf_k + rank + 1)

        for rank, doc_idx in enumerate(vector_ranking):
            if doc_idx not in rrf_scores:
                rrf_scores[doc_idx] = 0.0
            if vector_sims[doc_idx] > 0.08:
                rrf_scores[doc_idx] += 1.0 / (rrf_k + rank + 1)

        # Sort documents by total RRF score
        sorted_doc_indices = sorted(rrf_scores.keys(), key=lambda idx: rrf_scores[idx], reverse=True)

        results = []
        for idx in sorted_doc_indices:
            doc = self.indexer.documents[idx]
            score = rrf_scores[idx]
            results.append({
                "document": doc,
                "rrf_score": float(score),
                "bm25_score": float(bm25_scores[idx]),
                "vector_sim": float(vector_sims[idx])
            })

        top_results = results[:top_k]
        max_rrf = top_results[0]["rrf_score"] if top_results else 0.0

        # Out-of-Domain Confidence Rule:
        has_out_of_domain_term = any(term in norm_query for term in OUT_OF_DOMAIN_KEYWORDS)
        has_explicit_section = any(sec in norm_query for sec in ["420", "415", "417", "406", "302", "379", "428", "138", "120", "154", "9", "40", "৪২০", "৪০৬", "৩০২", "৩৭৯", "৪২৮", "১৩৮", "১২০", "১৫৪", "৯", "৪০"])

        is_low_confidence = (has_out_of_domain_term and not has_explicit_section) or (max_bm25 < 0.01 and max_vector_sim < 0.01)

        # 4. Dependency Expansion: Check if top match references a defining section
        doc_sec_numbers = {res["document"]["section_number"] for res in top_results}
        expanded_docs = list(top_results)

        if not is_low_confidence:
            for res in top_results:
                rel_secs = res["document"].get("related_sections", [])
                for rel_sec in rel_secs:
                    if rel_sec not in doc_sec_numbers and rel_sec in ["415", "405", "378", "429"]:
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
