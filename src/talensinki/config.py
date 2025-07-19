from pathlib import Path

from talensinki.pdf_chunking import AVAILABLE_PDF_CHUNKERS

PDF_FOLDER = Path("./data/pdfs")
OLLAMA_LOCAL_URL = "http://localhost:11434"
VECTOR_DATABASE_FILEPATH = Path("./data/chroma_database")
VECTOR_DATABASE_COLLECTION_NAME = "PDF_collection"

OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"

PDF_CHUNKING_FUNCTION = AVAILABLE_PDF_CHUNKERS["by_pages"]
