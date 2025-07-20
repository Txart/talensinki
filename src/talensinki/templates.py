from langchain.prompts import PromptTemplate

SYSTEM_PROMPT = PromptTemplate(
    input_variables=["question", "context"],
    template="""
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
""",
)


REFINE_PROMPT = PromptTemplate(
    input_variables=["question", "existing_answer", "context"],
    template="""
    You have been provided with an existing answer: {existing_answer}
    You have the opportunity to refine the existing answer with some more context below.
    
    Context: {context}
    
    Given the new context, refine the original answer to better address the question.
    If the context isn't useful, return the original answer.
    
    Question: {question}
    Refined Answer:""",
)
