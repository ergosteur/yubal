"""Cookies schemas."""

from pydantic import BaseModel


class CookiesStatusResponse(BaseModel):
    """Cookies status response model."""

    configured: bool


class CookiesUploadRequest(BaseModel):
    """Cookies upload request model."""

    content: str


class CookiesUploadResponse(BaseModel):
    """Cookies upload response model."""

    status: str
