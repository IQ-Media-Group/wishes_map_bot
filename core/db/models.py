import datetime

from sqlalchemy import Table, Column, Integer, String, MetaData, JSON, BigInteger, DateTime, ForeignKey, Boolean, Text

metadata_obj = MetaData()

# Table creation example
#
#         tg_users = Table(
#             "tg_users",
#             metadata_obj,
#             Column("id", Integer, primary_key=True),
#           )

