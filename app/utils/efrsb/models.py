from pydantic import BaseModel, Field, TypeAdapter
from datetime import datetime


class ObjectEFRSB(BaseModel):
    efrsb_id: int | None
    arbitr_manager_id: int | None = Field(alias='ArbitrManagerID')
    bankrupt_id: int | None = Field(alias='BankruptId')
    inn: str | None = Field(alias='INN')
    snils: str | None = Field(alias='SNILS')
    ogrn: str | None = Field(alias='OGRN')
    publish_date: datetime | None = Field(alias='PublishDate')
    body: str | None = Field(alias='Body')
    message_info_message_type: str | None = Field(alias='MessageInfo_MessageType')
    number: str | None = Field(alias='Number')
    message_guid: str | None = Field(alias='MessageGUID')
    revision: int | None = Field(alias='Revision')


ObjectEFRSBListAdapter = TypeAdapter(list[ObjectEFRSB])


# import xml.etree.ElementTree as ET
#
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
# from app.data.config import DB_NAME
#
# from typing import Optional
# from datetime import datetime
# from sqlalchemy import select
# from sqlalchemy.orm import Session
# from app.database.models import Delo
#
#
# class SyncDatabase:
#     def __init__(self, session: Session):
#         self.session = session
#
#     def get_all_efrsb(self) -> list[Delo]:
#         """Получить все дела из ЕФРСБ (синхронная версия)"""
#         result = self.session.scalars(select(Delo).order_by(Delo.id))
#         return list(result.all())
#
#     def add_delo_efrsb(
#             self,
#             revision: int,
#             fullname: Optional[str],
#             birthdate: datetime,
#             birthplace: str,
#             address: str,
#             inn: str,
#             snils: str,
#             court_region: str,
#             case_number: str,
#             decision_date: datetime,
#             publish_date: datetime
#     ) -> Delo:
#         """
#         Добавить новое дело в ЕФРСБ (синхронная версия)
#
#         Возвращает созданный объект Delo
#         """
#         delo = Delo(
#             id=revision,
#             fullname=fullname,
#             birthdate=birthdate,
#             birthplace=birthplace,
#             address=address,
#             inn=inn,
#             snils=snils,
#             court_region=court_region,
#             case_number=case_number,
#             decision_date=decision_date,
#             publish_date=publish_date
#         )
#
#         self.session.add(delo)
#         self.session.commit()
#         self.session.refresh(delo)  # Обновляем объект из БД
#         return delo
#
#     def get_delo_by_id(self, revision: int) -> Optional[Delo]:
#         """Получить дело по ID (синхронная версия)"""
#         return self.session.get(Delo, revision)
#
#
#
# def append_date_value(db: SyncDatabase, revision, fullname, birthdate, birthplace, address, inn, snils, court_region,
#                              case_number, decision_date, publish_date):
#     birthdate = datetime.strptime(birthdate, '%d.%m.%Y') if birthdate else None
#     decision_date = datetime.strptime(decision_date, '%Y-%m-%d') if decision_date else None
#     db.add_delo_efrsb(revision=revision, fullname=fullname, birthdate=birthdate, birthplace=birthplace,
#                             address=address, inn=inn, snils=snils, court_region=court_region, case_number=case_number,
#                             decision_date=decision_date, publish_date=publish_date)
#
# file_path = 'temp_fie.json'
# with open("/home/anton/projects/bankruptcy/new.json", 'r') as f:
#     res = ObjectEFRSBListAdapter.validate_json(f.read())
# print(len(res))
# engine = create_engine(f'sqlite:///{DB_NAME}')
# SessionLocal = sessionmaker(bind=engine)
# with SessionLocal() as session:
#     db = SyncDatabase(session=session)
# all_objts = []
# for obj in res:
#     root = ET.fromstring(obj.body)
#     print('-' * 50)
#     # Общие данные по банкроту
#     bankrupt = root.find('.//BankruptPerson')
#     fio = bankrupt
#     if bankrupt is None:
#         bankrupt = root.find('.//Bankrupt')
#         if bankrupt is None:
#             continue
#         fio = bankrupt.find(".//Fio")
#         if fio is None:
#             continue
#     # ФИО
#     first_name = fio.findtext('FirstName', default='') if fio is not None else ''
#     middle_name = fio.findtext('MiddleName', default='') if fio is not None else ''
#     last_name = fio.findtext('LastName', default='') if fio is not None else ''
#     full_name = f"{last_name} {first_name} {middle_name}".strip()
#     print(full_name)
#     print(bankrupt.findtext('Birthdate', default=''))
#     print(bankrupt.get('Birthdate', default=''))
#
#     # ФИО
#     first_name = bankrupt.get('FirstName', '')
#     middle_name = bankrupt.get('MiddleName', '')
#     last_name = bankrupt.get('LastName', '')
#     full_name = f"{last_name} {first_name} {middle_name}".strip()
#     birthdate = bankrupt.findtext('Birthdate', default='')
#     birthplace = bankrupt.findtext('Birthplace', default='')
#     address = bankrupt.get('Address', '')  # Место жительства
#     inn = bankrupt.findtext('INN', default='')
#     snils = bankrupt.findtext('SNILS', default='')
#
#     # Информация о сообщении
#     message_info = root.find('MessageInfo')
#     if message_info is None:
#         continue
#     message_type = message_info.get('MessageType', '')
#
#
#     # 1) Сообщение о судебном акте
#     if message_type == 'ArbitralDecree':
#         court_decision = message_info.find('CourtDecision')
#         if court_decision is None:
#             continue
#         # Проверяем наличие ключа CitizenNotReleasedFromResponsibility xsi:nil="true"
#         # для освобождения должника
#         citizen_not_released = court_decision.find('CitizenNotReleasedFromResponsibility')
#         if citizen_not_released is None or citizen_not_released.get(
#                 '{http://www.w3.org/2001/XMLSchema-instance}nil') != 'true':
#             # Ключ отсутствует или не равен true - не парсим
#             continue
#         # Название судебного акта
#         decision_type = court_decision.find('DecisionType')
#         decree_name = decision_type.get('Name') if decision_type is not None else ''
#
#         # Регион суда и номер дела
#         court_decree = court_decision.find('CourtDecree')
#         court_name = court_decree.findtext('CourtName', default='') if court_decree is not None else ''
#         file_number = court_decree.findtext('FileNumber',
#                                             default='') if court_decree is not None else ''
#         decision_date = court_decree.findtext('DecisionDate',
#                                               default='') if court_decree is not None else ''
#         if decree_name == 'о завершении реализации имущества гражданина':
#             court_decision = message_info.find('CourtDecision')
#             court_decree = court_decision.find('CourtDecree') if court_decision is not None else None
#             decision_date = court_decree.findtext('DecisionDate', default='') if court_decree is not None else ''
#
#             obj_info = {
#                 'type_message': 'Сообщение о завершении процедуры внесудебного банкротства гражданина',
#                 'full_name': full_name,
#                 'birthdate': birthdate,
#                 'birthplace': birthplace,
#                 'address': address,
#                 'inn': inn,
#                 'snils': snils,
#                 'court_region': 'ВБФЛ',
#                 'case_number': 'ВБФЛ',
#                 'decision_date': decision_date
#             }
#         else:
#             obj_info = {
#                 'type_message': 'Сообщение о судебном Акте',
#                 'court_decree_name': decree_name,
#                 'full_name': full_name,
#                 'birthdate': birthdate,
#                 'birthplace': birthplace,
#                 'address': address,
#                 'inn': inn,
#                 'snils': snils,
#                 'court_region': court_name,
#                 'case_number': file_number,
#                 'decision_date': decision_date
#             }
#         append_date_value(db=db, revision=obj.revision, fullname=full_name, birthdate=birthdate,
#                                 birthplace=birthplace, address=address, inn=inn, snils=snils,
#                                 court_region=court_name, case_number=file_number, decision_date=decision_date,
#                                 publish_date=obj.publish_date)
#         all_objts.append(obj_info)
#     # Если другой тип сообщения — игнорируем
#     continue
# # print(all_objts)
# print(True)
