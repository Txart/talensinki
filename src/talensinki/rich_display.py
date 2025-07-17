from talensinki.console import console


def print_command_title(s: str) -> None:
    console.print(f"\n[bold blue]{s}[/bold blue]")
    return None


def print_success(s: str) -> None:
    console.print(f"[bold green]✅ {s}[/bold green]\n")
