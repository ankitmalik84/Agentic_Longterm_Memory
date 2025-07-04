import os
import uuid
from dotenv import load_dotenv
from openai import OpenAI
from utils.sql_manager import SQLManager
from utils.user_manager import UserManager
from utils.chat_history_manager import ChatHistoryManager
from utils.prepare_system_prompt import prepare_system_prompt
from utils.config import Config

load_dotenv()


class Chatbot:
    """
    Chatbot class that handles conversational flow.
    """

    def __init__(self):
        """
        Initializes the Chatbot instance.

        Sets up OpenAI client, configuration settings, session ID, and database managers.
        """
        self.cfg = Config()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.chat_model = self.cfg.chat_model
        self.summary_model = self.cfg.summary_model
        self.max_history_pairs = self.cfg.max_history_pairs

        self.sql_manager = SQLManager(self.cfg.db_path)
        self.user_manager = UserManager(self.sql_manager)
        self.session_id = str(uuid.uuid4())

        self.chat_history_manager = ChatHistoryManager(
            self.sql_manager, self.user_manager.user_id, self.session_id, self.client, self.summary_model, self.cfg.max_tokens)

    def chat(self, user_message: str) -> str:
        """
        Handles a conversation with the user and manages chat history.

        Args:
            user_message (str): The message from the user.

        Returns:
            str: The chatbot's response or an error message.
        """
        self.previous_summary = self.chat_history_manager.get_latest_summary()
        system_prompt = prepare_system_prompt(self.user_manager.user_info,
                                              self.previous_summary,
                                              self.chat_history_manager.chat_history)
        print("System prompt:", system_prompt)
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_message}]
            )
            assistant_response = response.choices[0].message.content
            self.chat_history_manager.add_to_history(
                user_message, assistant_response, self.max_history_pairs)
            self.chat_history_manager.update_chat_summary(
                self.max_history_pairs)
            return assistant_response
        except Exception as e:
            return f"Error: {str(e)}"
