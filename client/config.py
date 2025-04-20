"""
This configuration file is responsible for managing server-related settings and secrets.
It uses environment variables to load sensitive data and provides utility functions to
update and retrieve the server's address. It defines default values for the 
secret key and algorithm used in authentication processes.
"""

import os

from dotenv import load_dotenv
from zookeeper import get_server

load_dotenv()

SERVER_IP_PORT = None
SERVER_ZOO = None

def update_server_zoo(ip_port: str | None):
    global SERVER_IP_PORT, SERVER_ZOO
    SERVER_IP_PORT = ip_port
    SERVER_ZOO = f"http://{SERVER_IP_PORT}"


def get_server_zoo():
    return SERVER_ZOO

SECRET_KEY = os.getenv("SECRET_KEY", "a_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
