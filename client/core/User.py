import requests
from config import SERVER_ZOO
from rich import print
from rich.prompt import Prompt
from Util import Util


class User:
    @staticmethod
    def register():
        """Registers a new user"""
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
        """Logs in and obtains a token"""
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
        response = requests.get(
            f"{SERVER_ZOO}/user/queues-topics", headers=Util.get_headers()
        )

        if response.status_code == 200:
            return response.json()["queues"]
        else:
            return None
