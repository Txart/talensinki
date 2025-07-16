# %%
from os import system
from langchain import hub
from pathlib import Path
from typing_extensions import TypedDict

from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph


# %% Read pdf
def main():
    print("business!")


pdf_path = Path("./pdfs/bg-20-2099-2023.pdf")


def load_pdf_pages(pdf_path: Path):
    loader = PyPDFLoader(str(pdf_path))
    pages = []
    for page in loader.lazy_load():
        pages.append(page)

    return pages


pages = load_pdf_pages(pdf_path=pdf_path)

print(f"{pages[0].metadata}\n")
print(pages[0].page_content)

# %% embeddings
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434",  # Default Ollama URL
)

vector_store = InMemoryVectorStore.from_documents(pages, embedding=embeddings)
# use chroma

# %% check similarity to query


# Define state for application
class State(TypedDict):
    question: str
    context: list[Document]
    answer: str


def retrieve(question: str):
    retrieved_docs = vector_store.similarity_search(query=question)
    return {"context": retrieved_docs}


# %% chat model
template_string = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""

prompt_template = ChatPromptTemplate.from_template(template_string)

question = "What is the effect of canal blocks on water table depth?"

retrieved_docs = retrieve(question)
single_doc = retrieved_docs["context"][1]

query = prompt_template.format_messages(question=question, context=single_doc)

llm = ChatOllama(
    model="llama3",
    temperature=0.8,
    num_predict=256,
)

response = llm.invoke(query)

# %%
doc = retrieved_docs["context"][1]
doc.page_content
