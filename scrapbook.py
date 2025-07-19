# %% import

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from talensinki import config, checks, database, rich_display

# %% get vector store

vector_store = database.init_and_get_vector_store()
docs = vector_store.get()

texts = docs["documents"]

texts[7]

docs["metadatas"][6]


def retrieve(question: str):
    retrieved_docs = vector_store.similarity_search(query=question)
    return {"context": retrieved_docs}


question_prompt = PromptTemplate(
    input_variables=["question", "context_str"],
    template="""
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context_str} 
Answer:
""",
)

refine_prompt = PromptTemplate(
    input_variables=["question", "existing_answer", "context_str"],
    template="""
    You have been provided with an existing answer: {existing_answer}
    You have the opportunity to refine the existing answer with some more context below.
    
    Context: {context_str}
    
    Given the new context, refine the original answer to better address the question.
    If the context isn't useful, return the original answer.
    
    Question: {question}
    Refined Answer:""",
)

question = "How many million children partake in after school activities?"

llm = ChatOllama(
    model="llama3:latest",
    temperature=0.01,
    num_predict=256,
)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="refine",
    retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
    chain_type_kwargs={
        "question_prompt": question_prompt,
        "refine_prompt": refine_prompt,
    },
    return_source_documents=True,
)

result = qa_chain({"query": question})
