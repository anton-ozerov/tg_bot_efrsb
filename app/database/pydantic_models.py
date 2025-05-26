from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PhoneOut(BaseModel):
    phone_number: str

    class Config:
        from_attributes = True


class EmailOut(BaseModel):
    email_address: str

    class Config:
        from_attributes = True


class DeloOut(BaseModel):
    id: int
    fullname: str
    birthdate: Optional[datetime]
    birthplace: Optional[str]
    address: Optional[str]
    inn: Optional[str]
    snils: Optional[str]
    court_region: Optional[str]
    case_number: Optional[str]
    decision_date: Optional[datetime]
    publish_date: Optional[datetime]
    phones: Optional[list[PhoneOut]] = []
    emails: Optional[list[EmailOut]] = []

    class Config:
        from_attributes = True
