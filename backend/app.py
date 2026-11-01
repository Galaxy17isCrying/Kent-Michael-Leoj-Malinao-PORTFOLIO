import logging
import time
from pathlib import Path
from flask import Flask, current_app, jsonify, request, send_from_directory
from werkzeug.exceptions import BadRequest, HTTPException

from backend.config import PROJECT_ROOT, Settings
from backend.database import MySQLDatabase
from backend.models import ContactValidationError
from backend.repositories import ContactRepository
from backend.services import ContactRateLimiter, ContactService


def create_app() -> Flask:
    application = Flask(__name__)
    settings = Settings()
    application.config["MAX_CONTENT_LENGTH"] = 16 * 1024
    application.config["CONTACT_SERVICE"] = ContactService(
        ContactRepository(MySQLDatabase(settings))
    )
    application.extensions["contact_rate_limiter"] = ContactRateLimiter(
        max_requests=5,
        window_seconds=60 * 60,
    )
    application.logger.setLevel(logging.INFO)

    @application.get("/")
    def home():
        return send_from_directory(PROJECT_ROOT, "index.html")

    @application.get("/styles.css")
    def styles():
        return send_from_directory(PROJECT_ROOT, "styles.css")

    @application.get("/script.js")
    def scripts():
        return send_from_directory(PROJECT_ROOT, "script.js")

    @application.get("/assets/<path:filename>")
    def assets(filename: str):
        return send_from_directory(Path(PROJECT_ROOT) / "assets", filename)

    @application.get("/api/health")
    def health():
        return jsonify({"ok": True, "service": "portfolio-api"})

    @application.post("/api/contact")
    def create_contact():
        allowed, retry_after = current_app.extensions["contact_rate_limiter"].check(
            request.remote_addr or "unknown",
            time.monotonic(),
        )
        if not allowed:
            response = jsonify(
                {"ok": False, "error": "Too many messages. Please try again later."}
            )
            response.status_code = 429
            response.headers["Retry-After"] = str(retry_after)
            return response

        if not request.is_json:
            return jsonify({"ok": False, "error": "Send your message as JSON."}), 400

        try:
            payload = request.get_json()
        except BadRequest:
            return jsonify({"ok": False, "error": "Send a valid JSON request."}), 400

        try:
            contact_id = current_app.config["CONTACT_SERVICE"].submit(payload)
        except ContactValidationError as error:
            return jsonify({"ok": False, "error": str(error)}), 400
        except Exception:
            current_app.logger.exception("Unable to save a portfolio contact message.")
            return (
                jsonify(
                    {
                        "ok": False,
                        "error": "Messages are temporarily unavailable. Please try again later.",
                    }
                ),
                503,
            )

        return jsonify({"ok": True, "id": contact_id}), 201

    @application.errorhandler(413)
    def request_too_large(_error):
        return jsonify({"ok": False, "error": "The request is too large."}), 413

    @application.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        if request.path.startswith("/api/"):
            return jsonify({"ok": False, "error": error.description}), error.code
        return error

    return application


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
