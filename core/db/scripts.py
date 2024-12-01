import datetime
import time

import requests, json
from aiogram import Bot

from core.db.database import engine
from core.db.models import metadata_obj, del_msgs
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import select, update, delete

from core.db.models import tg_users, payments
from core.db.config import settings


def create_tables():
    metadata_obj.create_all(engine)


create_tables()


def create_user(tg_id: int, fio: str, email: str) -> None:
    # is_started = False
    # if datetime.datetime.now().date() < datetime.date(2024, 12, 2):
    #     is_started = True
    with engine.connect() as conn:
        stmt = insert(tg_users).values(
            [
                {
                    "tg_id": tg_id,
                    "FIO": fio,
                    "email": email
                    # "is_started": is_started
                }
            ]
        ).on_conflict_do_nothing()
        conn.execute(stmt)
        conn.commit()


def update_user_phone(phone: str, tg_id: int):
    with engine.connect() as conn:
        stmt = update(tg_users).where(tg_users.c.tg_id == tg_id).values(phone=phone)
        conn.execute(stmt)
        conn.commit()


def get_user(tg_id: int) -> dict:
    with engine.connect() as conn:
        stmt = select(tg_users).where(tg_users.c.tg_id == tg_id)
        return conn.execute(stmt).fetchone()


def insert_payments(items: list):
    with engine.connect() as conn:
        for p in items:
            stmt = insert(payments).values(
                [
                    {
                        "payment_id": p[0],
                        "email": p[2],
                        "status": p[6],
                        "name": p[-1],
                    }
                ]
            ).on_conflict_do_nothing()
            conn.execute(stmt)
            conn.commit()


def get_payments():
    res = requests.get(f"{settings.GETCOURSE_URL}/pl/api/account/payments?key={settings.GETCOURSE_TOKEN}&status=accepted")
    export_id = (res.json().get('info').get('export_id'))
    count = 0
    while True:
        res = requests.get(f"{settings.GETCOURSE_URL}/pl/api/account/exports/{export_id}?key={settings.GETCOURSE_TOKEN}")
        res = res.json()

        if res.get('success'):
            insert_payments(res.get("info").get('items'))
            break

        if count == 11:
            print(f"Не удалось получить платежи - {res.text}")
            break

        count += 1
        print(f"Попытка получения платежей - {count}")

        time.sleep(5)


def get_payment_from_db(email: str) -> list[tuple]:
    with engine.connect() as conn:
        stmt = select(payments).where(
            payments.c.email == email
        ).where(payments.c.name.in_(['Марафон "Карта желаний 2025"', 'Предзапись', 'Марафон "Карта желаний 2025" Предзапись']))
        return conn.execute(stmt).fetchall()


def update_user_status(status, email):
    print("start updating user status")
    with engine.connect() as conn:
        stmt = update(tg_users).where(tg_users.c.email == email).values(payment_status=status)
        conn.execute(stmt)
        conn.commit()


def check_payment(email: str) -> None:
    user_payments: list = get_payment_from_db(email)
    if user_payments:
        status = True
    else:
        print("start getting payments")
        get_payments()
        user_payments: list = get_payment_from_db(email)
        if user_payments:
            status = True
        else:
            status = False

    update_user_status(status, email)
    print("End getting payments")


def get_user_data() -> list[dict]:
    with engine.connect() as conn:
        stmt = select(tg_users)
        result = conn.execute(stmt)
        return [row._asdict() for row in result]


def get_wish_settings() -> dict:
    with open("wish_days.json", "r") as fp:
        data = json.loads(fp.read())
    return data


def get_user_by(tg_id: int) -> list[dict]:
    with engine.connect() as conn:
        stmt = select(tg_users).where(tg_users.c.tg_id == tg_id)
        result = conn.execute(stmt)
        return [row._asdict() for row in result]


def update_day_counter(tg_id: int) -> None:
    with engine.connect() as conn:
        stmt = (
            update(tg_users)
            .where(tg_users.c.tg_id == tg_id)
            .values(day_counter=tg_users.c.day_counter + 1)
        )
        conn.execute(stmt)
        conn.commit()


def update_started_status(tg_id: int):
    with engine.connect() as conn:
        stmt = update(tg_users).where(tg_users.c.tg_id == tg_id).values(is_started=True)
        conn.execute(stmt)
        conn.commit()


def create_del_msg(msg_type: str, msg_id: int, chat_id: int):
    with engine.connect() as conn:
        stmt = insert(del_msgs).values(
            [
                {
                    "message_id": msg_id,
                    "chat_id": chat_id,
                    "type": msg_type
                }
            ]
        )
        conn.execute(stmt)
        conn.commit()


async def del_user_msgs(bot: Bot, msg_type: str):
    with engine.connect() as conn:
        stmt = select(del_msgs).where(del_msgs.c.type == msg_type)
        result = conn.execute(stmt)
        msgs = [row._asdict() for row in result]

    for msg in msgs:
        try:
            with engine.connect() as conn:
                stmt = delete(del_msgs).where(del_msgs.c.id == msg.get("id"))
                conn.execute(stmt)
                conn.commit()
            await bot.delete_message(chat_id=msg.get("chat_id"), message_id=msg.get("message_id"))
        except Exception as e:
            print(e)


def get_10_days_users():
    with engine.connect() as conn:
        stmt = select(tg_users).where(tg_users.c.day_counter == 10)
        result = conn.execute(stmt)
        return [row._asdict() for row in result]


def get_11_days_users():
    with engine.connect() as conn:
        stmt = select(tg_users).where(tg_users.c.day_counter == 11)
        result = conn.execute(stmt)
        return [row._asdict() for row in result]


def check_user_payment(email: str):
    payments = get_payment_from_db()
    if payments:
        return True
    else:
        return False


def update_users_status():
    get_payments()
    with engine.connect() as conn:
        stmt = select(tg_users).where(tg_users.c.is_started == False)
        result = conn.execute(stmt)
        users = [row._asdict() for row in result]

    for user in users:
        with engine.connect() as conn:
            stmt = select(payments).where(
                payments.c.email == user.get("email")
            ).where(payments.c.name.in_(
                ['Марафон "Карта желаний 2025"', 'Предзапись', 'Марафон "Карта желаний 2025" Предзапись']))
            res = conn.execute(stmt).fetchall()
        if res:
            with engine.connect() as conn:
                stmt = update(tg_users).where(tg_users.c.email == user.get("email")).values(payment_status=True, is_started=True)
                conn.execute(stmt)
                conn.commit()


