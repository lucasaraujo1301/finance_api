from decimal import Decimal
from typing import Annotated

from pydantic import Field, PlainSerializer

Money = Annotated[
    Decimal,
    Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
        examples=["4410.96"],
    ),
    PlainSerializer(
        lambda value: str(value),
        return_type=str,
        when_used="json",
    ),
]

Balance = Annotated[
    Decimal,
    Field(max_digits=12, decimal_places=2, examples=["150.00"]),
    PlainSerializer(
        lambda value: str(value),
        return_type=str,
        when_used="json",
    ),
]
