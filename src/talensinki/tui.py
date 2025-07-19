# %%
from os import system
from langchain import hub
from pathlib import Path
from typing_extensions import Annotated

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

from talensinki import config, checks, database, rich_display
from talensinki.console import console

# initialize typer app
app = typer.Typer()


# %% app


@app.command()
def info():
    console.print("pdf folder path:", config.PDF_FOLDER)


@app.command()
def checkhealth() -> None:
    rich_display.print_command_title("Health Check Results")
    checks.run_health_checks()
    return None


@app.command()
def sync_database() -> None:
    rich_display.print_command_title("Syncing database")

    vector_store = database.init_and_get_vector_store()

    pdf_paths_to_add, entry_ids_to_remove = (
        database.check_sync_status_between_folder_and_database(
            vector_store=vector_store, pdf_folder=config.PDF_FOLDER
        )
    )

    number_of_new_pdfs_in_folder = len(pdf_paths_to_add)
    number_of_unsynced_db_entries = len(entry_ids_to_remove)

    if number_of_new_pdfs_in_folder > 0:
        console.print(
            f"I detected {number_of_new_pdfs_in_folder} new pdfs that are not yet embedded in the database:"
        )
        console.print(pdf_paths_to_add)
        should_add = typer.confirm("Do you want to create their embeddings now?")
        if should_add:
            database.add_pdfs_to_database(
                vector_store=vector_store,
                pdf_paths=pdf_paths_to_add,
            )
    else:
        console.print("No new pdf files detected.")
    if number_of_unsynced_db_entries > 0:
        console.print(
            f"I detected {number_of_unsynced_db_entries} pdf chunks in the database that do not correspond to any pdf file."
        )

        should_delete = typer.confirm(
            "Do you want to remove them from the database now?"
        )
        if should_delete:
            console.print("I will delete them from the database now.")
            database.delete_entries_from_database(
                vector_store=vector_store, ids=entry_ids_to_remove
            )
    else:
        console.print(
            "I did not detect any database entry without a corresponding pdf file."
        )
    rich_display.print_success("Database and folder file are in sync")
    return None


def retrieve_docs(question: str) -> dict["str", list[Document]]:
    vector_store = database.init_and_get_vector_store()
    retrieved_docs = vector_store.similarity_search(query=question)
    return {"context": retrieved_docs}


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
    return None
