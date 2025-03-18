import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "a_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")