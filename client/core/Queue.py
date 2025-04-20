import requests
from config import get_server_zoo
from rich import print
from rich.prompt import Prompt
from rich.tree import Tree
from Util import Util


class Queue:
    """
    This class provides static methods to interact with queues on the server.
    It includes functionality for listing, creating, deleting, subscribing, unsubscribing,
    sending, and receiving messages from queues. This class acts as a client-side interface
    for managing queues and their messages.
    """
    
    @staticmethod
    def get_all(message: str = "Queues", only_owned: bool = False):
        #Lists all the queues
        
        SERVER_ZOO = get_server_zoo()
        response = requests.get(
            f"{SERVER_ZOO}/queues?{only_owned}", headers=Util.get_headers()
        )

        queues = response.json().get("queues", [])

        if response.status_code == 200:
            if not queues:
                print("[yellow]There aren't any queues yet.[/]")
                return
            else:
                #Prints the queues in a tree format
                tree_root = Tree(f"\n[bold yellow]{message}:[/]")
                for queue in queues:
                    tree_root.add(
                        "[bold]ID: "
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
        #Creates a new queue
        
        SERVER_ZOO = get_server_zoo()
        name = Prompt.ask("[cyan]Enter queue name[/]")

        response = requests.post(
            f"{SERVER_ZOO}/queues/", json={"name": name}, headers=Util.get_headers()
        )

        if response.status_code == 200:
            print(f"[green]Queue '{name}' created successfully![/]")
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")

    @staticmethod
    def delete():
        #Deletes a queue
        
        SERVER_ZOO = get_server_zoo()
        #Returns all the queues owned by the user
        queues = Queue.get_all("Your Queues", only_owned=True)

        if not queues:
            print("[yellow]You don't own any queues to delete.[/]")
            return

        queue_id = Prompt.ask("[cyan]Enter the queue ID to [bold red]delete[/]")

        delete_response = requests.delete(
            f"{SERVER_ZOO}/queues/{queue_id}", headers=Util.get_headers()
        )

        if delete_response.status_code == 200:
            print("[green]Queue deleted successfully![/]")
        else:
            print(
                f"[red]Error:[/] {delete_response.json().get('detail', 'Unknown error')}"
            )

    @staticmethod
    def subscribe():
        #Subscribes to a queue
        
        SERVER_ZOO = get_server_zoo()
        Queue.get_all()

        queue_id = Prompt.ask("[cyan]Enter queue ID[/]")

        response = requests.post(
            f"{SERVER_ZOO}/queues/subscribe?queue_id={queue_id}",
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print(f"[yellow]Subscribed to queue:[/] {queue_id}")
        else:
            print(
                f"""[red]Error:[/] {response.json().get("detail", "No queue found")}"""
            )

    @staticmethod
    def unsubscribe():
        #Unsubscribes from a queue
        
        SERVER_ZOO = get_server_zoo()
        Queue.get_all()

        queue_id = Prompt.ask("[cyan]Enter queue ID[/]")

        response = requests.post(
            f"{SERVER_ZOO}/queues/unsubscribe?queue_id={queue_id}",
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print(f"[yellow]Unsubscribe from queue:[/] {queue_id}")
        else:
            print(
                f"""[red]Error:[/] {response.json().get("detail", "No queue found")}"""
            )

    @staticmethod
    def send_message():
        #Sends a message to a queue
        
        SERVER_ZOO = get_server_zoo()
        queues = Queue.get_all()

        if not queues:
            print("[yellow]There aren't any queues yet.[/]")
            return

        queue_id = Prompt.ask("[cyan]Enter queue ID to send a message[/]")

        response = requests.post(
            f"{SERVER_ZOO}/queues/{queue_id}/publish",
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
        #Receives a message from a queue

        SERVER_ZOO = get_server_zoo()
        queues = Queue.get_all()

        if not queues:
            return

        queue_id = Prompt.ask("[cyan]Enter queue ID to receive message[/]")

        response = requests.get(
            f"{SERVER_ZOO}/queues/{queue_id}/consume",
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print(f"[yellow]Message received:[/] {response.json()['content']}")
        else:
            print(
                f"[red]Error:[/] {response.json().get('detail', 'No messages available')}"
            )
