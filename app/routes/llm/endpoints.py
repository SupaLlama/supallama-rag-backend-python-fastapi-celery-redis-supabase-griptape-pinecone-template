from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from app.config import settings
from . import llm_router
from .schemas import QueryPineconeIndexBody


@llm_router.post("/query-pinecone-index")
def query_pinecone_index(reqest_body: QueryPineconeIndexBody):
    print(f"Question for Index + OpenAI: {reqest_body.question}")
    print(f"Pinecone Index Name: {settings.PINECONE_INDEX_NAME}")

    question = reqest_body.question

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    embeddings = OpenAIEmbeddings()

    pinecone_index_name = settings.PINECONE_INDEX_NAME

    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=pinecone_index_name, embedding=embeddings
    )

    retriever = vectorstore.as_retriever()

    template = """You are an assistant for question-answering tasks. 
        Use the following pieces of retrieved context to answer the question. 
        If you don't know the answer, just say that you don't know. 
        Use three sentences maximum and keep the answer concise.
    Question: {question}
    Context: {context}
    Answer:
    """
    prompt = ChatPromptTemplate.from_template(template)
    print(f"The prompt template is:\n{prompt}")

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    answer = rag_chain.invoke(question)

    return {"answer": answer}