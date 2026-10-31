"""Uniform JSON errors: {"error": {"code": "...", "message": "..."}}. Never a stack trace."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApiError(Exception):
    """Raise from an endpoint to return a JSON error with a plain-language message."""

    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


_HTTP_MESSAGES = {
    404: ("not_found", "There is nothing at this address."),
    405: ("method_not_allowed", "This action is not allowed at this address."),
}


def error_response(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse({"error": {"code": code, "message": message}}, status_code=status)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError):
        return error_response(exc.status, exc.code, exc.message)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request: Request, exc: StarletteHTTPException):
        code, message = _HTTP_MESSAGES.get(exc.status_code, ("http_error", "The request could not be completed."))
        response = error_response(exc.status_code, code, message)
        if exc.headers:
            response.headers.update(exc.headers)  # for example "Allow" on 405
        return response

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        # The submitted values are not echoed back: they could contain secrets.
        return error_response(422, "invalid_request", "The request data is not valid.")
