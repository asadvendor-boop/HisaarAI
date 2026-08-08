"""Route-specific Google token verification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from fastapi import Header, HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token


VALID_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}


@dataclass(frozen=True)
class AuthenticatedCaller:
    subject: str
    email: str | None
    audience: str


def _bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A Google bearer ID token is required",
        )
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is empty",
        )
    return token


def verify_google_token(
    token: str,
    *,
    audience: str,
    expected_subject: str | None = None,
    expected_email: str | None = None,
) -> AuthenticatedCaller:
    try:
        claims = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=audience,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google ID token verification failed",
        ) from exc

    if claims.get("iss") not in VALID_ISSUERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google ID token issuer is invalid",
        )
    subject = str(claims.get("sub", ""))
    email = claims.get("email")
    if expected_subject and subject != expected_subject:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Caller subject is not authorized for this route",
        )
    if expected_email and email != expected_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Caller service account is not authorized for this route",
        )
    if expected_email and claims.get("email_verified") is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Caller service-account email is not verified",
        )
    return AuthenticatedCaller(subject=subject, email=email, audience=audience)


def require_google_caller(
    *,
    audience: str,
    expected_subject: str | None = None,
    expected_email: str | None = None,
) -> Callable[..., AuthenticatedCaller]:
    def dependency(
        authorization: str | None = Header(default=None),
    ) -> AuthenticatedCaller:
        return verify_google_token(
            _bearer_token(authorization),
            audience=audience,
            expected_subject=expected_subject,
            expected_email=expected_email,
        )

    return dependency

