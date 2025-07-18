from pathlib import Path

PDF_FOLDER = Path("./data/pdfs")
OLLAMA_LOCAL_URL = "http://localhost:11434"
VECTOR_DATABASE_FILEPATH = Path("./data/chroma_database")
VECTOR_DATABASE_COLLECTION_NAME = "PDF_collection"

OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"

PDF_CHUNKING_MODE = "unstructured"  # options: by_pages, unstructured
