"""One JSON error shape for every API error."""
from flask import jsonify
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    """An expected API error with an HTTP status and a stable error code."""
    def __init__(self, status: int, code: str, message: str, details: dict | None = None):
        """Store the status, code, message and optional details."""
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details or {}


def error_body(code: str, message: str, details: dict | None = None):
    """Build the one error shape: {"error": {code, message, details}}."""
    return {"error": {"code": code, "message": message, "details": details or {}}}


def register_error_handlers(app):
    """Make every error return the same JSON error shape."""
    @app.errorhandler(ApiError)
    def _api_error(err: ApiError):
        """Return an ApiError with its own status."""
        return jsonify(error_body(err.code, err.message, err.details)), err.status

    @app.errorhandler(ValidationError)
    def _validation_error(err: ValidationError):
        """Return 422 with a message for each invalid field."""
        fields = {".".join(str(p) for p in e["loc"]): e["msg"] for e in err.errors()}
        return jsonify(error_body("validation_error", "The request is not valid.", {"fields": fields})), 422

    @app.errorhandler(HTTPException)
    def _http_error(err: HTTPException):
        """Return Flask HTTP errors (404, 405) in the standard shape."""
        code = (err.name or "error").lower().replace(" ", "_")
        return jsonify(error_body(code, err.description or err.name)), err.code

    @app.errorhandler(Exception)
    def _unexpected(err: Exception):
        """Log the error and return 500 without internal details."""
        app.logger.exception("Unexpected error")
        return jsonify(error_body("internal_error", "An unexpected error occurred. Try again.")), 500
