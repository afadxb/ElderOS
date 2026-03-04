from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, detail: str = "Resource not found") -> None:
        self.detail = detail
        super().__init__(self.detail)


class ConflictError(Exception):
    """Raised when a request conflicts with the current state of a resource."""

    def __init__(self, detail: str = "Resource conflict") -> None:
        self.detail = detail
        super().__init__(self.detail)


class ForbiddenError(Exception):
    """Raised when the authenticated user lacks permission for the operation."""

    def __init__(self, detail: str = "Forbidden") -> None:
        self.detail = detail
        super().__init__(self.detail)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI application instance."""

    @app.exception_handler(NotFoundError)
    async def _not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.detail})

    @app.exception_handler(ConflictError)
    async def _conflict_handler(_request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": exc.detail})

    @app.exception_handler(ForbiddenError)
    async def _forbidden_handler(_request: Request, exc: ForbiddenError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": exc.detail})
