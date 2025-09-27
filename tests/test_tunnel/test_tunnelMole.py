import subprocess

import pytest
from unittest.mock import patch, MagicMock

from magic_utils.tunnel import TunnelMole

@pytest.fixture
def mock_popen():
    """Fixture that mocks subprocess.Popen so we don’t spawn a real process."""
    with patch('subprocess.Popen') as mock_popen_cls:
        process_mock = MagicMock()

        process_mock.stdout = iter([
            "Some log line...",
            "Forwarding: https://abc123.tunnelmole.net"
        ])

        def fake_terminate():
            process_mock.poll.return_value = 0

        process_mock.return_value = None
        process_mock.poll.return_value = None
        process_mock.terminate.side_effect = fake_terminate

        mock_popen_cls.return_value = process_mock

        yield mock_popen_cls

def test_tunnel_start_and_stop(mock_popen):
    tunnel = TunnelMole(port=9999)

    assert not tunnel.is_running()

    assert tunnel.start() == 'Some log line...Forwarding: https://abc123.tunnelmole.net'

    assert tunnel.public_url == "https://abc123.tunnelmole.net"
    assert tunnel.subdomain == "abc123"
    assert tunnel.is_running()

    # Ensure Popen was called correctly
    mock_popen.assert_called_once_with(
        ["npx", "tunnelmole", str(9999)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True
    )

    # Stop tunnel and check cleanup
    tunnel.stop()
    assert not tunnel.is_running()

def test_tunnel_exceptions(mock_popen):
    tunnel = TunnelMole(port=9999)

    tunnel.start()
    assert tunnel.is_running()
    with pytest.raises(RuntimeError, match="TunnelMole is already running."):
        tunnel.start()

    tunnel.stop()
    assert not tunnel.is_running()
    with pytest.raises(RuntimeError, match="TunnelMole is not running."):
        tunnel.stop()

def test_context_manager(mock_popen):
    with TunnelMole(port=9999) as tunnel:
        assert tunnel.is_running()
        assert tunnel.public_url == "https://abc123.tunnelmole.net"
        assert tunnel.subdomain == "abc123"

    assert not tunnel.is_running()