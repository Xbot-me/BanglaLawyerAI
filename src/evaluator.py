import os
import json
import logging
from src.indexer import LegalIndexer
from src.retriever import HybridRetriever
from src.llm_explainer import LLMBengaliExplainer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 10 Realistic Bengali Legal Test Scenarios
BENCHMARK_QUESTIONS = [
    {
        "id": 1,
        "query": "কেউ যদি মিথ্যা কথা বলে আমার টাকা নিয়ে আর ফেরত না দেয়, তাহলে এটা কি প্রতারণা?",
        "expected_sections": ["415", "420"],
        "expect_low_confidence": False,
        "description": "Cheating with property delivery (Penal Code 415/420)"
    },
    {
        "id": 2,
        "query": "জমি দখল করে রাখলে আইনের ৪২০ ধারা কি প্রযোজ্য হবে?",
        "expected_sections": ["420"],
        "expect_low_confidence": False,
        "description": "Property dispute query specifying Section 420"
    },
    {
        "id": 3,
        "query": "আমার কোম্পানি ৩ মাস ধরে বেতন দেয় না, আইন কী বলে?",
        "expected_sections": [],
        "expect_low_confidence": True,
        "description": "Labour Law query (Out of current Penal Code dataset domain)"
    },
    {
        "id": 4,
        "query": "চেক ডিজঅনার বা বাউন্স করলে কোন ধারায় মামলা হয়?",
        "expected_sections": [],
        "expect_low_confidence": True,
        "description": "Cheque Dishonor / NI Act query (Out of Penal Code dataset domain)"
    },
    {
        "id": 5,
        "query": "ধারা ৪২০ এর শাস্তি কত বছরের?",
        "expected_sections": ["420"],
        "expect_low_confidence": False,
        "description": "Direct punishment question for Section 420"
    },
    {
        "id": 6,
        "query": "৪১৫ ও ৪২০ ধারার মধ্যে প্রধান পার্থক্য কী?",
        "expected_sections": ["415", "420"],
        "expect_low_confidence": False,
        "description": "Comparative question between Section 415 and 420"
    },
    {
        "id": 7,
        "query": "ব্যবসায়িক চুক্তি ভঙ্গ করলে কি সরাসরি ৪২০ ধারায় জেলে পাঠানো যাবে?",
        "expected_sections": ["420"],
        "expect_low_confidence": False,
        "description": "Contract breach vs criminal cheating distinction query"
    },
    {
        "id": 8,
        "query": "জাল দলিল তৈরি করে সম্পত্তি হাতিয়ে নিলে আইনের বিধান কী?",
        "expected_sections": ["420"],
        "expect_low_confidence": False,
        "description": "Forgery and valuable security cheating query"
    },
    {
        "id": 9,
        "query": "আমানত রাখা টাকা ফেরত না দিলে কোন ধারায় খেয়ানতের মামলা হয়?",
        "expected_sections": ["406"],
        "expect_low_confidence": False,
        "description": "Criminal breach of trust query (Section 406)"
    },
    {
        "id": 10,
        "query": "সাধারণ প্রতারণার সর্বোচ্চ শাস্তি কত দিনের বা কত বছরের?",
        "expected_sections": ["417", "415"],
        "expect_low_confidence": False,
        "description": "Punishment for general cheating query (Section 417)"
    }
]

def run_evaluation(retriever: HybridRetriever, explainer: LLMBengaliExplainer):
    print("\n" + "="*80)
    print("🇧🇩 BANGLADESH LEGAL KNOWLEDGE PLATFORM - BENCHMARK EVALUATION (10 QUESTIONS)")
    print("="*80 + "\n")

    passed_count = 0
    results_summary = []

    for test in BENCHMARK_QUESTIONS:
        qid = test["id"]
        query = test["query"]
        expected_secs = test["expected_sections"]
        expect_low_conf = test["expect_low_confidence"]
        desc = test["description"]

        retrieval = retriever.retrieve(query, top_k=2)
        explanation_res = explainer.explain(query, retrieval)

        top_matches = retrieval["top_matches"]
        retrieved_secs = [m["document"]["section_number"] for m in top_matches]
        is_low_conf = retrieval["is_low_confidence"]

        # Check retrieval correctness
        if expect_low_conf:
            # For out-of-domain queries, success means flagging low confidence
            passed = is_low_conf or (explanation_res["status"] == "LOW_CONFIDENCE")
            notes = "Correctly flagged out-of-domain query (Low Confidence Warning Triggered)" if passed else "Failed: Did not flag low confidence for missing law"
        else:
            # Check if at least one expected section is retrieved
            matched_sec = any(sec in retrieved_secs for sec in expected_secs)
            passed = matched_sec and not is_low_conf
            notes = f"Retrieved: {retrieved_secs} (Expected: {expected_secs})" if matched_sec else f"Failed: Found {retrieved_secs}, expected {expected_secs}"

        if passed:
            passed_count += 1
            status_str = "✅ PASSED"
        else:
            status_str = "❌ FAILED"

        results_summary.append({
            "id": qid,
            "query": query,
            "description": desc,
            "passed": passed,
            "status_str": status_str,
            "retrieved_sections": retrieved_secs,
            "max_confidence_score": retrieval["max_confidence_score"],
            "is_low_confidence": is_low_conf,
            "notes": notes,
            "formatted_answer": explanation_res["formatted_answer"]
        })

        print(f"Test #{qid}: {query}")
        print(f"   Status: {status_str} | Max Score: {retrieval['max_confidence_score']:.4f}")
        print(f"   Notes: {notes}")
        print("-" * 80)

    accuracy_pct = (passed_count / len(BENCHMARK_QUESTIONS)) * 100
    print(f"\n📊 FINAL BENCHMARK SCORE: {passed_count}/{len(BENCHMARK_QUESTIONS)} ({accuracy_pct:.1f}% Accuracy)")
    print("="*80 + "\n")

    return {
        "passed_count": passed_count,
        "total_count": len(BENCHMARK_QUESTIONS),
        "accuracy_pct": accuracy_pct,
        "details": results_summary
    }

if __name__ == "__main__":
    from src.scraper import fetch_and_preserve_raw
    from src.parser import parse_raw_documents

    fetch_and_preserve_raw()
    parse_raw_documents()
    
    idx = LegalIndexer()
    idx.build_all()
    
    ret = HybridRetriever(idx)
    exp = LLMBengaliExplainer()
    
    run_evaluation(ret, exp)
