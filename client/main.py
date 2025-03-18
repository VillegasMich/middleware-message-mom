from Queue import Queue
from rich import print
from rich.prompt import Prompt
from Topic import Topic
from User import User
from Listener import Listener
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

    # Main menu after successful login
    while True:
        print("\n[bold cyan]Middleware MOM Client[/]")
        print("1. Create Queue")
        print("2. List all the Queues")
        print("3. Delete Queue")
        print("4. Send Message to Queue")
        print("5. Receive Message from Queue")
        print("6. Create Topic")
        print("7. Send Message to Topic")
        print("8. Receive Message from Topic")
        print("9. Exit")

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
    messages_queue = queue.Queue() 
    listener = Listener(period=10, queue=messages_queue)
    listener.start()
    main()
