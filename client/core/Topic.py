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

        topic_name = Prompt.ask("[cyan]Enter topic name to [bold red]delete[/]")

        delete_response = requests.delete(
            f"{SERVER_ZOO}/topics/{topic_name}", headers=Util.get_headers()
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

        topic_name = Prompt.ask("[cyan]Enter topic name to send a message[/]")

        topic = next((q for q in topics if q["name"] == topic_name), None)

        if topic is None:
            print(f"[red]Error:[/] Topic '{topic_name}' not found.")
            return

        topic_id = topic["id"]

        message = Prompt.ask("[cyan]Enter message[/]")

        response = requests.post(
            f"{SERVER_ZOO}/topics/{topic_id}/publish",
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
        Topic.get_all()

        topic_name = Prompt.ask("[cyan]Enter topic name[/]")

        response = requests.post(
            f"{SERVER_ZOO}/topics/subscribe",
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
            f"{SERVER_ZOO}/topics/{topic_id}/consume",
            headers=Util.get_headers(),
        )

        if response.status_code == 200:
            return tuple((response.json()["content"], response.json()["id"]))
        else:
            pass
