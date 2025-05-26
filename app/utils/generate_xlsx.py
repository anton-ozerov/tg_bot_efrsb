import time
from datetime import datetime
from pathlib import Path

import xlsxwriter

from app.database.requests import Database


async def generate_new_xlsx(db: Database, date_1: datetime, date_2: datetime, is_with_osint: bool = False) -> str:
    output_dir = Path("temp_files")
    output_dir.mkdir(exist_ok=True)
    excel_file_path = str(output_dir / f"result_{time.time()}.xlsx")
    workbook = xlsxwriter.Workbook(excel_file_path)
    worksheet = workbook.add_worksheet("ЕФРСБ")
    scores = []

    data = sorted(await db.get_delo_by_publish_date_range(date_1=date_1, date_2=date_2), key=lambda x: x.publish_date)
    scores.append(
        ['Ревизия', 'ФИО', 'Дата рождения', 'Место рождения', 'Адрес', 'ИНН', 'СНИЛС', 'Суд', 'Номер дела',
         'Дата решения', 'Дата публикации'])
    max_phones, max_emails = 0, 0

    if is_with_osint:  # добавляем столбцы для телефонов и почт
        max_phones = max(len(delo.phones) for delo in data)
        for phone_num in range(1, max_phones + 1):
            scores[0].append(f'Телефон {phone_num}')

        max_emails = max(len(delo.emails) for delo in data)
        for email_num in range(1, max_emails + 1):
            scores[0].append(f'Почта {email_num}')

    for delo in data:
        if date_1.date() <= delo.publish_date.date() <= date_2.date():

            decision_date = str(delo.decision_date.date()) if delo.decision_date is not None else None
            birthdate = str(delo.birthdate.date()) if delo.birthdate is not None else None

            row = [delo.id, delo.fullname, birthdate, delo.birthplace, delo.address, delo.inn,
                           delo.snils, delo.court_region, delo.case_number, decision_date, str(delo.publish_date)]

            if is_with_osint:  # добавляем телефоны и почты
                phones = [phone.phone_number for phone in delo.phones]
                for phone_num in range(max_phones):
                    if phone_num >= len(phones):
                        row.append('')
                    else:
                        row.append(phones[phone_num])

                emails = [email.email_address for email in delo.emails]
                for email_num in range(max_emails):
                    if email_num >= len(emails):
                        row.append('')
                    else:
                        row.append(emails[email_num])

            # Т.к. добавляем не только нужные данные в БД, то тут их не включаем
            # (добавляем ненужные, чтобы потом относительно их ревизий, дат запросы делать тоже)
            if 'incorrect' not in row:
                scores.append(row)
            else:
                pass

    for row, score in enumerate(scores):
        for col in range(len(score)):
            worksheet.write(row, col, score[col])

    workbook.close()
    return excel_file_path
