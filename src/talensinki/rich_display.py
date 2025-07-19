from talensinki.console import console
from rich.panel import Panel


def print_command_title(s: str) -> None:
    console.print(f"\n[bold blue]{s}[/bold blue]")
    return None


def print_success(s: str) -> None:
    console.print(Panel(s, style="green", padding=(1, 2)))


def print_failure(s: str) -> None:
    console.print(Panel(s, style="red", padding=(1, 2)))
