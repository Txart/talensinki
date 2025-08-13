# %%

import typer
from rich import print
from rich.table import Table


import time

from talensinki import config, checks, database, rich_display, llm
from talensinki.console import console
from talensinki.checks import HealthCheckResult

# initialize typer app
app = typer.Typer(invoke_without_command=True)


# %% app


@app.command()
def info():
    console.print("pdf folder path:", config.PDF_FOLDER)


def _display_health_checks(check_results: list[HealthCheckResult]) -> None:
    # Create a table for the results
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Status", style="", width=8)
    table.add_column("Check", style="", min_width=20)
    table.add_column("Details", style="dim", no_wrap=False)

    all_passed = True

    # Display results
    for result in check_results:
        if result.passed:
            status = "[green]✅ PASS[/green]"
            details = "[dim]OK[/dim]"
        else:
            status = "[red]❌ FAIL[/red]"
            details = (
                f"[red]{result.details}[/red]"
                if result.details
                else "[red]Failed[/red]"
            )
            all_passed = False

        table.add_row(status, result.name, details)

    console.print(table)

    # Summary panel
    if all_passed:
        rich_display.print_success("All health checks passed!")
    else:
        rich_display.print_failure("Some health checks failed!")

    if not all_passed:
        raise typer.Exit(1)  # Exit with error code


@app.command()
def checkhealth() -> None:
    rich_display.print_command_title("Health Check Results")
    check_results = checks.run_health_checks()
    _display_health_checks(check_results=check_results)
    return None


@app.command()
def sync_database() -> None:
    rich_display.print_command_title("Syncing database")

    params = config.Params()

    vector_store = database.init_and_get_vector_store(params=params)

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
                params=params,
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
    params = config.Params()
    answer = llm.ask_question(question=question, params=params)
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
