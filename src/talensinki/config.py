from pathlib import Path
from dataclasses import dataclass
import ollama
from typing import Literal


# %% Get models from ollama


@dataclass
class OllamaModel:
    name: str
    type: Literal["embedding", "llm"]


def get_available_ollama_models() -> list[OllamaModel]:
    """
    Get all available Ollama models
    """
    ollama_models = []
    try:
        response = ollama.list()
        for model in response["models"]:
            model_name = model["model"]
            model_type = guess_model_type(model_name=model_name)

            ollama_models.append(OllamaModel(name=model_name, type=model_type))

        return ollama_models

    except Exception as e:
        raise ValueError(f"Error fetching models: {e}")


def guess_model_type(model_name: str) -> Literal["embedding", "llm"]:
    """
    Attempt to categorize models based on naming patterns.
    Note: Ollama doesn't provide explicit model type tags.
    """
    # Common embedding model name patterns
    embedding_keywords = ["embed", "embedding", "nomic", "bge", "sentence"]

    model_lower = model_name.lower()
    if any(keyword in model_lower for keyword in embedding_keywords):
        return "embedding"
    else:
        return "llm"


ollama_models = get_available_ollama_models()
AVAILABLE_LLM_MODELS = [model.name for model in ollama_models if model.type == "llm"]
AVAILABLE_EMBEDDING_MODELS = [
    model.name for model in ollama_models if model.type == "embedding"
]

# %% Parameters

PDF_FOLDER = Path("./data/pdfs")
OLLAMA_LOCAL_URL = "http://localhost:11434"
VECTOR_DATABASE_FILEPATH = Path("./data/chroma_database")
VECTOR_DATABASE_COLLECTION_NAME = "PDF_collection"


@dataclass()
class Params:
    ollama_embedding_model: str = "nomic-embed-text:latest"
    pdf_chunking_method: str = "by_sections"
    ollama_llm_model: str = "llama3:latest"

    def __post_init__(self):
        if self.ollama_llm_model not in AVAILABLE_LLM_MODELS:
            raise ValueError(
                f"invalid LLM model chosen. It should be one of {AVAILABLE_LLM_MODELS}, and you chose {self.ollama_llm_model}."
            )

        if self.ollama_embedding_model not in AVAILABLE_EMBEDDING_MODELS:
            raise ValueError(
                f"invalid embedding model chosen. It should be one of {AVAILABLE_EMBEDDING_MODELS}, and you chose {self.ollama_embedding_model}."
            )
