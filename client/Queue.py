import requests
from boostrap import SERVER_URL
from rich import print
from rich.prompt import Prompt
from rich.tree import Tree
from Util import Util


class Queue:
    @staticmethod
    def get_all():
        """
        Lists all the queues
        Response:
        {
            "message": "message_output"
            "queues": "[
                {
                    "name": queue_name
                    "id": queue_id
                },
                ...
            ]"
        }
        """
        response = requests.get(f"{SERVER_URL}/queues/")

        if response.status_code == 200:
            tree_root = Tree("\n[bold yellow]Queues:[/]")
            for queue in response.json()["queues"]:
                tree_root.add(
                    "[bold]#"
                    + str(queue["id"])
                    + "[/]"
                    + " - "
                    + "'"
                    + queue["name"]
                    + "'"
                )
            print(tree_root)
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")

    @staticmethod
    def create():
        """
        Creates a new queue
        Request body:
        {
            "name": "queue_name"
        }
        Response:
        {
            "message": "Queue created successfully",
            "id": "queue_id"
        }
        """
        name = Prompt.ask("[cyan]Enter queue name[/]")

        response = requests.post(
            # f"{SERVER_URL}/queues/", json={"name": name}, headers=Util.get_headers()
            f"{SERVER_URL}/queues/",
            json={"name": name},
        )

        if response.status_code == 200:
            print(f"[green]Queue '{name}' created successfully![/]")
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")

    @staticmethod
    def delete():
        """Deletes a queue"""
        queue_id = Prompt.ask("[cyan]Enter queue id to [bold red]delete[/]")

        response = requests.delete(
            # f"{SERVER_URL}/queues/{queue_id}", headers=Util.get_headers()
            f"{SERVER_URL}/queues/{queue_id}",
        )

        if response.status_code == 200:
            print("[green]Queue deleted successfully![/]")
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

    # TODO:
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
