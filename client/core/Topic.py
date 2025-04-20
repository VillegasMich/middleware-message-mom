import requests
from config import get_server_zoo
from rich import print
from rich.prompt import Prompt
from rich.tree import Tree
from Util import Util


class Topic:
    
    """
    This class provides static methods to interact with topics on the server.
    It includes functionality for listing, creating, deleting, subscribing, unsubscribing,
    sending, and receiving messages from topics. This class acts as a client-side interface
    for managing topics and their messages.
    """
    
    @staticmethod
    def get_all(message: str = "Topics", only_owned: bool = False):
        #Lists all the topics
        
        SERVER_ZOO = get_server_zoo()
        response = requests.get(
            f"{SERVER_ZOO}/topics?{only_owned}", headers=Util.get_headers()
        )

        topics = response.json().get("topics", [])

        if response.status_code == 200:
            if not topics:
                print("[yellow]There aren't any topics yet.[/]")
                return
            else:
                #Prints the topics in a tree format.
                tree_root = Tree(f"\n[bold yellow]{message}:[/]")
                for topic in topics:
                    tree_root.add(
                        "[bold]ID: "
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

        return topics


    @staticmethod
    def create():
        #Creates a new topic
        
        SERVER_ZOO = get_server_zoo()
        name = Prompt.ask("[cyan]Enter topic name[/]")

        response = requests.post(
            f"{SERVER_ZOO}/topics/",
            json={"name": name},
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print(f"[green]Topic '{name}' created successfully![/]")
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")


    @staticmethod
    def delete():
        #Deletes a topic
        SERVER_ZOO = get_server_zoo()

        #Returns all the topics owned by the user.
        topics = Topic.get_all("Your Topics", only_owned=True)

        if not topics:
            print("[yellow]You don't own any topics to delete.[/]")
            return

        topic_id = Prompt.ask("[cyan]Enter topic ID to [bold red]delete[/]")

        delete_response = requests.delete(
            f"{SERVER_ZOO}/topics/{topic_id}", headers=Util.get_headers()
        )

        if delete_response.status_code == 200:
            print("[green]Topic deleted successfully![/]")
        else:
            print(
                f"[red]Error:[/] {delete_response.json().get('detail', 'Unknown error')}"
            )


    @staticmethod
    def send_message():
        #Sends a message to a topic

        SERVER_ZOO = get_server_zoo()
        topics = Topic.get_all()

        if not topics:
            print("[yellow]There aren't any topics yet.[/]")
            return

        topic_id = Prompt.ask("[cyan]Enter topic ID to send a message[/]")

        message = Prompt.ask("[cyan]Enter message[/]")
        routing_key = Prompt.ask("[cyan]Enter routing key[/]")

        response = requests.post(
            f"{SERVER_ZOO}/topics/{topic_id}/publish",
            json={"content": message, "routing_key": routing_key},
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print("[green]Message sent successfully![/]")
        else:
            print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")


    @staticmethod
    def show_collected_messages(message_dict: dict[str, set]):
        #Show all collected messages from the user's subscribed topics
        
        tree_root = Tree("\n[bold yellow]Topics:[/]")

        for topic in message_dict.keys():
            topic_root = tree_root.add("[bold]" + topic + "[/]")
            for message in message_dict[topic]:
                topic_root.add(str(message))
        print(tree_root)


    @staticmethod
    def subscribe():
        #Subscribes to a topic
        
        SERVER_ZOO = get_server_zoo()
        Topic.get_all()

        topic_id = Prompt.ask("[cyan]Enter topic ID[/]")
        routing_key = Prompt.ask("[cyan]Enter routing key[/]")

        response = requests.post(
            f"{SERVER_ZOO}/topics/subscribe",
            json={
                "topic_id": topic_id,
                "routing_key": routing_key,
            },
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print(f"[yellow]Subscribed to topic:[/] {topic_id}")
        else:
            print(
                f"""[red]Error:[/] {response.json().get("detail", "No topic found")}"""
            )
            
    
    def unsubscribe():
        #Unsubscribes from a topic
        
        SERVER_ZOO = get_server_zoo()
        Topic.get_all()

        topic_id = Prompt.ask("[cyan]Enter topic ID[/]")
        routing_key = Prompt.ask("[cyan]Enter routing key[/]")

        response = requests.post(
            f"{SERVER_ZOO}/topics/unsubscribe",
            json={
                "topic_id": topic_id,
                "routing_key": routing_key,
            },
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print(f"[yellow]Unsubscribed from topic:[/] {topic_id}")
        else:
            try:
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    error_detail = response.json().get("detail", "No detail provided.")
                else:
                    error_detail = response.text or "Empty response"
            except Exception as e:
                error_detail = f"Unexpected error: {e}"

            print(f"[red]Error:[/] {error_detail}")


    @staticmethod
    def pull_message(queue_id: int):
        #Retrieves all collected messages from a specific user's subscribed topic
        
        SERVER_ZOO = get_server_zoo()
        response = requests.get(
            f"{SERVER_ZOO}/topics/queues/{queue_id}/consume", headers=Util.get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            return list(zip(data["content"], data["ids"]))

        return None
