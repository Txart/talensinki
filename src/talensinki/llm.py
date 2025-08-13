from pathlib import Path
from typing import TypedDict

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from langgraph.graph import START, StateGraph

from talensinki import templates, config, database


class State(TypedDict):
    question: str
    context: list[Document]
    answer: str


def create_chat_object(params: config.Params) -> ChatOllama:
    return ChatOllama(
        model=params.ollama_llm_model,
        temperature=0.01,
        num_predict=256,
        base_url="http://localhost:11434",
    )


def retrieve(state: State, params: config.Params) -> dict[str, list[Document]]:
    vector_store = database.init_and_get_vector_store(params=params)

    retrieved_docs = retrieve_docs_by_similarity_search(
        state, vector_store, number_of_docs_to_retrieve=5
    )

    return {"context": retrieved_docs}


def retrieve_docs_by_similarity_search(
    state: State,
    vector_store: Chroma,
    number_of_docs_to_retrieve: int,
) -> list[Document]:
    return vector_store.similarity_search(
        query=state["question"], k=number_of_docs_to_retrieve
    )


def combine_document_contents(state: State) -> str:
    return "\n\n".join(doc.page_content for doc in state["context"])


def generate(state: State, params: config.Params):
    docs_content = combine_document_contents(state)
    llm = create_chat_object(params=params)
    messages = templates.SYSTEM_PROMPT.invoke(
        {"question": state["question"], "context": docs_content}
    )
    response = llm.invoke(messages)
    return {"answer": response.content}


def build_graph(params: config.Params):
    graph_builder = StateGraph(State).add_sequence(
        [
            ("retrieve", lambda state: retrieve(state, params=params)),
            ("generate", lambda state: generate(state, params=params)),
        ]
    )
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()
    return graph


def save_graph_image(graph, filepath=Path("output/graph.png")) -> None:
    with open(filepath, "wb") as f:
        png_data = graph.get_graph().draw_mermaid_png()
        f.write(png_data)


def ask_question(question: str, params: config.Params) -> str:
    state = State(question=question, context=[], answer="")
    graph = build_graph(params=params)
    result = graph.invoke(state)

    return result["answer"]
