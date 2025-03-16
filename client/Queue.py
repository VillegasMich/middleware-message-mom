import requests
from boostrap import SERVER_URL
from rich.prompt import Prompt
from Util import Util


class Queue:
    @staticmethod
    def create():
        """Creates a new queue"""
        name = Prompt.ask("[cyan]Enter queue name[/]")

        response = requests.post(
            f"{SERVER_URL}/queues/", json={"name": name}, headers=Util.get_headers()
        )

        if response.status_code == 200:
            print(f"[green]Queue '{name}' created successfully![/]")
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")

    @staticmethod
    def send_message():
        """Sends a message to a queue"""
        queue_name = Prompt.ask("[cyan]Enter queue name[/]")
        message = Prompt.ask("[cyan]Enter message[/]")

        response = requests.post(
            f"{SERVER_URL}/queues/{queue_name}/send/",
            json={"message": message},
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print("[green]Message sent successfully![/]")
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")

    @staticmethod
    def receive_message():
        """Receives a message from a queue"""
        queue_name = Prompt.ask("[cyan]Enter queue name[/]")

        response = requests.get(
            f"{SERVER_URL}/queues/{queue_name}/receive/", headers=Util.get_headers()
        )

        if response.status_code == 200:
            print(f"[yellow]Message received:[/] {response.json()['message']}")
        else:
            print(
                f"[red]Error:[/] {
                    response.json().get('detail', 'No messages available')
                }"
            )
