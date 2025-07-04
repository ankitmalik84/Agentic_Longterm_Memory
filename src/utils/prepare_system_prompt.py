

def prepare_system_prompt(user_info: str, chat_summary: str, chat_history: str) -> str:
    prompt = """You are a professional assistant of the following user.

    {user_info}

    Here is a summary of the previous conversation history:

    {chat_summary}

    Here is the previous conversation between you and the user:

    {chat_history}
    """

    return prompt.format(
        user_info=user_info,
        chat_summary=chat_summary,
        chat_history=chat_history,
    )


def prepare_system_prompt_for_agentic_chatbot_v2(user_info: str, chat_summary: str, chat_history: str, function_call_result_section: str) -> str:

    prompt = """## You are a professional assistant of the following user.

    {user_info}

    ## Here is a summary of the previous conversation history:

    {chat_summary}

    ## Here is the previous conversation between you and the user:

    {chat_history}

    ## You have access to two functions: search_chat_history and add_user_info_to_database.

    - If you need more information about the user or details from previous conversations to answer the user's question, use the search_chat_history function.
    - Monitor the conversation, and if the user provides any of the following details that differ from the initial information, call this function to update 
    the user's database record. Do not call the function unless you have enough information or the full context.

    ### Keys for Updating the User's Information:

    - name: str
    - last_name: str
    - age: int
    - gender: str
    - location: str
    - occupation: str
    - interests: list[str]

    ## IMPORTANT: You are the only agent talking to the user, so you are responsible for both the conversation and function calling.
    - If you call a function, the result will appear below.
    - If the result confirms that the function was successful, or the maximum limit of function calls is reached, don't call it again.
    - You can also check the chat history to see if you already called the function.
    
    {function_call_result_section}
    """

    return prompt.format(
        user_info=user_info,
        chat_summary=chat_summary,
        chat_history=chat_history,
        function_call_result_section=function_call_result_section
    )


def prepare_system_prompt_for_agentic_chatbot_v3(user_info: str, chat_summary: str, chat_history: str, function_call_result_section: str) -> str:

    prompt = """## You are a professional assistant of the following user.

    {user_info}

    ## You have access to two functions: search_vector_db and add_user_info_to_database.

    - If you need more information about the user or details from previous conversations to answer the user's question, use the search_vector_db function.
    This function performs a vector search on the chat history of the user and the chatbot. The best way to do this is to search with a very clear query.
    - Monitor the conversation, and if the user provides any of the following details that differ from the initial information, call this function to update 
    the user's database record.

    ### Keys for Updating the User's Information:

    - name: str
    - last_name: str
    - age: int
    - gender: str
    - location: str
    - occupation: str
    - interests: list[str]

    ## IMPORTANT: You are the only agent talking to the user, so you are responsible for both the conversation and function calling.
    - If you call a function, the result will appear below.
    - If the result confirms that the function was successful, or the maximum limit of function calls is reached, don't call it again.
    - You can also check the chat history to see if you already called the function.
    
    {function_call_result_section}

    ## Here is a summary of the previous conversation history:

    {chat_summary}

    ## Here is the previous conversation between you and the user:

    {chat_history}

    ## Here is the user's new question
    """

    return prompt.format(
        user_info=user_info,
        chat_summary=chat_summary,
        chat_history=chat_history,
        function_call_result_section=function_call_result_section
    )


def prepare_system_prompt_for_rag_chatbot() -> str:
    prompt = """You will receive a user query and the search results retrieved from a chat history vector database. The search results will include the most likely relevant responses to the query.

    Your task is to summarize the key information from both the query and the search results in a clear and concise manner.

    Remember keep it concise and focus on the most relevant information."""

    return prompt
