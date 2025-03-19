import requests
from boostrap import SERVER_URL
from rich import print
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
        response = requests.get(f"{SERVER_URL}/topics/", headers=Util.get_headers())

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
            f"{SERVER_URL}/topics/",
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
        queue_id = Prompt.ask("[cyan]Enter topic id to [bold red]delete[/]")

        response = requests.delete(
            f"{SERVER_URL}/topic/{queue_id}",
            headers=Util.get_headers(),
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

        topic_response = requests.get(
            f"{SERVER_URL}/topics/", headers=Util.get_headers()
        )
        topics = topic_response.json().get("topics", [])

        topic = next((t for t in topics if t["name"] == topic_name), None)

        if topic is None:
            print(f"[red]Error:[/] Topic '{topic_name}' not found.")
            return

        topic_id = topic["id"]

        response = requests.post(
            f"{SERVER_URL}/topics/{topic_id}/publish",
            json={"content": message, "routing_key": "default"},
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
        topic_name = Prompt.ask("[cyan]Enter topic name[/]")

        response = requests.post(
            f"{SERVER_URL}/topics/subscribe",
            json={"name": topic_name},
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            print(f"[yellow]Subscribed to topic:[/] {topic_name}")
        else:
            print(
                f"""[red]Error:[/] {response.json().get("detail", "No topic found")}"""
            )

    @staticmethod
    def pull_message(topic_id: int):
        response = requests.get(
            f"{SERVER_URL}/topics/{topic_id}/consume",
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            return tuple((response.json()["content"], response.json()["id"]))
        else:
            pass
