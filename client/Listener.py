import requests
from boostrap import SERVER_URL
from Util import Util
import time
import queue
import threading
from Topic import Topic

class Listener:

    def __init__(self, period: int, queue: queue):
        self.period = period
        self.queue = queue
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

    def listen(self):
        while True:
            try:
                #! Fetch messages from the subscribed topics.
                pass
            except Exception as e:
                print(f"Error al realizar la petición: {e}")

            time.sleep(self.period)