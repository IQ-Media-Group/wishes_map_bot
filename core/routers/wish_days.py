import asyncio
import datetime
import logging

from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import F

from core.db.models import del_msgs
from core.db.scripts import get_user_data, get_user_by, get_wish_settings, update_day_counter, update_started_status, \
    create_del_msg, del_user_msgs
from core.keyboards.wish_kb import y_or_n, instruction_2, instruction_3

router = Router()


@router.callback_query()
async def get_callback(call: CallbackQuery):
    data = call.data
    user_data = get_user_by(call.message.chat.id)[0]
    wish_s = get_wish_settings()
    if data == "instruction":
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer("""🪧Карту желаний можно делать в электронном виде или на бумаге.
Для начала перед тем как приступить к созданию карты желаний рекомендуем выбрать свою самую лучшую фотографию. Ту, где вы на себя любуетесь. Сделанную в моменты самого высочайшего счастья и удовлетворения. В состоянии покоя и гармонии. Советуем подобрать фотографию до начала марафона!
Для электронного варианта мы рекомендуем использовать следующие приложения:---Так же мы подготовили шаблон карты, куда можно добавлять свои изображения.
Для бумажного формата вам потребуется:
✅Ватман формата А2 или А1.✅Линейка, карандаши/фломастеры для нанесения разметки✅Клей - карандаш/скотч для приклеивания нужных картинок✅Картинки можно напечатать на принтере или вырезать из журналов и каталогов.
✨ Для создания приятной атмосферы предварительно подготовьте свечи и вкусный чай. Создайте плейлист с приятной музыкой🍵.""")

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
        update_started_status(call.message.chat.id)
        user = get_user_data()[0]
        if user.get("day_counter") <= 9:
            user_day = user.get("day_counter", 1)
            await call.message.edit_reply_markup(reply_markup=instruction_3.as_markup())
            message = await call.message.answer(text=wish_s.get("tasks").get(str(user_day)))
            try:
                create_del_msg("task", message.message_id, message.chat.id)
            except:
                ...


async def send_users_msg(bot: Bot):
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

