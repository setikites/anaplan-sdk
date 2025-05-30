from typing import Literal

import httpx

from anaplan_sdk._base import _AsyncBaseClient
from anaplan_sdk.models import User

Event = Literal["all", "byok", "user_activity"]


class _AsyncAuditClient(_AsyncBaseClient):
    def __init__(self, client: httpx.AsyncClient, retry_count: int) -> None:
        self._limit = 10_000
        self._url = "https://audit.anaplan.com/audit/api/1/events"
        super().__init__(retry_count, client)

    async def list_users(self, search_pattern: str | None = None) -> list[User]:
        """
        Lists all the Users in the authenticated users default tenant.
        :param search_pattern: Optionally filter for specific users. When provided,
               case-insensitive matches users with emails or names containing this string.
               You can use the wildcards `%` for 0-n characters, and `_` for exactly 1 character.
               When None (default), returns all users.
        :return: The List of Users.
        """
        params = {"s": search_pattern} if search_pattern else None
        return [
            User.model_validate(e)
            for e in await self._get_paginated(
                "https://api.anaplan.com/2/0/users", "users", params=params
            )
        ]

    async def get_user(self, user_id: str = "me") -> User:
        """
        Retrieves information about the specified user, or the authenticated user if none specified.
        :return: The requested or currently authenticated User.
        """
        return User.model_validate(
            (await self._get(f"https://api.anaplan.com/2/0/users/{user_id}")).get("user")
        )

    async def get_events(self, days_into_past: int = 30, event_type: Event = "all") -> list:
        """
        Get audit events from Anaplan Audit API.
        :param days_into_past: The nuber of days into the past to get events for. The API provides
               data for up to 30 days.
        :param event_type: The type of events to get.
        :return: A list of audit events.
        """
        return list(
            await self._get_paginated(
                self._url,
                "response",
                params={"type": event_type, "intervalInHours": days_into_past * 24},
            )
        )
