import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://usuario:contraseña@localhost:3306/mi_db")
SECRET_KEY = os.getenv("SECRET_KEY", "a_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")