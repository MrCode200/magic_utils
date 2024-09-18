from functools import total_ordering

@total_ordering 
class channel():
    def __init__(self):
        self.subscribers = list[callable]

    def subscribe(self, new_subscriber: callable, *args, **kwargs):
        self.subscribers.append((new_subscriber, args, kwargs)) 

    def unsubscribe(self, subscriber: callable):
        self.subscribers = [(sub, args, kwargs) for sub, args, kwargs in self.subscribers if sub[0] != subscriber] 

    def clear(self):
        self.subscribers = []

    def notify(self):
        for sub, args, kwargs in self.subscribers:
            sub(args, kwargs) 

    def __getitem__(self, func: callable):
         return [(sub, args, kwargs) for sub, args, kwargs in self.subscribers if func == sub]

    def __len__(self):
        return len(self.subscribers)
    
    def __eq__(self, other):
        return self.subscribers == other.subscribers