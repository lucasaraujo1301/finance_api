from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from modules.user.config import UserSettings


def create_access_token(
    user_id: UUID,
    settings: UserSettings,
    token_type: str = "access",
    expires_delta: timedelta | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    expires_delta = expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {
            "sub": str(user_id),
            "type": token_type,
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "iat": now,
            "exp": now + expires_delta,
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
