from openai import OpenAI
from utils.utils import Utils
from utils.sql_manager import SQLManager


class SearchManager:
    def __init__(self, sql_manager: SQLManager, utils: Utils, client: OpenAI, summary_model: str, max_characters: int = 1000):
        """
        Initializes the SearchManager instance.

        Args:
            sql_manager (SQLManager): The database manager instance.
            utils (Utils): The utility class instance.
            client (OpenAI): The OpenAI client instance.
            summary_model (str): The summary model to use.
            max_characters (int): The maximum number of characters to summarize.
        """
        self.sql_manager = sql_manager
        self.utils = utils
        self.client = client
        self.summary_model = summary_model
        self.max_characters = max_characters

    def search_chat_history(self, search_term: str) -> list:
        """
        Searches chat history for a term, performing a case-insensitive lookup.

        Args:
            search_term(str): The keyword to search in the chat history.

        Returns:
            list: List of tuples containing matching question, answer, and timestamp.
        """
        try:
            search_term = search_term.lower()
            query = """
            SELECT question, answer, timestamp FROM chat_history
            WHERE LOWER(question) LIKE ? OR LOWER(answer) LIKE ?
            ORDER BY timestamp ASC
            LIMIT 3;
            """

            results = self.sql_manager.execute_query(
                query, (f"%{search_term}%", f"%{search_term}%"), fetch_all=True)
            # Ensure the results maintain the order of question, then answer
            formatted_results = [(q, a, t) for q, a, t in results]
            if formatted_results == []:
                return "Function call failed.", "No results found. Please try again with a different word."

            num_characters = self.utils.count_number_of_characters(
                str(results))
            print(f"Number of characters in search results: {num_characters}")
            if num_characters > self.max_characters:
                results_summary = self.summarize_search_result(
                    str(formatted_results))
                return "Function call successful.", results_summary
            return "Function call successful.", formatted_results
        except Exception as e:
            return "Function call failed.", f"Error: {e}"

    def summarize_search_result(self, search_result: str) -> str:
        """
        Summarizes a search result if it exceeds the character limit.

        Args:
            search_result (str): The search result to summarize.

        Returns:
            str: A summarized version of the search result.
        """
        response = self.client.chat.completions.create(
            model=self.summary_model,
            messages=[{"role": "system", "content": f"Summarize the following conversation within {self.max_characters} characters"},
                      {"role": "user", "content": search_result}]
        )
        response = response.choices[0].message.content
        return response
