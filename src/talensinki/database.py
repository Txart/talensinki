from pathlib import Path
import hashlib
from typing import Any

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import chromadb
from chromadb.api import ClientAPI
from chromadb import Collection

from talensinki import config


def get_pdf_files() -> list[Path]:
    return _get_pdf_files_in_folder(folder=config.PDF_FOLDER)


def _get_pdf_files_in_folder(folder: Path) -> list[Path]:
    return [pdf_file for pdf_file in folder.glob("*.pdf")]


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    hasher = hashlib.sha256()

    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def initialize_chroma_database_client() -> ClientAPI:
    return chromadb.PersistentClient(path=config.VECTOR_DATABASE_FILEPATH)


def get_or_create_database_collection(chroma_client: ClientAPI) -> Collection:
    print("WARNING: SEPARATE INTO GETTING AND CREATING FOR SECURITY")
    return chroma_client.get_or_create_collection(
        name=config.VECTOR_DATABASE_COLLECTION_NAME,
    )


def get_vector_store_from_client(chroma_client: ClientAPI) -> Chroma:
    return Chroma(
        client=chroma_client,
        collection_name=config.VECTOR_DATABASE_COLLECTION_NAME,
        embedding_function=OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=config.OLLAMA_LOCAL_URL,
        ),
    )


def query_database():
    return collection.query(where={"file_hash": file_hash}, limit=1)
