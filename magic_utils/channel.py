"""
channel_module
---------------

This module defines the `Channel` class, which facilitates the management of subscribers and the notification process.

The `Channel` class allows subscribers to be added, removed, and notified either sequentially or in parallel. Subscribers are callable objects that can be invoked with arguments and keyword arguments.

Usage example:
--------------
    # Create a new channel
    ch = Channel()

    # Define some subscriber functions
    def subscriber1(arg1, kwarg1=None):
        print(f"Subscriber 1: {arg1}, {kwarg1}")

    def subscriber2(arg1, kwarg1=None):
        print(f"Subscriber 2: {arg1}, {kwarg1}")

    # Subscribe to the channel
    ch.subscribe(subscriber1, 'data1', kwarg1='value1')
    ch.subscribe(subscriber2, 'data2')

    # Notify all subscribers sequentially
    ch.notify_all()

    # Notify all subscribers in parallel (2 threads)
    ch.notify_parallel(num_threads=2)
"""
import threading

class Channel:
    """
    A class to manage subscribers and their notifications.

    The `Channel` class manages a list of subscribers and supports adding, removing, and notifying these subscribers. Subscribers can be notified sequentially with `notify_all` or in parallel with `notify_parallel`.

    :ivar subscribers: A list where each element is a tuple containing a callable subscriber and its associated arguments and keyword arguments.
    """
    def __init__(self):
        self.subscribers = []  # List of (callable, args, kwargs)

    def subscribe(self, subscriber: callable, *subscriber_args, **subscriber_kwargs):
        """
        Add a new subscriber to the channel.

        :param subscriber: A callable object that will be notified.
        :param subscriber_args: Arguments to be passed to the subscriber callable.
        :param subscriber_kwargs: Keyword arguments to be passed to the subscriber callable.
        """
        self.subscribers.append((subscriber, subscriber_args, subscriber_kwargs))

    def unsubscribe(self, subscriber: callable):
        """
       Remove a subscriber from the channel.

       :param subscriber: The callable object to be removed from the list of subscribers.
       """
        self.subscribers = [(sub, args, kwargs) for sub, args, kwargs in self.subscribers if sub != subscriber]

    def clear(self):
        """
        Remove all subscribers from the channel.
        """
        self.subscribers = []

    def _notify(self, subs):
        """
        Notify a list of subscribers by calling each subscriber with its associated arguments and keyword arguments.

        :param subs: List of tuples, where each tuple contains a callable subscriber, its arguments, and keyword arguments.
        """
        for sub, args, kwargs in subs:
            sub(*args, **kwargs)

    def notify_all(self):
        """
        Notify all subscribers sequentially.
        """
        self._notify(self.subscribers)

    def notify_parallel(self, num_threads: int = 2):
        """
        Notify all subscribers in parallel using the specified number of threads.

        :param num_threads: The number of threads to use for parallel notification. Must be 2 or higher.
        :raises ValueError: If `num_threads` is less than 2.
        """
        if num_threads <= 1:
            raise ValueError("Number of threads must be 2 or higher")

        # Divide subscribers into chunks
        chunks = [self.subscribers[i::num_threads] for i in range(num_threads)]
        threads = []

        for chunk in chunks:
            thread = threading.Thread(target=self._notify, args=(chunk,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def __getitem__(self, subscriber: callable) -> list[tuple(callable, any, any)]:
        """
        Get the list of arguments and keyword arguments for a specific subscriber.

        :param subscriber: The callable subscriber to retrieve arguments for.
        :return: A list of tuples containing the subscriber, its arguments, and keyword arguments.
        """
        return [(sub, args, kwargs) for sub, args, kwargs in self.subscribers if sub == subscriber]

    def __len__(self) -> int:
        return len(self.subscribers)
    
    def __eq__(self, other):
        """
        Check if this `Channel` instance is equal to another `Channel` instance.

        :param other: The other `Channel` instance to compare with.
        :return: True if both instances have the same subscribers, False otherwise.
        """
        if not isinstance(other, Channel):
            return NotImplemented
        return self.subscribers == other.subscribers