from pathlib import Path
import hashlib
from typing import Any
from uuid import uuid4
from rich.progress import track
from rich import print

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import chromadb
from chromadb.api import ClientAPI
from chromadb import Collection

from talensinki import config


def get_pdf_filepaths_in_folder() -> list[Path]:
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
            model=config.OLLAMA_EMBEDDING_MODEL,
            base_url=config.OLLAMA_LOCAL_URL,
        ),
    )


def chunk_pdf_by_pages(pdf_path: Path) -> list[Document]:
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


def chunk_pdfs_with_metadata(
    pdf_paths: list[Path], chunk_mode: str
) -> list[list[Document]]:
    match chunk_mode:
        case "by_pages":
            chunking_function = chunk_pdf_by_pages
        case _:
            raise NotImplementedError(
                "The selected PDF chunking mode is not implemented."
            )
    chunks_with_metadata = []
    for pdf_path in pdf_paths:
        pdf_file_hash = calculate_file_hash(file_path=pdf_path)
        pdf_chunks = chunking_function(pdf_path)
        chunks_with_metadata.append(
            [
                assign_source_pdf_metadata_info_to_document(
                    doc=pdf_chunk, source_pdf_hash=pdf_file_hash
                )
                for pdf_chunk in pdf_chunks
            ]
        )

    return chunks_with_metadata


def embed_pdfs_to_database(
    vector_store: Chroma, chunks_for_all_pdfs: list[list[Document]]
) -> None:
    for chunks_for_single_pdf in track(
        chunks_for_all_pdfs, description="Embedding pdfs into the database..."
    ):
        # each chunk needs to have a different id in the database
        uuids = [str(uuid4()) for _ in range(len(chunks_for_single_pdf))]
        vector_store.add_documents(
            documents=chunks_for_single_pdf,
            ids=uuids,
        )
    print("Embedded all new pdfs.")
    return None


def add_pdfs_to_database(vector_store: Chroma, pdf_paths: list[Path]) -> None:
    chunks_for_all_pdfs = chunk_pdfs_with_metadata(
        pdf_paths=pdf_paths, chunk_mode=config.PDF_CHUNKING_MODE
    )
    embed_pdfs_to_database(
        vector_store=vector_store, chunks_for_all_pdfs=chunks_for_all_pdfs
    )
    return None


def get_pdf_hashes_in_database(vector_store: Chroma) -> set[str]:
    docs_ids_and_metadatas = vector_store.get(include=["metadatas"])

    return set(
        (
            metadata["source_pdf_hash"]
            for metadata in docs_ids_and_metadatas["metadatas"]
        )
    )


def does_pdf_exist_in_database(vector_store: Chroma, pdf_file_hash: str) -> bool:
    """Check if documents with the given PDF hash already exist"""
    existing_docs = vector_store.get(where={"source_pdf_hash": pdf_file_hash})
    return len(existing_docs["ids"]) > 0
