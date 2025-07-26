import logging
import operator
import os
from typing import TypedDict, List, Annotated, Dict, Any

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.exceptions import LangChainException

from app.config import settings
from app.prompts.query_enrichment_prompt import query_prompt
from app.prompts.response_prompt import resp_prompt
from app.qdrant.vector_search import search_documents
from app.utils.response_perser import parse_ai_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

THREAD_ID = "student-thread-1"
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
llm = ChatOpenAI(model_name=settings.MODEL_ID, temperature=0.3)


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


query_enrichment_chain = query_prompt | llm
response_chain = resp_prompt | llm


def vector_search_qdrant(query):
    return search_documents(query)


def enrich_and_search(state: AgentState) -> AgentState:
    user_msg = state["messages"][-1]
    chat_history = "\n".join([msg.content for msg in state["messages"][:-1]])

    try:
        enriched = query_enrichment_chain.invoke({
            "question": user_msg.content,
            "chat_history": chat_history
        })
        enriched_query = enriched.content
    except (LangChainException, Exception) as e:
        error_message = f"[Error in enrichment step] {str(e)}"
        logger.exception(error_message)
        return {
            "messages": state["messages"] + [AIMessage(content=error_message)]
        }

    try:
        vector_result = vector_search_qdrant(enriched_query)
    except Exception as e:
        error_message = f"[Error in vector search] {str(e)}"
        logger.exception(error_message)
        return {
            "messages": state["messages"] + [AIMessage(content=error_message)]
        }

    try:
        response = response_chain.invoke({
            "question": user_msg.content,
            "chat_history": chat_history,
            "vector_result": vector_result
        })
        return {
            "messages": state["messages"] + [AIMessage(content=response.content)]
        }
    except (LangChainException, Exception) as e:
        error_message = f"[Error in response generation] {str(e)}"
        logger.exception(error_message)
        return {
            "messages": state["messages"] + [AIMessage(content=error_message)]
        }


workflow = StateGraph(AgentState)
workflow.add_node("qa_step", enrich_and_search)
workflow.set_entry_point("qa_step")
workflow.add_edge("qa_step", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


def process_query(user_query: str, thread_id: str) -> Dict[str, Any]:
    try:
        result = app.invoke(
            {"messages": [HumanMessage(content=user_query)]},
            config={"configurable": {"thread_id": thread_id}}
        )
        raw_response = result["messages"][-1]
        parsed = parse_ai_message(raw_response)
        return parsed
    except Exception as e:
        logger.exception(f"Error during query processing: {str(e)}")
        return {"error": f"Failed to process query: {str(e)}"}


def reset_conversation_memory(thread_id: str) -> Dict[str, str]:
    try:
        if hasattr(memory, 'storage'):
            storage = memory.storage
            keys_to_remove = [key for key in list(storage.keys()) if thread_id in str(key)]
            for key in keys_to_remove:
                storage.pop(key, None)
            logger.info(f"Memory reset successfully for thread: {thread_id} - Removed {len(keys_to_remove)} entries")

        elif hasattr(memory, 'store'):
            store = memory.store
            keys_to_remove = [key for key in list(store.keys()) if thread_id in str(key)]
            for key in keys_to_remove:
                store.pop(key, None)
            logger.info(f"Memory reset successfully for thread: {thread_id} - Removed {len(keys_to_remove)} entries")

        else:
            logger.warning(f"No recognizable memory store found for thread: {thread_id}")
        
        return {"message": f"Memory reset for thread: {thread_id}"}
    except Exception as e:
        logger.error(f"Error resetting memory for thread {thread_id}: {str(e)}")
        return {"error": f"Failed to reset memory: {str(e)}"}
