import streamlit as st
import pandas as pd

from talensinki import database, config, llm, checks
from talensinki.checks import HealthCheckResult


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


def set_params(llm_model: str, embedding_model: str) -> None:
    params = config.Params(
        ollama_llm_model=llm_model,
        ollama_embedding_model=embedding_model,
    )
    st.session_state.params = params

    return None


def display_health_checks_gui(check_results: list[HealthCheckResult]) -> None:
    """
    Display health check results in Streamlit GUI format.
    """

    # Count passed/failed checks
    passed_count = sum(1 for result in check_results if result.passed)
    total_count = len(check_results)
    failed_count = total_count - passed_count

    # Display summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Total Checks", value=total_count, delta=None)

    with col2:
        st.metric(
            label="Passed",
            value=passed_count,
        )

    with col3:
        st.metric(
            label="Failed",
            value=failed_count,
        )

    # Overall status
    all_passed = passed_count == total_count

    if all_passed:
        st.success("🎉 All health checks passed!")
    else:
        st.error(
            f"⚠️ {failed_count} health check{'s' if failed_count != 1 else ''} failed!"
        )

    # Detailed results table
    st.subheader("📋 Detailed Results")

    # Prepare data for the table
    table_data = []
    for result in check_results:
        status_icon = "✅" if result.passed else "❌"
        status_text = "PASS" if result.passed else "FAIL"
        details = (
            result.details if result.details else ("OK" if result.passed else "Failed")
        )

        table_data.append(
            {
                "Status": f"{status_icon} {status_text}",
                "Check Name": result.name,
                "Details": details,
            }
        )

    # Create DataFrame and display as table
    df = pd.DataFrame(table_data)

    # Style the table
    def style_status(val):
        if "✅" in val:
            return "background-color: #d4edda; color: #155724; font-weight: bold;"
        elif "❌" in val:
            return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
        return ""

    def style_details(val):
        if val == "OK":
            return "color: #6c757d; font-style: italic;"
        return ""

    styled_df = df.style.map(style_status, subset=["Status"]).map(
        style_details, subset=["Details"]
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn(
                "Status",
                width="small",
            ),
            "Check Name": st.column_config.TextColumn(
                "Check Name",
                width="medium",
            ),
            "Details": st.column_config.TextColumn(
                "Details",
                width="large",
            ),
        },
    )

    # Refresh button
    st.markdown("---")
    if st.button("🔄 Run Health Checks Again", type="primary"):
        st.rerun()


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
    with st.sidebar:
        llm_model = st.selectbox(
            label="LLM model",
            options=config.AVAILABLE_LLM_MODELS,
        )

        embedding_model = st.selectbox(
            label="Embedding model",
            options=config.AVAILABLE_EMBEDDING_MODELS,
        )
    set_params(llm_model=llm_model, embedding_model=embedding_model)

    return None


st.title("Talensinki GUI")

initialize_session_state()
build_sidebar()

tab_checks, tab_db, tab_chat = st.tabs(["Checks", "Database", "Chat"])
with tab_checks:
    display_health_checks_gui(check_results=checks.run_health_checks())

with tab_db:
    database_sync_button()
    if st.session_state.sync_checked:
        sync_database_UI()

with tab_chat:
    chat_area()
