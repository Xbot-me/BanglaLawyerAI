# 🇧🇩 Bangladesh Legal Knowledge Platform — Docker Setup

This project is an AI-powered ground-truth legal retrieval & simple Bengali explanation engine built for Bangladesh laws (`bdlaws.minlaw.gov.bd`).

---

## 🚀 Quick Start with Docker

You can run this project with Docker in 2 simple commands:

### Option A: Using Docker Compose (Recommended)

```bash
# 1. Clone or extract the project folder
cd Lawyer

# 2. Build and start the container
docker compose up --build
```

Now open your browser and navigate to:
👉 **`http://localhost:8000`**

---

### Option B: Using Standard Docker Commands

```bash
# 1. Build the Docker image
docker build -t bangladesh-lawyer-app .

# 2. Run the container
docker run -p 8000:8000 -v $(pwd)/storage:/app/storage bangladesh-lawyer-app
```

Now open your browser and navigate to:
👉 **`http://localhost:8000`**

---

## 🧪 Running the Benchmark Test Suite inside Docker

To run the 10-question evaluation benchmark suite inside Docker:

```bash
docker exec -it bangladesh_legal_platform python run_pipeline.py
```

---

## 🔑 Optional: Setting Gemini API Key

By default, the platform uses a deterministic, ground-truth Bengali template generator. 

If you want to use Google Gemini for dynamic Bengali LLM explanations:

```bash
docker run -p 8000:8000 -e GEMINI_API_KEY="your_api_key_here" bangladesh-lawyer-app
```

Or set `GEMINI_API_KEY` in `docker-compose.yml`.

---

## 📁 Project Structure

```
Lawyer/
 ├── Dockerfile                  # Container definition
 ├── docker-compose.yml          # Container orchestration setup
 ├── app.py                      # FastAPI Web UI & API Application
 ├── run_pipeline.py             # CLI Pipeline & Benchmark Test Suite
 ├── requirements.txt            # Dependency specification
 ├── src/                        # Core Python Engine
 │    ├── scraper.py             # Raw law document scraper & preservation
 │    ├── parser.py              # Text cleaner & metadata extractor
 │    ├── indexer.py             # BM25 + Multilingual Vector Indexer
 │    ├── retriever.py           # Hybrid Search Engine (BM25 + Dense Vectors + RRF)
 │    ├── llm_explainer.py       # Bengali Legal Explanation Layer
 │    └── evaluator.py           # 10-Question Benchmark Suite
 └── storage/                    # Preserved Legal Documents & Data
      ├── raw/bdlaws/            # Preserved raw HTML documents
      ├── processed/             # Cleaned JSON section records
      └── cache/                 # Answer cache
```
