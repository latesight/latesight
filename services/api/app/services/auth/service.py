from typing import Optional

from app.schemas.auth import LoginRequest, LoginResponse, UserProfile

DEV_ACCESS_TOKEN = "dev-token"


def _build_dev_user(email: str = "admin@latesight.com") -> UserProfile:
    return UserProfile(
        id=1,
        email=email,
        full_name="System Admin",
        roles=["super_admin"],
    )


async def authenticate_user(payload: LoginRequest) -> Optional[LoginResponse]:
    if payload.email != "admin@latesight.com" or payload.password != "change-me-123":
        return None

    user = _build_dev_user(payload.email)
    return LoginResponse(access_token=DEV_ACCESS_TOKEN, user=user)


async def get_current_user() -> UserProfile:
    return _build_dev_user()


async def get_user_for_access_token(access_token: str | None) -> Optional[UserProfile]:
    if access_token != DEV_ACCESS_TOKEN:
        return None
    return _build_dev_user()
