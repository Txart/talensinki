from os import sync
from altair.vegalite import data
import click
import streamlit as st

from talensinki import database, config


def initialize_session_state() -> None:
    if "sync_checked" not in st.session_state:
        st.session_state.sync_checked = False
    if "pdf_paths_to_add" not in st.session_state:
        st.session_state.pdf_paths_to_add = []
    if "entry_ids_to_remove" not in st.session_state:
        st.session_state.entry_ids_to_remove = []


def database_sync_button() -> None:
    if st.button("🔍 Check Database Synchronization", type="primary"):
        with st.spinner("Checking synchronization status..."):
            pdf_paths_to_add, entry_ids_to_remove = (
                database.check_sync_status_between_folder_and_database(
                    vector_store=database.init_and_get_vector_store(),
                    pdf_folder=config.PDF_FOLDER,
                )
            )

        st.session_state.sync_checked = True
        st.session_state.pdf_paths_to_add = pdf_paths_to_add
        st.session_state.entry_ids_to_remove = entry_ids_to_remove
        st.rerun()


def sync_database_UI() -> None:
    # Display status with metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("New PDFs to embed", len(st.session_state.pdf_paths_to_add))
    with col2:
        st.metric(
            "Out of sync DB entries to remove",
            len(st.session_state.entry_ids_to_remove),
        )

    # Action buttons
    add_col, delete_col = st.columns([1, 1])

    with add_col:
        if len(st.session_state.pdf_paths_to_add) > 0:
            st.write(st.session_state.pdf_paths_to_add)
            if st.button("🚀 Embed PDFs"):
                with st.spinner("Embedding PDFs..."):
                    database.add_pdfs_to_database(
                        vector_store=database.init_and_get_vector_store(),
                        pdf_paths=st.session_state.pdf_paths_to_add,
                    )
                st.success(
                    f"✅ Embedded {len(st.session_state.pdf_paths_to_add)} PDFs!"
                )
                st.session_state.pdf_paths_to_add = []
                st.rerun()

    with delete_col:
        if len(st.session_state.entry_ids_to_remove) > 0:
            if st.button("🗑️ Remove Entries"):
                with st.spinner("Removing entries..."):
                    database.delete_entries_from_database(
                        vector_store=database.init_and_get_vector_store(),
                        ids=st.session_state.entry_ids_to_remove,
                    )
                st.success(
                    f"✅ Removed {len(st.session_state.entry_ids_to_remove)} entries!"
                )
                st.session_state.entry_ids_to_remove = []
                st.rerun()


st.title("Talensinki GUI")

initialize_session_state()

database_sync_button()

if st.session_state.sync_checked:
    sync_database_UI()
