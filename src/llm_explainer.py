import os
import re
import logging
import json
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configurable LLM Provider: "llama_groq", "llama_ollama", "gemini", or "ground_truth"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "llama_groq" if GROQ_API_KEY else "ground_truth")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

class LLMBengaliExplainer:
    """
    Ground-Truth Legal Decision Explainer with Groq Llama 3.3 70B Integration & Strict Safety Rules.
    - Zero Truncation (Max Tokens = 2000).
    - Zero Hallucinated Case Law.
    - Zero Fake Percentage Scores.
    """

    def __init__(self, provider: str = LLM_PROVIDER):
        self.provider = provider
        logger.info(f"Initialized LLMBengaliExplainer with provider: {self.provider}")

    def _call_llama_groq(self, act_bn: str, sec_num: str, content_bn: str, query: str) -> str:
        """
        Calls Groq API (Llama 3.3 70B) with 2000 max_tokens to prevent Bengali token truncation.
        """
        api_key = os.getenv("GROQ_API_KEY") or GROQ_API_KEY
        if not api_key:
            logger.info("GROQ_API_KEY not set. Operating in Ground-Truth Engine mode.")
            return ""
            
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            system_prompt = (
                "You are an expert Bangladesh Legal Assistant. Explain the provided statutory law text "
                "in simple, complete, conversational, empathetic Bengali for an ordinary citizen.\n"
                "CRITICAL RULES:\n"
                "1. Always finish your sentences completely. Do NOT cut off mid-sentence.\n"
                "2. Do NOT invent fake court case names, legal precedents, or win percentages.\n"
                "3. Base your response ONLY on the provided ground-truth statutory law text.\n"
                "4. If the provided section does NOT actually answer the user's question (e.g. the section is about "
                "appointing an Inspector-General but the user asks about police assault), you MUST say clearly "
                "in Bengali that this section is not relevant to the question and advise consulting a registered lawyer "
                "or the official bdlaws portal. Do NOT force an irrelevant section to fit the query.\n"
                "5. When the section IS relevant, explain rights and practical next steps simply."
            )
            user_prompt = (
                f"আইনের নাম: {act_bn}\n"
                f"ধারা নম্বর: {sec_num}\n"
                f"অফিশিয়াল আইনের হুবহু টেক্সট: \"{content_bn}\"\n\n"
                f"ব্যবহারকারীর প্রশ্ন: \"{query}\"\n\n"
                f"উপরের অফিশিয়াল আইনটি ব্যবহারকারীর প্রশ্নের সাথে প্রাসঙ্গিক কিনা বিচার করুন। "
                f"প্রাসঙ্গিক হলে সংক্ষিপ্ত, স্পষ্ট, সম্পূর্ণ বাংলায় ব্যাখ্যা দিন এবং কী করা যায় তা বলুন। "
                f"প্রাসঙ্গিক না হলে স্পষ্ট করে বলুন যে এই ধারাটি প্রশ্নের উত্তর নয়। বাক্য পূর্ণাঙ্গভাবে শেষ করুন।"
            )
            
            for model_name in [GROQ_MODEL, "llama-3.3-70b-versatile", "llama3-70b-8192", "llama-3.1-8b-instant"]:
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 2000
                }
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=8
                )
                if response.status_code == 200:
                    result = response.json()
                    explanation = result["choices"][0]["message"]["content"].strip()
                    logger.info(f"Successfully generated Groq ({model_name}) complete explanation ({len(explanation)} chars).")
                    return explanation
                else:
                    logger.warning(f"Groq API model {model_name} returned status code {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Groq Llama API call failed ({e}). Falling back to ground-truth engine.")
        return ""

    def _is_section_relevant(self, query: str, doc: dict, rrf_score: float) -> bool:
        """Heuristic relevance guard: reject clearly mismatched top hits."""
        q = (query or "").lower()
        title = f"{doc.get('section_title_en', '')} {doc.get('section_title_bn', '')}".lower()
        content = f"{doc.get('content_en', '')} {doc.get('content_bn', '')}".lower()
        sec = str(doc.get("section_number", "")).lower()
        kws = " ".join(doc.get("keywords") or []).lower()

        # Hard reject: pure administrative Police Act appointment sections for assault queries
        police_assault_signals = [
            "police", "pulish", "পুলিশ", "ojotha", "marse", "marche", "beating",
            "assault", "মারধর", "আঘাত", "নির্যাতন", "torture", "amare mar"
        ]
        admin_markers = [
            "inspector-general", "inspector general", "appointing persons to exercise",
            "appoint some person to exercise", "2b", "general police-district"
        ]
        if any(s in q for s in police_assault_signals):
            if any(m in title or m in content or m in kws for m in admin_markers):
                logger.warning(f"Relevance guard rejected admin section {sec} for assault query.")
                return False
            # Prefer hurt / torture sections
            if sec in {"323", "324", "325", "326", "323-325+torture"}:
                return True

        # Very weak score → not relevant
        if rrf_score < 0.15:
            return False

        # Basic token overlap with title/keywords/content
        q_tokens = set(t for t in re.findall(r"\b\w+\b", q) if len(t) > 2)
        doc_tokens = set(t for t in re.findall(r"\b\w+\b", title + " " + kws + " " + content[:500]) if len(t) > 2)
        if not q_tokens:
            return True
        overlap = q_tokens & doc_tokens
        if len(overlap) == 0 and rrf_score < 0.35:
            return False
        return True

    def explain(self, query: str, retrieval_result: dict) -> dict:
        is_low_conf = retrieval_result.get("is_low_confidence", False)
        matches = retrieval_result.get("top_matches", [])
        max_score = retrieval_result.get("max_confidence_score", 0.0)

        # 1. Low Confidence Fallback Handler
        if is_low_conf or not matches:
            return {
                "query": query,
                "status": "LOW_CONFIDENCE",
                "max_confidence_score": max_score,
                "sections": self._build_low_confidence_sections(query)
            }

        # 2. Relevance guard — pick first relevant match, else low-confidence
        primary_match = None
        primary_score = 0.0
        for m in matches:
            doc = m["document"]
            score = float(m.get("rrf_score", 0))
            if self._is_section_relevant(query, doc, score):
                primary_match = doc
                primary_score = score
                break

        if primary_match is None:
            logger.warning("No relevant section after relevance guard — returning LOW_CONFIDENCE.")
            return {
                "query": query,
                "status": "LOW_CONFIDENCE",
                "max_confidence_score": max_score,
                "sections": self._build_low_confidence_sections(query)
            }

        # 3. Call Groq Llama 3.3 70B API
        api_key = os.getenv("GROQ_API_KEY") or GROQ_API_KEY
        llama_output = ""
        if api_key or self.provider == "llama_groq":
            llama_output = self._call_llama_groq(
                act_bn=primary_match["act_name_bn"],
                sec_num=primary_match["section_number"],
                content_bn=primary_match["content_bn"],
                query=query
            )

        sections = self._build_dynamic_sections(query, primary_match, llama_output)

        return {
            "query": query,
            "status": "SUCCESS",
            "provider_used": "Groq Llama 3.3 70B Cloud API" if llama_output else "Ground-Truth Verified Engine",
            "max_confidence_score": primary_score or max_score,
            "sections": sections
        }

    def _build_low_confidence_sections(self, query: str) -> list:
        return [
          {
            "id": 1,
            "title": "আসল আইনটি কী বলে?",
            "open": False,
            "html": f"""<div class="highlight-box">
              <p><strong>⚠️ অফিশিয়াল ডেটাবেসে অনুপস্থিত:</strong> আমাদের সংকলিত ডেটাবেসে আপনার এই নির্দিষ্ট ঘটনার সুনির্দিষ্ট আইন পাওয়া যায়নি।</p>
            </div>
            <a href="http://bdlaws.minlaw.gov.bd" class="source-link" target="_blank" rel="noopener noreferrer">সরকারি অফিশিয়াল পোর্টাল দেখুন (bdlaws.minlaw.gov.bd) →</a>"""
          },
          {
            "id": 2,
            "title": "সহজ বাংলায় বুঝুন",
            "open": True,
            "html": f"""<div class="simple-text">
              <p>আপনার প্রশ্ন: <strong>"{query}"</strong></p>
              <p>সঠিক আইনি অনুচ্ছেদ ছাড়া অনুমানভিত্তিক তথ্য দেওয়া বিপজ্জনক। ভুল ধারায় মামলা দায়ের করলে মামলা খারিজ হয়ে যাওয়ার ঝুঁকি থাকে।</p>
              <div class="highlight-box">
                <p><strong>পরামর্শ:</strong> বাংলাদেশ বার কাউন্সিলের নিবন্ধিত আইনজীবীর সরাসরি সহায়তা নিন অথবা জাতীয় আইনি সহায়তা সংস্থা (NLASO - ১৬৪৩০) তে যোগাযোগ করুন।</p>
              </div>
            </div>"""
          }
        ]

    def _get_dynamic_content_for_section(self, doc: dict) -> tuple:
        act_id = doc.get("act_id")
        sec_num = str(doc.get("section_number"))

        if sec_num in ("323", "324", "325", "323-325+Torture", "323-325+torture"):
            ex_html = """<div class="example-item">
              <div class="example-label">পরিস্থিতি ১ — পুলিশ বা অন্য কারো অযথা মারধর (ধারা ৩২৩/৩২৪/৩২৫)</div>
              <p class="example-text">পুলিশ বা কোনো ব্যক্তি যদি অযথা (ojotha) আপনাকে মারধর করে, লাঠিচার্জ করে বা হেফাজতে নির্যাতন করে — এটি বেআইনি। দণ্ডবিধির ৩২৩ (সাধারণ আঘাত), ৩২৪ (বিপজ্জনক অস্ত্র), ৩২৫ (গুরুতর আঘাত) এবং নির্যাতন আইন ২০১৩ প্রযোজ্য হতে পারে।</p>
            </div>"""

            ev_html = """<div class="evidence-category">
              <div class="evidence-header"><div class="evidence-dot strong" aria-hidden="true"></div><div class="evidence-title">প্রাথমিক শক্ত প্রমাণ (Primary Evidence)</div></div>
              <ul class="evidence-list">
                <li><strong>মেডিকেল সার্টিফিকেট / সুরতহাল রিপোর্ট:</strong> সরকারি হাসপাতালের ডাক্তারি প্রমাণ</li>
                <li><strong>CCTV / মোবাইল ভিডিও / প্রত্যক্ষদর্শী:</strong> ঘটনার সরাসরি প্রমাণ</li>
                <li><strong>আঘাতের ছবি ও পোশাক:</strong> শারীরিক আঘাতের দৃশ্যমান প্রমাণ</li>
              </ul>
            </div>"""

            st_html = """<div class="step-flow">
              <div class="step-item"><div class="step-circle" aria-hidden="true">১</div><div class="step-text"><strong>তাৎক্ষণিক সরকারি হাসপাতালে সুরতহাল / মেডিকেল সার্টিফিকেট করান</strong></div></div>
              <div class="step-item"><div class="step-circle" aria-hidden="true">২</div><div class="step-text"><strong>নিকটস্থ থানায় এজাহার/জিডি দায়ের করুন; না নিলে ম্যাজিস্ট্রেট আদালতে সরাসরি অভিযোগ করুন</strong></div></div>
              <div class="step-item"><div class="step-circle" aria-hidden="true">৩</div><div class="step-text"><strong>জেলা পুলিশ সুপার (SP) / কমিশনার বরাবর লিখিত অভিযোগ দিন</strong></div></div>
              <div class="step-item"><div class="step-circle" aria-hidden="true">৪</div><div class="step-text"><strong>জাতীয় মানবাধিকার কমিশন (NHRC) এবং রেজিস্টার্ড আইনজীবীর সহায়তা নিন</strong></div></div>
            </div>"""

            return ex_html, ev_html, st_html

        elif sec_num == "428":
            ex_html = """<div class="example-item">
              <div class="example-label">পরিস্থিতি ১ — পশু হত্যা বা নির্যাতন (ধারা ৪২৮) প্রযোজ্য হওয়ার সম্ভাবনা</div>
              <p class="example-text">কেউ যদি অন্যায়ভাবে আপনার পোষা বিড়াল, কুকুর বা অন্য কোনো প্রাণীকে বিষপ্রয়োগে বা পিটিয়ে হত্যা করে বা পঙ্গু বানায়।</p>
            </div>"""

            ev_html = """<div class="evidence-category">
              <div class="evidence-header"><div class="evidence-dot strong" aria-hidden="true"></div><div class="evidence-title">প্রাথমিক শক্ত প্রমাণ (Primary Evidence)</div></div>
              <ul class="evidence-list">
                <li><strong>পশু চিকিৎসকের (Vet) সুরতহাল / ময়নাতদন্ত রিপোর্ট:</strong> প্রাণীকে হত্যা বা বিষপ্রয়োগের মেডিকেল সনদ</li>
                <li><strong>CCTV ফুটেজ বা ভিডিও:</strong> সরাসরি আঘাতের প্রমাণ</li>
              </ul>
            </div>"""

            st_html = """<div class="step-flow">
              <div class="step-item"><div class="step-circle" aria-hidden="true">১</div><div class="step-text"><strong>পশু চিকিৎসকের মাধ্যমে প্রাথমিক আঘাতের রিপোর্ট তৈরি করুন</strong></div></div>
              <div class="step-item"><div class="step-circle" aria-hidden="true">২</div><div class="step-text"><strong>নিকটস্থ থানায় লিখিত অভিযোগ/জিডি অথবা ম্যাজিস্ট্রেট আদালতে সিআর মামলা দায়ের করুন</strong></div></div>
            </div>"""

            return ex_html, ev_html, st_html

        elif sec_num == "379":
            ex_html = """<div class="example-item">
              <div class="example-label">পরিস্থিতি ১ — চুরি (ধারা ৩৭৯) প্রযোজ্য হওয়ার সম্ভাবনা</div>
              <p class="example-text">আপনার সম্মতি ছাড়া অসাধু উদ্দেশ্যে কেউ আপনার টাকা, মানিব্যাগ, মোবাইল বা মালামাল চুরি করে সরিয়ে নিয়ে গেছে।</p>
            </div>"""

            ev_html = """<div class="evidence-category">
              <div class="evidence-header"><div class="evidence-dot strong" aria-hidden="true"></div><div class="evidence-title">প্রাথমিক শক্ত প্রমাণ (Primary Evidence)</div></div>
              <ul class="evidence-list">
                <li><strong>CCTV ফুটেজ বা চুরির ঘটনার সরাসরি ভিডিও/ছবি</strong></li>
                <li><strong>চুরি যাওয়া পণ্যের রসিদ / ক্যাশ মেমো / আইএমইআই নম্বর</strong></li>
              </ul>
            </div>"""

            st_html = """<div class="step-flow">
              <div class="step-item"><div class="step-circle" aria-hidden="true">১</div><div class="step-text"><strong>চুরির স্থান ও সময় উল্লেখ করে নিকটস্থ থানায় জিডি/এজাহার দায়ের করুন</strong></div></div>
              <div class="step-item"><div class="step-circle" aria-hidden="true">২</div><div class="step-text"><strong>চুরি হওয়া পণ্যের মেমো, আইএমইআই বা সিসিটিভি ফুটেজ পুলিশের কাছে জমা দিন</strong></div></div>
            </div>"""

            return ex_html, ev_html, st_html

        elif sec_num == "302":
            ex_html = """<div class="example-item">
              <div class="example-label">পরিস্থিতি ১ — নির্দোষ ব্যক্তিকে মিথ্যা হত্যা মামলায় (ধারা ৩০২) আসামি করা</div>
              <p class="example-text">ঝগড়া বা মারামারির সময় আপনি সেখানে ছিলেন না বা অন্য কোথাও ছিলেন, কিন্তু শত্রুতার জেরে এজাহারে আপনার নাম দেওয়া হয়েছে।</p>
            </div>"""

            ev_html = """<div class="evidence-category">
              <div class="evidence-header"><div class="evidence-dot strong" aria-hidden="true"></div><div class="evidence-title">প্রাথমিক শক্ত প্রমাণ (Primary Evidence of Alibi)</div></div>
              <ul class="evidence-list">
                <li><strong>CCTV ফুটেজ বা ডিজিটাল লোকেশন রেকর্ড:</strong> ঘটনার সময় অন্য স্থানে অবস্থানের রেকর্ড</li>
                <li><strong>অফিশিয়াল ডিউটি রোস্টার বা বাস/ট্রেন/বিমান টিকেট</strong></li>
              </ul>
            </div>"""

            st_html = """<div class="step-flow">
              <div class="step-item"><div class="step-circle" aria-hidden="true">১</div><div class="step-text"><strong>ঘটনার সময় অন্য কোথাও উপস্থিত থাকার (Alibi) প্রমাণ সংগ্রহ করুন</strong></div></div>
              <div class="step-item"><div class="step-circle" aria-hidden="true">২</div><div class="step-text"><strong>বিজ্ঞ জেলা ও দায়রা জজ বা হাইকোর্ট বিভাগে আগাম জামিনের (Anticipatory Bail) আবেদন করুন</strong></div></div>
            </div>"""

            return ex_html, ev_html, st_html

        else:
            ex_html = f"""<div class="example-item">
              <div class="example-label">পরিস্থিতি ১ — ধারা {sec_num} প্রযোজ্য হওয়ার সম্ভাবনা</div>
              <p class="example-text">যদি সূচনালগ্নেই অসৎ উদ্দেশ্যে মিথ্যা তথ্য বা ভুয়া কাগজ দেখিয়ে সম্পত্তি নেওয়া হয়।</p>
            </div>"""

            ev_html = """<div class="evidence-category">
              <div class="evidence-header"><div class="evidence-dot strong" aria-hidden="true"></div><div class="evidence-title">প্রাথমিক শক্ত প্রমাণ (Primary Evidence)</div></div>
              <ul class="evidence-list">
                <li><strong>ব্যাংক স্টেটমেন্ট ও ক্যাশ রসিদ:</strong> অর্থ হস্তান্তরের অফিশিয়াল প্রমাণ</li>
              </ul>
            </div>"""

            st_html = """<div class="step-flow">
              <div class="step-item"><div class="step-circle" aria-hidden="true">১</div><div class="step-text"><strong>সব প্রমাণ সংগ্রহ করে স্থানীয় থানায় জিডি বা আদালতে মামলা করুন</strong></div></div>
            </div>"""

            return ex_html, ev_html, st_html

    def _build_dynamic_sections(self, query: str, doc: dict, llama_output: str = "") -> list:
        sec_num = doc["section_number"]
        act_bn = doc["act_name_bn"]
        title_bn = doc["section_title_bn"]
        url = doc["source_url"]
        content_bn = doc["content_bn"]

        def format_sec(sn: str) -> str:
            return f"ধারা {sn}" if sn and sn[0].isdigit() else sn

        sec_formatted = format_sec(sec_num)

        sec1_html = f"""<div class="law-quote">
          "{content_bn}"
          <br><br>
          <strong>{act_bn} — {sec_formatted} ({title_bn})</strong>
        </div>
        <a href="{url}" class="source-link" target="_blank" rel="noopener noreferrer">
          সরকারি অফিশিয়াল উৎস দেখুন (bdlaws.minlaw.gov.bd) →
        </a>"""

        if llama_output:
            easy_exp = f"""<div style="background:#f0fdf4; border:1px solid #86efac; padding:12px 16px; border-radius:10px; margin-bottom:12px;">
              <span style="background:#16a34a; color:white; padding:2px 8px; border-radius:6px; font-size:0.8rem; font-weight:700;">🦙 Groq Llama 3.3 70B বিশ্লেষণ</span>
              <p style="margin-top:8px; font-size:1.05rem; line-height:1.7;">{llama_output}</p>
            </div>"""
        else:
            easy_exp = doc.get("easy_explanation_bn", f"যদি কেউ আইনের বিধান লঙ্ঘন করে, তবে {act_bn}-এর {sec_num} ধারা অনুযায়ী ব্যবস্থা নেওয়া যায়।")

        sec2_html = f"""<div class="simple-text">
          {easy_exp}
          <div class="highlight-box">
            <p><strong>মনে রাখবেন:</strong> যেকোনো আইনি পদক্ষেপে মামলার উপযুক্ত বিচারিক এখতিয়ার ও প্রমাণপত্র উপস্থাপন করা আবশ্যক।</p>
          </div>
        </div>"""

        ex_html, ev_html, st_html = self._get_dynamic_content_for_section(doc)

        sec3_html = f"""<div style="background:#fef3c7; border:1px solid #f59e0b; padding:10px 14px; border-radius:8px; margin-bottom:14px; font-size:0.9rem; color:#92400e;">
          ⚠️ <strong>সাধারণ নির্দেশনা:</strong> নিচের পরিস্থিতিগুলো {act_bn}-এর {sec_formatted} সহজভাবে বোঝার সুবিধার্থে তৈরি করা হয়েছে।
        </div>{ex_html}"""

        sec4_html = f"""<div style="background:#fef3c7; border:1px solid #f59e0b; padding:10px 14px; border-radius:8px; margin-bottom:14px; font-size:0.9rem; color:#92400e;">
          ⚠️ <strong>সাধারণ নির্দেশিকা:</strong> {act_bn}-এর {sec_formatted}-এ প্রয়োজনীয় প্রমাণের তালিকা।
        </div>{ev_html}"""

        sec5_html = f"""<div style="background:#fef3c7; border:1px solid #f59e0b; padding:10px 14px; border-radius:8px; margin-bottom:14px; font-size:0.9rem; color:#92400e;">
          ⚠️ <strong>সাধারণ পদক্ষেপ:</strong> যেকোনো আনুষ্ঠানিক পদক্ষেপের পূর্বে রেজিস্টার্ড আইনজীবীর পরামর্শ নেওয়া উচিত।
        </div>{st_html}"""

        sections = [
            {"id": 1, "title": "আসল আইনটি কী বলে?", "open": False, "html": sec1_html},
            {"id": 2, "title": "সহজ বাংলায় বুঝুন (Groq Llama 3.3 70B)", "open": True, "html": sec2_html},
            {"id": 3, "title": f"বাস্তব উদাহরণ ({act_bn} — {sec_formatted})", "open": False, "html": sec3_html},
            {"id": 4, "title": f"কী প্রমাণ লাগবে? ({sec_formatted}-এর জন্য)", "open": False, "html": sec4_html},
            {"id": 5, "title": "কী করবেন? — ধাপে ধাপে (সাধারণ পদক্ষেপ)", "open": False, "html": sec5_html}
        ]

        return sections
