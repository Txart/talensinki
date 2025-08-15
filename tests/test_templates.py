from pathlib import Path

from langchain.prompts import PromptTemplate

from talensinki import templates, checks


def create_mock_pdf_folderpath(tmp_path: Path) -> Path:
    temp_dir = tmp_path / "sub"
    temp_dir.mkdir()
    return temp_dir


def get_system_template_text() -> str:
    return """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""


def get_refine_template_text() -> str:
    return """
You have been provided with an existing answer: {existing_answer}
You have the opportunity to refine the existing answer with some more context below.

Context: {context}

Given the new context, refine the original answer to better address the question.
If the context isn't useful, return the original answer.

Question: {question}
Refined Answer:"""


def get_system_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["question", "context"],
        template="""
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
""",
    )


def get_refine_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["question", "existing_answer", "context"],
        template="""
You have been provided with an existing answer: {existing_answer}
You have the opportunity to refine the existing answer with some more context below.

Context: {context}

Given the new context, refine the original answer to better address the question.
If the context isn't useful, return the original answer.

Question: {question}
Refined Answer:""",
    )


def test_get_templates_from_file(tmp_path: Path):
    sys_temp = tmp_path / "sys_temp.txt"
    ref_temp = tmp_path / "ref_temp.txt"

    sys_temp.write_text(data=get_system_template_text())
    ref_temp.write_text(data=get_refine_template_text())

    assert templates.get_prompt_template_from_file(sys_temp) == get_system_prompt()
    assert templates.get_prompt_template_from_file(ref_temp) == get_refine_prompt()

    assert checks._check_prompt_template_has_expected_variables(
        template_filepath=sys_temp, input_variables=["question", "context"]
    )

    assert not checks._check_prompt_template_has_expected_variables(
        template_filepath=sys_temp, input_variables=["question", "context", "pyramid"]
    )
