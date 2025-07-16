from pathlib import Path
import hashlib
from typing import Any

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
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
    try:
        collection = chroma_client.get_collection(
            name=config.VECTOR_DATABASE_COLLECTION_NAME
        )
        print(
            f"Fetched the collection {config.VECTOR_DATABASE_COLLECTION_NAME} from the database"
        )

    except Exception as e:
        print(f"The collection was not found or could not be opened (exception: {e})")
        print(f"Creating a new collection at {config.VECTOR_DATABASE_FILEPATH}...")

        collection = chroma_client.create_collection(
            name=config.VECTOR_DATABASE_COLLECTION_NAME,
        )
        print("New collection created!")

    return collection


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


def load_single_pdf_pages(pdf_path: Path):
    loader = PyPDFLoader(str(pdf_path))
    pages = []
    for page in loader.lazy_load():
        pages.append(page)

    return pages


def assign_source_pdf_metadata_info_to_document(
    doc: Document, source_pdf_hash: str
) -> Document:
    return Document(
        page_content=doc.page_content,
        metadata={
            "source_pdf_hash": source_pdf_hash,
            **doc.metadata,  # This preserves existing metadata
        },
    )


def does_pdf_exist_in_database(vector_store: Chroma, pdf_file_hash: str) -> bool:
    """Check if documents with the given PDF hash already exist"""
    existing_docs = vector_store.get(where={"source_pdf_hash": pdf_file_hash})
    return len(existing_docs["ids"]) > 0
