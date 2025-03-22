from core.Listener import Listener
from core.Queue import Queue
from core.Topic import Topic
from core.User import User
from rich import print
from rich.prompt import Prompt

TOKEN = ""


def main():
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
            print("\n[bold cyan]Middleware MOM Client[/]")
            print("1. List all the Queues")
            print("2. Create Queue")
            print("3. Delete Queue")
            print("4. Send Message to Queue")
            print("5. Receive Message from Queue")
            print("6. Subscribe to a queue")
            print("7. Unsubscribe to a queue")
            print("8. List all the Topics")
            print("9. Create Topic")
            print("10. Delete Topic")
            print("11. Show collected Messages from Topic")
            print("12. Send Message to Topic")
            print("13. Subscribe to a topic")
            print("14. Exit")

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
                Queue.subscribe()
            elif choice == "7":
                Queue.unsubscribe()
            elif choice == "8":
                Topic.get_all()
            elif choice == "9":
                Topic.create()
            elif choice == "10":
                Topic.delete()
            elif choice == "11":
                Topic.show_collected_messages(messages_dict)
            elif choice == "12":
                Topic.send_message()
            elif choice == "13":
                Topic.subscribe()
            elif choice == "14":
                print("[bold red]Exiting...[/]")
                break
            else:
                print("[red]Invalid option, try again.[/]")
    except KeyboardInterrupt:
        print("[bold red]\nDisconnecting...[/]")


if __name__ == "__main__":
    main()
