import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load .env file automatically if present
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

from src.retriever import HybridRetriever
from src.llm_explainer import LLMBengaliExplainer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Bangladesh Legal Knowledge Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global lazy initialization of retriever & explainer
logger.info("Initializing Bangladesh Legal Platform v5...")
retriever = HybridRetriever()
explainer = LLMBengaliExplainer()
logger.info("Legal Platform v5 Ready.")

class LegalQueryRequest(BaseModel):
    query: str

@app.get("/health")
def health_check():
    return {"status": "ok", "provider": explainer.provider}

@app.post("/api/ask")
def process_legal_query(req: LegalQueryRequest):
    q = req.query.strip()
    if not q:
        return JSONResponse(status_code=400, content={"error": "Query cannot be empty"})

    retrieval_res = retriever.retrieve(q)
    explanation = explainer.explain(q, retrieval_res)
    return explanation

@app.get("/api/laws")
def get_all_laws():
    return {"acts": retriever.indexer.documents}

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Bangladesh Legal Platform API is Running</h1>"

@app.get("/styles.css")
def serve_styles():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    return JSONResponse(status_code=404, content={"error": "CSS not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
