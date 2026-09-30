# Dietary Guidance RAG Chatbot

This project is a complete Retrieval-Augmented Generation (RAG) system built to provide answers about nutrition, food safety, and healthy eating based entirely on official dietary guidelines (e.g., WHO, NHS, Harvard). 

## Setup

1. Copy `.env.example` to `.env` and configure your API keys:
   ```bash
   cp .env.example .env
   ```
   Add your `GROQ_API_KEY`.

2. Install dependencies (or use Docker):
   ```bash
   pip install -r requirements.txt
   ```

3. Run the ingestion pipeline to scrape, parse, chunk, and embed documents:
   ```bash
   python scripts/ingest.py --step all
   ```

## Running the Application

You can use Docker Compose to spin up both the FastAPI backend and Streamlit UI:

```bash
docker-compose up --build
```
- **API**: http://localhost:8000/docs
- **UI**: http://localhost:8501

## Architecture

This project follows a 7-phase implementation:
1. **Bootstrap & Configuration**
2. **Data Acquisition**: Scraping HTML & PDF documents from official sources.
3. **Parsing & Chunking**: Structure-aware chunking preserving tables and section context.
4. **Embedding**: Using BAAI/bge-small-en-v1.5 and ChromaDB.
5. **Retrieval**: Scope guards (refusing weight loss, medical advice queries), relevance threshold, and cross-document grouping using a Maximal Marginal Relevance (MMR) style algorithm (oversampling `fetch_k=30` and filtering to `max_docs=3` and `max_chunks_per_doc=4`) to ensure diverse context.
6. **Answer Generation**: Groq LLM generating context-bound answers with precise inline citations.
7. **Integration**: FastAPI and Streamlit UI.

## Testing
Run tests using pytest:
```bash
pytest
```
# trigger redeploy
# redeploy trigger
