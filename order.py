from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, NonNegativeFloat, validator


available_currencies = ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY", "SEK", "NZD"]


def give_id():
  string_uuid = str(uuid4())
  return string_uuid.split('-')[0]

class StatusEnum(Enum):
  pending = 0
  executed = 1
  canceled = 2

  
@validator("stocks")
def check_currency_pair(cls, value):    
    if value[:3] not in available_currencies or value[3:] not in available_currencies:
        raise ValueError("Invalid stock name")
    return value

class Order(BaseModel):
  status: StatusEnum = StatusEnum.pending
  id: UUID = Field(default_factory=give_id)
  stocks: str = Field(..., min_length=6, max_length=6)
  quantity: NonNegativeFloat






