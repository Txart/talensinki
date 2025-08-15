from pathlib import Path
from dataclasses import dataclass

from langchain.prompts import PromptTemplate


@dataclass
class TemplateType:
    dir: Path
    input_variables: list[str]


def get_template_types() -> list[TemplateType]:
    TEMPLATES_GENERAL_DIR = Path("./prompt_templates")

    # There should be one type per subfolder in {TEMPLATER_GENERAL_DIR}
    system_template = TemplateType(
        dir=TEMPLATES_GENERAL_DIR.joinpath("system"),
        input_variables=["context", "question"],
    )

    # Register template types
    return [
        system_template,
    ]


def get_prompt_template_from_file(filepath: Path) -> PromptTemplate:
    return PromptTemplate.from_file(template_file=filepath)
