from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Phone(Base):
    __tablename__ = 'phone'

    id: Mapped[int] = mapped_column(primary_key=True)
    delo_id: Mapped[int] = mapped_column(ForeignKey('delo.id'))
    phone_number: Mapped[str] = mapped_column(String, nullable=False)


class Email(Base):
    __tablename__ = 'email'

    id: Mapped[int] = mapped_column(primary_key=True)
    delo_id: Mapped[int] = mapped_column(ForeignKey('delo.id'))
    email_address: Mapped[str] = mapped_column(String, nullable=False)


class Delo(Base):
    __tablename__ = 'delo'

    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String, nullable=False)
    birthdate: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    birthplace: Mapped[str] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=True)
    inn: Mapped[str] = mapped_column(String, nullable=True)
    snils: Mapped[str] = mapped_column(String, nullable=True)
    court_region: Mapped[str] = mapped_column(String, nullable=True)
    case_number: Mapped[str] = mapped_column(String, nullable=True)
    decision_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    publish_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    phones: Mapped[list[Phone]] = relationship('Phone', backref='delo', cascade='all, delete-orphan',
                                               lazy="selectin")
    emails: Mapped[list[Email]] = relationship('Email', backref='delo', cascade='all, delete-orphan',
                                               lazy="selectin")
