from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Delo, Phone, Email
from app.database.pydantic_models import DeloOut


class Database:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_efrsb(self) -> list[DeloOut]:
        query = select(Delo).options(selectinload(Delo.phones), selectinload(Delo.emails))
        dela = await self.session.scalars(query)
        return [DeloOut.model_validate(d, from_attributes=True) for d in dela.all()]


    async def get_delo_by_publish_date_range(self, date_1: datetime, date_2: datetime) -> list[DeloOut]:
        date_2 += timedelta(days=1)
        query = (
            select(Delo)
            .where(Delo.publish_date >= date_1, Delo.publish_date <= date_2)
            .options(
                selectinload(Delo.phones),
                selectinload(Delo.emails)
            )
        )
        result = await self.session.execute(query)
        dela = result.scalars().all()
        return [DeloOut.model_validate(d, from_attributes=True) for d in dela]


    async def add_delo_efrsb(self, revision, fullname, birthdate, birthplace, address, inn, snils, court_region,
                             case_number, decision_date, publish_date):
        delo = await self.session.get(Delo, revision)
        if not delo:
            delo = Delo(
                id=revision, fullname=fullname, birthdate=birthdate, birthplace=birthplace, address=address, inn=inn, snils=snils,
                court_region=court_region, case_number=case_number, decision_date=decision_date, publish_date=publish_date
            )
            self.session.add(delo)
        await self.session.commit()

    async def add_phone_to_delo(self, delo_id: int, phone_number: str):
        delo = await self.session.get(Delo, delo_id)
        if not delo:
            raise ValueError("Delo not found")

        # Проверка, есть ли уже такой номер для этого дела
        existing_phone_query = select(Phone).where(
            Phone.phone_number == phone_number,
            Phone.delo_id == delo_id
        )
        result = await self.session.execute(existing_phone_query)
        existing_phone = result.scalar_one_or_none()

        if existing_phone:
            return existing_phone  # или просто return None, если не хочешь возвращать

        # Добавление нового
        phone = Phone(phone_number=phone_number, delo=delo)
        self.session.add(phone)
        await self.session.commit()
        return phone

    async def add_email_to_delo(self, delo_id: int, email_address: str):
        delo = await self.session.get(Delo, delo_id)
        if not delo:
            raise ValueError("Delo not found")

        existing_email_query = select(Email).where(
            Email.email_address == email_address,
            Email.delo_id == delo_id
        )
        result = await self.session.execute(existing_email_query)
        existing_email = result.scalar_one_or_none()

        if existing_email:
            return existing_email

        email = Email(email_address=email_address, delo=delo)
        self.session.add(email)
        await self.session.commit()
        return email
