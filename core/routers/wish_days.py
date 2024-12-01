import asyncio
import datetime
import logging

from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram import F

from core.db.scripts import get_user_data, get_user_by, get_wish_settings, update_day_counter, update_started_status, \
    create_del_msg, del_user_msgs, get_10_days_users, get_11_days_users, check_user_payment, update_users_status
from core.keyboards.wish_kb import y_or_n, instruction_2, instruction_3, final_kb
from texts import INSTRUCTION

router = Router()


@router.callback_query()
async def get_callback(call: CallbackQuery):
    data = call.data
    user_data = get_user_by(call.message.chat.id)[0]
    wish_s = get_wish_settings()
    if data == "instruction":
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(INSTRUCTION)

    if call.data == "yes":
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(text=wish_s.get("positive").get(str(user_data.get("day_counter"))))
        update_day_counter(call.message.chat.id)

    if call.data == "no":
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(text=wish_s.get("negative").get(str(user_data.get("day_counter"))))
        update_day_counter(call.message.chat.id)

    if call.data == "moon_calendar":
        await call.message.answer(text="""01.01-13.01, 30.01-11.02, 01.03-13.03, 30.03-12.04, 28.04-11.05, 28.05-10.06, 26.06-09.07, 25.07-08.08, 24.08-06.09, 22.09-05.10, 22.10-04.11, 21.11-04.12, 21.12-31.12""", reply_markup=instruction_2.as_markup())

    if call.data == "start_magic":
        user = get_user_data()[0]
        if check_user_payment(user.get("email")):
            update_started_status(call.message.chat.id)
            if user.get("day_counter") <= 9:
                user_day = user.get("day_counter", 1)
                await call.message.edit_reply_markup(reply_markup=instruction_3.as_markup())
                message = await call.message.answer(text=wish_s.get("tasks").get(str(user_day)))
                try:
                    create_del_msg("task", message.message_id, message.chat.id)
                except:
                    ...
        else:
            await call.message.answer(text="Не удается найти оплату")


async def send_users_msg(bot: Bot):
    update_users_status()
    users = get_user_data()
    wish_s = get_wish_settings()
    await del_user_msgs(bot, "task")
    for user in users:
        if user.get("day_counter") <= 9:
            user_day = user.get("day_counter", 1)
            message = await bot.send_message(user.get("tg_id"), text=wish_s.get("tasks").get(str(user_day)))
            create_del_msg("task", message.message_id, message.chat.id)


async def send_users_end_msg(bot: Bot):
    users = get_user_data()
    await del_user_msgs(bot, "question")
    for user in users:
        if user.get("day_counter") <= 9:
            message = await bot.send_message(user.get("tg_id"), "Сегодняшний сектор карты уже готов?", reply_markup=y_or_n.as_markup())
            create_del_msg("question", message.message_id, message.chat.id)


async def send_wish_day_msg(bot: Bot):
    while True:
        # now = datetime.datetime.now()
        # if now.date() >= datetime.date(2024, 11, 27) and now.time() >= datetime.time(hour=9, minute=0, second=0):
        #     # users_data = get_user_data()
        #     # print(users_data)
        now = datetime.datetime.now()
        target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)

        try:
            await send_users_msg(bot)
        except Exception as e:
            logging.error(f"Failed to send message to 334019728: {e}")

        if now >= target_time:
            # target_time += datetime.timedelta(days=1)
            target_time = now + datetime.timedelta(minutes=2)
            print(target_time)

        await asyncio.sleep((target_time - now).total_seconds())


async def send_end_wish_day_msg(bot: Bot):
    while True:
        # now = datetime.datetime.now()
        # if now.date() >= datetime.date(2024, 11, 27) and now.time() >= datetime.time(hour=9, minute=0, second=0):
        #     # users_data = get_user_data()
        #     # print(users_data)
        now = datetime.datetime.now()
        target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)

        try:
            await send_users_end_msg(bot)
        except Exception as e:
            logging.error(f"Failed to send message to 334019728: {e}")

        if now >= target_time:
            # target_time += datetime.timedelta(days=1)
            target_time = now + datetime.timedelta(minutes=2)

        await asyncio.sleep((target_time - now).total_seconds())


@router.message(F.document | F.photo)
async def get_user_map(msg: Message):
    user = get_user_by(msg.chat.id)[0]
    if user.get("day_counter") == 10 and user.get("payment_status"):
        await msg.answer("🎉")
        update_day_counter(user.get("tg_id"))


async def send_10_day_msg(bot: Bot):
    users = get_10_days_users()
    for user in users:
        await bot.send_message(chat_id=user.get("tg_id"), text="""Жду от вас фото вашей карты желаний!

То что вы пришлете, не увидит никто кроме вас. Но именно сейчас, настало время вашей ответственности: какую фотографию карты желаний вы вышлите, то и активируется.""")


async def send_10_day(bot: Bot):
    while True:
        now = datetime.datetime.now()
        target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)

        try:
            await send_10_day_msg(bot)
        except Exception as e:
            logging.error(f"Failed to send message to 334019728: {e}")

        if now >= target_time:
            # target_time += datetime.timedelta(days=1)
            target_time = now + datetime.timedelta(minutes=2)

        await asyncio.sleep((target_time - now).total_seconds())


async def send_11_day_msg(bot: Bot):
    users = get_11_days_users()
    for user in users:
        if user.get("day_counter") == 11 and user.get("payment_status"):
            await bot.send_message(chat_id=user.get("tg_id"), text="""Настал тот самый день! Сегодня вы получите инструкции, как сделать так, чтобы ваша карта заработала на полную мощность!""")
            update_day_counter(user.get("tg_id"))
            await bot.send_message(chat_id=user.get("tg_id"),
                                   text="""Благодарим за то, что прошли этот Марафон до конца. Пусть эта карта будет вашим компасом для достижения целей. Для этого вам может понадобиться обучение. Узнать об образовательных продуктах Norland academy""",
                                   reply_markup=final_kb.as_markup())


async def send_11_day(bot: Bot):
    while True:
        now = datetime.datetime.now()
        target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)

        try:
            await send_11_day_msg(bot)
        except Exception as e:
            logging.error(f"Failed to send message to 334019728: {e}")

        if now >= target_time:
            # target_time += datetime.timedelta(days=1)
            target_time = now + datetime.timedelta(minutes=2)

        await asyncio.sleep((target_time - now).total_seconds())
