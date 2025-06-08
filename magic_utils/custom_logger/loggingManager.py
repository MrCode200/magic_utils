import logging
from logging import getLogger

from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler

from logging import DEBUG

from logging import Formatter
from .loggingFormatter import ColoredFormatter, JsonFormatter, extra_args


def setup_logger(
        logger_name: str,
        stream_level: int,
        log_file_name: str,
        stream_in_color: bool = True,
        log_in_json: bool = True,
        extra_log_args: list[str] = None
):
    """
       Configure and initialize a logger with stream and timed rotating file handlers.

       :param logger_name: The name of the logger to configure.
       :param stream_level: The log level for the stream handler (e.g., logging.DEBUG, logging.INFO).
       :param log_file_name: The filename where logs will be written, with daily rotation.
       :param stream_in_color: If True, logs to stdout will use colored formatting. Defaults to True.
       :param log_in_json: If True, logs to file will be written in JSON format. Defaults to True.
       :param extra_log_args: List of extra attribute keys to include in the logs (e.g., ['command', 'profile_id']).
           These keys will be added to the colored formatter output if present.

       :return: None
       """
    if extra_log_args:
        extra_args.extend(extra_log_args)

    logger: logging.Logger = getLogger(logger_name)
    logger.setLevel(DEBUG)

    stream_handler: logging.Handler = StreamHandler()
    stream_handler.setLevel(stream_level)
    stream_handler.setFormatter(
        ColoredFormatter() if stream_in_color else Formatter(
            '[%(asctime)s | %(levelname)s] [%(filename)s | lineno%(lineno)d | %(funcName)s] => %(message)s'
        )
    )

    timed_rotating_file_handler: logging.Handler = TimedRotatingFileHandler(log_file_name, when='midnight', interval=1,
                                                                            backupCount=3)
    timed_rotating_file_handler.setLevel(DEBUG)
    timed_rotating_file_handler.setFormatter(
        JsonFormatter() if log_in_json else Formatter(
            '[%(asctime)s | %(levelname)s] [%(filename)s | lineno%(lineno)d | %(funcName)s] => %(message)s'
        )
    )

    logger.addHandler(stream_handler)
    logger.addHandler(timed_rotating_file_handler)

    logger.propagate = False


if __name__ == '__main__':
    setup_logger('oracle.app', DEBUG, '/logs/app.jsonl', log_in_json=False, stream_in_color=True)

    logger = getLogger('oracle.app')
    logger.debug('Testing Logger: DEBUG')
    logger.info('Testing Logger: INFO')
    logger.warning('Testing Logger: WARNING')
    logger.error('Testing Logger: ERROR')
    logger.critical('Testing Logger: CRITICAL')
