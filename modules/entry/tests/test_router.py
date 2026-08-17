from datetime import date, timedelta
from uuid import UUID

import pytest

from fastapi import status

from modules.entry.enums import EntryTypeEnum, PaymentMethodEnum
from modules.entry.repository import EntryRepository
from modules.entry.tests.fixtures.factories import EntryFactory


@pytest.mark.asyncio(loop_scope="session")
class TestEntryRouter:
    base_url = "/api/v1/entries/"

    async def test_create_entry_persists_entry_for_configured_user(self, client, db_session, user, monkeypatch):
        monkeypatch.setattr("modules.entry.router.HARDCODED_USER_ID", user.id)
        payload = {
            "amount": "10.50",
            "payment_method": "pix",
            "category": "Food",
            "description": "Lunch",
            "payment_date": date.today().isoformat(),
        }

        response = await client.post(self.base_url, json=payload)

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

    async def test_create_entry_rejects_future_payment_date(self, client):
        response = await client.post(
            self.base_url,
            json={
                "amount": "10.50",
                "payment_method": "pix",
                "category": "Food",
                "payment_date": (date.today() + timedelta(days=1)).isoformat(),
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert "payment_date cannot be in the future" in response.text

    async def test_create_from_telegram_persists_entry_for_authenticated_service_account(
        self,
        client,
        db_session,
        user,
        service_account_with_api_key,
    ):
        service_account, api_key = service_account_with_api_key
        payload = {
            "telegram_id": user.telegram_id,
            "amount": "10.50",
            "payment_method": "pix",
            "category": "Food",
            "description": "Lunch",
            "payment_date": date.today().isoformat(),
        }

        response = await client.post(
            f"{self.base_url}telegram",
            json=payload,
            headers={"X-API-KEY": api_key},
        )

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
        assert entries[0].created_by_service_account_id == service_account.id

    async def test_get_entries_returns_filtered_page(self, client, db_session, user, monkeypatch):
        monkeypatch.setattr("modules.entry.router.HARDCODED_USER_ID", user.id)
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
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 2
        assert response.json()["page"] == 1
        assert response.json()["size"] == 1
        assert response.json()["pages"] == 2
        assert [entry["id"] for entry in response.json()["items"]] == [str(newer_entry.id)]

    async def test_get_entries_accepts_no_filters(self, client, user, monkeypatch):
        monkeypatch.setattr("modules.entry.router.HARDCODED_USER_ID", user.id)

        response = await client.get(self.base_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["items"] == []
        assert response.json()["total"] == 0
