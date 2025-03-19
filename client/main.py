from core.Listener import Listener
from core.Queue import Queue
from core.Topic import Topic
from core.User import User
from rich import print
from rich.prompt import Prompt

TOKEN = ""


def main():
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
        print("\n[bold cyan]Middleware MOM Client[/]")
        print("1. List all the Queues")
        print("2. Create Queue")
        print("3. Delete Queue")
        print("4. Send Message to Queue")
        print("5. Receive Message from Queue")
        print("6. List all the Topics")
        print("7. Create Topic")
        print("8. Delete Topic")
        print("9. Show collected Messages from Topic")
        print("10. Receive Message from Topic")
        print("11. Subscribe to a topic")
        print("12. Exit")

        choice = Prompt.ask("[bold yellow]Choose an option[/]")

        if choice == "1":
            Queue.get_all() 
        elif choice == "2":
            Queue.create()
        elif choice == "3":
            Queue.delete()
        elif choice == "4":
            Queue.send_message()
        elif choice == "5":
            Queue.receive_message()
        elif choice == "6":
            Topic.get_all()
        elif choice == "7":
            Topic.create()
        elif choice == "8":
            Topic.delete()
        elif choice == "9":
            Topic.show_collected_messages(messages_dict)
        elif choice == "10":
            Topic.receive_message()
        elif choice == "11":
            Topic.subscribe()
        elif choice == "12":
            print("[bold red]Exiting...[/]")
            break
        else:
            print("[red]Invalid option, try again.[/]")
    print("[bold yellow]Disconnecting...[/]")


if __name__ == "__main__":
    main()
