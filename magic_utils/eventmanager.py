"""
channel_module
---------------

This module defines the ``Channel`` class, which facilitates the management of subscribers and the notification process.

The ``Channel`` class allows subscribers to be added, removed, and notified either sequentially or in parallel. Subscribers are callable objects that can be invoked with arguments and keyword arguments.

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
import warnings

class EventManager:
    """
    A class to manage subscribers and their notifications.

    The `EventManager` class manages a list of subscribers and supports adding, removing, and notifying these subscribers. Subscribers can be notified sequentially with `notify_all` or in parallel with `notify_parallel`.

    :ivar subscribers: A list where each element is a tuple containing a callable subscriber and its associated arguments and keyword arguments.
    """
    def __init__(self):
        self.subscribers = [] # List of (callable, args, kwargs)

    def subscribe(self, subscriber: callable, *subscriber_args, **subscriber_kwargs):
        """
        Add a new subscriber to the EventManager.

        :param subscriber: A callable object that will be notified.
        :param subscriber_args: Arguments to be passed to the subscriber callable.
        :param subscriber_kwargs: Keyword arguments to be passed to the subscriber callable.
        """
        self.subscribers.append((subscriber, subscriber_args, subscriber_kwargs))

    def unsubscribe(self, subscriber: callable):
        """
       Remove a subscriber from the EventManager.

       :param subscriber: The callable object to be removed from the list of subscribers.
       """
        self.subscribers = [(sub, args, kwargs) for sub, args, kwargs in self.subscribers if sub != subscriber]

    def clear(self):
        """
        Remove all subscribers from the EventManager.
        """
        self.subscribers = []

    def _notify(self, subs) -> dict[tuple[str, tuple[any], tuple[tuple[str, any]] | tuple], any]:
        """
        Notify a list of subscribers by calling each subscriber with its associated arguments and keyword arguments.

        :param subs: List of tuples, where each tuple contains a callable subscriber, its arguments, and keyword arguments.
        :return: Dict of {tuple(sub, args, tuple(kwargs.items())) : returned_value}. The order of the items represents the order in which they were called
        """
        results = {}

        for sub, args, kwargs in subs:
            result = sub(*args, **kwargs)

            results[(sub, args, tuple(kwargs.items()))] = result

        return results

    def notify_all(self) -> dict[tuple[str, tuple[any], tuple[tuple[str, any]] | tuple], any]:
        """
        Notify all subscribers sequentially.

        :return: Dict of {tuple(sub, args, tuple(kwargs.items())) : returned_value}. The order of the items represents the order in which they were called
        """
        return self._notify(self.subscribers)

    def notify_parallel(self, num_threads: int = 2) -> dict[tuple[str, tuple[any], tuple[tuple[str, any]] | tuple], any]:
        """
        Notify all subscribers in parallel using the specified number of threads.

        If the specified number of threads exceeds the number of subscribers,
        a warning will be issued and the number of threads will be automatically
        adjusted to match the number of available subscribers.

        :param num_threads: The number of threads to use for parallel notification. Must be 2 or higher.
        :return: Dict of {tuple(sub, args, tuple(kwargs.items())) : returned_value}.
                 The order of the items represents the order in which they were called.
        :raises ValueError: If `num_threads` is less than 2.
        """
        if num_threads <= 1:
            raise ValueError("Number of threads must be 2 or higher")

        num_of_subs = len(self.subscribers)
        if num_threads > num_of_subs:
            warnings.warn(
                f"Number of threads ({num_threads}) exceeds the number of subscribers ({len(self.subscribers)})."
                f" Adjusting num_threads to the number of subscribers to {num_of_subs}.",
                UserWarning
            )
            num_threads = num_of_subs

        # Divide subscribers into chunks
        chunks = [self.subscribers[i::num_threads] for i in range(num_threads)]
        threads = []

        results = {}
        lock = threading.Lock()

        def _notify_worker(chunk):
            """Calls all functions and saves values returned while ensuring that threads dont access the results simultaneously
            :param subs: List of tuples, where each tuple contains a callable subscriber, its arguments, and keyword arguments.
            """
            for sub, args, kwargs in chunk:
                result = sub(*args, **kwargs)
                with lock:
                    results[(sub, tuple(args), tuple(kwargs.items()))] = result

        for chunk in chunks:
            thread = threading.Thread(target=_notify_worker, args=(chunk,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return results

    def __getitem__(self, subscriber: callable) -> list[tuple[callable, any, any]]:
        """
        Get the list of arguments and keyword arguments for a specific subscriber.

        :param subscriber: The callable subscriber to retrieve arguments for.
        :return: A list of tuples containing the subscriber, its arguments, and keyword arguments as a tuple.
        """
        return [(sub, args, tuple(kwargs.items())) for sub, args, kwargs in self.subscribers if sub == subscriber]

    def __len__(self) -> int:
        return len(self.subscribers)
    
    def __eq__(self, other):
        """
        Check if this `EventManager` instance is equal to another `EventManager` instance by comparing both subscribers lists.

        :param other: The other `EventManager` instance to compare with.
        :return: True if both instances have the same subscribers, False otherwise.
        """
        if not isinstance(other, EventManager):
            return NotImplemented
        return self.subscribers == other.subscribers