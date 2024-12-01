import datetime

from sqlalchemy import Table, Column, Integer, String, MetaData, JSON, BigInteger, DateTime, ForeignKey, Boolean, Text

metadata_obj = MetaData()


tg_users = Table(
    "tg_users",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("tg_id", BigInteger, unique=True),
    Column("FIO", Text, nullable=True),
    Column("email", Text, nullable=True),
    Column("phone", Text, nullable=True),
    Column("payment_status", Boolean, default=False),
    Column("join_date", DateTime, default=datetime.datetime.now()),
    Column("day_counter", Integer, default=1),
    Column("is_started", Boolean, default=False)
)


payments = Table(
    "payments",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("payment_id", BigInteger, unique=True),
    Column("email", Text, nullable=True),
    Column("status", Text, nullable=True),
    Column("name", Text, nullable=True)
)

del_msgs = Table(
    "del_msgs",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("message_id", BigInteger, unique=True),
    Column("chat_id", BigInteger),
    Column("type", String, default="task"),
)
