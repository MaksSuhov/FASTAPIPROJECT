from pathlib import Path
from dotenv import load_dotenv
import os

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BACKEND_DIR/'.env')

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() in {"1", "true", "yes", "on"}


