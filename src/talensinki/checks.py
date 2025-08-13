import requests


from dataclasses import dataclass
from pathlib import Path

from talensinki import config, database


@dataclass
class HealthCheckResult:
    passed: bool
    name: str
    details: str = ""


def run_health_checks() -> list[HealthCheckResult]:
    return [
        check_pdf_folder_exists(),
        check_config_file_exists(),
        check_database_connection(),
        check_ollama_connection(),
    ]


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
        database.init_and_get_vector_store(params=config.Params())

        return HealthCheckResult(passed=True, name=check_name)
    except Exception as e:
        return HealthCheckResult(
            passed=False, name=check_name, details=f"Connection failed: {str(e)}"
        )


def check_ollama_connection(base_url="http://localhost:11434") -> HealthCheckResult:
    check_name = "ollama is connected"
    try:
        requests.get(f"{base_url}/api/version", timeout=5)
    except Exception:
        return HealthCheckResult(
            passed=False,
            name=check_name,
            details=f"Could not connect to ollama at url {base_url}",
        )
    return HealthCheckResult(passed=True, name=check_name)
