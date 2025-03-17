import requests
from boostrap import SERVER_URL
from rich.prompt import Prompt
from rich.tree import Tree
from Util import Util


class Topic:
    @staticmethod
    def get_all():
        """
        Lists all the topics
        Response:
        {
            "message": "message_output"
            "topics": "[
                {
                    "name": queue_name
                    "id": queue_id
                },
                ...
            ]"
        }
        """
        response = requests.get(f"{SERVER_URL}/topics/")

        if response.status_code == 200:
            tree_root = Tree("\n[bold yellow]Topics:[/]")
            for topic in response.json()["topics"]:
                tree_root.add(
                    "[bold]#"
                    + str(topic["id"])
                    + "[/]"
                    + " - "
                    + "'"
                    + topic["name"]
                    + "'"
                )
            print(tree_root)
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")

    @staticmethod
    def create():
        """
        Creates a new topic
        Request body:
        {
            "name": "topic_name"
        }
        Response:
        {
            "message": "Topic created successfully",
            "id": "topic_id"
        }
        """
        name = Prompt.ask("[cyan]Enter topic name[/]")

        response = requests.post(
            # f"{SERVER_URL}/queues/", json={"name": name}, headers=Util.get_headers()
            f"{SERVER_URL}/topics/",
            json={"name": name},
        )

        if response.status_code == 200:
            print(f"[green]Topic '{name}' created successfully![/]")
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")

    @staticmethod
    def delete():
        """Deletes a topic"""
        queue_id = Prompt.ask("[cyan]Enter topic id to [bold red]delete[/]")

        response = requests.delete(
            # f"{SERVER_URL}/queues/{queue_id}", headers=Util.get_headers()
            f"{SERVER_URL}/topic/{queue_id}",
        )

        if response.status_code == 200:
            print("[green]Topic deleted successfully![/]")
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")

    @staticmethod
    def send_message():
        """Sends a message to a topic"""
        topic_name = Prompt.ask("[cyan]Enter topic name[/]")
        message = Prompt.ask("[cyan]Enter message[/]")

        response = requests.post(
            f"{SERVER_URL}/topic/{topic_name}/send/",
            json={"message": message},
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print("[green]Message sent successfully![/]")
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")

    @staticmethod
    def receive_message():
        """Receives a message from a topic"""
        topic_name = Prompt.ask("[cyan]Enter topic name[/]")

        response = requests.get(
            f"{SERVER_URL}/queues/{topic_name}/receive/", headers=Util.get_headers()
        )

        if response.status_code == 200:
            print(f"[yellow]Message received:[/] {response.json()['message']}")
        else:
            print(
                f"[red]Error:[/] {
                    response.json().get('detail', 'No messages available')
                }"
            )
