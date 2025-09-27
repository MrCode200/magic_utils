"""
Manage a tunnelmole process that exposes a local port via a public URL.
"""

import subprocess
import re
from typing import Optional


class TunnelMole:
    """Manage a tunnelmole process that exposes a local port via a public URL."""

    _process: Optional[subprocess.Popen] = None
    _url_pattern = re.compile(r"https?://([^.]+)\.tunnelmole\.net")

    def __init__(self, port: int = 8000):
        self.port = port
        self.subdomain: Optional[str] = None
        self.public_url: Optional[str] = None

    def start(self) -> Optional[str]:
        """
        Start the tunnelmole process.

        :return: If successful returns None, if no url was found the shell response of the command is returned.
        """
        if self.is_running():
            raise RuntimeError("TunnelMole is already running.")

        self._process = subprocess.Popen(
            ["npx", "tunnelmole", str(self.port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )

        # Wait until we get the URL
        log = ""
        for line in self._process.stdout:
            log += line
            match = self._url_pattern.search(line)
            if match:
                self.subdomain = match.group(1)
                self.public_url = f"https://{self.subdomain}.tunnelmole.net"

        return log

    def stop(self):
        """Stop the tunnelmole process if it’s running."""
        if not self.is_running():
            raise RuntimeError("TunnelMole is not running.")

        self._process.terminate()
        self._process = None
        self.subdomain = None
        self.public_url = None

    def is_running(self) -> bool:
        """Check if tunnelmole is still running."""
        return self._process is not None and self._process.poll() is None

    def __enter__(self):
        """Context manager entry — automatically starts the tunnel."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit — ensures tunnel is stopped."""
        self.stop()