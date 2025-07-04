from pyprojroot import here
from yaml import load, Loader


class Config:
    def __init__(self):
        with open(here("config/config.yml"), "r") as f:
            config = load(f, Loader=Loader)
        # directories
        self.db_path = here(config["directories"]["db_path"])
        self.vectordb_dir = here(config["directories"]["vectordb_dir"])
        # llm_config
        self.chat_model = config["llm_config"]["chat_model"]
        self.summary_model = config["llm_config"]["summary_model"]
        self.rag_model = config["llm_config"]["rag_model"]
        self.temperature = config["llm_config"]["temperature"]
        # chat_history_config
        self.max_history_pairs = config["chat_history_config"]["max_history_pairs"]
        self.max_characters = config["chat_history_config"]["max_characters"]
        self.max_tokens = config["chat_history_config"]["max_tokens"]
        # search_config
        # self.num_retrieved_content = config["search_config"]["num_retrieved_content"]
        # agent_config
        self.max_function_calls = config["agent_config"]["max_function_calls"]
        # vectordb_config
        self.collection_name = config["vectordb_config"]["collection_name"]
        self.embedding_model = config["vectordb_config"]["embedding_model"]
        self.k = config["vectordb_config"]["k"]
