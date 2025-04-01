import requests
from config import SERVER_ZOO
from rich import print
from rich.prompt import Prompt
from rich.tree import Tree
from Util import Util


class Topic:
    @staticmethod
    def get_all(message: str = "Topics", only_owned: bool = False):
        """
        Lists all the topics
        Response:
        {
            "message": "message_output"
            "topics": "[
                {
                    "name": topic_name
                    "id": topic_id
                },
                ...
            ]"
        }
        """
        response = requests.get(
            f"{SERVER_ZOO}/topics?{only_owned}", headers=Util.get_headers()
        )

        topics = response.json().get("topics", [])

        if response.status_code == 200:
            if not topics:
                print("[yellow]There aren't any topics yet.[/]")
                return
            else:
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
        """Deletes a topic"""

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
        """Sends a message to a topic"""

        topics = Topic.get_all()

        if not topics:
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
        """Show all collected messages from user topics"""
        tree_root = Tree("\n[bold yellow]Topics:[/]")

        for topic in message_dict.keys():
            topic_root = tree_root.add("[bold]" + topic + "[/]")
            for message in message_dict[topic]:
                topic_root.add(str(message))
        print(tree_root)

    @staticmethod
    def subscribe():
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

    @staticmethod
    def pull_message(queue_id: int):
        response = requests.get(
            f"{SERVER_ZOO}/topics/queues/{queue_id}/consume", headers=Util.get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            return list(zip(data["content"], data["ids"]))

        return None
