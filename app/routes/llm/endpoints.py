from griptape.drivers import OpenAiChatPromptDriver, OpenAiEmbeddingDriver, PineconeVectorStoreDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import PromptResponseRagModule, VectorStoreRetrievalRagModule
from griptape.engines.rag.stages import RetrievalRagStage, ResponseRagStage
from griptape.rules import Ruleset, Rule
from griptape.structures import Agent
from griptape.tools import RagClient


from app.config import settings
from . import llm_router
from .schemas import QueryPineconeIndexBody


@llm_router.post("/query-pinecone-index")
def query_pinecone_index(reqest_body: QueryPineconeIndexBody):
    print(f"Question for Index + OpenAI: {reqest_body.question}")
    print(f"Pinecone Index Name: {settings.PINECONE_INDEX_NAME}")

    question = reqest_body.question

    namespace = "web-content"

    vector_store_driver = PineconeVectorStoreDriver(
        api_key=settings.PINECONE_API_KEY,
        environment="",
        index_name=settings.PINECONE_INDEX_NAME,
        embedding_driver=OpenAiEmbeddingDriver(),
    )    

    engine = RagEngine(
        retrieval_stage=RetrievalRagStage(
            retrieval_modules=[
                VectorStoreRetrievalRagModule(
                    vector_store_driver=vector_store_driver,
                    query_params= {
                        "namespace": namespace,
                        "top_n": 20,
                    }
                )
            ]
        ),
        response_stage=ResponseRagStage(
            response_module=PromptResponseRagModule(
                prompt_driver=OpenAiChatPromptDriver(model="gpt-4o-2024-08-06")
            )
        )
    )
    
    vector_store_tool = RagClient(
        description="Contains contextual information pertaining to the user's questions. "
                    "Use it to answer any questions from the user if possible. ",
        rag_engine=engine
    )
    
    agent = Agent(
        rulesets=[
            Ruleset(
                name="Assistant",
                rules=[
                    Rule(
                        "Always introduce yourself as a question-answering chatbot."
                    ),
                    Rule(
                        "Be truthful. Only discuss information related to the user's questions."
                    ),
                    Rule(
                        "Use at most three sentences and keep the answer as concise as possible."
                    ),
                ]
            )
        ],
        tools=[vector_store_tool]
    )

    agent.run(question)

    return {"answer": agent.output.value}
