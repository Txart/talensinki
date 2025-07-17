import typer

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


from dataclasses import dataclass
from pathlib import Path

from talensinki import config, rich_display
from talensinki.console import console


@dataclass
class HealthCheckResult:
    passed: bool
    name: str
    details: str = ""


def run_health_checks() -> None:
    """
    Run all health checks and display results.
    """
    check_results = _run_checks()

    _display_health_checks(check_results=check_results)


def _run_checks() -> list[HealthCheckResult]:
    return [
        check_pdf_folder_exists(),
        check_config_file_exists(),
        check_database_connection(),
    ]


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
        panel_style = "green"
    else:
        summary_text = "[bold red]❌ Some health checks failed![/bold red]"
        panel_style = "red"

    console.print(Panel(summary_text, style=panel_style, padding=(1, 2)))

    if not all_passed:
        raise typer.Exit(1)  # Exit with error code


# %% Checks


def check_pdf_folder_exists() -> HealthCheckResult:
    check_name = "PDF folder exists"
    if _folder_exists(path_to_folder=config.PDF_FOLDER):
        return HealthCheckResult(passed=True, name=check_name)
    else:
        return HealthCheckResult(
            passed=False,
            name=check_name,
            details=f"folder not found: {config.PDF_FOLDER}",
        )


def _folder_exists(path_to_folder: Path) -> bool:
    return path_to_folder.is_dir()


def check_config_file_exists() -> HealthCheckResult:
    """Check if configuration file exists."""
    check_name = "Configuration file exists"
    config_path = Path(
        "./src/talensinki/config.py"
    )  # Replace with your actual config path

    if config_path.exists():
        return HealthCheckResult(passed=True, name=check_name)
    else:
        return HealthCheckResult(
            passed=False,
            name=check_name,
            details=f"Config file not found: {config_path}",
        )


def check_database_connection() -> HealthCheckResult:
    """Check database connectivity."""
    check_name = "Database connection"

    try:
        # Replace with your actual database connection test
        # db.connect()
        # db.execute("SELECT 1")

        return HealthCheckResult(passed=False, name=check_name)
    except Exception as e:
        return HealthCheckResult(
            passed=False, name=check_name, details=f"Connection failed: {str(e)}"
        )
