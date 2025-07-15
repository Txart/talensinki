from pathlib import Path
from talensinki import config


def read_pdf_files_in_folder() -> list[Path]:
    return [pdf_file for pdf_file in config.PDF_FOLDER.glob("*.pdf")]
