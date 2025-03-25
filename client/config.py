import os

from dotenv import load_dotenv
from zookeeper import get_server

load_dotenv()

SERVER_IP_PORT = get_server()
SERVER_ZOO = f"http://{SERVER_IP_PORT}"


SECRET_KEY = os.getenv("SECRET_KEY", "a_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
