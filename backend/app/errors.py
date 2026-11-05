"""One JSON error shape for every API error."""
from flask import jsonify
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details or {}


def error_body(code: str, message: str, details: dict | None = None):
    return {"error": {"code": code, "message": message, "details": details or {}}}


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def _api_error(err: ApiError):
        return jsonify(error_body(err.code, err.message, err.details)), err.status

    @app.errorhandler(ValidationError)
    def _validation_error(err: ValidationError):
        fields = {".".join(str(p) for p in e["loc"]): e["msg"] for e in err.errors()}
        return jsonify(error_body("validation_error", "The request is not valid.", {"fields": fields})), 422

    @app.errorhandler(HTTPException)
    def _http_error(err: HTTPException):
        code = (err.name or "error").lower().replace(" ", "_")
        return jsonify(error_body(code, err.description or err.name)), err.code

    @app.errorhandler(Exception)
    def _unexpected(err: Exception):
        app.logger.exception("Unexpected error")
        return jsonify(error_body("internal_error", "An unexpected error occurred. Try again.")), 500
