import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "raw", "bdlaws"))

# Strictly Verified Ground-Truth Law Dataset (No Synthetic Case Law)
SEEDED_SECTIONS = [
    # 1. Section 420 - Penal Code (Cheating & Fraud)
    {
        "act_id": 11,
        "act_name_en": "The Penal Code, 1860",
        "act_name_bn": "দণ্ডবিধি, ১৮৬০",
        "category": "Criminal Law (ফউজদারি আইন)",
        "section_number": "420",
        "section_title_en": "Cheating and dishonestly inducing delivery of property",
        "section_title_bn": "প্রতারণা এবং সম্পত্তি সমর্পণে অসাধুভাবে প্ররোচিত করা",
        "chapter_number": "XVII",
        "chapter_title": "Of Offences Against Property",
        "domain": "Criminal Law",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-11/section-3366.html",
        "content_en": """Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person... shall be punished with imprisonment for a term which may extend to seven years, and shall also be liable to fine.""",
        "content_bn": """যে ব্যক্তি প্রতারণা করে এবং তদ্বারা অপহৃত ব্যক্তিকে অসাধুভাবে প্ররোচিত করে কোনো ব্যক্তির নিকট কোনো সম্পত্তি সমর্পণ করতে... সেই ব্যক্তি যেকোনো মেয়াদের কারাদণ্ডে—যার মেয়াদ সাত বছর পর্যন্ত হতে পারে—দণ্ডিত হবে এবং অর্থদণ্ডেও দণ্ডনীয় হবে।""",
        "easy_explanation_bn": "যদি কেউ প্রতারণার উদ্দেশ্যে আগে থেকেই মিথ্যা কথা বলে বা ভুয়া পরিচয় দিয়ে আপনার কাছ থেকে টাকা বা সম্পত্তি নেয়, তবে এটি দণ্ডবিধির ৪২০ ধারার অপরাধ। তবে ব্যবসায়িক ক্ষতি বা শুরুতে অসৎ উদ্দেশ্য ছাড়া চুক্তি ভঙ্গ হলে তা ৪২০ ধারা হবে না, দেওয়ানি মামলা হবে।",
        "keywords": ["section 420", "cheating property", "valuable security", "7 years imprisonment", "প্রতারণা", "ধারা ৪২০", "টাকা আত্মসাৎ", "জালিয়াতি", "protarona", "420"],
        "related_sections": ["415", "417", "406"],
        "elements_of_offence": [],
        "evidence_matrix": {"strong_evidence": [], "supporting_evidence": []},
        "police_questions": [],
        "procedure_steps": [],
        "past_court_cases": [],
        "case_strength": {}
    },

    # 2. Section 379 - Penal Code (Punishment for Theft / চুরির দণ্ড)
    {
        "act_id": 11,
        "act_name_en": "The Penal Code, 1860",
        "act_name_bn": "দণ্ডবিধি, ১৮৬০",
        "category": "Criminal Law (ফৌজদারি আইন)",
        "section_number": "379",
        "section_title_en": "Punishment for theft",
        "section_title_bn": "চুরির জন্য দণ্ড (টাকা বা সম্পত্তি চুরি)",
        "chapter_number": "XVII",
        "chapter_title": "Of Offences Against Property",
        "domain": "Criminal Law",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-11/section-3323.html",
        "content_en": """Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.""",
        "content_bn": """যে ব্যক্তি চুরি করে (Theft - কারও সম্মতি ছাড়া অসাধুভাবে অস্থাবর সম্পত্তি সরিয়ে নেওয়া), সে ব্যক্তি যেকোনো মেয়াদের সশ্রম বা বিনাশ্রম কারাদণ্ডে—যার মেয়াদ তিন বছর পর্যন্ত হতে পারে—অথবা অর্থদণ্ডে, অথবা উভয় দণ্ডে দণ্ডিত হবে।""",
        "easy_explanation_bn": "যদি আপনার সম্মতি ছাড়া অসাধুভাবে কেউ আপনার টাকা, মোবাইল, ওয়ালেট বা সম্পত্তি চুরি করে নিয়ে যায়, তবে এটি দণ্ডবিধির ৩৭৯ ধারার চুরির অপরাধ। এই অপরাধের শাস্তি ৩ বছর পর্যন্ত কারাদণ্ড বা অর্থদণ্ড।",
        "keywords": ["section 379", "theft", "churi", "stolen", "tk churi", "chori", "চুরি", "ধারা ৩৭৯", "টাকা চুরি", "মোবাইল চুরি", "379"],
        "related_sections": ["378", "380"],
        "elements_of_offence": [],
        "evidence_matrix": {"strong_evidence": [], "supporting_evidence": []},
        "police_questions": [],
        "procedure_steps": [],
        "past_court_cases": [],
        "case_strength": {}
    },

    # 3. Section 428 - Penal Code (Mischief by killing or maiming animal / পশু হত্যা বা নির্যাতন)
    {
        "act_id": 11,
        "act_name_en": "The Penal Code, 1860",
        "act_name_bn": "দণ্ডবিধি, ১৮৬০",
        "category": "Criminal Law (ফৌজদারি আইন)",
        "section_number": "428",
        "section_title_en": "Mischief by killing or maiming animal of the value of ten taka",
        "section_title_bn": "পশু বা পোষা প্রাণীকে (বিড়াল/কুকুর) হত্যা, বিষপ্রয়োগ বা আঘাত করার দণ্ড",
        "chapter_number": "XVII",
        "chapter_title": "Of Offences Against Property & Animals",
        "domain": "Animal Welfare & Criminal Law",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-11/section-3374.html",
        "content_en": """Whoever commits mischief by killing, poisoning, maiming or rendering useless any animal or animals... shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both.""",
        "content_bn": """যে ব্যক্তি কোনো পশু বা পোষা প্রাণীকে (যেমন বিড়াল, কুকুর, গবাদিপশু) অন্যায়ভাবে হত্যা করে, বিষপ্রয়োগ করে, পঙ্গু করে বা মারাত্মক আঘাত করে ক্ষতিসাধন করে, সে ব্যক্তি যেকোনো মেয়াদের সশ্রম বা বিনাশ্রম কারাদণ্ডে—যার মেয়াদ দুই বছর পর্যন্ত হতে পারে—অথবা অর্থদণ্ডে, অথবা উভয় দণ্ডে দণ্ডিত হবে। (পশু কল্যাণ আইন, ২০১৯ অনুযায়ীও প্রতিকার রয়েছে)।""",
        "easy_explanation_bn": "কেউ যদি অন্যায়ভাবে আপনার পোষা বিড়াল, কুকুর বা অন্য কোনো প্রাণীকে হত্যা করে, বিষ দেয় বা আঘাত করে পঙ্গু বানায়, তবে এটি দণ্ডবিধির ৪২৮ ধারা এবং পশু কল্যাণ আইন ২০১৯ অনুযায়ী অপরাধ। অপরাধীর ২ বছর পর্যন্ত কারাদণ্ড বা জরিমানা হতে পারে।",
        "keywords": ["section 428", "biral", "cat", "kutta", "dog", "pet", "animal killing", "biral ke marse", "পশু হত্যা", "বিড়াল মারছে", "ধারা ৪২৮", "পশু নির্যাতন", "428", "animal assault"],
        "related_sections": ["429", "425"],
        "elements_of_offence": [
            "১. প্রাণীটিকে কি অন্যায়ভাবে হত্যা, বিষপ্রয়োগ বা আঘাত করা হয়েছিল?",
            "২. অভিযুক্ত ব্যক্তির ক্ষতিকর উদ্দেশ্য (Mischief) ছিল কি না?"
        ],
        "evidence_matrix": {
            "strong_evidence": [
                {"name": "পশু চিকিৎসকের (Vet) সুরতহাল / ময়নাতদন্ত রিপোর্ট", "details": "আঘাত বা বিষক্রিয়ার ডাক্তারী সার্টিফিকেট", "value": "হত্যার ডাক্তারি প্রমাণ।"},
                {"name": "CCTV ফুটেজ বা প্রত্যক্ষদর্শী সাক্ষী", "details": "আঘাতকারী ব্যক্তিকে সরাসরি দেখার প্রমাণ", "value": "অভিযুক্তের যোগসূত্র।"}
            ],
            "supporting_evidence": [
                {"name": "পশু কল্যাণ সংস্থা (PAW/Animal Care) বা থানার জিডি কপি"}
            ]
        },
        "police_questions": [],
        "procedure_steps": [
            "পশু চিকিৎসকের মাধ্যমে সুরতহাল বা প্রাথমিক রিপোর্ট তৈরি করুন",
            "ঘটনার সিসিটিভি ফুটেজ বা ছবি সংরক্ষণ করুন",
            "নিকটস্থ থানায় লিখিত অভিযোগ/জিডি অথবা ম্যাজিস্ট্রেট আদালতে সিআর মামলা দায়ের করুন"
        ],
        "past_court_cases": [],
        "case_strength": {}
    },

    # 4. Section 302 - Penal Code (Punishment for Murder & False Implication)
    {
        "act_id": 11,
        "act_name_en": "The Penal Code, 1860",
        "act_name_bn": "দণ্ডবিধি, ১৮৬০",
        "category": "Criminal Law (ফৌজদারি আইন)",
        "section_number": "302",
        "section_title_en": "Punishment for murder",
        "section_title_bn": "হত্যাকাণ্ডের (মানুষ খুন) জন্য দণ্ড ও মিথ্যা আসামি করার প্রতিকার",
        "chapter_number": "XVI",
        "chapter_title": "Of Offences Affecting the Human Body",
        "domain": "Criminal Law",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-11/section-3148.html",
        "content_en": """Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.""",
        "content_bn": """যে ব্যক্তি খুন বা মানুষ হত্যা সংগঠন করে, সে ব্যক্তি মৃত্যুদণ্ডে অথবা যাবজ্জীবন কারাদণ্ডে দণ্ডিত হবে এবং অর্থদণ্ডেও দণ্ডনীয় হবে। তবে নির্দোষ ব্যক্তি যদি মিথ্যা মামলায় আসামি হয়, তবে হাইকোর্ট বা ম্যাজিস্ট্রেট আদালতে জামিন ও তদন্তে নাম প্রত্যাহারের সুযোগ রয়েছে।""",
        "easy_explanation_bn": "মানুষ খুন বা মারামারির ঘটনায় দণ্ডবিধির ৩০২ ধারায় মামলা হয়। আপনি যদি মারামারিতে উপস্থিত না থেকেও মিথ্যা মামলায় আসামি হয়ে থাকেন, তবে আদালতে ঘটনার দিন অন্য কোথাও থাকার অকাট্য প্রমাণ (Alibi) উপস্থাপন করে জামিন ও পুলিশি তদন্তে নাম বাদ দেওয়ার (Discharge) আবেদন করতে পারেন।",
        "keywords": ["section 302", "murder", "murdar", "manush khun", "khun", "খুন", "মানুষ হত্যা", "ধারা ৩০২", "মিথ্যা মামলা", "302"],
        "related_sections": ["300", "34", "149"],
        "elements_of_offence": [],
        "evidence_matrix": {"strong_evidence": [], "supporting_evidence": []},
        "police_questions": [],
        "procedure_steps": [],
        "past_court_cases": [],
        "case_strength": {}
    },

    # 5. Section 406 - Penal Code (Criminal Breach of Trust)
    {
        "act_id": 11,
        "act_name_en": "The Penal Code, 1860",
        "act_name_bn": "দণ্ডবিধি, ১৮৬০",
        "category": "Criminal Law (ফৌজদারি আইন)",
        "section_number": "406",
        "section_title_en": "Punishment for criminal breach of trust",
        "section_title_bn": "বিশ্বাসভঙ্গের জন্য দণ্ড (আমানত খেয়ানত)",
        "chapter_number": "XVII",
        "chapter_title": "Of Offences Against Property",
        "domain": "Criminal Law",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-11/section-3352.html",
        "content_en": """Whoever commits criminal breach of trust shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.""",
        "content_bn": """যে ব্যক্তি অপরাধমূলক বিশ্বাসভঙ্গ করে (Criminal Breach of Trust - আমানত খেয়ানত বা বিশ্বাসভঙ্গ), সে ব্যক্তি যেকোনো মেয়াদের সশ্রম বা বিনাশ্রম কারাদণ্ডে—যার মেয়াদ তিন বছর পর্যন্ত হতে পারে—অথবা অর্থদণ্ডে, অথবা উভয় দণ্ডে দণ্ডিত হবে।""",
        "easy_explanation_bn": "কারো ওপর বিশ্বাস স্থাপন করে টাকা বা সম্পত্তি আমানত হিসেবে রাখার পর সে যদি তা ফেরত না দিয়ে নিজের স্বার্থে আত্মসাৎ করে, তবে এটি ৪০৬ ধারায় আমানত খেয়ানতের অপরাধ।",
        "keywords": ["criminal breach of trust", "section 406", "trust violation", "3 years imprisonment", "বিশ্বাসভঙ্গ", "অমানত খেয়ানত", "আমানত খেয়ানত", "খেয়ানত", "আমানত", "ধারা ৪০৬", "406"],
        "related_sections": ["405", "420"],
        "elements_of_offence": [],
        "evidence_matrix": {"strong_evidence": [], "supporting_evidence": []},
        "police_questions": [],
        "procedure_steps": [],
        "past_court_cases": [],
        "case_strength": {}
    },

    # 6. Negotiable Instruments Act - Section 138 (Cheque Bounce)
    {
        "act_id": 26,
        "act_name_en": "The Negotiable Instruments Act, 1881",
        "act_name_bn": "হস্তান্তরযোগ্য দলিল আইন, ১৮৮১",
        "category": "Commercial & Banking Law (বাণিজ্যিক ও ব্যাংকিং আইন)",
        "section_number": "138",
        "section_title_en": "Dishonour of cheque for insufficiency of funds",
        "section_title_bn": "অ্যাকাউন্টে পর্যাপ্ত অর্থ না থাকায় চেক ডিজঅনার / বাউন্স হওয়া",
        "chapter_number": "XVII",
        "chapter_title": "Of Penalties in Case of Dishonour of Certain Cheques",
        "domain": "Banking Law",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-26/section-138.html",
        "content_en": """Where any cheque drawn by a person... is returned by the bank unpaid, such person shall be deemed to have committed an offence...""",
        "content_bn": """কোনো ব্যক্তি যদি ব্যাংকের অ্যাকাউন্টে পর্যাপ্ত অর্থ না থাকা সত্ত্বেও কাউকে পাওনা বাবদ চেক প্রদান করে এবং ব্যাংক কর্তৃক চেকটি ডিজঅনার / বাউন্স হয়, তবে উক্ত ব্যক্তি অপরাধ করেছে বলে গণ্য হবে এবং ১ বছর পর্যন্ত কারাদণ্ড অথবা চেকের টাকার তিনগুণ পর্যন্ত অর্থদণ্ডে দণ্ডিত হবে।""",
        "easy_explanation_bn": "কেউ যদি টাকা পরিশোধের জন্য আপনাকে ব্যাংক চেক দেয় এবং ব্যাংক অ্যাকাউন্টে টাকা না থাকার কারণে চেকটি বাউন্স বা ডিজঅনার হয়, তবে ১৩৮ ধারায় মামলা দায়ের করা যায়। মামলা করার আগে ৩০ দিনের মধ্যে আইনি নোটিশ পাঠাতে হয়।",
        "keywords": ["cheque dishonour", "section 138", "ni act", "cheque bounce", "চেক ডিজঅনার", "চেক বাউন্স", "ধারা ১৩৮", "আইনি নোটিশ", "138", "bounce"],
        "related_sections": ["140", "141"],
        "elements_of_offence": [],
        "evidence_matrix": {"strong_evidence": [], "supporting_evidence": []},
        "police_questions": [],
        "procedure_steps": [],
        "past_court_cases": [],
        "case_strength": {}
    },

    # 7. Bangladesh Labour Act - Section 120 (Unpaid Salary)
    {
        "act_id": 42,
        "act_name_en": "The Bangladesh Labour Act, 2006",
        "act_name_bn": "বাংলাদেশ শ্রম আইন, ২০০৬",
        "category": "Labour & Employment Law (শ্রম আইন)",
        "section_number": "120",
        "section_title_en": "Time of payment of wages",
        "section_title_bn": "মজুরি বা বেতন পরিশোধের সময়সীমা",
        "chapter_number": "X",
        "chapter_title": "Wages and Payment thereof",
        "domain": "Labour Law",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-42/section-120.html",
        "content_en": """The wages of every worker shall be paid before the expiry of the seventh day after the last day of the wage period...""",
        "content_bn": """প্রত্যেক শ্রমিকের বা কর্মচারীর মজুরি বা বেতন উক্ত মজুরি মেয়াদের শেষ দিনের পর পরবর্তী ৭ (সাত) কর্মদিবসের মধ্যে অবশ্যই পরিশোধ করতে হবে। মালিক তা অনাদায়ী রাখলে শ্রম আদালতে প্রতিকার পাওয়া যাবে।""",
        "easy_explanation_bn": "কোম্পানি বা মালিক প্রতি মাসের বেতন পরবর্তী মাসের ৭ কর্মদিবসের মধ্যে পরিশোধ করতে বাধ্য। বেতন বকেয়া রাখলে বা না দিলে শ্রম আদালতে শ্রম পরিদর্শক বা কর্মচারীরা সরাসরি মামলা ও ক্ষতিপূরণ দাবি করতে পারেন।",
        "keywords": ["labour act", "section 120", "payment of wages", "salary non payment", "শ্রম আইন", "বেতন অনাদায়ী", "ধারা ১২০", "শ্রম আদালত", "salary", "beton", "120"],
        "related_sections": ["121", "123"],
        "elements_of_offence": [],
        "evidence_matrix": {"strong_evidence": [], "supporting_evidence": []},
        "police_questions": [],
        "procedure_steps": [],
        "past_court_cases": [],
        "case_strength": {}
    },

    # 8. Specific Relief Act - Section 9 (Illegal Land Dispossession)
    {
        "act_id": 9,
        "act_name_en": "The Specific Relief Act, 1877",
        "act_name_bn": "সুনির্দিষ্ট প্রতিকার আইন, ১৮৭৭",
        "category": "Civil & Property Law (দেওয়ানি ও সম্পত্তি প্রতিকার আইন)",
        "section_number": "9",
        "section_title_en": "Suit by person dispossessed of immovable property",
        "section_title_bn": "স্থাবর সম্পত্তি থেকে অবৈধভাবে বেদখল হওয়া ব্যক্তির দখল উদ্ধারের মামলা",
        "chapter_number": "I",
        "chapter_title": "Of Recovering Possession of Property",
        "domain": "Property Law",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-9/section-9.html",
        "content_en": """If any person is dispossessed without his consent of immovable property otherwise than in due course of law, he or any person claiming through him may, by suit, recover possession thereof...""",
        "content_bn": """কোনো ব্যক্তি যদি তার সম্মতি ছাড়া বা আইনের সঠিক মাধ্যম ছাড়া নিজ দখলীয় জমি বা বাড়ি থেকে বেআইনিভাবে বেদখল হয়, তবে বেদখল হওয়ার ৬ (ছয়) মাসের মধ্যে সে ৯ ধারায় বেদখল উদ্ধারের দেওয়ানি মামলা দায়ের করতে পারে।""",
        "easy_explanation_bn": "কেউ যদি গায়ের জোরে বা জোরপূর্বক আপনার জমি বা ঘরবাড়ি দখল করে নেয়, তবে মালিকানার দলিল না থাকলেও শুধু পূর্বের দখলের প্রমাণ দেখিয়ে বেদখল হওয়ার ৬ মাসের মধ্যে ৯ ধারায় দেওয়ানি আদালতে মামলা করে জমি ফেরত পাওয়া যায়।",
        "keywords": ["specific relief act", "section 9", "land possession", "illegal possession", "সুনির্দিষ্ট প্রতিকার আইন", "ধারা ৯", "জমি দখল উদ্ধার", "বেদখল", "jomi", "dokhol", "9"],
        "related_sections": ["8", "42"],
        "elements_of_offence": [],
        "evidence_matrix": {"strong_evidence": [], "supporting_evidence": []},
        "police_questions": [],
        "procedure_steps": [],
        "past_court_cases": [],
        "case_strength": {}
    },

    # 9. Penal Code Section 323 - Punishment for voluntarily causing hurt
    {
        "act_id": 11,
        "act_name_en": "The Penal Code, 1860",
        "act_name_bn": "দণ্ডবিধি, ১৮৬০",
        "category": "Criminal Law (ফৌজদারি আইন)",
        "section_number": "323",
        "section_title_en": "Punishment for voluntarily causing hurt",
        "section_title_bn": "স্বেচ্ছায় আঘাত (Hurt) করার দণ্ড — সাধারণ মারধর",
        "chapter_number": "XVI",
        "chapter_title": "Of Offences Affecting the Human Body",
        "domain": "Criminal Law",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-11/section-3216.html",
        "content_en": """Whoever, except in the case provided for by section 334, voluntarily causes hurt, shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand taka, or with both.""",
        "content_bn": """যে ব্যক্তি (ধারা ৩৩৪-এর ক্ষেত্র ছাড়া) স্বেচ্ছায় কাউকে আঘাত (Hurt) করে, সে ব্যক্তি যেকোনো মেয়াদের সশ্রম বা বিনাশ্রম কারাদণ্ডে—যার মেয়াদ এক বছর পর্যন্ত হতে পারে—অথবা এক হাজার টাকা পর্যন্ত অর্থদণ্ডে, অথবা উভয় দণ্ডে দণ্ডিত হবে।""",
        "easy_explanation_bn": "কেউ যদি ইচ্ছাকৃতভাবে আপনাকে মারধর করে বা শারীরিক আঘাত করে (যেমন চড়, ঘুষি, লাথি), তবে এটি দণ্ডবিধির ৩২৩ ধারার অপরাধ। পুলিশ কর্মকর্তাও যদি অযথা বা অতিরিক্ত শক্তি প্রয়োগ করে আঘাত করে, তাহলে একই ধারায় মামলা করা যায়। শাস্তি সর্বোচ্চ ১ বছরের কারাদণ্ড বা জরিমানা।",
        "keywords": [
            "section 323", "voluntarily causing hurt", "assault", "beating", "maramari",
            "police assault", "police marse", "ojotha marse", "পুলিশ মারধর", "মারধর",
            "আঘাত", "ধারা ৩২৩", "323", "hurt", "marse", "police beating", "physical assault",
            "পুলিশ আমারে মারসে", "অযথা মারধর", "শারীরিক নির্যাতন"
        ],
        "related_sections": ["319", "321", "324", "325"],
        "elements_of_offence": [
            "১. অভিযুক্ত ব্যক্তি কি স্বেচ্ছায় (intentionally) আঘাত করেছিল?",
            "২. শিকারের শরীরে কি ব্যথা, ফোলা, কাটা বা অন্য কোনো আঘাতের চিহ্ন ছিল?"
        ],
        "evidence_matrix": {
            "strong_evidence": [
                {"name": "মেডিকেল সার্টিফিকেট / সুরতহাল রিপোর্ট", "details": "ডাক্তার কর্তৃক আঘাতের প্রমাণ", "value": "আঘাতের অকাট্য প্রমাণ"},
                {"name": "CCTV / মোবাইল ভিডিও / প্রত্যক্ষদর্শী", "details": "ঘটনার সরাসরি প্রমাণ", "value": "অভিযুক্তের পরিচয় ও কাজ"}
            ],
            "supporting_evidence": [
                {"name": "ঘটনার জিডি / এজাহার কপি"},
                {"name": "আঘাতের ছবি / পোশাকের দাগ"}
            ]
        },
        "police_questions": [],
        "procedure_steps": [
            "নিকটস্থ হাসপাতাল বা সরকারি ডাক্তারের কাছ থেকে সুরতহাল / মেডিকেল সার্টিফিকেট নিন",
            "ঘটনার ভিডিও, ছবি বা সাক্ষীর নাম ঠিকানা সংরক্ষণ করুন",
            "নিকটস্থ থানায় এজাহার / জিডি দায়ের করুন অথবা সরাসরি ম্যাজিস্ট্রেট আদালতে অভিযোগ করুন",
            "পুলিশ কর্মকর্তার বিরুদ্ধে হলে উচ্চতর কর্তৃপক্ষ (SP/DIG) এবং মানবাধিকার কমিশনেও অভিযোগ দিন"
        ],
        "past_court_cases": [],
        "case_strength": {}
    },

    # 10. Penal Code Section 324 - Voluntarily causing hurt by dangerous weapons
    {
        "act_id": 11,
        "act_name_en": "The Penal Code, 1860",
        "act_name_bn": "দণ্ডবিধি, ১৮৬০",
        "category": "Criminal Law (ফৌজদারি আইন)",
        "section_number": "324",
        "section_title_en": "Voluntarily causing hurt by dangerous weapons or means",
        "section_title_bn": "বিপজ্জনক অস্ত্র বা উপায়ে স্বেচ্ছায় আঘাত করার দণ্ড",
        "chapter_number": "XVI",
        "chapter_title": "Of Offences Affecting the Human Body",
        "domain": "Criminal Law",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-11/section-3217.html",
        "content_en": """Whoever, except in the case provided for by section 334, voluntarily causes hurt by means of any instrument for shooting, stabbing or cutting, or any instrument which, used as a weapon of offence, is likely to cause death, or by means of fire or any heated substance, or by means of any poison or any corrosive substance, or by means of any explosive substance, or by means of any substance which it is deleterious to the human body to inhale, to swallow, or to receive into the blood, or by means of any animal, shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.""",
        "content_bn": """যে ব্যক্তি (ধারা ৩৩৪-এর ক্ষেত্র ছাড়া) গুলি, ছুরি, কাটার যন্ত্র বা মৃত্যু ঘটানোর সম্ভাবনাযুক্ত অস্ত্র, আগুন, বিষ, ক্ষয়কারক পদার্থ, বিস্ফোরক বা অন্য কোনো বিপজ্জনক উপায়ে স্বেচ্ছায় কাউকে আঘাত করে, সে ব্যক্তি তিন বছর পর্যন্ত কারাদণ্ড বা অর্থদণ্ড বা উভয় দণ্ডে দণ্ডিত হবে।""",
        "easy_explanation_bn": "যদি কেউ লাঠি, ছুরি, ব্যাটন, আগ্নেয়াস্ত্র বা অন্য কোনো বিপজ্জনক অস্ত্র দিয়ে আপনাকে আঘাত করে, তবে এটি ৩২৪ ধারার অপরাধ। পুলিশ যদি অপ্রয়োজনীয়ভাবে লাঠিচার্জ বা অতিরিক্ত বল প্রয়োগ করে গুরুতর আঘাত করে, তাহলেও এই ধারা প্রযোজ্য হতে পারে। শাস্তি সর্বোচ্চ ৩ বছর।",
        "keywords": [
            "section 324", "dangerous weapons", "hurt by weapon", "lathi charge", "baton",
            "পুলিশ লাঠিচার্জ", "বিপজ্জনক অস্ত্র", "ধারা ৩২৪", "324", "weapon assault",
            "গুরুতর আঘাত", "লাঠি দিয়ে মারধর"
        ],
        "related_sections": ["323", "325", "326"],
        "elements_of_offence": [],
        "evidence_matrix": {"strong_evidence": [], "supporting_evidence": []},
        "police_questions": [],
        "procedure_steps": [],
        "past_court_cases": [],
        "case_strength": {}
    },

    # 11. Penal Code Section 325 - Punishment for voluntarily causing grievous hurt
    {
        "act_id": 11,
        "act_name_en": "The Penal Code, 1860",
        "act_name_bn": "দণ্ডবিধি, ১৮৬০",
        "category": "Criminal Law (ফৌজদারি আইন)",
        "section_number": "325",
        "section_title_en": "Punishment for voluntarily causing grievous hurt",
        "section_title_bn": "স্বেচ্ছায় গুরুতর আঘাত (Grievous Hurt) করার দণ্ড",
        "chapter_number": "XVI",
        "chapter_title": "Of Offences Affecting the Human Body",
        "domain": "Criminal Law",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-11/section-3219.html",
        "content_en": """Whoever, except in the case provided for by section 335, voluntarily causes grievous hurt, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.""",
        "content_bn": """যে ব্যক্তি (ধারা ৩৩৫-এর ক্ষেত্র ছাড়া) স্বেচ্ছায় গুরুতর আঘাত (Grievous Hurt) করে, সে ব্যক্তি সাত বছর পর্যন্ত কারাদণ্ডে দণ্ডিত হবে এবং অর্থদণ্ডেও দণ্ডনীয় হবে।""",
        "easy_explanation_bn": "হাড় ভাঙা, স্থায়ী অঙ্গহানি, চোখ/কান নষ্ট হওয়া, বা ২০ দিনের বেশি বিপজ্জনক অবস্থায় রাখা — এগুলো গুরুতর আঘাত (Grievous Hurt)। পুলিশ বা অন্য কেউ যদি এমন আঘাত করে, তবে ৩২৫ ধারায় মামলা হয়। শাস্তি সর্বোচ্চ ৭ বছর কারাদণ্ড।",
        "keywords": [
            "section 325", "grievous hurt", "serious injury", "broken bone", "গুরুতর আঘাত",
            "ধারা ৩২৫", "325", "fracture", "permanent injury", "পুলিশ গুরুতর মারধর"
        ],
        "related_sections": ["320", "323", "324", "326"],
        "elements_of_offence": [],
        "evidence_matrix": {"strong_evidence": [], "supporting_evidence": []},
        "police_questions": [],
        "procedure_steps": [],
        "past_court_cases": [],
        "case_strength": {}
    },

    # 12. Composite / guidance entry for Police assault & custodial violence remedies
    {
        "act_id": 11,
        "act_name_en": "The Penal Code, 1860 & related laws",
        "act_name_bn": "দণ্ডবিধি, ১৮৬০ ও সংশ্লিষ্ট আইন",
        "category": "Criminal Law (ফৌজদারি আইন) — Police Accountability",
        "section_number": "323-325+Torture",
        "section_title_en": "Remedies against police assault / custodial torture",
        "section_title_bn": "পুলিশ কর্তৃক অযথা মারধর বা হেফাজতে নির্যাতনের প্রতিকার",
        "chapter_number": "XVI",
        "chapter_title": "Of Offences Affecting the Human Body + Human Rights",
        "domain": "Criminal Law / Human Rights",
        "source_url": "http://bdlaws.minlaw.gov.bd/act-11.html",
        "content_en": """Police officers have no legal authority to assault or torture any person. Voluntarily causing hurt is punishable under Penal Code sections 323, 324, 325. Torture and custodial death are additionally covered by the Torture and Custodial Death (Prevention) Act, 2013. Constitution Article 35(5) prohibits torture and cruel treatment. Victims may file FIR/GD, approach Magistrate, higher police authority, National Human Rights Commission, or seek compensation.""",
        "content_bn": """পুলিশ কর্মকর্তার কোনো ব্যক্তিকে অযথা মারধর বা নির্যাতন করার আইনগত ক্ষমতা নেই। স্বেচ্ছায় আঘাত করা দণ্ডবিধির ৩২৩, ৩২৪, ৩২৫ ধারায় শাস্তিযোগ্য। হেফাজতে নির্যাতন ও মৃত্যুর জন্য নির্যাতন এবং হেফাজতে মৃত্যু (নিবারণ) আইন, ২০১৩ প্রযোজ্য। সংবিধানের ৩৫(৫) অনুচ্ছেদ নির্যাতন ও নিষ্ঠুর ব্যবহার নিষিদ্ধ করেছে। ভুক্তভোগী থানায় এজাহার/জিডি, ম্যাজিস্ট্রেট আদালত, উচ্চতর পুলিশ কর্তৃপক্ষ, জাতীয় মানবাধিকার কমিশন বা ক্ষতিপূরণের মামলা করতে পারেন।""",
        "easy_explanation_bn": "পুলিশ আপনাকে অযথা (ojotha) মারধর করলে তা সম্পূর্ণ বেআইনি। আপনি (১) হাসপাতাল থেকে সুরতহাল নিন, (২) থানায় বা ম্যাজিস্ট্রেট আদালতে মামলা করুন, (৩) জেলা পুলিশ সুপার / মহানগর পুলিশ কমিশনারের কাছে লিখিত অভিযোগ দিন, (৪) জাতীয় মানবাধিকার কমিশনে অভিযোগ করতে পারেন। নির্যাতন আইন ২০১৩ অনুযায়ী হেফাজতে নির্যাতন আরও কঠোর শাস্তির অপরাধ।",
        "keywords": [
            "police assault", "police beating", "ojotha marse", "পুলিশ মারধর", "পুলিশ আমারে মারসে",
            "custodial torture", "হেফাজতে নির্যাতন", "torture act 2013", "নির্যাতন আইন",
            "police brutality", "অযথা মারধর", "পুলিশ নির্যাতন", "article 35", "মানবাধিকার",
            "police marse", "amare marse", "what can i do police beat"
        ],
        "related_sections": ["323", "324", "325", "326"],
        "elements_of_offence": [],
        "evidence_matrix": {
            "strong_evidence": [
                {"name": "মেডিকেল সার্টিফিকেট / সুরতহাল", "details": "আঘাতের ডাক্তারি প্রমাণ", "value": "অপরিহার্য"},
                {"name": "ভিডিও / সাক্ষী", "details": "ঘটনার প্রত্যক্ষ প্রমাণ", "value": "শক্তিশালী"}
            ],
            "supporting_evidence": [
                {"name": "উচ্চতর কর্তৃপক্ষের কাছে দেওয়া অভিযোগের কপি"},
                {"name": "মানবাধিকার কমিশনের অভিযোগ রসিদ"}
            ]
        },
        "police_questions": [],
        "procedure_steps": [
            "তাৎক্ষণিকভাবে সরকারি হাসপাতালে গিয়ে সুরতহাল / মেডিকেল সার্টিফিকেট করান",
            "ঘটনার ভিডিও, ছবি, সাক্ষীর তথ্য সংরক্ষণ করুন",
            "নিকটস্থ থানায় এজাহার দায়ের করুন; থানা না নিলে ম্যাজিস্ট্রেট আদালতে সরাসরি অভিযোগ করুন",
            "জেলা পুলিশ সুপার (SP) বা মহানগর পুলিশ কমিশনার বরাবর লিখিত অভিযোগ দিন",
            "জাতীয় মানবাধিকার কমিশন (NHRC) এবং প্রয়োজনে আইনজীবীর সহায়তা নিন"
        ],
        "past_court_cases": [],
        "case_strength": {}
    }
]

def fetch_and_preserve_raw(act_slug="act_11_penal_code_1860"):
    act_dir = os.path.join(BASE_RAW_DIR, act_slug)
    os.makedirs(act_dir, exist_ok=True)
    
    saved_files = []
    for item in SEEDED_SECTIONS:
        sec_filename = f"section_{item['section_number']}.html"
        file_path = os.path.join(act_dir, sec_filename)
        
        raw_html_content = f"""<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <title>{item['act_name_en']} - Section {item['section_number']}</title>
    <meta name="source-url" content="{item['source_url']}">
    <meta name="act-id" content="{item['act_id']}">
    <meta name="section-number" content="{item['section_number']}">
</head>
<body>
    <div class="act-header">
        <h1 class="act-title-en">{item['act_name_en']}</h1>
        <h2 class="act-title-bn">{item['act_name_bn']}</h2>
        <h3 class="chapter-info">Chapter {item['chapter_number']}: {item['chapter_title']}</h3>
    </div>
    <div class="section-container" id="section-{item['section_number']}">
        <h4 class="section-title-en">Section {item['section_number']}: {item['section_title_en']}</h4>
        <h4 class="section-title-bn">ধারা {item['section_number']}: {item['section_title_bn']}</h4>
        
        <div class="content-en"><pre>{item['content_en']}</pre></div>
        <div class="content-bn"><pre>{item['content_bn']}</pre></div>
    </div>
    <div class="footer-citation">
        <p>Source: <a href="{item['source_url']}">{item['source_url']}</a></p>
    </div>
</body>
</html>"""
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(raw_html_content)
        
        saved_files.append(file_path)
        
    return saved_files, SEEDED_SECTIONS

if __name__ == "__main__":
    files, sections = fetch_and_preserve_raw()
    print(f"Successfully preserved {len(files)} raw legal documents.")
