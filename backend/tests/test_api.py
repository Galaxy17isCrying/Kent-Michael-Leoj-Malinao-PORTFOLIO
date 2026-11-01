import unittest

from backend.app import create_app
from backend.models import ContactMessage
from backend.services import ContactService


VALID_CONTACT = {
    "name": "Alex",
    "email": "alex@example.com",
    "subject": "Hello",
    "message": "I'd like to get in touch.",
    "website": "",
}


class InMemoryContactRepository:
    def __init__(self) -> None:
        self.messages: list[ContactMessage] = []

    def save(self, contact: ContactMessage) -> int:
        self.messages.append(contact)
        return len(self.messages)


class FailingContactRepository:
    def save(self, _contact: ContactMessage) -> int:
        raise RuntimeError("database unavailable")


class ContactApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.repository = InMemoryContactRepository()
        self.app.config["CONTACT_SERVICE"] = ContactService(self.repository)
        self.client = self.app.test_client()

    def test_health_endpoint(self) -> None:
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"ok": True, "service": "portfolio-api"})

    def test_api_not_found_returns_json(self) -> None:
        response = self.client.get("/api/missing")

        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.get_json()["ok"])
        self.assertTrue(response.get_json()["error"])

    def test_serves_portfolio_and_does_not_expose_env(self) -> None:
        homepage = self.client.get("/")
        stylesheet = self.client.get("/styles.css")
        certificate = self.client.get(
            "/assets/certificates/Malinao_Certificate_ITsupport.pdf"
        )
        self.assertEqual(homepage.status_code, 200)
        self.assertEqual(stylesheet.status_code, 200)
        self.assertEqual(certificate.status_code, 200)
        self.assertTrue(certificate.content_type.startswith("application/pdf"))
        homepage.close()
        stylesheet.close()
        certificate.close()
        self.assertEqual(self.client.get("/.env").status_code, 404)

    def test_accepts_and_saves_valid_contact_message(self) -> None:
        response = self.client.post("/api/contact", json=VALID_CONTACT)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"ok": True, "id": 1})
        self.assertEqual(self.repository.messages[0].name, "Alex")

    def test_database_failure_returns_temporary_unavailable_response(self) -> None:
        self.app.config["CONTACT_SERVICE"] = ContactService(FailingContactRepository())

        with self.assertLogs(self.app.logger, level="ERROR"):
            response = self.client.post("/api/contact", json=VALID_CONTACT)

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.get_json(),
            {
                "ok": False,
                "error": "Messages are temporarily unavailable. Please try again later.",
            },
        )

    def test_rejects_invalid_email_without_saving(self) -> None:
        payload = {**VALID_CONTACT, "email": "not-an-email"}
        response = self.client.post("/api/contact", json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("email address", response.get_json()["error"])
        self.assertEqual(self.repository.messages, [])

    def test_requires_json(self) -> None:
        response = self.client.post("/api/contact", data="not json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("JSON", response.get_json()["error"])
        self.assertEqual(self.repository.messages, [])

    def test_rejects_oversized_and_missing_fields(self) -> None:
        for payload in (
            {**VALID_CONTACT, "message": "x" * 5001},
            {key: value for key, value in VALID_CONTACT.items() if key != "subject"},
        ):
            with self.subTest(payload=payload):
                response = self.client.post("/api/contact", json=payload)
                self.assertEqual(response.status_code, 400)

        self.assertEqual(self.repository.messages, [])

    def test_rejects_filled_honeypot(self) -> None:
        response = self.client.post(
            "/api/contact",
            json={**VALID_CONTACT, "website": "spam.example"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.repository.messages, [])

    def test_limits_contact_submissions(self) -> None:
        for _ in range(5):
            self.assertEqual(
                self.client.post("/api/contact", json=VALID_CONTACT).status_code,
                201,
            )

        response = self.client.post("/api/contact", json=VALID_CONTACT)
        self.assertEqual(response.status_code, 429)
        self.assertIn("Retry-After", response.headers)
        self.assertEqual(len(self.repository.messages), 5)


if __name__ == "__main__":
    unittest.main()
