from Queue import Queue
from rich import print
from rich.prompt import Prompt
from Topic import Topic
from User import User

TOKEN = ""  # Stores authentication token


def main():
    """Main interactive loop"""
    while True:
        print("\n[bold cyan]Middleware MOM Client[/]")
        print("1. Register")
        print("2. Login")
        print("3. Create Queue")
        print("4. Send Message to Queue")
        print("5. Receive Message from Queue")
        print("6. Create Topic")
        print("7. Send Message to Topic")
        print("8. Receive Message from Topic")

        print("9. Exit")

        choice = Prompt.ask("[bold yellow]Choose an option[/]")

        if choice == "1":
            User.register()
        elif choice == "2":
            User.login(TOKEN)
        elif choice == "3":
            Queue.create()
        elif choice == "4":
            Queue.send_message()
        elif choice == "5":
            Queue.receive_message()
        elif choice == "6":
            Topic.create()
        elif choice == "7":
            Topic.send_message()
        elif choice == "8":
            Topic.receive_message()
        elif choice == "9":
            print("[bold red]Exiting...[/]")
            break
        else:
            print("[red]Invalid option, try again.[/]")


if __name__ == "__main__":
    main()
