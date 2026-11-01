from backend.database import MySQLDatabase
from backend.models import ContactMessage


class ContactRepository:
    def __init__(self, database: MySQLDatabase) -> None:
        self._database = database

    def save(self, contact: ContactMessage) -> int:
        statement = """
            INSERT INTO contact_messages (name, email, subject, message)
            VALUES (%s, %s, %s, %s)
        """

        with self._database.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(statement, (contact.name, contact.email, contact.subject, contact.message))
                return cursor.lastrowid
