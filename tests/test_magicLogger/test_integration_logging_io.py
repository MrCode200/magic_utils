import logging
import json

from magic_utils import setup_logger

def test_logging_to_file(log_file_path):
    logger = setup_logger('test.logger', log_file_path, extra_log_args=['extra1'])
    logger.info('test message', extra={'extra1': 'value1'})
    expected_jsonl = {
        'level': 'INFO',
        'message': 'test message',
        'file': 'test_integration_logging_io.py',
        'line_number': 8,
        'function': 'test_logging_to_file',
        'exc_info': None,
        'extra1':'value1'
    }

    logging.shutdown()
    with open(log_file_path, 'r') as f:
        logline = json.loads(f.readline())
        print(logline)
        assert 'timestamp' in logline
        assert expected_jsonl == {k: v for k, v in logline.items() if k != 'timestamp'}