import requests
from bootstrap import SERVER_URL
from rich import print
from rich.prompt import Prompt
from rich.tree import Tree
from Util import Util


class Queue:
    @staticmethod
    def get_all(message: str = "Queues", only_owned: bool = False):
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
        response = requests.get(
            f"{SERVER_URL}/queues?{only_owned}", headers=Util.get_headers()
        )

        queues = response.json().get("queues", [])

        if response.status_code == 200:
            if not queues:
                print("[yellow]There aren't any queues yet.[/]")
                return
            else:
                tree_root = Tree(f"\n[bold yellow]{message}:[/]")
                for queue in queues:
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

        return queues

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
            f"{SERVER_URL}/queues/", json={"name": name}, headers=Util.get_headers()
        )

        if response.status_code == 200:
            print(f"[green]Queue '{name}' created successfully![/]")
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")

    @staticmethod
    def delete():
        """Deletes a queue"""

        queues = Queue.get_all("Your Queues", only_owned=True)

        if not queues:
            print("[yellow]You don't own any queues to delete.[/]")
            return

        queue_name = Prompt.ask("[cyan]Enter queue name to [bold red]delete[/]")

        delete_response = requests.delete(
            f"{SERVER_URL}/queues/{queue_name}", headers=Util.get_headers()
        )

        if delete_response.status_code == 200:
            print("[green]Queue deleted successfully![/]")
        else:
            print(
                f"[red]Error:[/] {delete_response.json().get('detail', 'Unknown error')}"
            )

    @staticmethod
    def subscribe():
        Queue.get_all()

        queue_name = Prompt.ask("[cyan]Enter queue name[/]")

        response = requests.post(
            f"{SERVER_URL}/queues/subscribe",
            json={"name": queue_name},
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print(f"[yellow]Subscribed to queue:[/] {queue_name}")
        else:
            print(
                f"""[red]Error:[/] {response.json().get("detail", "No queue found")}"""
            )

    @staticmethod
    def unsubscribe():
        Queue.get_all()

        queue_name = Prompt.ask("[cyan]Enter queue name[/]")

        response = requests.post(
            f"{SERVER_URL}/queues/unsubscribe",
            json={"name": queue_name},
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print(f"[yellow]Unsubscribe from queue:[/] {queue_name}")
        else:
            print(
                f"""[red]Error:[/] {response.json().get("detail", "No queue found")}"""
            )

    @staticmethod
    def send_message():
        """Sends a message to a queue"""

        queues = Queue.get_all()

        if not queues:
            return

        queue_name = Prompt.ask("[cyan]Enter queue name to send a message[/]")

        queue = next((q for q in queues if q["name"] == queue_name), None)

        if queue is None:
            print(f"[red]Error:[/] Queue '{queue_name}' not found.")
            return

        queue_id = queue["id"]

        response = requests.post(
            f"{SERVER_URL}/queues/{queue_id}/publish",
            json={
                "content": Prompt.ask("[cyan]Enter message[/]"),
                "routing_key": "default",
            },
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print("[green]Message sent successfully![/]")
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")

    @staticmethod
    def receive_message():
        """Receives a message from a queue"""

        queues = Queue.get_all()

        if not queues:
            return

        queue_name = Prompt.ask("[cyan]Enter queue name[/]")

        queue = next((q for q in queues if q["name"] == queue_name), None)

        if queue is None:
            print(f"[red]Error:[/] Queue '{queue_name}' not found.")
            return

        queue_id = queue["id"]

        response = requests.get(
            f"{SERVER_URL}/queues/{queue_id}/consume",
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print(f"[yellow]Message received:[/] {response.json()['content']}")
        else:
            print(
                f"[red]Error:[/] {response.json().get('detail', 'No messages available')}"
            )
