from magic_utils.eventmanager import EventManager

import warnings
import pytest

# Sample subscriber functions for testing
def subscriber_function_test_1(arg1, kwarg1=None):
    return f"Subscriber 1: {arg1}, {kwarg1}"

def subscriber_function_test_2(arg1, kwarg1=None):
    return f"Subscriber 2: {arg1}, {kwarg1}"


def test_subscribe():
    event = EventManager()
    event.subscribe(subscriber_function_test_1, 'data', kwarg1='value')

    assert len(event) == 1
    assert event[subscriber_function_test_1] == [(subscriber_function_test_1, ('data',), (('kwarg1', 'value'),))]


def test_unsubscribe():
    event = EventManager()
    event.subscribe(subscriber_function_test_1, 'data', kwarg1='value')
    event.unsubscribe(subscriber_function_test_1)

    assert len(event) == 0


def test_clear():
    event = EventManager()
    event.subscribe(subscriber_function_test_1, 'data', kwarg1='value1')
    event.subscribe(subscriber_function_test_2, 'data', kwarg1='value1')

    event.clear()

    assert len(event) == 0


def test_notify_all():
    event = EventManager()
    event.subscribe(subscriber_function_test_1, 'data1', kwarg1='value1')
    event.subscribe(subscriber_function_test_2, 'data2')

    result = event.notify_all()

    expected = {
        (subscriber_function_test_1, ('data1',), (('kwarg1', 'value1'),)) : "Subscriber 1: data1, value1",
        (subscriber_function_test_2, ('data2',), ()) : "Subscriber 2: data2, None"
    }

    assert result == expected


def test_notify_parallel():
    event = EventManager()

    event.subscribe(subscriber_function_test_1, 'data1', kwarg1='value1')
    event.subscribe(subscriber_function_test_2, 'data2')

    result = event.notify_parallel()

    expected = {
        (subscriber_function_test_1, ('data1',), (('kwarg1', 'value1'),)) : "Subscriber 1: data1, value1",
        (subscriber_function_test_2, ('data2',), ()) : "Subscriber 2: data2, None"
    }

    assert result == expected


def test_notify_parallel_invalid_num_threads():
    event = EventManager()

    with pytest.raises(ValueError):
        event.notify_parallel(num_threads=1)


def test_notify_parallel_subscribers_exceeding_threads():
    event = EventManager()

    event.subscribe(subscriber_function_test_1, 'data1', kwarg1='value1')
    event.subscribe(subscriber_function_test_2, 'data2')

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        event.notify_parallel(num_threads=5)

        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)
        assert 'Number of threads (5) exceeds the number of subscribers (2).' in str(w[-1].message)
        assert 'Adjusting num_threads to the number of subscribers to 2.' in str(w[-1].message)

def test_eq():
    event1 = EventManager()
    event2 = EventManager()

    event1.subscribe(subscriber_function_test_1, 'data', kwarg1 = 'value1')
    event2.subscribe(subscriber_function_test_1, 'data', kwarg1 = 'value1')

    assert event1 == event2

    event1.clear()
    event2.clear()

    event1.subscribe(subscriber_function_test_1, 'data', kwarg1 = 'value1')
    event2.subscribe(subscriber_function_test_1, 'otherdata', kwarg1 = 'value1')

    assert event1 != event2

    assert event1.__eq__('Not an event Manager') is NotImplemented