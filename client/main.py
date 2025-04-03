import config
from core.Listener import Listener
from core.Queue import Queue
from core.Topic import Topic
from core.User import User
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from zookeeper import get_server

TOKEN = ""

console = Console()


def show_menu():
    table = Table(
        title="Middleware MOM Client", show_header=False, header_style="bold cyan"
    )

    # Add column with proper padding
    table.add_column("Option", justify="center", style="bold blue")
    table.add_column("Description", justify="left", style="white")

    # Add rows
    menu_items = [
        ("1", "List all the Queues"),
        ("2", "Create Queue"),
        ("3", "Delete Queue"),
        ("4", "Send Message to Queue"),
        ("5", "Receive Message from Queue"),
        ("6", "Subscribe to a queue"),
        ("7", "Unsubscribe to a queue"),
        ("-", "---------------------------------"),
        ("8", "List all the Topics"),
        ("9", "Create Topic"),
        ("10", "Delete Topic"),
        ("11", "Show collected Messages from Topic"),
        ("12", "Send Message to Topic"),
        ("13", "Subscribe to a topic"),
        ("14", "Exit"),
    ]

    for option, description in menu_items:
        table.add_row(option, description)

    console.print(table)


def main():
    new_server = get_server()
    config.update_server_zoo(new_server)
    if config.SERVER_IP_PORT:
        try:
            """Main interactive loop"""
            global TOKEN

            while True:
                print("\n[bold]Welcome to the Middleware MOM Client![/]")
                print("1. Register")
                print("2. Login")

                choice = Prompt.ask("[bold yellow]Choose an option[/]")

                if choice == "1":
                    User.register()
                    break
                elif choice == "2":
                    TOKEN = User.login()
                    if TOKEN:
                        break
                    else:
                        print("[red]Login failed. Try again.[/]")
                else:
                    print("[red]Invalid option, try again.[/]")

            messages_dict = {}
            listener = Listener(period=10, dict=messages_dict)
            listener.start()

            # Main menu after successful login
            while True:
                show_menu()

                choice = Prompt.ask("[bold yellow]Choose an option[/]")

                if choice == "1":
                    print("\033c", end="")
                    Queue.get_all()
                elif choice == "2":
                    print("\033c", end="")
                    Queue.create()
                elif choice == "3":
                    print("\033c", end="")
                    Queue.delete()
                elif choice == "4":
                    print("\033c", end="")
                    Queue.send_message()
                elif choice == "5":
                    print("\033c", end="")
                    Queue.receive_message()
                elif choice == "6":
                    print("\033c", end="")
                    Queue.subscribe()
                elif choice == "7":
                    print("\033c", end="")
                    Queue.unsubscribe()
                elif choice == "8":
                    print("\033c", end="")
                    Topic.get_all()
                elif choice == "9":
                    print("\033c", end="")
                    Topic.create()
                elif choice == "10":
                    print("\033c", end="")
                    Topic.delete()
                elif choice == "11":
                    print("\033c", end="")
                    Topic.show_collected_messages(messages_dict)
                elif choice == "12":
                    print("\033c", end="")
                    Topic.send_message()
                elif choice == "13":
                    print("\033c", end="")
                    Topic.subscribe()
                elif choice == "14":
                    print("[bold red]Exiting...[/]")
                    break
                else:
                    print("\033c", end="")
                    print("[red]Invalid option, try again.[/]")
                new_server = get_server()
                config.update_server_zoo(new_server)
        except KeyboardInterrupt:
            print("[bold red]\nDisconnecting...[/]")


if __name__ == "__main__":
    main()
