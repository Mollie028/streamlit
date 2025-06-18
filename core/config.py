from dotenv import load_dotenv
load_dotenv()
import os

DB_URL = os.getenv("DATABASE_URL") 
