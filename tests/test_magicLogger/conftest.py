import pytest
import logging

@pytest.fixture(scope="function")
def log_file_path(tmp_path):
    logger = logging.getLogger('test.logger')
    logger.handlers.clear()

    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = logs_dir / "test.jsonl"
    log_file.touch()

    yield log_file
