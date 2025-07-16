from pathlib import Path
import hashlib

from talensinki import config


def get_pdf_files() -> list[Path]:
    return _get_pdf_files_in_folder(folder=config.PDF_FOLDER)


def _get_pdf_files_in_folder(folder: Path) -> list[Path]:
    return [pdf_file for pdf_file in folder.glob("*.pdf")]


def calculate_file_hash(file_path: Path):
    """Calculate SHA256 hash of a file"""
    hasher = hashlib.sha256()

    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()
