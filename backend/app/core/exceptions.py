from fastapi import Request, status
from fastapi.responses import JSONResponse


class LedgrError(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "ledgr_error"
    default_message: str = "Something went wrong"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(LedgrError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    default_message = "Resource not found"


class AuthError(LedgrError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"
    default_message = "Missing or invalid credentials"


class ConflictError(LedgrError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"
    default_message = "Request conflicts with the current state"


class InvalidStateError(LedgrError):
    status_code = status.HTTP_409_CONFLICT
    code = "invalid_state"
    default_message = "Resource is not in a state that allows this operation"


class ValidationError(LedgrError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "validation_error"
    default_message = "Request is semantically invalid"


async def ledgr_error_handler(request: Request, exc: LedgrError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


def register_exception_handlers(app) -> None:
    app.add_exception_handler(LedgrError, ledgr_error_handler)
