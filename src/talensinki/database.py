from pathlib import Path
import hashlib
from typing import Any
from uuid import uuid4
from rich.progress import track
from rich import print
import typer

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain_unstructured import UnstructuredLoader
from langchain_community.vectorstores.utils import filter_complex_metadata
import chromadb
from chromadb.api import ClientAPI
from chromadb import Collection

from talensinki import config, rich_display
from talensinki.console import console


def get_pdf_filepaths_in_folder(folder: Path) -> list[Path]:
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
        console.print(
            f"Fetched the collection {config.VECTOR_DATABASE_COLLECTION_NAME} from the database"
        )

    except Exception as e:
        console.print(
            f"The collection was not found or could not be opened (exception: {e})"
        )
        console.print(
            f"Creating a new collection at {config.VECTOR_DATABASE_FILEPATH}..."
        )

        collection = chroma_client.create_collection(
            name=config.VECTOR_DATABASE_COLLECTION_NAME,
        )
        console.print("New collection created!")

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


def chunk_pdf_by_sections(pdf_path: Path) -> list[Document]:
    loader = UnstructuredLoader(
        file_path=pdf_path, strategy="hi_res", languages=["eng"]
    )

    docs = []
    for doc in loader.load():
        docs.append(doc)

    console.print("Leaving out complex metadata from the UnstructuredLoader...")
    filtered_docs = filter_complex_metadata(docs)

    return filtered_docs


def chunk_pdfs_with_metadata(
    pdf_paths: list[Path], chunk_mode: str
) -> list[list[Document]]:
    match chunk_mode:
        case "by_pages":
            chunking_function = chunk_pdf_by_pages
        case "unstructured":
            chunking_function = chunk_pdf_by_sections
        case _:
            raise NotImplementedError(
                "The selected PDF chunking mode is not implemented."
            )
    chunks_with_metadata = []

    for pdf_path in track(
        pdf_paths,
        description=f"Chunking the PDFs using the {config.PDF_CHUNKING_MODE} chunking mode...",
    ):
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
        chunks_for_all_pdfs,
        description=f"Embedding pdfs into the database using the {config.OLLAMA_EMBEDDING_MODEL} embedding model...",
    ):
        # each chunk needs to have a different id in the database
        uuids = [str(uuid4()) for _ in range(len(chunks_for_single_pdf))]
        vector_store.add_documents(
            documents=chunks_for_single_pdf,
            ids=uuids,
        )
    console.print("Embedded all new pdfs.")
    return None


def add_pdfs_to_database(vector_store: Chroma, pdf_paths: list[Path]) -> None:
    chunks_for_all_pdfs = chunk_pdfs_with_metadata(
        pdf_paths=pdf_paths, chunk_mode=config.PDF_CHUNKING_MODE
    )
    embed_pdfs_to_database(
        vector_store=vector_store, chunks_for_all_pdfs=chunks_for_all_pdfs
    )
    return None


def delete_entries_from_database(vector_store: Chroma, ids: list[str]) -> None:
    vector_store.delete(ids=ids)
    return None


def get_item_id_and_metadata_from_database(vector_store: Chroma) -> tuple[list, list]:
    # gets all items from database
    docs_ids_and_metadatas = vector_store.get(include=["metadatas"])
    docs_ids = docs_ids_and_metadatas["ids"]
    docs_metadatas = docs_ids_and_metadatas["metadatas"]
    return docs_ids, docs_metadatas


def get_pdf_hashes_in_database(vector_store: Chroma) -> tuple[str]:
    # gets all items from database
    ids, metadatas = get_item_id_and_metadata_from_database(vector_store)
    return tuple(metadata["source_pdf_hash"] for metadata in metadatas)


def does_pdf_exist_in_database(vector_store: Chroma, pdf_file_hash: str) -> bool:
    """Check if documents with the given PDF hash already exist"""
    existing_docs = vector_store.get(where={"source_pdf_hash": pdf_file_hash})
    return len(existing_docs["ids"]) > 0


def get_hashes_of_files_in_folder_but_not_in_database(
    hash_to_path_dict: dict, hashes_in_database: tuple
) -> tuple[str]:
    return tuple(set(hash_to_path_dict.keys()).difference(set(hashes_in_database)))


def get_hashes_of_files_in_database_but_not_in_folder(
    hash_to_path_dict: dict, hashes_in_database: tuple
) -> tuple[str]:
    return tuple(set(hashes_in_database).difference(set(hash_to_path_dict.keys())))


def get_ids_of_entries_with_specific_hashes(
    vector_store: Chroma, hashes: tuple[str, ...]
) -> list[str]:
    docs_ids, docs_metadatas = get_item_id_and_metadata_from_database(
        vector_store=vector_store
    )
    docs_ids_with_hash = []
    for doc_id, doc_metadata in zip(docs_ids, docs_metadatas):
        if doc_metadata["source_pdf_hash"] in hashes:
            docs_ids_with_hash.append(doc_id)
    return docs_ids_with_hash


def check_sync_status_between_folder_and_database(
    vector_store: Chroma, pdf_folder: Path
) -> tuple[list[Path], list[str]]:
    """
    Returns:
    - New files not in database, i.e., file paths of pdfs in folder but not in database
    - Files removed from folder but not from database, i.e., ids of entries in database corresponding to files that are no longer pdf folder
    """
    pdf_filepaths = get_pdf_filepaths_in_folder(folder=pdf_folder)
    # compute folder file hash to save as a metadata and be able to check uniqueness later
    hash_to_path_dict = {
        calculate_file_hash(file_path=pdf_path): pdf_path for pdf_path in pdf_filepaths
    }

    hashes_in_database = get_pdf_hashes_in_database(vector_store=vector_store)

    new_pdf_hashes_in_folder = get_hashes_of_files_in_folder_but_not_in_database(
        hash_to_path_dict=hash_to_path_dict, hashes_in_database=hashes_in_database
    )

    database_hashes_corresponding_to_removed_pdfs = (
        get_hashes_of_files_in_database_but_not_in_folder(
            hash_to_path_dict=hash_to_path_dict, hashes_in_database=hashes_in_database
        )
    )

    new_pdf_paths = [
        hash_to_path_dict[new_pdf_hash] for new_pdf_hash in new_pdf_hashes_in_folder
    ]

    old_database_entry_ids = get_ids_of_entries_with_specific_hashes(
        vector_store=vector_store, hashes=database_hashes_corresponding_to_removed_pdfs
    )

    return new_pdf_paths, old_database_entry_ids


def init_and_get_vector_store() -> Chroma:
    # create and/or get chroma database
    db_client = initialize_chroma_database_client()

    # get database collection. If it does not exist, create it.
    # This is used to make sure that the database exists.
    _ = get_or_create_database_collection(chroma_client=db_client)

    # The vector store, not the collection, is what is used later
    return get_vector_store_from_client(chroma_client=db_client)
