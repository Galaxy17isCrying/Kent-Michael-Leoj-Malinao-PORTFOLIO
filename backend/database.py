import pymysql

from backend.config import Settings


class MySQLDatabase:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def connect(self) -> pymysql.connections.Connection:
        return pymysql.connect(
            host=self._settings.host,
            port=self._settings.port,
            user=self._settings.username,
            password=self._settings.password,
            database=self._settings.database,
            charset="utf8mb4",
            connect_timeout=self._settings.connection_timeout,
            autocommit=True,
        )
