# %%
from os import system
from langchain import hub
from pathlib import Path
from uuid import uuid4

import typer
from rich import print
from rich.console import Console


from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph, message

import time

from talensinki import config, checks, database

# initialize typer app
app = typer.Typer()
console = Console()


# %% app


@app.command()
def info():
    print("pdf folder path:", config.PDF_FOLDER)


@app.command()
def checkhealth() -> None:
    checks.run_health_checks(console)


@app.command()
def sync_database() -> None:
    PUT SOME API ORDER IN HERE!!
    # get pdf filenames
    pdf_list = database.get_pdf_files()

    # create and/or get chroma database
    db_client = database.initialize_chroma_database_client()
    collection = database.get_or_create_database_collection(chroma_client=db_client)
    vector_store = database.get_vector_store_from_client(chroma_client=db_client)

    pages = database.load_single_pdf_pages(pdf_path=pdf_list[0])
    # compute file hash to save as a metadata and be able to check uniqueness later
    pdf_file_hash = database.calculate_file_hash(file_path=pdf_list[0])
    pages_with_metadata = [
        database.assign_source_pdf_metadata_info_to_document(
            doc=page, source_pdf_hash=pdf_file_hash
        )
        for page in pages
    ]

    uuids = [str(uuid4()) for _ in range(len(pages_with_metadata))]
    print("Embedding pdf 1...")
    vector_store.add_documents(
        documents=pages_with_metadata,
        ids=uuids,
    )
    print("Embedded!")

    print(vector_store)
    # collection = database.get_or_create_database_collection(chroma_client=db_client)
    # collection.query(where={"source_pdf_hash": pdf_file_hash})
    is_pdf_in_database = database.does_pdf_exist_in_database(
        vector_store=vector_store, pdf_file_hash=pdf_file_hash
    )
    if is_pdf_in_database:
        print("PDF is already in database!")
    elif not is_pdf_in_database:
        print("This PDF is not in the database!")

    print("TODO: Query database by pdf file hashes")
    print(
        "TODO: Compare pdfs with database. If any pdf not in database, update database. AND: if pdf not in directory anymore, remove entry from database."
    )


@app.command()
def run():
    print("Talensinki app starting...")

    # Your RAG setup will go here

    # Keep the container running
    print("App is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
