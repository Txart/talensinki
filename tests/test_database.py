from pathlib import Path
from langchain_community.embeddings import DeterministicFakeEmbedding
from langchain_chroma import Chroma
from langchain_core.documents import Document

from talensinki import database


def create_mock_pdf_folderpath(tmp_path: Path) -> Path:
    pdf_dir = tmp_path / "sub"
    pdf_dir.mkdir()
    return pdf_dir


def create_mock_pdf_files(pdf_dir: Path):
    file1 = pdf_dir / "file_1.pdf"
    file2 = pdf_dir / "file_2.pdf"

    file1.write_text(data="lilili")
    file2.write_text(data="lilila")
    return None


def create_mock_txt_files(pdf_dir: Path):
    file1 = pdf_dir / "file_1.txt"
    file2 = pdf_dir / "file_2.txt"

    file1.write_text(data="lilili")
    file2.write_text(data="lilila")
    return None


def test_get_pdf_files_in_folder(tmp_path: Path):
    pdf_dir = create_mock_pdf_folderpath(tmp_path)
    create_mock_pdf_files(pdf_dir=pdf_dir)
    create_mock_txt_files(pdf_dir=pdf_dir)
    assert len(database.get_pdf_filepaths_in_folder(folder=pdf_dir)) == 2


def create_mock_embeddings_database(tmp_path: Path) -> Chroma:
    # create database directory
    d_dir = tmp_path / "dat"
    d_dir.mkdir()

    embeddings = DeterministicFakeEmbedding(size=4096)
    return Chroma(
        collection_name="test_collection",
        embedding_function=embeddings,
        persist_directory=str(d_dir),
    )


def add_mock_documents_to_database(vector_store: Chroma) -> None:
    document_1 = Document(page_content="foo", metadata={"source_pdf_hash": "123"})
    document_2 = Document(page_content="bar", metadata={"source_pdf_hash": "456"})
    document_3 = Document(page_content="foo3", metadata={"source_pdf_hash": "789"})

    documents = [document_1, document_2, document_3]
    ids = ["1", "2", "3"]
    vector_store.add_documents(documents=documents, ids=ids)
    return None


def test_get_pdf_hashes_in_database(tmp_path: Path) -> None:
    vector_store = create_mock_embeddings_database(tmp_path=tmp_path)
    add_mock_documents_to_database(vector_store)

    db_hashes = database.get_pdf_hashes_in_database(vector_store)
    assert set(db_hashes) == set(["123", "456", "789"])


def test_delete_entries_from_database(tmp_path: Path):
    vector_store = create_mock_embeddings_database(tmp_path=tmp_path)
    add_mock_documents_to_database(vector_store)

    database.delete_entries_from_database(vector_store=vector_store, ids=["1"])

    docs_ids, _ = database.get_item_id_and_metadata_from_database(vector_store)

    assert docs_ids == ["2", "3"]


def test_get_hashes_of_files_in_folder_but_not_in_database():
    hash_to_path_dict = {"hash1": Path(), "hash2": Path()}
    hashes_in_database = ("432134", "hash1")

    assert tuple(
        ["hash2"]
    ) == database.get_hashes_of_files_in_folder_but_not_in_database(
        hash_to_path_dict=hash_to_path_dict, hashes_in_database=hashes_in_database
    )


def test_get_hashes_of_files_in_database_but_not_in_folder():
    hash_to_path_dict = {"hash1": Path(), "hash2": Path()}
    hashes_in_database = ("432134", "hash1")

    assert tuple(
        ["432134"]
    ) == database.get_hashes_of_files_in_database_but_not_in_folder(
        hash_to_path_dict=hash_to_path_dict, hashes_in_database=hashes_in_database
    )


def test_get_ids_of_entries_with_specific_hashes(tmp_path: Path):
    vector_store = create_mock_embeddings_database(tmp_path=tmp_path)
    add_mock_documents_to_database(vector_store)

    ids = database.get_ids_of_entries_with_specific_hashes(
        vector_store, hashes=tuple(["123", "456"])
    )

    assert ["1", "2"] == ids


def test_check_sync_status_between_folder_and_database(tmp_path: Path):
    pdf_dir = create_mock_pdf_folderpath(tmp_path)
    create_mock_pdf_files(pdf_dir=pdf_dir)
    create_mock_txt_files(pdf_dir=pdf_dir)

    vector_store = create_mock_embeddings_database(tmp_path=tmp_path)
    add_mock_documents_to_database(vector_store)

    pdf_paths_to_add, entry_ids_to_remove = (
        database.check_sync_status_between_folder_and_database(
            vector_store=vector_store, pdf_folder=pdf_dir
        )
    )

    assert set(pdf_paths_to_add) == set(
        tuple([Path(pdf_dir / "file_1.pdf"), Path(pdf_dir / "file_2.pdf")])
    )

    assert set(entry_ids_to_remove) == set(["1", "2", "3"])
