from datetime import date, timedelta
from uuid import UUID

import pytest

from fastapi import status

from modules.entry.enums import EntryTypeEnum, PaymentMethodEnum
from modules.entry.repository import EntryRepository
from modules.entry.tests.fixtures.factories import EntryFactory
from modules.user.models import UserModel


@pytest.mark.asyncio(loop_scope="session")
class TestEntryRouter:
    base_url = "/api/v1/entries/"

    async def test_create_entry_persists_authenticated_user_entry(self, client, db_session, user_with_api_key):
        user, raw_api_key = user_with_api_key
        payload = {
            "amount": "10.50",
            "payment_method": "pix",
            "category": "Food",
            "description": "Lunch",
            "payment_date": date.today().isoformat(),
        }

        response = await client.post(self.base_url, json=payload, headers={"X-API-KEY": raw_api_key})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "id": str(UUID(response.json()["id"])),
            "amount": "10.50",
            "entry_type": EntryTypeEnum.DEBIT.label,
            "payment_method": PaymentMethodEnum.PIX.label,
            "category": "Food",
            "description": "Lunch",
            "payment_date": payload["payment_date"],
            "is_fixed": False,
            "created_at": response.json()["created_at"],
            "updated_at": None,
            "deleted_at": None,
        }

        entries = await EntryRepository(db_session).get_by_user_id(user.id)
        assert len(entries) == 1
        assert entries[0].id == UUID(response.json()["id"])
        assert entries[0].user_id == user.id

    async def test_create_entry_requires_api_key(self, client):
        response = await client.post(
            self.base_url,
            json={"amount": "10.50", "payment_method": "pix", "category": "Food"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["error"]["message"] == "ApiKey missing from headers"

    async def test_create_entry_rejects_future_payment_date(self, client, user_with_api_key: tuple[UserModel, str]):
        _, raw_api_key = user_with_api_key

        response = await client.post(
            self.base_url,
            json={
                "amount": "10.50",
                "payment_method": "pix",
                "category": "Food",
                "payment_date": (date.today() + timedelta(days=1)).isoformat(),
            },
            headers={"X-API-KEY": raw_api_key},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert "payment_date cannot be in the future" in response.text

    async def test_get_entries_returns_filtered_page(self, client, db_session, user_with_api_key):
        user, raw_api_key = user_with_api_key
        EntryFactory.__async_session__ = db_session
        today = date.today()
        await EntryFactory.create_async(
            user=user,
            payment_date=today - timedelta(days=2),
            category="food",
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        newer_entry = await EntryFactory.create_async(
            user=user,
            payment_date=today - timedelta(days=1),
            category="food",
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        await EntryFactory.create_async(
            user=user,
            payment_date=today - timedelta(days=1),
            category="transport",
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )

        response = await client.get(
            self.base_url,
            params={
                "page": 1,
                "size": 1,
                "start_date": (today - timedelta(days=3)).isoformat(),
                "end_date": today.isoformat(),
                "category": "food",
                "entry_type": "debit",
                "payment_method": "pix",
            },
            headers={"X-API-KEY": raw_api_key},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 2
        assert response.json()["page"] == 1
        assert response.json()["size"] == 1
        assert response.json()["pages"] == 2
        assert [entry["id"] for entry in response.json()["items"]] == [str(newer_entry.id)]

    async def test_get_entries_accepts_no_filters(self, client, user_with_api_key):
        _, raw_api_key = user_with_api_key

        response = await client.get(self.base_url, headers={"X-API-KEY": raw_api_key})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["items"] == []
        assert response.json()["total"] == 0
