from pathlib import Path
from dataclasses import dataclass

PDF_FOLDER = Path("./data/pdfs")
OLLAMA_LOCAL_URL = "http://localhost:11434"
VECTOR_DATABASE_FILEPATH = Path("./data/chroma_database")
VECTOR_DATABASE_COLLECTION_NAME = "PDF_collection"


# DEFAULT_PARAMETERS = {
#     "OLLAMA_EMBEDDING_MODEL": "nomic-embed-text",
#     # Check pdf_chunking.AVAILABLE_CHUNKING_METHODS for a complete list
#     "PDF_CHUNKING_METHOD": "by_sections",
#     "OLLAMA_LLM_MODEL": "llama3:latest",
# }


@dataclass()
class Params:
    ollama_embedding_model: str = "nomic-embed-text"
    pdf_chunking_method: str = "by_sections"
    ollama_llm_model: str = "llama3:latest"
    # ollama_llm_model:str = "llama3.2:1b"
