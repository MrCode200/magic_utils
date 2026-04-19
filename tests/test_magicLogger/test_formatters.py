import datetime
import json
import pytest

import logging

from magic_utils.magicLogger import setup_logger
from magic_utils.magicLogger.loggingFormatter import ColoredFormatter, JsonFormatter

record_testcase: dict[str, any] = {
    'name': 'test_logger',
    'level': logging.WARNING,
    'fn': 'fake_file.py',
    'lno': 123,
    'msg': 'hello world',
    'args': (),
    'exc_info': None,
    'func': 'fake_function',
}

@pytest.mark.parametrize("level,expected_color,level_name", [
    (logging.DEBUG, '\033[94m', 'DEBUG'),
    (logging.INFO, '\033[92m', 'INFO'),
    (logging.WARNING, '\033[93m', 'WARNING'),
    (logging.ERROR, '\033[91m', 'ERROR'),
    (logging.CRITICAL, '\033[95m', 'CRITICAL'),
], ids=["debug-test", "info-test", "warning-test", "error-test", "critical-test"])
def test_colored_formatter_outputs_ansi_and_formatted_fields(log_file_path, level, expected_color, level_name):
    logger = setup_logger('test.logger', log_file_path)

    record_testcase_level = record_testcase.copy()
    record_testcase_level['level'] = level

    record = logger.makeRecord(**record_testcase_level)
    formatter = ColoredFormatter()
    formatted = formatter.format(record)

    assert datetime.date.today().strftime("%Y-%m-%d") in formatted
    assert formatted.startswith(expected_color)
    assert '\033[0m' in formatted
    assert "Message: hello world" in formatted
    assert level_name in formatted
    assert "fake_file.py" in formatted
    assert "lineno(123)" in formatted
    assert "fake_function" in formatted

def test_json_formatter_outputs_valid_json_and_keys(log_file_path):
    logger = setup_logger('test.logger', log_file_path)
    record = logger.makeRecord(
        **record_testcase
    )

    formatter = JsonFormatter()
    formatted = json.loads(formatter.format(record))

    assert isinstance(formatted, dict)
    assert 'timestamp' in formatted and datetime.date.today().strftime("%Y-%m-%d") in formatted['timestamp']
    assert 'level' in formatted and formatted['level'] == 'WARNING'
    assert 'file' in formatted and formatted['file'] == 'fake_file.py'
    assert 'line_number' in formatted and formatted['line_number'] == 123
    assert 'function' in formatted and formatted['function'] == 'fake_function'
    assert 'message' in formatted and formatted['message'] == 'hello world'
    assert 'exc_info' in formatted and formatted['exc_info'] is None

def test_formatters_include_extra_args(log_file_path):
    logger = setup_logger('test.logger', log_file_path, extra_log_args=['extra1', 'extra2'])
    record = logger.makeRecord(
        **record_testcase,
    )
    record.extra1 = 'value1'
    # extra2 not passed, therefor its value should be None

    jf = JsonFormatter(extra_args=['extra1', 'extra2'])
    json_formatted = json.loads(jf.format(record))

    assert 'extra1' in json_formatted and json_formatted['extra1'] == 'value1'
    assert 'extra2' in json_formatted and json_formatted['extra2'] == 'None'

    cf = ColoredFormatter(extra_args=['extra1', 'extra2'])
    colored_formatted = cf.format(record)

    assert 'extra1' in colored_formatted and 'value1' in colored_formatted
    assert 'extra2' in colored_formatted and 'None' in colored_formatted


if __name__ == '__main__':
    pytest.main([__file__])