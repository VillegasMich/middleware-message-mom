import requests
from config import get_server_zoo
from rich import print
from rich.prompt import Prompt
from Util import Util


class User:
    """
    This class provides static methods for user-related operations such as registration,
    login, and retrieving the user's subscribed queues. It acts as a client-side interface
    for managing user authentication and associated data.
    """
    
    @staticmethod
    def register():
        #Registers a new user
        
        SERVER_ZOO = get_server_zoo()

        username = Prompt.ask("[cyan]Enter username[/]")
        password = Prompt.ask("[cyan]Enter password[/]", password=True)

        response = requests.post(
            f"{SERVER_ZOO}/register/", json={"username": username, "password": password}
        )

        if response.status_code == 200:
            print("[green]User registered successfully![/]")
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")


    @staticmethod
    def login():
        #Logs in and obtains a token for the user
        
        SERVER_ZOO = get_server_zoo()
        username = Prompt.ask("[cyan]Enter username[/]")
        password = Prompt.ask("[cyan]Enter password[/]", password=True)

        response = requests.post(
            f"{SERVER_ZOO}/login/", json={"username": username, "password": password}
        )

        if response.status_code == 200:
            token = response.json()["access_token"]
            Util.set_token(token)
            print("[green]Login successful![/]")
            return token
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")
            return None


    @staticmethod
    def get_user_queues():
        #Retrieves the private queues of the topics that the user is subscribed to
        
        SERVER_ZOO = get_server_zoo()
        response = requests.get(
            f"{SERVER_ZOO}/user/queues-topics", headers=Util.get_headers()
        )

        if response.status_code == 200:
            return response.json()["queues"]
        else:
            return None
