from core.Queue import Queue
from rich import print
from rich.prompt import Prompt
from core.Topic import Topic
from core.User import User
from core.Listener import Listener
import queue

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
        print("1. Create Queue")
        print("2. List all the Queues")
        print("3. Delete Queue")
        print("4. Send Message to Queue")
        print("5. Receive Message from Queue")
        print("6. List all the Topics")
        print("7. Create Topic")
        print("8. Send Message to Topic")
        print("9. Receive Message from Topic")
        print("10. Subscribe to a topic")
        print("11. Exit")

        choice = Prompt.ask("[bold yellow]Choose an option[/]")

        if choice == "1":
            Queue.create() 
        elif choice == "2":
            Queue.get_all()
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
            Topic.send_message()
        elif choice == "9":
            Topic.receive_message()
        elif choice == "10":
            Topic.subscribe()
        elif choice == "11":
            print("[bold red]Exiting...[/]")
            break
        else:
            print("[red]Invalid option, try again.[/]")
    print(messages_dict)

if __name__ == "__main__":
    main()
