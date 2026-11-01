import re
from dataclasses import dataclass
from typing import Any


class ContactValidationError(ValueError):
    """Raised when a contact message does not meet the API validation rules."""


@dataclass(frozen=True)
class ContactMessage:
    name: str
    email: str
    subject: str
    message: str

    @classmethod
    def from_payload(cls, payload: Any) -> "ContactMessage":
        if not isinstance(payload, dict):
            raise ContactValidationError("Send your message as a JSON object.")

        values: dict[str, str] = {}
        limits = {"name": 100, "email": 254, "subject": 150, "message": 5000}

        for field, maximum in limits.items():
            value = payload.get(field)
            if not isinstance(value, str):
                raise ContactValidationError(f"Enter a valid {field}.")

            cleaned = value.strip()
            if not cleaned:
                raise ContactValidationError(f"Enter a valid {field}.")
            if len(cleaned) > maximum:
                raise ContactValidationError(
                    f"{field.capitalize()} must be {maximum} characters or fewer."
                )
            if any(ord(character) < 32 and character not in "\n\t" for character in cleaned):
                raise ContactValidationError(f"{field.capitalize()} contains an invalid character.")

            values[field] = cleaned

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", values["email"]):
            raise ContactValidationError("Enter a valid email address.")
        if payload.get("website"):
            raise ContactValidationError("Unable to accept this submission.")

        return cls(**values)
