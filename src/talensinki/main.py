# %%
from os import system
from langchain import hub
from pathlib import Path

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
    # create and/or get chroma database
    db_client = database.initialize_chroma_database_client()

    # get database collection. If it does not exist, create it.
    # This is used to make sure that the database exists.
    database.get_or_create_database_collection(chroma_client=db_client)

    # The vector store, not the collection, is what is used in langchain.
    vector_store = database.get_vector_store_from_client(chroma_client=db_client)

    # get pdf filenames
    pdf_filepaths = database.get_pdf_filepaths_in_folder()

    # compute file hash to save as a metadata and be able to check uniqueness later
    hash_to_path_dict = {
        database.calculate_file_hash(file_path=pdf_path): pdf_path
        for pdf_path in pdf_filepaths
    }

    # get all items from database
    hashes_in_database: set[str] = database.get_pdf_hashes_in_database(
        vector_store=vector_store
    )

    # File hashes in folder but not in database
    new_pdf_hashes_in_folder = set(hash_to_path_dict.keys()).difference(
        hashes_in_database
    )

    # File hashes in database but not in folder
    database_entries_corresponding_to_removed_pdfs = hashes_in_database.difference(
        set(hash_to_path_dict.keys())
    )

    number_of_new_pdfs_in_folder = len(new_pdf_hashes_in_folder)
    number_of_unsynced_db_entries = len(database_entries_corresponding_to_removed_pdfs)

    if number_of_new_pdfs_in_folder > 0:
        print(
            f"I detected {number_of_new_pdfs_in_folder} new pdfs that are not yet embedded in the database:"
        )
        new_pdf_paths = [
            hash_to_path_dict[new_pdf_hash] for new_pdf_hash in new_pdf_hashes_in_folder
        ]
        print(new_pdf_paths)
        print("TODO: PROMPT FOR CONFIRMATION!")
        print("I will add them to the database now.")

        database.add_pdfs_to_database(
            vector_store=vector_store,
            pdf_paths=new_pdf_paths,
        )
    else:
        print("No new pdf files detected.")
    if number_of_unsynced_db_entries > 0:
        print(
            f"I detected {number_of_unsynced_db_entries} new pdfs that are not yet embedded in the database."
        )
        print("I will delete them from the database now.")

        print("TODO: PROMPT FOR CONFIRMATION!")
        raise NotImplementedError("database deletion not implemented yet!")
    else:
        print("No unsynced database entries detected.")

    print("TODO: if pdf not in directory anymore, remove entry from database.")

    print(f"Database is synchronized with pdf folder {config.PDF_FOLDER}.")


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
