from enum import Enum
from typing import Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, NonNegativeFloat, validator


available_currencies = [
    "USD",
    "EUR",
    "JPY",
    "GBP",
    "AUD",
    "CAD",
    "CHF",
    "CNY",
    "SEK",
    "NZD",
]


def give_id():
    string_uuid = str(uuid4())
    return string_uuid.split("-")[0]


class Order(BaseModel):
    status: str = Literal["PENDING", "EXECUTED", "CANCELLED"]
    id: UUID = Field(default_factory=give_id)
    stocks: str = Field(..., min_length=6, max_length=6)
    quantity: NonNegativeFloat

    @validator("stocks")
    def check_currency_pair(value: str):
        value = value.upper()
        if (
            value[:3] not in available_currencies
            or value[3:] not in available_currencies
        ):
            raise ValueError("Invalid stock name")
        return value


def retrieve_order(order_id: str, order_list: list, delete: bool = False) -> dict:
    for id in range(len(order_list)):
        if order_list[id].id == order_id and order_list[id].status != "CANCELLED":
            if delete:
                order_list[id].status = "CANCELLED"
            return order_list[id]
