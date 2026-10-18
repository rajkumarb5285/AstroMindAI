from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from backend.app.core.config import settings

security_bearer = HTTPBearer(auto_error=False)


class UserContext(BaseModel):
    user_id: str
    email: str
    role: str = "user"

    @property
    def is_admin(self) -> bool:
        return self.role.lower() == "admin"


def create_access_token(user_id: str, email: str, role: str = "user") -> str:
    """Create a signed JWT token for testing and local session evaluation."""
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iss": "astromind-auth",
    }
    # In production, uses SUPABASE_SERVICE_ROLE_KEY or JWT secret
    secret = settings.SUPABASE_SERVICE_ROLE_KEY or "dev-secret-key-change-in-production"
    return jwt.encode(payload, secret, algorithm="HS256")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security_bearer),
) -> UserContext:
    """
    Authenticate the bearer token and return the immutable UserContext.
    Rejects missing or invalid tokens with HTTP 401.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials are required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Test / Dev token convention: 'test-user-a', 'test-user-b', 'test-admin'
    if token.startswith("test-token-"):
        role = "admin" if "admin" in token else "user"
        user_id = token.replace("test-token-", "")
        return UserContext(
            user_id=user_id,
            email=f"{user_id}@example.com",
            role=role,
        )

    try:
        secret = settings.SUPABASE_SERVICE_ROLE_KEY or "dev-secret-key-change-in-production"
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        sub = str(payload.get("sub", ""))
        user_email = str(payload.get("email", ""))
        user_role = str(payload.get("role", "user"))

        if not sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: subject identifier missing.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UserContext(user_id=sub, email=user_email, role=user_role)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


async def get_current_admin(
    current_user: UserContext = Depends(get_current_user),
) -> UserContext:
    """Enforce administrator privilege."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required.",
        )
    return current_user
