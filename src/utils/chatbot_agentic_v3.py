import os
import uuid
import json
from dotenv import load_dotenv
from openai import OpenAI
from traceback import format_exc
from utils.sql_manager import SQLManager
from utils.user_manager import UserManager
from utils.chat_history_manager import ChatHistoryManager
from utils.search_manager import SearchManager
from utils.prepare_system_prompt import prepare_system_prompt_for_agentic_chatbot_v2
from utils.utils import Utils
from utils.config import Config
from utils.vector_db_manager import VectorDBManager

load_dotenv()


class Chatbot:
    """
    Chatbot class that handles conversational flow, manages user data, and executes function calls using OpenAI's API.
    """

    def __init__(self):
        """
        Initializes the Chatbot instance.

        Sets up OpenAI client, configuration settings, session ID, and database managers.
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.cfg = Config()
        self.chat_model = self.cfg.chat_model
        self.summary_model = self.cfg.summary_model
        self.temperature = self.cfg.temperature
        self.max_history_pairs = self.cfg.max_history_pairs

        self.session_id = str(uuid.uuid4())
        self.utils = Utils()
        self.sql_manager = SQLManager(self.cfg.db_path)
        self.user_manager = UserManager(self.sql_manager)
        self.chat_history_manager = ChatHistoryManager(
            self.sql_manager, self.user_manager.user_id, self.session_id, self.client, self.summary_model, self.cfg.max_tokens)

        self.vector_db_manager = VectorDBManager(self.cfg)

        self.search_manager = SearchManager(
            self.sql_manager, self.utils, self.client, self.summary_model, self.cfg.max_characters)
        self.agent_functions = [self.utils.jsonschema(self.user_manager.add_user_info_to_database),
                                self.utils.jsonschema(self.vector_db_manager.search_vector_db)]

    def execute_function_call(self, function_name: str, function_args: dict) -> tuple[str, str]:
        """
        Executes the requested function based on the function name and arguments.

        Args:
            function_name (str): The name of the function to execute.
            function_args (dict): The arguments required for the function.

        Returns:
            tuple[str, str]: A tuple containing the function state and result.
        """
        if function_name == "search_vector_db":
            return self.vector_db_manager.search_vector_db(**function_args)
        elif function_name == "add_user_info_to_database":
            return self.user_manager.add_user_info_to_database(function_args)

    def chat(self, user_message: str) -> str:
        """
        Handles a conversation with the user, manages chat history, and executes function calls if needed.

        Args:
            user_message (str): The message from the user.

        Returns:
            str: The chatbot's response or an error message.
        """
        function_call_result_section = ""
        function_call_state = None
        chat_state = "thinking"
        function_call_count = 0
        self.chat_history = self.chat_history_manager.chat_history
        # function_call_prompt = f"""## Based on the last user's message you called the following functions:\n"""
        self.previous_summary = self.chat_history_manager.get_latest_summary()
        while chat_state != "finished":
            try:
                if function_call_state == "Function call successful.":
                    chat_state = "finished"
                    if function_name == "add_user_info_to_database":
                        self.user_manager.refresh_user_info()
                    function_call_result_section = (
                        f"## Function Call Executed\n\n"
                        f"- The assistant just called the function `{function_name}` in response to the user's most recent message.\n"
                        f"- Arguments provided:\n"
                        + "".join([f"  - {k}: {v}\n" for k,
                                   v in function_args.items()])
                        + f"- Outcome: ✅ {function_call_state}\n\n"
                        "Please proceed with the conversation using the new context.\n\n"
                        + f"{function_call_result}"
                    )
                    print("************************************")
                    print(function_call_result)
                    print("************************************")
                elif function_call_state == "Function call failed.":
                    function_call_result_section = (
                        f"## Function Call Attempted\n\n"
                        f"- The assistant attempted to call `{function_name}` with the following arguments:\n"
                        + "".join([f"  - {k}: {v}\n" for k,
                                   v in function_args.items()])
                        + f"- Outcome: ❌ {function_call_state} - {function_call_result}\n\n"
                        "Please assist the user based on this result."
                    )

                if function_call_count >= self.cfg.max_function_calls:
                    function_call_result_section = f"""  # Function Call Limit Reached.\n
                    Please conclude the conversation with the user based on the available information."""
                system_prompt = prepare_system_prompt_for_agentic_chatbot_v2(self.user_manager.user_info,
                                                                             self.previous_summary,
                                                                             self.chat_history,
                                                                             function_call_result_section)
                print("\n\n==========================================")
                print(f"System prompt: {system_prompt}")

                print("\n\nchat_State:", chat_state)
                response = self.client.chat.completions.create(
                    model=self.chat_model,
                    messages=[{"role": "system", "content": system_prompt},
                              {"role": "user", "content": user_message}],
                    functions=self.agent_functions,
                    function_call="auto",
                    temperature=self.cfg.temperature
                )

                if response.choices[0].message.content:
                    assistant_response = response.choices[0].message.content
                    self.chat_history_manager.add_to_history(
                        user_message, assistant_response, self.max_history_pairs
                    )
                    self.chat_history_manager.update_chat_summary(
                        self.max_history_pairs
                    )
                    chat_state = "finished"
                    msg_pair = f"user: {user_message}, assistant: {assistant_response}"
                    self.vector_db_manager.update_vector_db(
                        msg_pair)
                    function_call_state = None
                    self.vector_db_manager.refresh_vector_db_client()
                    return assistant_response

                elif response.choices[0].message.function_call:
                    if function_call_count >= self.cfg.max_function_calls or chat_state == "finished":
                        print("Trigerring the fallback model...")
                        fallback_response = self.client.chat.completions.create(
                            model=self.chat_model,
                            messages=[{"role": "system", "content": system_prompt},
                                      {"role": "user", "content": user_message}],
                            temperature=self.cfg.temperature
                        )
                        assistant_response = fallback_response.choices[0].message.content
                        self.chat_history_manager.add_to_history(
                            user_message, assistant_response, self.max_history_pairs
                        )
                        msg_pair = f"user: {user_message}, assistant: {assistant_response}"
                        self.vector_db_manager.update_vector_db(
                            msg_pair)
                        function_call_state = None
                        self.vector_db_manager.refresh_vector_db_client()
                        return assistant_response

                    function_call_count += 1
                    function_name = response.choices[0].message.function_call.name
                    function_args = json.loads(
                        response.choices[0].message.function_call.arguments)
                    print("Function name that was requested by the LLM:",
                          function_name)
                    print("Function arguments:", function_args)
                    function_call_state, function_call_result = self.execute_function_call(
                        function_name, function_args)
                # Neither function call nor message content (edge case)
                else:
                    return "Warning: No valid assistant response from the chatbot. Please try again."

            except Exception as e:
                return f"Error: {str(e)}\n{format_exc()}"
