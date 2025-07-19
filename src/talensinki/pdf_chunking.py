from pathlib import Path
from typing import Protocol, runtime_checkable

from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain_unstructured import UnstructuredLoader
from langchain_community.vectorstores.utils import filter_complex_metadata

from rich.progress import track

from talensinki import config, database
from talensinki.console import console


@runtime_checkable
class PDFChunker(Protocol):
    """
    Protocol (function blueprint, or in Rust, trait) for PDF chunking functions that take a Path and return a list of langchain Documents.
    """

    def __call__(self, pdf_path: Path) -> list[Document]:
        """Chunk a PDF file into a list of Document objects."""
        ...


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
    pdf_paths: list[Path], chunker_function: PDFChunker
) -> list[list[Document]]:
    chunks_with_metadata = []

    for pdf_path in track(
        pdf_paths,
        description=f"Chunking the PDFs using the {config.PDF_CHUNKING_FUNCTION} chunking function...",
    ):
        pdf_file_hash = database.calculate_file_hash(file_path=pdf_path)
        pdf_chunks = chunker_function(pdf_path)
        chunks_with_metadata.append(
            [
                assign_source_pdf_metadata_info_to_document(
                    doc=pdf_chunk, source_pdf_hash=pdf_file_hash
                )
                for pdf_chunk in pdf_chunks
            ]
        )

    return chunks_with_metadata


AVAILABLE_PDF_CHUNKERS: dict[str, PDFChunker] = {
    "by_pages": chunk_pdf_by_pages,
    "by_sections": chunk_pdf_by_sections,
}

CHUNKER_METADATA = {
    "by_pages": {
        "name": "Page-based Chunking",
        "description": "Splits PDF by pages using PyPDFLoader",
        "function": chunk_pdf_by_pages,
    },
    "by_sections": {
        "name": "Section-based Chunking",
        "description": "Splits PDF by sections using UnstructuredLoader with hi-res strategy",
        "function": chunk_pdf_by_sections,
    },
}


def get_chunker(name: str) -> PDFChunker:
    """Get a chunker by name from configuration."""
    if name not in AVAILABLE_PDF_CHUNKERS:
        available = list(AVAILABLE_PDF_CHUNKERS.keys())
        raise ValueError(f"Unknown chunker '{name}'. Available: {available}")
    return AVAILABLE_PDF_CHUNKERS[name]
