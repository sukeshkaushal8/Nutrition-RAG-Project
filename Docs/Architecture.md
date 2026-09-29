# Architecture: Dietary Guidance RAG Chatbot

> Companion document to [ProblemStatement.md](file:///Users/sukesh/Documents/AI%20Projects%20%26%20Learning/Nutrition-RAG/Docs/ProblemStatement.md)

---

## 1. System Overview

```
                           ┌─────────────────────────────────────────────────────┐
                           │                   Client Layer                      │
                           │          (Streamlit / Gradio / REST API)            │
                           └───────────────────────┬─────────────────────────────┘
                                                   │  user query
                                                   ▼
┌──────────────────┐      ┌─────────────────────────────────────────────────────┐
│                  │      │                  Orchestrator                       │
│  Scope Guard     │◄────►│  1. Scope check ──► 2. Retrieve ──► 3. Generate    │
│  (Blocklist +    │      │                                                     │
│   Classifier)    │      └────────┬────────────────────┬───────────────────────┘
│                  │               │                    │
└──────────────────┘               ▼                    ▼
                        ┌──────────────────┐  ┌──────────────────────┐
                        │  Retrieval Engine │  │   Answer Generator   │
                        │  (Vector Search   │  │   (LLM + Prompt      │
                        │   + Metadata      │  │    Template +         │
                        │   Filtering)      │  │    Citation Builder)  │
                        └────────┬─────────┘  └──────────────────────┘
                                 │
                        ┌────────┴─────────┐
                        │   Vector Store    │
                        │  (ChromaDB /      │
                        │   Qdrant)         │
                        └──────────────────┘
                                 ▲
                                 │  offline ingestion
                        ┌────────┴─────────┐
                        │  Ingestion        │
                        │  Pipeline         │
                        │  (Scrape ──►      │
                        │   Parse ──►       │
                        │   Chunk ──►       │
                        │   Embed ──►       │
                        │   Store)          │
                        └──────────────────┘
```

---

## 2. Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Language** | Python 3.11+ | Ecosystem maturity for ML/NLP pipelines |
| **Embedding Model** | `BAAI/bge-small-en-v1.5` (default), swappable | Fast, free, higher quality for English prose |
| **Vector Store** | ChromaDB (dev) / Qdrant (prod) | ChromaDB is zero-config for prototyping; Qdrant offers metadata filtering at scale |
| **LLM** | Groq (Llama 3 / Mixtral) | Free tier, fast inference, no GPU needed locally |
| **Document Parsing** | `BeautifulSoup4` (HTML), `PyMuPDF` / `pdfplumber` (PDF) | Handles both web pages and PDF documents in the corpus |
| **Chunking** | Custom structure-aware chunker | Required by the problem — fixed-size chunking destroys tables and numbered lists |
| **Web Framework** | FastAPI (API) + Streamlit (UI) | FastAPI for clean REST endpoints; Streamlit for rapid prototype UI |
| **Configuration** | Pydantic Settings + `.env` | Type-safe config, secrets stay out of code |
| **Testing** | pytest + pytest-asyncio | Standard Python testing |

---

## 3. Data Ingestion Pipeline

The ingestion pipeline runs **offline** (not at query time). It transforms raw documents into embedded, searchable chunks stored in the vector database.

### 3.1 Pipeline Stages

```
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│  Scrape / │───►│  Parse &  │───►│  Chunk    │───►│  Embed    │───►│  Store    │
│  Download │    │  Extract  │    │  (Smart)  │    │  (Vectors)│    │  (VectorDB│
└───────────┘    └───────────┘    └───────────┘    └───────────┘    └───────────┘
```

### 3.2 Document Registry

Every document in the corpus is tracked in a **`corpus_registry.json`** file:

```json
{
  "documents": [
    {
      "doc_id": "who-healthy-diet",
      "title": "Healthy Diet Fact Sheet",
      "publisher": "WHO",
      "year": 2024,
      "source_url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
      "retrieval_date": "2026-09-29",
      "format": "html",
      "local_path": "data/raw/who-healthy-diet.html",
      "category": "nutrition"
    }
  ]
}
```

### 3.3 Scraping & Download

| Source Type | Tool | Notes |
|------------|------|-------|
| HTML pages | `requests` + `BeautifulSoup4` | Strip navbars, footers, cookie banners |
| PDF files | `requests` (download) → `PyMuPDF` / `pdfplumber` (extract) | Preserve table structure where possible |

**Output:** Raw files saved to `data/raw/` with filenames matching `doc_id`.

### 3.4 Parsing & Text Extraction

```python
# Pseudocode
class ParsedDocument:
    doc_id: str
    title: str
    publisher: str
    year: int
    source_url: str
    sections: list[Section]  # preserves document structure

class Section:
    heading: str        # e.g., "Key Recommendations", "Table 3: ..."
    content: str        # raw text
    section_type: str   # "prose" | "table" | "list"
```

**Key rules:**
- Preserve section headings — they become chunk metadata.
- Detect tables and keep them intact (don't let them get split across chunks).
- Strip boilerplate (headers, footers, navigation, disclaimers).

---

## 4. Chunking Strategy

> The problem statement explicitly warns: *"These documents are full of tables and numbered recommendations that fixed-size chunking will cut in half."*

### 4.1 Approach: Structure-Aware Chunking

Instead of naïve fixed-size windows, the chunker respects document structure:

```
┌─────────────────────────────────────────────────┐
│            Structure-Aware Chunker              │
│                                                  │
│  1. Split on section headings (H1, H2, H3) to build breadcrumbs │
│  2. Within sections, split on paragraphs        │
│  3. Keep lists as atomic units; split large tables by row       │
│     while preserving headers                    │
│  4. Merge small adjacent chunks (< min_tokens)  │
│  5. Split oversized chunks at sentence boundary │
│  6. Inject breadcrumb metadata directly into    │
│     the chunk content to preserve hierarchy     │
└─────────────────────────────────────────────────┘
```

### 4.2 Chunk Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `max_chunk_tokens` | 512 | Balances retrieval granularity with context |
| `min_chunk_tokens` | 50 | Prevents degenerate tiny chunks |
| `overlap_tokens` | 50 | Preserves context at chunk boundaries |
| `atomic_types` | `["list"]` | Never split lists across chunks |

### 4.3 Chunk Schema

Every chunk carries full provenance metadata:

```python
class Chunk:
    chunk_id: str              # unique identifier (doc_id + section + index)
    doc_id: str                # → links back to corpus_registry
    document_name: str         # "Healthy Diet Fact Sheet"
    publisher: str             # "WHO"
    year: int                  # 2024
    section_heading: str       # "Key Recommendations"
    source_url: str            # original URL
    content: str               # the actual text
    token_count: int           # for diagnostics
    chunk_index: int           # position within the document
```

---

## 5. Vector Store Design

### 5.1 Collection Schema (ChromaDB)

```python
collection = chroma_client.get_or_create_collection(
    name="dietary_guidance",
    metadata={"hnsw:space": "cosine"}
)

# Each chunk is stored as:
collection.add(
    ids=[chunk.chunk_id],
    documents=[chunk.content],
    embeddings=[embedding_vector],
    metadatas=[{
        "doc_id": chunk.doc_id,
        "document_name": chunk.document_name,
        "publisher": chunk.publisher,
        "year": chunk.year,
        "section_heading": chunk.section_heading,
        "source_url": chunk.source_url,
        "chunk_index": chunk.chunk_index
    }]
)
```

### 5.2 Indexing Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Distance metric | Cosine similarity | Standard for sentence-transformer embeddings |
| Embedding dimension | 384 (BGE-Small) | Good speed/quality trade-off |
| Metadata filtering | By `doc_id`, `publisher`, `category` | Required: per-document retrieval (§4.3 of problem statement) |

---

## 6. Retrieval Engine

### 6.1 Query Flow

```
User Query
    │
    ├─── Is a specific document named? ──► YES ──► Filter by doc_id
    │                                       │
    │                                       ▼
    │                                  Vector search (top-k, filtered)
    │
    └─── NO ──► Vector search (top-k, all documents)
                    │
                    ▼
              Re-rank results (optional, cross-encoder)
                    │
                    ▼
              Group results by doc_id (for cross-doc answers)
```

### 6.2 Retrieval Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `top_k` | 10 | Number of chunks to retrieve |
| `distance_threshold` | 0.40 | Above this → "not in the corpus" refusal |
| `max_docs_in_answer` | 3 | Cap on distinct documents in one answer |

### 6.3 Document-Filtered Retrieval

When the user names a specific document (e.g., *"What does the WHO say about salt?"*):

```python
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k,
    where={"publisher": "WHO"}   # or {"doc_id": "who-healthy-diet"}
)
```

### 6.4 Cross-Document Grouping

For queries spanning multiple sources, retrieved chunks are grouped by `doc_id` before being passed to the answer layer — ensuring **per-document answers with separate citations** (§4.5).

```python
def group_by_document(results: list[Chunk]) -> dict[str, list[Chunk]]:
    groups = defaultdict(list)
    for chunk in results:
        groups[chunk.doc_id].append(chunk)
    return dict(groups)
```

---

## 7. Answer Generation Layer

### 7.1 System Prompt Template

```
You are a dietary guidance assistant. You answer questions about food,
nutrition, and food safety using ONLY the provided reference chunks.

RULES:
1. Answer ONLY from the provided chunks. Do not use prior knowledge.
2. Cite every claim with [Document Name, Publisher, Year](source_url).
3. When chunks from multiple documents are relevant, provide SEPARATE
   answers per document. NEVER blend sources into a single claim.
4. If the provided chunks do not contain the answer, say:
   "The dietary guidance documents I searched do not cover this topic.
    I searched: {list of documents searched}."
5. NEVER provide medical advice, calorie targets, weight-loss plans,
   or body-weight recommendations. If asked, respond:
   "This falls outside what I can help with. Please consult a
    qualified healthcare professional."
```

### 7.2 Prompt Construction

```
┌─────────────────────────────────────────────┐
│              Final Prompt                    │
│                                              │
│  [System Prompt]                            │
│                                              │
│  --- Retrieved Context ---                  │
│  Source 1: {doc_name} ({publisher}, {year})  │
│  > {chunk_content}                          │
│                                              │
│  Source 2: {doc_name} ({publisher}, {year})  │
│  > {chunk_content}                          │
│  ...                                         │
│                                              │
│  --- User Question ---                      │
│  {user_query}                               │
└─────────────────────────────────────────────┘
```

### 7.3 Citation Format

Every answer includes inline citations:

```
According to the WHO, a healthy diet includes at least 400g of fruits
and vegetables per day [Healthy Diet Fact Sheet, WHO, 2024](https://www.who.int/...).

The NHS recommends aiming for at least 5 portions of fruit and
vegetables daily [Eat Well Guide, NHS (UK), 2024](https://www.nhs.uk/...).
```

---

## 8. Scope Guard & Refusal Logic

### 8.1 Two-Layer Refusal (Enforced in Code)

```
User Query
    │
    ▼
┌──────────────────────┐     YES     ┌──────────────────────────┐
│  Layer 1: Blocklist  │────────────►│ REFUSE: "Out of scope.   │
│  + Keyword Detector  │             │  Please consult a         │
│                      │             │  healthcare professional."│
│  Triggers:           │             └──────────────────────────┘
│  - medical advice    │
│  - calorie targets   │
│  - weight/BMI        │
│  - diagnosis         │
│  - medication        │
└──────────┬───────────┘
           │ PASS
           ▼
┌──────────────────────┐     LOW     ┌──────────────────────────┐
│  Layer 2: Retrieval  │────────────►│ REFUSE: "The guidance     │
│  Relevance Check     │  RELEVANCE  │  doesn't cover this.      │
│                      │             │  I searched: [doc list]"   │
│  similarity < 0.35   │             └──────────────────────────┘
└──────────┬───────────┘
           │ PASS
           ▼
     Generate Answer
```

### 8.2 Blocklist Implementation

```python
BLOCKED_TOPICS = [
    "medical advice", "diagnos", "prescri", "medication",
    "calorie target", "calorie goal", "weight loss", "lose weight",
    "BMI", "body mass index", "how much should I weigh",
    "diet plan for weight", "eating disorder"
]

def is_out_of_scope(query: str) -> bool:
    query_lower = query.lower()
    return any(term in query_lower for term in BLOCKED_TOPICS)
```

> **Note:** This is a first-pass keyword filter. A future iteration could use a lightweight classifier for more robust detection.

---

## 9. API Design

### 9.1 REST Endpoints (FastAPI)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat` | Send a query, get an answer with citations |
| `GET` | `/api/v1/documents` | List all documents in the corpus |
| `GET` | `/api/v1/documents/{doc_id}` | Get metadata for a specific document |
| `POST` | `/api/v1/ingest` | Trigger re-ingestion of the corpus (admin) |
| `GET` | `/api/v1/health` | Health check |

### 9.2 Chat Request / Response Schema

**Request:**
```json
{
  "query": "What does the WHO recommend for daily salt intake?",
  "filter_document": null,
  "top_k": 10
}
```

**Response:**
```json
{
  "answer": "According to the WHO, adults should consume less than 5g of salt per day...",
  "citations": [
    {
      "document_name": "Healthy Diet Fact Sheet",
      "publisher": "WHO",
      "year": 2024,
      "source_url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
      "chunk_excerpt": "Adults should consume less than 5 g of salt..."
    }
  ],
  "documents_searched": ["who-healthy-diet", "nhs-eatwell-guide", "..."],
  "refusal_type": null
}
```

---

## 10. Project Structure

```
Nutrition-RAG/
├── Docs/
│   ├── ProblemStatement.md
│   └── Architecture.md              ← this document
│
├── data/
│   ├── raw/                         # downloaded HTML/PDF files
│   ├── parsed/                      # extracted structured text (JSON)
│   ├── chunks/                      # chunked documents (JSON)
│   └── corpus_registry.json         # document metadata registry
│
├── src/
│   ├── __init__.py
│   ├── config.py                    # Pydantic settings, env loading
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── scraper.py               # download HTML/PDF from URLs
│   │   ├── parser.py                # extract text, detect structure
│   │   ├── chunker.py               # structure-aware chunking
│   │   ├── embedder.py              # generate embeddings
│   │   └── pipeline.py              # orchestrate full ingestion
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── vector_store.py          # ChromaDB / Qdrant wrapper
│   │   ├── retriever.py             # query, filter, group results
│   │   └── reranker.py              # optional cross-encoder reranking
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── llm_client.py            # Groq API wrapper
│   │   ├── prompt_builder.py        # construct prompts with context
│   │   └── citation_builder.py      # format citations from metadata
│   │
│   ├── guardrails/
│   │   ├── __init__.py
│   │   ├── scope_guard.py           # blocklist + keyword detection
│   │   └── relevance_check.py       # similarity threshold check
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app
│   │   ├── routes.py                # endpoint definitions
│   │   └── schemas.py               # Pydantic request/response models
│   │
│   └── orchestrator.py              # ties scope check → retrieve → generate
│
├── ui/
│   └── app.py                       # Streamlit chat interface
│
├── tests/
│   ├── test_chunker.py
│   ├── test_retriever.py
│   ├── test_scope_guard.py
│   ├── test_citation_builder.py
│   └── test_e2e.py                  # end-to-end query tests
│
├── scripts/
│   ├── ingest.py                    # CLI: run full ingestion
│   └── evaluate.py                  # CLI: run eval suite
│
├── .env.example                     # template for secrets
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 11. Configuration

### 11.1 Environment Variables

```bash
# .env.example

# --- LLM ---
GROQ_API_KEY=gsk_...
LLM_MODEL=llama3-70b-8192
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1024

# --- Embedding ---
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

# --- Vector Store ---
VECTOR_STORE_TYPE=chroma          # "chroma" or "qdrant"
CHROMA_PERSIST_DIR=./data/chroma
QDRANT_URL=http://localhost:6333  # only if using Qdrant

# --- Retrieval ---
TOP_K=10
DISTANCE_THRESHOLD=0.40

# --- Server ---
API_HOST=0.0.0.0
API_PORT=8000
```

### 11.2 Pydantic Settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM
    groq_api_key: str
    llm_model: str = "llama3-70b-8192"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1024

    # Embedding
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Vector Store
    vector_store_type: str = "chroma"
    chroma_persist_dir: str = "./data/chroma"

    # Retrieval
    top_k: int = 10
    distance_threshold: float = 0.40

    class Config:
        env_file = ".env"
```

---

## 12. Data Flow: End-to-End Query

```
 User: "How long can I keep cooked rice in the fridge?"
  │
  ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ 1. SCOPE CHECK                                              │
 │    is_out_of_scope("How long can I keep cooked rice...") │
 │    → False (not medical advice / weight-related)             │
 └──────────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ 2. EMBED QUERY                                              │
 │    embed("How long can I keep cooked rice in the fridge?")   │
 │    → [0.023, -0.118, 0.045, ...]  (384-dim vector)          │
 └──────────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ 3. RETRIEVE                                                 │
 │    top-8 chunks, cosine similarity                          │
 │    Results:                                                 │
 │      • WHO Five Keys: "Cooked food should not be stored..." (sim: 0.82)│
 │      • Australia Dietary: "Refrigerate leftovers within 2h..." (sim: 0.76)│
 └──────────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ 4. RELEVANCE CHECK                                          │
 │    max similarity = 0.82 > threshold (0.35) → PASS          │
 └──────────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ 5. GROUP BY DOCUMENT                                        │
 │    {                                                        │
 │      "who-five-keys": [chunk_1],                            │
 │      "australia-dietary-guidelines": [chunk_2]              │
 │    }                                                        │
 └──────────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ 6. BUILD PROMPT + GENERATE                                  │
 │    System prompt + grouped context + user query → LLM       │
 └──────────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ 7. RESPONSE                                                 │
 │                                                              │
 │  According to the WHO, cooked food should not be stored      │
 │  indefinitely [Five Keys to Safer Food Manual, WHO, 2006]    │
 │  (https://iris.who.int/...).                                 │
 │                                                              │
 │  The Australian Dietary Guidelines add that all leftovers    │
 │  should be refrigerated [Australian Dietary Guidelines,      │
 │  NHMRC, 2013](https://www.eatforhealth.gov.au/...).          │
 └──────────────────────────────────────────────────────────────┘
```

---

## 13. Testing Strategy

### 13.1 Test Categories

| Category | What It Tests | Example |
|----------|--------------|---------|
| **Unit** | Individual components in isolation | Chunker preserves tables, scope guard catches "weight loss" |
| **Integration** | Component interactions | Retriever returns chunks with correct metadata from vector store |
| **E2E** | Full query pipeline | "What does WHO say about sugar?" → answer with correct citation |
| **Refusal** | Both refusal paths work | Medical question → scope refusal; obscure query → corpus refusal |
| **Regression** | Golden Q&A pairs produce stable answers | Curated set of 20+ question-answer pairs |

### 13.2 Key Test Cases

```python
# test_scope_guard.py
def test_blocks_medical_advice():
    assert is_out_of_scope("Should I take vitamin D supplements?") == True

def test_allows_food_safety():
    assert is_out_of_scope("How long can I keep chicken in the fridge?") == False

# test_retriever.py
def test_filtered_retrieval_returns_only_target_doc():
    results = retriever.query("salt intake", filter_doc="who-healthy-diet")
    assert all(r.doc_id == "who-healthy-diet" for r in results)

# test_citation_builder.py
def test_citation_contains_all_fields():
    citation = build_citation(chunk)
    assert citation.document_name
    assert citation.publisher
    assert citation.year
    assert citation.source_url.startswith("http")
```

---

## 14. Deployment Plan

### 14.1 Environments

| Environment | Purpose | Vector Store | LLM |
|-------------|---------|-------------|-----|
| **Local Dev** | Development & testing | ChromaDB (local dir) | Groq (free tier) |
| **Staging** | Pre-release validation | Qdrant (Docker) | Groq |
| **Production** | User-facing | Qdrant (managed) | Groq / self-hosted |

### 14.2 Docker Compose (Local Dev)

```yaml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./data:/app/data
    depends_on:
      - qdrant

  ui:
    build:
      context: .
      dockerfile: Dockerfile.ui
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  qdrant_data:
```

---

## 15. Future Enhancements (Out of Scope for v1)

| Enhancement | Description |
|------------|-------------|
| **Hybrid Search** | Combine vector search with BM25 keyword search for better recall |
| **Cross-Encoder Reranking** | Add a reranking step with `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| **Conversation Memory** | Multi-turn context window for follow-up questions |
| **Nutrient Database** | Structured DB for per-food nutrient lookup (Milestone 3 in the main project) |
| **Evaluation Framework** | RAGAS-based automated evaluation (faithfulness, relevance, context recall) |
| **Streaming Responses** | SSE-based token streaming for better UX |
| **Multi-language** | Corpus expansion to non-English dietary guidelines |

---

> **Document Version:** 1.0  
> **Last Updated:** 2026-09-29  
> **Status:** Draft — ready for review
