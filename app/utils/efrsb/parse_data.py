import logging
import xml.etree.ElementTree
import xml.etree.ElementTree as ET
from datetime import datetime

import aiohttp

from app.data.config import EFRSB_TOKEN
from app.database.requests import Database
from app.utils.efrsb.models import ObjectEFRSBListAdapter
from app.utils.generate_xlsx import generate_new_xlsx

logger = logging.getLogger(__name__)


async def get_needed_info(data: ObjectEFRSBListAdapter, db: Database) -> list[dict]:
    all_objts = []
    for obj in data:
        try:
            root = ET.fromstring(obj.body)
        except xml.etree.ElementTree.ParseError:
            await append_delo_db(db=db, revision=obj.revision, publish_date=obj.publish_date, fullname='incorrect')
            continue
        except Exception as e:
            await append_delo_db(db=db, revision=obj.revision, publish_date=obj.publish_date, fullname='incorrect')
            continue
        # Общие данные по банкроту
        bankrupt = root.find('.//BankruptPerson')
        fio = bankrupt
        if bankrupt is None:
            bankrupt = root.find('.//Bankrupt')
            if bankrupt is None:
                await append_delo_db(db=db, revision=obj.revision, publish_date=obj.publish_date, fullname='incorrect')
                continue
            fio = bankrupt.find(".//Fio")
            if fio is None:
                await append_delo_db(db=db, revision=obj.revision, publish_date=obj.publish_date, fullname='incorrect')
                continue
        # ФИО
        first_name = fio.findtext('FirstName', default='') if fio is not None else ''
        middle_name = fio.findtext('MiddleName', default='') if fio is not None else ''
        last_name = fio.findtext('LastName', default='') if fio is not None else ''
        full_name = f"{last_name} {first_name} {middle_name}".strip()

        birthdate = bankrupt.findtext('Birthdate', default='')
        birthplace = bankrupt.findtext('Birthplace', default='')
        address = bankrupt.findtext("Address", "")  # Место жительства
        inn = bankrupt.findtext("Inn", "")
        snils = bankrupt.findtext("Snils", "")
        # Информация о сообщении
        message_info = root.find('MessageInfo')
        if message_info is None:
            court_name = 'incorrect'
            case_number = 'incorrect'
            decision_date = None
            await append_delo_db(db=db, revision=obj.revision, fullname=full_name, birthdate=birthdate,
                                 birthplace=birthplace, address=address, inn=inn, snils=snils,
                                 court_region=court_name, case_number=case_number, decision_date=decision_date,
                                 publish_date=obj.publish_date)
            continue
        message_type = message_info.attrib.get('MessageType', '')

        # 1) Сообщение о судебном акте
        if message_type == 'ArbitralDecree':
            court_decision = message_info.find('CourtDecision')
            if court_decision is None:
                continue
            # Проверяем наличие ключа CitizenNotReleasedFromResponsibility xsi:nil="true"
            # для освобождения должника
            citizen_not_released = court_decision.find('CitizenNotReleasedFromResponsibility')
            if citizen_not_released is None or citizen_not_released.get(
                    '{http://www.w3.org/2001/XMLSchema-instance}nil') != 'true':
                # Ключ отсутствует или не равен true - не парсим
                court_name = 'incorrect'
                case_number = 'incorrect'
                decision_date = None
                await append_delo_db(db=db, revision=obj.revision, fullname=full_name, birthdate=birthdate,
                                     birthplace=birthplace, address=address, inn=inn, snils=snils,
                                     court_region=court_name, case_number=case_number, decision_date=decision_date,
                                     publish_date=obj.publish_date)
                continue
            # Название судебного акта
            decision_type = court_decision.find('DecisionType')
            decree_name = decision_type.attrib.get('Name') if decision_type is not None else ''

            # Регион суда и номер дела
            court_decree = court_decision.find('CourtDecree')
            court_name = court_decree.findtext('CourtName', default='') if court_decree is not None else ''

            # Судебное дело
            case_number = root.findtext(".//CaseNumber", "").strip()
            decision_date = court_decree.findtext('DecisionDate',
                                                  default='') if court_decree is not None else ''

            if decree_name == 'о завершении реализации имущества гражданина':
                type_message = 'Сообщение о завершении реализации имущества гражданина'
            else:
                type_message = None
                court_name = 'incorrect'
                case_number = 'incorrect'
                decision_date = None
        elif message_type == 'CompletionOfExtrajudicialBankruptcy':
            type_message = 'Сообщение о завершении процедуры внесудебного банкротства гражданина'
            court_name = 'ВБФЛ'
            case_number = 'ВБФЛ'
            decision_date = None
        else:
            type_message = None
            court_name = 'incorrect'
            case_number = 'incorrect'
            decision_date = None
        # Добавление в БД
        decision_date = datetime.strptime(decision_date, '%Y-%m-%d') if decision_date else None
        birthdate = datetime.strptime(birthdate, '%d.%m.%Y') if birthdate else None
        obj_info = {
            'type_message': type_message,
            'full_name': full_name,
            'birthdate': birthdate,
            'birthplace': birthplace,
            'address': address,
            'inn': inn,
            'snils': snils,
            'court_region': court_name,
            'case_number': case_number,
            'decision_date': decision_date,
            'publish_date': obj.publish_date,
            'revision': obj.revision
        }
        await append_delo_db(db=db, revision=obj.revision, fullname=full_name, birthdate=birthdate,
                             birthplace=birthplace, address=address, inn=inn, snils=snils,
                             court_region=court_name, case_number=case_number, decision_date=decision_date,
                             publish_date=obj.publish_date)
        all_objts.append(obj_info)
    return all_objts


async def get_async_request(db: Database = None, min_revision: int = 0, portion_size: int = 2000, token: str = EFRSB_TOKEN):
    url = "https://probili.ru/efrsb/repl-api.php/message"
    params = {
        "portion-size": portion_size,
        "revision-greater-than": min_revision,
        "auth-token": token,
        "no-base64": ""
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                logger.info("Запрос прошел успешно")
                data = await response.text()
                valid_data = ObjectEFRSBListAdapter.validate_json(data)
                res = await get_needed_info(valid_data, db)
                logger.info(f"Получили данные запросом для ЕФРСБ до {str(sorted(res, key=lambda x: x["publish_date"])[-1]['publish_date'])}")
                return res
            else:
                logger.error(f"Ошибка {response.status} при получении данных с ЕФРСБ")
                return None


async def append_delo_db(db: Database, revision, fullname=None, birthdate=None, birthplace=None, address=None, inn=None,
                         snils=None, court_region=None, case_number=None, publish_date=None, decision_date=None):
    await db.add_delo_efrsb(revision=revision, fullname=fullname, birthdate=birthdate, birthplace=birthplace,
                            address=address, inn=inn, snils=snils, court_region=court_region, case_number=case_number,
                            decision_date=decision_date, publish_date=publish_date)


async def get_nearest_values(db: Database, date1: datetime, date2: datetime):
    data = await db.get_all_efrsb()

    if not data:
        await get_async_request(db=db, min_revision=17_000_000, portion_size=2000)
        data = await db.get_all_efrsb()

    # Преобразуем строки дат в datetime и сортируем
    parsed_dates = sorted(
        [(delo.publish_date, delo.id) for delo in data]
    )

    before_date1 = None
    after_date2 = None

    for d, v in parsed_dates:
        if d.date() < date1.date():
            before_date1 = (d, v, True)
        if d.date() > date2.date() and after_date2 is None:
            after_date2 = (d, v, True)
            break
    if before_date1 is None:
        before_date1 = (*parsed_dates[0], False)
    if after_date2 is None:
        after_date2 = (*parsed_dates[-1], False)
    logger.info("Получены ближайшие даты")
    return {
        "before_date1": before_date1,
        "after_date2": after_date2
    }


async def get_objects_in_date_range(date_1: datetime, date_2: datetime, db: Database):
    dates = await get_nearest_values(db, date_1, date_2)
    before_date1, after_date2 = dates['before_date1'], dates['after_date2']
    step = 2000

    # сначала идем от before_date1 до date_1, если before_date1 > date_1 (не было подходящей даты)
    if before_date1[2] is False:
        logger.info('before_date1 не подходит. Ищем новый')
        min_revision = before_date1[1] - step
        while True:
            res = await get_async_request(db=db, min_revision=min_revision, portion_size=step)
            min_revision -= step
            if res is None:
                return None
            if res[0]['publish_date'].date() < date_1.date():
                logger.info("Обновили before_date1")
                before_date1 = (res[0]['publish_date'], res[0]['revision'])
                # если новые данные лучше подходят, чем те, что в бд:
                if after_date2[2] is False and after_date2[0].date() < res[-1]['publish_date'].date() < date_2.date():
                    logger.info("Обновили after_date2 вместе с before_date1")
                    after_date2 = (res[-1]['publish_date'], res[-1]['revision'])
                break

    # потом идем от after_date2 до date_2, если after_date2 < date_2 (не было подходящей даты)
    if after_date2[2] is False:
        logger.info('after_date2 не подходит. Ищем новый')
        min_revision = after_date2[1]
        while True:
            res = await get_async_request(db=db, min_revision=min_revision, portion_size=step)
            min_revision += step
            if res is None:
                return None
            if res[-1]['publish_date'].date() > date_2.date():
                logger.info("Обновили after_date2")
                after_date2 = (res[-1]['publish_date'], res[-1]['revision'])
                break

    logger.info("Проходимся по остаткам ЕФРСБ")
    # а тут проходимся по всем оставшимся
    all_revisions_in_db = [delo.id for delo in await db.get_all_efrsb()]
    for i in range(before_date1[1], after_date2[1], step):
        min_revision = i

        # если нет всех 2000 (step) объектов в бд, то делаем запрос
        if not all(rev in all_revisions_in_db for rev in range(min_revision, min_revision + step + 1)):
            res = await get_async_request(db=db, min_revision=min_revision, portion_size=step)
            if res is None:
                return None
        else:
            logger.info(f'Все объекты с {min_revision} по {min_revision + step} есть в БД')

    # получаем обновленные данные и создаем эксель файл
    file_name = await generate_new_xlsx(db=db, date_1=date_1, date_2=date_2)
    return file_name
