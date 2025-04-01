import threading
import time

from core.Topic import Topic
from core.User import User


class Listener:
    def __init__(self, period: int, dict={}):
        self.period = period
        self.dict = dict
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.listen, daemon=True)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()

    """
        Main method executed by the client thread, pulls the first message
        from the subscribed topics. Stores them in a global variable 'messages_dict'
        instanced in main.
    """

    def listen(self):
        while True:
            try:
                queues = User.get_user_queues()
                if queues and len(queues) > 0:
                    for queue in queues:
                        messages = Topic.pull_message(queue.get("id"))
                        if messages:
                            for message in messages:
                                if queue["name"] in self.dict:
                                    self.dict[queue["name"]].add(message)
                                else:
                                    self.dict[queue["name"]] = {message}
            except Exception as e:
                print(f"Error al realizar la petición: {e}")

            time.sleep(self.period)
