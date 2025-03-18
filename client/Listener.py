import requests
from boostrap import SERVER_URL
from Util import Util
import time
import queue
import threading
from Topic import Topic
from User import User

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

    def listen(self):
        while True:
            try:
                topics = User.get_user_topics()
                if topics and len(topics) > 0:
                    for topic in topics:
                        message = Topic.pull_messages(topic['id'])
                        if message:
                            if topic['name'] in self.dict:
                                self.dict[topic['name']].add(message) 
                            else:
                                self.dict[topic['name']] = {message} 
            except Exception as e:
                print(f"Error al realizar la petición: {e}")

            time.sleep(self.period)