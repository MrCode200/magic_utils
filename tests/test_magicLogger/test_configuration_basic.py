import logging
from logging import StreamHandler, Formatter
from logging.handlers import TimedRotatingFileHandler

import pytest

from magic_utils.magicLogger.loggingManager import setup_logger


def test_setup_logger_creates_logger_with_name(log_file_path):
    logger = setup_logger('test.logger', log_file_path)

    assert isinstance(logger, logging.Logger)
    assert logger.name == 'test.logger'
    assert len(logger.handlers) == 2  # Created both stream and file handlers
    for handler in logger.handlers:
        assert handler.level == logging.DEBUG

    assert logger.propagate == False


def test_setup_logger_sets_handler_levels(log_file_path):
    logger = setup_logger(
        'test.logger',
        log_file_path,
        stream_level=logging.INFO,
        log_level=logging.INFO
    )
    for handler in logger.handlers:
        assert handler.level == logging.INFO


def test_setup_logger_uses_custom_timed_rotating_kwargs(log_file_path):
    custom_kwargs = {
        'filename': str(log_file_path),
        'when': 'midnight',  # must be lowercase
        'interval': 2,
        'backupCount': 6
    }

    logger = setup_logger(
        'test.logger',
        str(log_file_path),
        timed_rotating_file_handler_kwargs=custom_kwargs
    )

    trfh = None
    for handler in logger.handlers:
        if isinstance(handler, TimedRotatingFileHandler):
            trfh = handler
            break

    assert trfh is not None, "TimedRotatingFileHandler not found"

    assert str(log_file_path) in trfh.baseFilename
    assert trfh.when == custom_kwargs['when'].upper()
    assert trfh.interval == custom_kwargs['interval'] * 24 * 60 * 60
    assert trfh.backupCount == custom_kwargs['backupCount']


def test_setup_logger_raises_for_conflicting_stream_formatter():
    with pytest.raises(ValueError, match="stream_in_color cannot be True while stream_formatter is of instance Formatter"):
        setup_logger(
            'test.logger',
            '/logs/app.jsonl',
            stream_in_color=True,
            stream_formatter=Formatter()
        )


def test_setup_logger_raises_for_conflicting_file_formatter():
    with pytest.raises(ValueError, match="log_in_json cannot be True while file_formatter is of instance Formatter"):
        setup_logger(
            'test.logger',
            '/logs/app.jsonl',
            log_in_json=True,
            file_formatter=Formatter()
        )


def test_setup_logger_clears_previous_handlers(log_file_path):
    logger = logging.getLogger('test.logger')
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(logging.FileHandler(log_file_path))
    assert len(logger.handlers) == 2

    setup_logger('test.logger', log_file_path)
    assert len(logger.handlers) == 2


def test_custom_stream_formatter(log_file_path, capsys):
    custom_formatter: Formatter = Formatter(
        '[%(funcName)s] => %(message)s'
    )
    logger = setup_logger(
        'test.logger',
        log_file_path,
        stream_formatter=custom_formatter,
        stream_in_color=False
    )
    logger.warning("This is a test")

    captured = capsys.readouterr()
    output = captured.err.strip()

    assert "[test_custom_stream_formatter] => This is a test" == output

def test_custom_file_formatter(log_file_path, caplog):
    custom_formatter: Formatter = Formatter(
        '[%(funcName)s] => %(message)s'
    )
    logger = setup_logger(
        'test.logger',
        log_file_path,
        log_in_json=False,
        file_formatter=custom_formatter
    )
    logger.warning("This is a test")
    with open(log_file_path, 'r') as f:
        logline = f.read().strip()
        assert "[test_custom_file_formatter] => This is a test" == logline

