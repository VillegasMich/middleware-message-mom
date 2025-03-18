import requests
from boostrap import SERVER_URL
from rich.prompt import Prompt
from rich import print
from Util import Util

class User:
    @staticmethod
    def register():
        """Registers a new user"""
        username = Prompt.ask("[cyan]Enter username[/]")
        password = Prompt.ask("[cyan]Enter password[/]", password=True)

        response = requests.post(
            f"{SERVER_URL}/register/", json={"username": username, "password": password}
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
            f"{SERVER_URL}/login/", json={"username": username, "password": password}
        )

        if response.status_code == 200:
            token = response.json()["access_token"]
            Util.set_token(token)
            print("[green]Login successful![/]")
            return token
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")
            return None
        
    def get_user_topics():
        response = requests.get( f"{SERVER_URL}/users/topics", headers=Util.get_headers())
        
        if response.status_code == 200:
            return response.json()['topics']
        else:
            return None