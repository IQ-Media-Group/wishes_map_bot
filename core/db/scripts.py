import time

import requests, json

from core.db.database import engine
from core.db.models import metadata_obj
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import select, update
from sqlalchemy.engine import Row

from core.db.models import tg_users, payments
from core.db.config import settings


def create_tables():
    metadata_obj.create_all(engine)


create_tables()


def create_user(tg_id: int, fio: str, email: str) -> None:
    with engine.connect() as conn:
        stmt = insert(tg_users).values(
            [
                {
                    "tg_id": tg_id,
                    "FIO": fio,
                    "email": email
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
