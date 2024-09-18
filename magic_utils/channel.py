class channel():
    def __init__(self):
        self.subscribers = list[callable]

    def subscribe(self, new_subscriber: callable | tuple[callable]):
        self.subscribers.append(new_subscriber) 

    def unsubscribe(self, subscriber: callable | tuple[callable]):
        self.subscribers.remove(subscriber) 

    def clear(self):
        self.subscribers = []

    def call(self):
        for sub in self.subscribers:
            sub() 
