from typing import Annotated

from pydantic import PlainSerializer

from modules.entry.enums import EntryTypeEnum, PaymentMethodEnum

EntryType = Annotated[
    EntryTypeEnum,
    PlainSerializer(
        lambda value: value.value.title(),
        return_type=str,
        when_used="json",
    ),
]

PaymentMethod = Annotated[
    PaymentMethodEnum,
    PlainSerializer(
        lambda value: value.value.replace("_", " ").title(),
        return_type=str,
        when_used="json",
    ),
]
