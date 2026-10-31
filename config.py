from dotenv import load_dotenv
import os

load_dotenv()

FRONT_END_URL = os.getenv("FRONT_END_URL", "localhost:3000")
BACK_END_URL  = os.getenv("BACK_END_URL", "localhost:8000")
SECRET_KEY    = os.getenv("SECRET_KEY")
ALGO          = os.getenv("ALGO")
DATABASE_URL = os.getenv("DATABASE_URL")
