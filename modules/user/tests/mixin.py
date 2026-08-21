from typing import Any

from httpx import AsyncClient, Response

from modules.user.config import user_settings
from modules.user.models import UserModel
from modules.user.tokens import create_access_token


class AuthRequestMixin:
    base_url = ""

    def _generate_jwt(self, user: UserModel) -> str:
        return create_access_token(user, user_settings)

    async def auth_request(
        self,
        client: AsyncClient,
        user: UserModel | None,
        method: str,
        path: str | None = None,
        **kwargs: Any,
    ) -> Response:
        url = self.base_url if not path else f"{self.base_url}{path}"
        if "headers" not in kwargs:
            if user is None:
                raise ValueError("user is required when headers are not provided")
            kwargs["headers"] = {"Authorization": f"Bearer {self._generate_jwt(user)}"}

        return await client.request(
            method,
            url,
            **kwargs,
        )

    async def auth_get(
        self,
        client: AsyncClient,
        user: UserModel | None = None,
        path: str | None = None,
        **kwargs: Any,
    ) -> Response:
        return await self.auth_request(client, user, "GET", path, **kwargs)

    async def auth_post(
        self,
        client: AsyncClient,
        user: UserModel | None = None,
        path: str | None = None,
        **kwargs: Any,
    ) -> Response:
        return await self.auth_request(client, user, "POST", path, **kwargs)

    async def auth_patch(
        self,
        client: AsyncClient,
        user: UserModel | None = None,
        path: str | None = None,
        **kwargs: Any,
    ) -> Response:
        return await self.auth_request(client, user, "PATCH", path, **kwargs)
