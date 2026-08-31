from datetime import date, timedelta
from uuid import UUID

import pytest

from fastapi import status

from modules.finance.enums import EntryTypeEnum, PaymentMethodEnum
from modules.finance.repository import EntryRepository
from modules.finance.tests.fixtures.factories import EntryFactory
from modules.user.exceptions import InvalidCredentials
from modules.user.tests.mixin import AuthRequestMixin


@pytest.mark.asyncio(loop_scope="session")
class TestEntryRouter(AuthRequestMixin):
    base_url = "/api/v1/entries"

    async def test_create_entry_persists_entry_for_configured_user(self, client, db_session, user):
        payload = {
            "amount": "10.50",
            "payment_method": "pix",
            "category": "snack",
            "description": "Lunch",
            "payment_date": date.today().isoformat(),
        }

        response = await self.auth_post(client, user, path="/", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["success"] is True
        assert response.json()["data"] == {
            "id": str(UUID(response.json()["data"]["id"])),
            "amount": "10.50",
            "entry_type": EntryTypeEnum.DEBIT.label,
            "payment_method": PaymentMethodEnum.PIX.label,
            "category": "snack",
            "description": "Lunch",
            "payment_date": payload["payment_date"],
            "created_at": response.json()["data"]["created_at"],
            "updated_at": None,
            "deleted_at": None,
        }

        entries = await EntryRepository(db_session).get_by_user_id(user.id)
        assert len(entries) == 1
        assert entries[0].id == UUID(response.json()["data"]["id"])
        assert entries[0].user_id == user.id

    async def test_create_entry_rejects_future_payment_date(self, client, user):
        response = await self.auth_post(
            client,
            user,
            path="/",
            json={
                "amount": "10.50",
                "payment_method": "pix",
                "category": "snack",
                "payment_date": (date.today() + timedelta(days=1)).isoformat(),
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["success"] is False
        assert response.json()["errors"]["detail"] == [
            {
                "loc": "payment_date",
                "msg": "Value error, payment_date cannot be in the future",
                "type": "value_error",
            }
        ]

    async def test_create_entry_accepts_null_description(self, client, user):
        response = await self.auth_post(
            client,
            user,
            path="/",
            json={
                "amount": "4410.96",
                "payment_method": "account_transfer",
                "category": "other",
                "entry_type": "credit",
                "description": None,
                "payment_date": "2012-01-25",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["description"] is None

    async def test_create_entry_requires_jwt(self, client):
        response = await self.auth_post(
            client,
            path="/",
            headers=None,
            json={
                "amount": "10.50",
                "payment_method": "pix",
                "category": "snack",
                "payment_date": date.today().isoformat(),
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["success"] is False
        assert response.json()["errors"]["message"] == InvalidCredentials.message

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
            "category": "snack",
            "description": "Lunch",
            "payment_date": date.today().isoformat(),
        }

        response = await self.auth_post(
            client,
            path="/telegram",
            json=payload,
            headers={"X-API-KEY": api_key},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["success"] is True
        assert response.json()["data"] == {
            "id": str(UUID(response.json()["data"]["id"])),
            "amount": "10.50",
            "entry_type": EntryTypeEnum.DEBIT.label,
            "payment_method": PaymentMethodEnum.PIX.label,
            "category": "snack",
            "description": "Lunch",
            "payment_date": payload["payment_date"],
            "created_at": response.json()["data"]["created_at"],
            "updated_at": None,
            "deleted_at": None,
        }

        entries = await EntryRepository(db_session).get_by_user_id(user.id)
        assert len(entries) == 1
        assert entries[0].id == UUID(response.json()["data"]["id"])
        assert entries[0].user_id == user.id
        assert entries[0].created_by_service_account_id == service_account.id

    async def test_get_entries_returns_filtered_page(self, client, db_session, user):
        EntryFactory.__async_session__ = db_session
        today = date.today()
        await EntryFactory.create_async(
            user_id=user.id,
            payment_date=today - timedelta(days=2),
            category="snack",
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        newer_entry = await EntryFactory.create_async(
            user_id=user.id,
            payment_date=today - timedelta(days=1),
            category="snack",
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        await EntryFactory.create_async(
            user_id=user.id,
            payment_date=today - timedelta(days=1),
            category="transport",
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )

        response = await self.auth_get(
            client,
            user,
            path="/",
            params={
                "page": 1,
                "size": 1,
                "start_date": (today - timedelta(days=3)).isoformat(),
                "end_date": today.isoformat(),
                "category": "snack",
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

    async def test_get_entries_accepts_no_filters(self, client, user):
        response = await self.auth_get(
            client,
            user,
            path="/",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["items"] == []
        assert response.json()["total"] == 0

    async def test_get_entries_rejects_invalid_date_range(self, client, user):
        today = date.today()

        response = await self.auth_get(
            client,
            user,
            path="/",
            params={"start_date": today.isoformat(), "end_date": today.isoformat()},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["errors"]["detail"][0]["msg"] == "Value error, end_date must be after start_date"

    async def test_get_entries_summary_returns_analytics(self, client, db_session, user):
        EntryFactory.__async_session__ = db_session
        await EntryFactory.create_async(
            user_id=user.id,
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        await EntryFactory.create_async(
            user_id=user.id,
            entry_type=EntryTypeEnum.CREDIT,
            payment_method=PaymentMethodEnum.CASH,
        )

        response = await self.auth_get(client, user, path="/summary")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True
        assert response.json()["data"]["by_entry_type"] == {"debit": 1, "credit": 1}
        assert response.json()["data"]["by_payment_method"] == {
            "debit_card": 0,
            "credit_card": 0,
            "pix": 1,
            "cash": 1,
            "account_transfer": 0,
        }
        assert response.json()["data"]["last_balance"] is None
        assert response.json()["data"]["current_balance"] == "0.00"
        assert response.json()["data"]["balance"] == "0.00"

    async def test_get_entries_summary_ignores_entry_filters(self, client, db_session, user):
        EntryFactory.__async_session__ = db_session
        await EntryFactory.create_async(user_id=user.id, category="other", entry_type=EntryTypeEnum.CREDIT)
        await EntryFactory.create_async(user_id=user.id, category="snack", entry_type=EntryTypeEnum.DEBIT)

        response = await self.auth_get(
            client,
            user,
            path="/summary",
            params={"category": "snack", "entry_type": "debit", "payment_method": "pix"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["by_entry_type"] == {"debit": 1, "credit": 1}
