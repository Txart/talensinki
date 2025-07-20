# %%

import typer
from rich import print


from langchain_core.documents import Document

import time

from talensinki import config, checks, database, rich_display, llm
from talensinki.console import console

# initialize typer app
app = typer.Typer(invoke_without_command=True)


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


@app.command()
def ask(question: str) -> None:
    answer = llm.ask_question(question=question)
    console.print(answer)
    return None


def run_by_default() -> None:
    print("Talensinki app starting...")

    # Your RAG setup will go here

    # Keep the container running
    print("App is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")


@app.callback()
def main(context: typer.Context) -> None:
    """
    Ask some qusetion about your pdfs!
    """
    # Main function that runs when no subcommand is specified.
    if context.invoked_subcommand is None:
        # This code runs when no subcommand is provided
        run_by_default()
    return None
