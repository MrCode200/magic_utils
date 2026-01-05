import logging
from logging import DEBUG, Logger
from logging import Formatter
from logging import StreamHandler
from logging import getLogger
from logging.handlers import TimedRotatingFileHandler
from typing import Optional, Literal

from .loggingFormatter import ColoredFormatter, JsonFormatter


def setup_logger(
        logger_name: str,
        log_file_path: str,
        stream_level: int = DEBUG,
        log_level: int = DEBUG,
        stream_in_color: bool = True,
        stream_formatter: Optional[Formatter | Literal['default']] = 'default', # TODO: test Literal['default'] vs None
        file_formatter: Optional[Formatter | Literal['default']] = 'default', # TODO: test Literal['default']
        log_in_json: bool = True,
        extra_log_args: list[str] = None,
        remove_previous_handlers: bool = True,
        timed_rotating_file_handler_kwargs: Optional[dict] = None
) -> Logger:
    """
       Configure and initialize a logger with stream and timed rotating file handlers.

       Note:
        - logger.propagate = False
        - removes previous handlers from logger
        - Default format (this isn't the colored format): [%(asctime)s | %(levelname)s] [%(filename)s | lineno%(lineno)d | %(funcName)s] => %(message)s

       :param logger_name: The name of the logger to configure.
       :param log_file_path: The filename where logs will be written, with daily rotation. (e.g., '/logs/app.jsonl')
       :param stream_level: The log level for the stream handler (e.g., logging.DEBUG, logging.INFO) Defaults to DEBUG.
       :param log_level: The log level for the file handler (e.g., logging.DEBUG, logging.INFO) Defaults to DEBUG.
       :param stream_in_color: If True, logs to stdout will use colored formatting. Defaults to True.
       :param stream_formatter: The formatter to use for the stream handler. Defaults to ColoredFormatter if stream_in_color is True,
       otherwise uses the default formatter when 'default' is used. To disable the stream Handler set it to None.
       :param file_formatter: The formatter to use for the file handler. Defaults to JsonFormatter if log_in_json is True,
       otherwise uses the default formatter when 'default' is used. To disable the stream Handler set it to None.
       :param log_in_json: If True, logs to file will be written in JSON format. Defaults to True.
       :param remove_previous_handlers: If True, removes previous handlers from the logger. Defaults to True.
       :param extra_log_args: List of extra attribute keys to include in the logs (e.g., ['arg1', 'arg2']).
           These keys will be added to the colored formatter output if present.
       :param timed_rotating_file_handler_kwargs: Kwargs to pass to the TimedRotatingFileHandler constructor.
           Overwrites all the default kwargs {'filename': log_file_name, 'when': 'midnight', 'interval': 1, 'backupCount': 3}

       :return: None
       """
    if stream_in_color and isinstance(stream_formatter, Formatter):
        raise ValueError("stream_in_color cannot be True while stream_formatter is of instance Formatter")
    if log_in_json and isinstance(file_formatter, Formatter):
        raise ValueError("log_in_json cannot be True while file_formatter is of instance Formatter")

    logger: logging.Logger = getLogger(logger_name)
    logger.handlers.clear() if remove_previous_handlers else None
    logger.setLevel(DEBUG)

    if stream_formatter is not None:
        stream_formatter: Formatter = stream_formatter if isinstance(stream_formatter, Formatter) else (
            ColoredFormatter(extra_args=extra_log_args)) if stream_in_color else Formatter(
            '[%(asctime)s | %(levelname)s] [%(filename)s | lineno%(lineno)d | %(funcName)s] => %(message)s'
        )
        stream_handler: logging.Handler = StreamHandler()
        stream_handler.setLevel(stream_level)
        stream_handler.setFormatter(
            stream_formatter
        )
        logger.addHandler(stream_handler)

    if file_formatter is not None:
        timed_rotating_file_handler_kwargs = timed_rotating_file_handler_kwargs if timed_rotating_file_handler_kwargs is not None \
            else {
            'filename': log_file_path,
            'when': 'midnight',
            'interval': 1,
            'backupCount': 3
        }

        file_formatter: Formatter = file_formatter if isinstance(file_formatter, Formatter) else (
            JsonFormatter(extra_args=extra_log_args)) if log_in_json else Formatter(
            '[%(asctime)s | %(levelname)s] [%(filename)s | lineno%(lineno)d | %(funcName)s] => %(message)s'
        )
        timed_rotating_file_handler: logging.Handler = TimedRotatingFileHandler(
            **timed_rotating_file_handler_kwargs
        )
        timed_rotating_file_handler.setLevel(log_level)
        timed_rotating_file_handler.setFormatter(
            file_formatter
        )

        logger.addHandler(timed_rotating_file_handler)

    logger.propagate = False

    return logger