from pathlib import Path
from dataclasses import dataclass

from langchain.prompts import PromptTemplate


class TemplateType:
    # Each type corresponds to a subdir in ./prompt_templates
    def __init__(self, name: str, input_variables: list[str]):
        self.name = name
        self.input_variables = input_variables

        TEMPLATES_GENERAL_DIR = Path("./prompt_templates")
        self.dir = TEMPLATES_GENERAL_DIR.joinpath("system")


@dataclass
class PromptTemplateFromFile:
    # Each template corresponds to a .txt file in ./prompt_templates/<template type>/
    filename: str
    prompt: PromptTemplate


def get_template_types() -> list[TemplateType]:
    # There should be one type per subfolder in {TEMPLATER_GENERAL_DIR}
    system_template = TemplateType(
        name="system",
        input_variables=["context", "question"],
    )

    # Register template types
    return [
        system_template,
    ]


def get_prompt_template_from_file(filepath: Path) -> PromptTemplateFromFile:
    return PromptTemplateFromFile(
        filename=filepath.name, prompt=PromptTemplate.from_file(template_file=filepath)
    )


def get_template_filenames_of_given_type(template_type: TemplateType) -> list[Path]:
    return [filepath for filepath in template_type.dir.glob("*.txt")]


def get_templates_given_type(
    template_type: TemplateType,
) -> list[PromptTemplateFromFile]:
    templates = []

    for filepath in get_template_filenames_of_given_type(template_type=template_type):
        templates.append(get_prompt_template_from_file(filepath=filepath))

    return templates


def get_all_prompt_templates_by_type() -> dict[str, list[PromptTemplateFromFile]]:
    return {
        template_type.name: get_templates_given_type(template_type)
        for template_type in get_template_types()
    }
