import sqlite3
import pandas as pd
from pyprojroot import here
from IPython.display import display

# Database file
DB_PATH = here("data/chatbot.db")


def get_table_names():
    """Retrieve all table names from the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql_query(query, conn)['name'].tolist()
    conn.close()
    return tables


def fetch_table_data(table_name):
    """Fetch and return data from a specified table in the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
    conn.close()
    return df


def load_database():
    """Load all tables, their shapes, and store their data in a dictionary of DataFrames."""
    table_names = get_table_names()
    table_data = {}

    for table in table_names:
        df = fetch_table_data(table)
        # Show table name and shape
        print(f"📌 Table: {table} | Shape: {df.shape}")
        table_data[table] = df  # Store DataFrame in a dictionary

    return table_data


tables_dict = load_database()

display(tables_dict["user_info"])

display(tables_dict["chat_history"])

display(tables_dict["summary"])
