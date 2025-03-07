import os
from dotenv import load_dotenv

# Get absolute path of the current directory (config/)
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(CONFIG_DIR, ".env")

# Load .env explicitly from config/
load_dotenv(dotenv_path=ENV_PATH)

class Config:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    # Debugging: Print values to confirm they are loaded
    print(f"🔹 DB_USER: {DB_USER}")
    print(f"🔹 DB_PASSWORD: {DB_PASSWORD}")
    print(f"🔹 SECRET_KEY: {SECRET_KEY}")

    # Construct DATABASE_URL dynamically
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
