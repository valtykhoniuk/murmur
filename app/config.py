import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
ALGORITHM = "HS256"

OWNER_EMAIL = os.getenv("OWNER_EMAIL")
OWNER_PASSWORD = os.getenv("OWNER_PASSWORD")
FRIEND_EMAIL = os.getenv("FRIEND_EMAIL")
FRIEND_PASSWORD = os.getenv("FRIEND_PASSWORD")
DEMO_EMAIL = os.getenv("DEMO_EMAIL", "demo@murmur.dev")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD")
