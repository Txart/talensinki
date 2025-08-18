import requests


from dataclasses import dataclass
from pathlib import Path

from talensinki import config, database, templates, utils


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
        check_prompt_templates(),
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


# %% Templates


def _check_prompt_template_has_expected_variables(
    template_filepath: Path, input_variables: list[str]
) -> bool:
    """
    Returns true if the template from the file has the same input variables as the expected for its type.
    Each template subfolder corresponds to a template type.
    """
    template = templates.get_prompt_template_from_file(filepath=template_filepath)

    return set(template.prompt.input_variables) == set(input_variables)


def create_healthcheck_error(
    template_filepath: Path, required_input_variables: list[str]
) -> str:
    return f"Template {template_filepath.parent.name}/{template_filepath.name} must have the input variables {required_input_variables}."


def format_list_of_strings_into_bulletpoints(ls: list[str]) -> str:
    return "\n".join(["- " + s for s in ls])


def check_prompt_templates():
    """
    Checks that templates are valid and that they have the right variables for their type.
    """
    check_name = "templates are valid"

    # Unified healthcheck message
    healthcheck_errors: list[str] = []

    # Perform checks for all registered types
    for template_type in templates.get_template_types():
        template_filepaths = templates.get_template_filenames_of_given_type(
            template_type=template_type
        )
        for template_filepath in template_filepaths:
            if not _check_prompt_template_has_expected_variables(
                template_filepath=template_filepath,
                input_variables=template_type.input_variables,
            ):
                healthcheck_errors.append(
                    create_healthcheck_error(
                        template_filepath=template_filepath,
                        required_input_variables=template_type.input_variables,
                    )
                )

    # return HealthCheckResult
    if not healthcheck_errors:
        return HealthCheckResult(passed=True, name=check_name)
    else:
        return HealthCheckResult(
            passed=False,
            name=check_name,
            details=format_list_of_strings_into_bulletpoints(healthcheck_errors),
        )
