from pathlib import Path
from dotenv import load_dotenv
import os

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BACKEND_DIR/'.env')

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() in {"1", "true", "yes", "on"}
ROUTERAI_API_KEY=os.getenv('ROUTERAI_API_KEY')
ROUTERAI_BASE_URL=os.getenv("ROUTERAI_BASE_URL")
DEFAULT_MODEL=os.getenv('DEFAULT_MODEL', "qwen/qwen3.7-flash")
