import chromadb
import os
import pandas as pd
from IPython.display import display
from utils.config import Config
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from pyprojroot import here

load_dotenv(here("../.env"))

CFG = Config()
openai_embedding_function = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name=CFG.embedding_model
)

db_client = chromadb.PersistentClient(path=str(CFG.vectordb_dir))
db_collection = db_client.get_or_create_collection(
    name=CFG.collection_name,
    embedding_function=openai_embedding_function,
    metadata={"hnsw:space": "cosine"}
)
print("DB collection created:", db_collection)
print("DB collection count:", db_collection.count())

results = db_collection.get()
# Create a DataFrame from the retrieved data
df = pd.DataFrame({
    'id': results['ids'],
    'document': results['documents'],
})

# Display the dataframe
display(df)
