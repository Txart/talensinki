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

# initialize typer app
app = typer.Typer()


# %% app


@app.command()
def info():
    print("pdf folder path:", config.PDF_FOLDER)


@app.command()
def checkhealth() -> None:
    rich_display.print_command_title("Health Check Results")
    checks.run_health_checks()


@app.command()
def sync_database() -> None:
    rich_display.print_command_title("Syncing database")
    database.sync_database_and_folder()


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
