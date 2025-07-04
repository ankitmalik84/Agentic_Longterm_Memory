import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from pyprojroot import here
from utils.config import Config

load_dotenv()


def prepare_vector_db():
    """
    Prepares a vector database using ChromaDB and OpenAI embeddings.

    This function sets up a vector database by:
    - Loading configuration from the `Config` class.
    - Creating an OpenAI embedding function using the provided API key and model.
    - Creating the vector database directory if it doesn't exist.
    - Initializing a persistent ChromaDB client at the specified directory.
    - Creating or retrieving a collection in the vector database with cosine similarity.

    Steps:
        1. Load OpenAI API key and model name from environment and configuration.
        2. Create vector database directory if it doesn't already exist.
        3. Initialize a ChromaDB client with a persistent storage path.
        4. Create or get an existing collection with specified name and embedding function.
        5. Log the creation and the number of items in the collection.
    """
    CFG = Config()
    openai_embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=CFG.embedding_model
    )
    if not os.path.exists(here(CFG.vectordb_dir)):
        # If it doesn't exist, create the directory and create the embeddings
        os.makedirs(here(CFG.vectordb_dir))
        print(f"Directory '{CFG.vectordb_dir}' was created.")
    db_client = chromadb.PersistentClient(path=str(CFG.vectordb_dir))
    db_collection = db_client.get_or_create_collection(
        name=CFG.collection_name,
        embedding_function=openai_embedding_function,
        metadata={"hnsw:space": "cosine"}
    )
    print("DB collection created:", db_collection)
    print("DB collection count:", db_collection.count())


if __name__ == "__main__":
    prepare_vector_db()
