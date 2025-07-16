from pathlib import Path
from langchain_community.embeddings import DeterministicFakeEmbedding
from langchain_chroma import Chroma

from talensinki.database import _get_pdf_files_in_folder


def test_get_pdf_files_in_folder(tmp_path: Path):
    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()

    file1 = sub_dir / "file_1.pdf"
    file2 = sub_dir / "file_2.pdf"
    file3_not_pdf = sub_dir / "file_3.txt"

    file1.write_text(data="lilili")
    file2.write_text(data="lilila")
    file3_not_pdf.write_text(data="lililo")

    assert len(_get_pdf_files_in_folder(folder=sub_dir)) == 2


# def create_fake_embeddings_database(tmp_path: Path):
#     # create database directory
#     d_dir = tmp_path / "dat"
#     d_dir.mkdir()
#
#     embeddings = DeterministicFakeEmbedding(size=4096)
#     vector_store = Chroma(
#         collection_name="test_collection",
#         embedding_function=embeddings,
#         persist_directory=d_dir,
#     )
