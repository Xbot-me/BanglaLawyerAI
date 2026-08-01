#!/usr/bin/env python3
"""
Bangladesh Legal Knowledge Platform - Main Prototype Entry Point
"""
import os
import sys
import logging

from src.scraper import fetch_and_preserve_raw
from src.parser import parse_raw_documents
from src.indexer import LegalIndexer
from src.retriever import HybridRetriever
from src.llm_explainer import LLMBengaliExplainer
from src.evaluator import run_evaluation

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    print("""
====================================================================
🇧🇩 BANGLADESH LEGAL KNOWLEDGE PLATFORM - PHASE 1 PROTOTYPE ENGINE 🇧🇩
====================================================================
Ground Truth Legal RAG & Simple Bengali Explanation System
Official Data Source: bdlaws.minlaw.gov.bd
""")

    # Step 1: Raw Data Collection & Preservation
    logger.info("[Step 1/5] Ingesting and preserving raw official HTML documents...")
    files, sections = fetch_and_preserve_raw()
    print(f"   ✓ Preserved {len(files)} raw HTML files under storage/raw/bdlaws/")

    # Step 2: Parsing & Structured Record Generation
    logger.info("[Step 2/5] Cleaning text & building structured JSON records...")
    records = parse_raw_documents()
    print(f"   ✓ Extracted {len(records)} legal section records with metadata into storage/processed/sections.json")

    # Step 3: Hybrid Search Indexing
    logger.info("[Step 3/5] Building BM25 keyword index and multilingual dense vector embeddings...")
    indexer = LegalIndexer()
    indexer.build_all()
    print("   ✓ BM25 index and dense vector embedding matrix constructed successfully.")

    # Step 4: Initialize Retriever and LLM Explainer
    retriever = HybridRetriever(indexer)
    explainer = LLMBengaliExplainer()

    # Step 5: Run Evaluation Benchmark
    logger.info("[Step 5/5] Executing 10-Question Benchmark Suite...")
    eval_results = run_evaluation(retriever, explainer)

    # Sample interactive query demonstration
    sample_q = "জমি দখল করে প্রতারণা করার চেষ্টা করলে ধারা ৪২০ কি প্রযোজ্য হবে?"
    print("\n" + "="*80)
    print(f"💡 DEMONSTRATION QUERY: '{sample_q}'")
    print("="*80)

    retrieval_res = retriever.retrieve(sample_q, top_k=2)
    ans = explainer.explain(sample_q, retrieval_res)
    print(ans["formatted_answer"])
    print("="*80 + "\n")

    return eval_results

if __name__ == "__main__":
    main()
