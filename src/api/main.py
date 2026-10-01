from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from src.api.routes import router

app = FastAPI(title="Dietary Guidance RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

ui_path = os.path.join(os.path.dirname(__file__), "..", "..", "ui")

@app.get("/")
async def read_index():
    index_file = os.path.join(ui_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "UI not found"}

@app.get("/ping")
async def ping():
    return {"ping": "ok"}

@app.get("/api/v1/debug/corpus")
async def debug_corpus():
    """Returns Chroma vector count + persist path – use to verify ingestion."""
    import os
    from src.retrieval.vector_store import VectorStore
    from src.config import settings
    vs = VectorStore()
    count = vs.count()
    return {
        "chroma_persist_dir": settings.chroma_persist_dir,
        "abs_path": os.path.abspath(settings.chroma_persist_dir),
        "dir_exists": os.path.isdir(settings.chroma_persist_dir),
        "vector_count": count,
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=port)
