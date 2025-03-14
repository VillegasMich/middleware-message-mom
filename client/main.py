import requests
from boostrap import BASE_URL
from rich import print
from rich.prompt import Prompt

TOKEN = None  # Stores authentication token


def set_token(token: str):
    """Stores the authentication token"""
    global TOKEN
    TOKEN = token


def get_headers():
    """Returns headers with authentication token"""
    if not TOKEN:
        return {}
    return {"Authorization": f"Bearer {TOKEN}"}


def register():
    """Registers a new user"""
    username = Prompt.ask("[cyan]Enter username[/]")
    password = Prompt.ask("[cyan]Enter password[/]", password=True)

    response = requests.post(
        f"{BASE_URL}/register/", json={"username": username, "password": password}
    )

    if response.status_code == 200:
        print("[green]User registered successfully![/]")
    else:
        print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")


def login():
    """Logs in and obtains a token"""
    username = Prompt.ask("[cyan]Enter username[/]")
    password = Prompt.ask("[cyan]Enter password[/]", password=True)

    response = requests.post(
        f"{BASE_URL}/login/", json={"username": username, "password": password}
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        set_token(token)
        print("[green]Login successful![/]")
    else:
        print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")


def create_queue():
    """Creates a new queue"""
    name = Prompt.ask("[cyan]Enter queue name[/]")

    response = requests.post(
        f"{BASE_URL}/queues/", json={"name": name}, headers=get_headers()
    )

    if response.status_code == 200:
        print(f"[green]Queue '{name}' created successfully![/]")
    else:
        print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")


def send_message():
    """Sends a message to a queue"""
    queue_name = Prompt.ask("[cyan]Enter queue name[/]")
    message = Prompt.ask("[cyan]Enter message[/]")

    response = requests.post(
        f"{BASE_URL}/queues/{queue_name}/send/",
        json={"message": message},
        headers=get_headers(),
    )

    if response.status_code == 200:
        print("[green]Message sent successfully![/]")
    else:
        print(f"[red]Error:[/] {response.json().get('detail', 'Unknown error')}")


def receive_message():
    """Receives a message from a queue"""
    queue_name = Prompt.ask("[cyan]Enter queue name[/]")

    response = requests.get(
        f"{BASE_URL}/queues/{queue_name}/receive/", headers=get_headers()
    )

    if response.status_code == 200:
        print(f"[yellow]Message received:[/] {response.json()['message']}")
    else:
        print(
            f"[red]Error:[/] {response.json().get('detail', 'No messages available')}"
        )


def main():
    """Main interactive loop"""
    while True:
        print("\n[bold cyan]Middleware MOM Client[/]")
        print("1. Register")
        print("2. Login")
        print("3. Create Queue")
        print("4. Send Message")
        print("5. Receive Message")
        print("6. Exit")

        choice = Prompt.ask("[bold yellow]Choose an option[/]")

        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            create_queue()
        elif choice == "4":
            send_message()
        elif choice == "5":
            receive_message()
        elif choice == "6":
            print("[bold red]Exiting...[/]")
            break
        else:
            print("[red]Invalid option, try again.[/]")


if __name__ == "__main__":
    main()
