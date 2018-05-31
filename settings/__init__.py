import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DB_USER = os.environ.get("DB_USER")
DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")
TEST_DATA_PATH = os.environ.get("TEST_DATA_PATH")
