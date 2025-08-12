import streamlit as st

from talensinki import database, config, llm


def initialize_session_state() -> None:
    if "sync_checked" not in st.session_state:
        st.session_state.sync_checked = False
    if "pdf_paths_to_add" not in st.session_state:
        st.session_state.pdf_paths_to_add = []
    if "entry_ids_to_remove" not in st.session_state:
        st.session_state.entry_ids_to_remove = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "params" not in st.session_state:
        st.session_state.params = config.Params()


def set_params(llm_model: str) -> None:
    params = config.Params(ollama_llm_model=llm_model)
    st.session_state.params = params

    return None


def database_sync_button() -> None:
    if st.button("Check Database Synchronization", type="primary"):
        with st.spinner("Checking synchronization status..."):
            pdf_paths_to_add, entry_ids_to_remove = (
                database.check_sync_status_between_folder_and_database(
                    vector_store=database.init_and_get_vector_store(
                        params=st.session_state.params
                    ),
                    pdf_folder=config.PDF_FOLDER,
                )
            )

        st.session_state.sync_checked = True
        st.session_state.pdf_paths_to_add = pdf_paths_to_add
        st.session_state.entry_ids_to_remove = entry_ids_to_remove
        st.rerun()


def sync_database_UI() -> None:
    if (
        len(st.session_state.pdf_paths_to_add) == 0
        and len(st.session_state.entry_ids_to_remove) == 0
        and st.session_state.sync_checked
    ):
        st.success("✅ Database and pdf folder are synced")

    else:
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
                            vector_store=database.init_and_get_vector_store(
                                params=st.session_state.params
                            ),
                            pdf_paths=st.session_state.pdf_paths_to_add,
                            params=st.session_state.params,
                        )
                    st.session_state.pdf_paths_to_add = []
                    st.rerun()

        with delete_col:
            if len(st.session_state.entry_ids_to_remove) > 0:
                if st.button("🗑️ Remove Entries"):
                    with st.spinner("Removing entries..."):
                        database.delete_entries_from_database(
                            vector_store=database.init_and_get_vector_store(
                                params=st.session_state.params
                            ),
                            ids=st.session_state.entry_ids_to_remove,
                        )
                    st.session_state.entry_ids_to_remove = []
                    st.rerun()


def chat_area():
    st.title("Chat without memory")
    st.info(
        "No memory is retained between succesive calls to the LLM. Each new question goes in without any previous context about the ongoing conversation.",
        icon="ℹ️",
    )

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(placeholder="your question about the pdfs")

    if question:
        with st.chat_message("human"):
            st.markdown(question)

        st.session_state.messages.append({"role": "human", "content": question})

        with st.spinner(
            f"generating response with model {st.session_state.params.ollama_llm_model}..."
        ):
            answer = llm.ask_question(question=question, params=st.session_state.params)

        with st.chat_message("ai"):
            st.markdown(answer)

        st.session_state.messages.append({"role": "ai", "content": answer})


def build_sidebar() -> None:
    with st.form("Sidebar configuration form"):
        with st.sidebar:
            llm_model = st.selectbox(
                label="Select LLM model",
                options=config.AVAILABLE_LLM_MODELS,
            )
            st.form_submit_button(
                "Set config", on_click=set_params(llm_model=llm_model)
            )

    return None


st.title("Talensinki GUI")

initialize_session_state()
build_sidebar()

tab_db_sync, tab_chat = st.tabs(["Database", "Chat"])
with tab_db_sync:
    database_sync_button()
    if st.session_state.sync_checked:
        sync_database_UI()

llm.check_ollama_connection()

with tab_chat:
    chat_area()
