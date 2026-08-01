import os
import json
import math
import logging
import numpy as np
from rank_bm25 import BM25Okapi

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "processed"))
EMBEDDINGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "embeddings"))

# General question stopwords to exclude from BM25 scoring so generic terms like 'আইন' or 'ধারা' don't cause false hits
BENGALI_STOPWORDS = {
    "আইন", "কী", "কি", "বলে", "বলুন", "বলেন", "কোন", "ধারায়", "ধারায়", "ধারা", "মামলা", "হয়", "হয়", 
    "করা", "করায়", "করালে", "হলে", "হল", "যায়", "যায়", "জন্য", "থাকে", "থাকলে", "কোনটি", "কীভাবে",
    "কেমন", "এর", "এবং", "বা", "বাস্তব", "সম্পর্কে", "সম্পর্কিত", "বিবরণ", "অধীনে", "অধীন",
    "law", "section", "act", "under", "what", "which", "is", "are", "the", "for", "in", "of"
}

class PurePythonNgramVectorizer:
    """
    Pure Python + NumPy Multilingual Character & Word N-gram Vectorizer.
    Provides semantic cosine similarity across Bengali and English without native lib dependencies.
    """
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
            # Word token
            ngrams.append(f"w_{clean_word}")
            # Character ngrams for subword matching (captures Bengali word inflections)
            padded = f"^{clean_word}$"
            for n in range(self.ngram_range[0], self.ngram_range[1] + 1):
                for i in range(len(padded) - n + 1):
                    ngrams.append(padded[i:i+n])
        return ngrams

    def fit_transform(self, corpus_texts):
        doc_ngrams_list = [self._get_ngrams(text) for text in corpus_texts]
        df = {}
        N = len(corpus_texts)
        
        for doc_ngrams in doc_ngrams_list:
            unique_ngrams = set(doc_ngrams)
            for ng in unique_ngrams:
                df[ng] = df.get(ng, 0) + 1
                
        self.vocab = {ng: idx for idx, ng in enumerate(sorted(df.keys()))}
        self.idf = {ng: math.log((N + 1) / (df[ng] + 1)) + 1.0 for ng in df}
        
        vocab_size = len(self.vocab)
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
        vocab_size = len(self.vocab)
        vec = np.zeros((1, vocab_size), dtype=np.float32)
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

    def load_documents(self, json_path=None):
        if json_path is None:
            json_path = os.path.join(PROCESSED_DIR, "sections.json")
            
        with open(json_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)
            
        logger.info(f"Loaded {len(self.documents)} documents for indexing.")
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
        for doc in self.documents:
            # Include section number explicitly and content keywords
            text = f"{doc['section_number']} धारा {doc['section_number']} {doc['section_title_bn']} {doc['section_title_en']} {doc['content_bn']} {doc['content_en']} {' '.join(doc['keywords'])}"
            tokens = self._tokenize(text, remove_stopwords=True)
            corpus_tokens.append(tokens)
            
        self.bm25 = BM25Okapi(corpus_tokens)
        logger.info("BM25 keyword index constructed successfully.")

    def build_vector_index(self):
        os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
        raw_corpus = [f"{doc['section_number']} {doc['section_title_bn']} {doc['content_bn']} {doc['content_en']} {' '.join(doc['keywords'])}" for doc in self.documents]
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
