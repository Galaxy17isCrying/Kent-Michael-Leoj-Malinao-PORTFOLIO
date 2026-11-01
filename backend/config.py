import os
import re
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    def __init__(self) -> None:
        self.host = os.getenv("MYSQL_HOST", "127.0.0.1")
        self.port = self._read_port(os.getenv("MYSQL_PORT", "3306"))
        self.database = os.getenv("MYSQL_DATABASE", "portfolio_db")
        self.username = os.getenv("MYSQL_USER", "root")
        self.password = os.getenv("MYSQL_PASSWORD", "")
        self.connection_timeout = 5

        if not re.fullmatch(r"[A-Za-z0-9_]+", self.database):
            raise ValueError("MYSQL_DATABASE may contain only letters, numbers, and underscores.")

        if not self.username:
            raise ValueError("MYSQL_USER must not be empty.")

    @staticmethod
    def _read_port(value: str) -> int:
        try:
            port = int(value)
        except ValueError as error:
            raise ValueError("MYSQL_PORT must be an integer.") from error

        if not 1 <= port <= 65535:
            raise ValueError("MYSQL_PORT must be between 1 and 65535.")

        return port
