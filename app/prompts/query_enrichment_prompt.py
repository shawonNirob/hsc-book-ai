from langchain.prompts import PromptTemplate

query_prompt = PromptTemplate( input_variable=["question", "chat_history"], template="""
    You are an intelligent system who Can enrich the user query for efficient vector search in vector database. 

    User Query:
    "{question}"
                             
    Conversation History:
    "{chat_history}"

    Analyze the user question and chat_history properly.

    Respond ONLY in this JSON format:

    - provide a clear query based on the user query and chat history for anaphora resolution, like this: return as it is if chat history is blank,
    {{
        "action": "response",
        "content": "a clear query solving anaphora resolution"
    }}

    """
)