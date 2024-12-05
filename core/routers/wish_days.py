import asyncio
import datetime
import logging

from aiogram import Router, Bot
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram import F

from core.db.scripts import get_user_data, get_user_by, get_wish_settings, update_day_counter, create_del_msg, \
    del_user_msgs, get_usr_by_tg, set_user_day, create_msg_to_send, get_send_msgs, set_msgs_sent
from core.keyboards.wish_kb import y_or_n, instruction_2, final_kb
from texts import INSTRUCTION

router = Router()


async def send_user_day(msg: Message, day: int, user: dict):
    wish_s = get_wish_settings()
    videos = wish_s['video'].get(str(day))
    if videos:
        if isinstance(videos, str):
            try:
                await msg.answer_video(video=videos)
            except Exception as e:
                logging.info(e)
        elif isinstance(videos, list):
            for video in videos:
                try:
                    await msg.answer_video(video=video)
                except Exception as e:
                    logging.info(e)
    await msg.answer(text=wish_s.get("tasks").get(str(user['day_counter'])), parse_mode=ParseMode.HTML)
    create_msg_to_send(
        user['tg_id'],
        datetime.datetime.now() + datetime.timedelta(seconds=15),
        "Сегодняшний сектор карты уже готов?",
        msg_type="question"
    )


async def send_user_day_2(bot: Bot, text: str, user: dict):
    if user['day_counter'] <= 9:
        wish_s = get_wish_settings()
        videos = wish_s['video'].get(str(user['day_counter']))

        if videos:
            if isinstance(videos, str):
                try:
                    await bot.send_video(chat_id=user['tg_id'], video=videos)
                except Exception as e:
                    logging.info(e)
            elif isinstance(videos, list):
                for video in videos:
                    try:
                        await bot.send_video(chat_id=user['tg_id'], video=video)
                    except Exception as e:
                        logging.info(e)

        await bot.send_message(chat_id=user['tg_id'], text=text, parse_mode=ParseMode.HTML)
        create_msg_to_send(
            user['tg_id'],
            datetime.datetime.now() + datetime.timedelta(seconds=15),
            "Сегодняшний сектор карты уже готов?",
            msg_type="question"
        )


async def send_user_day_3(bot: Bot, text: str, user: dict):
    wish_s = get_wish_settings()
    if "Благодарим за то, что прошли этот Марафон до конца." in text:
        await bot.send_message(user['tg_id'], text, reply_markup=final_kb.as_markup())
    elif "Настал тот самый день!" in text:
        videos = wish_s.get("video").get("10")
        await bot.send_message(user['tg_id'], text)
        for video in videos:
            try:
                await bot.send_video(user['tg_id'], video=video)
            except Exception as e:
                logging.info(e)
    else:
        await bot.send_message(user['tg_id'], text)


@router.callback_query()
async def get_callback(call: CallbackQuery):
    data = call.data
    user_data = get_user_by(call.message.chat.id)[0]
    wish_s = get_wish_settings()
    if data == "instruction":
        await call.message.answer(INSTRUCTION, reply_markup=instruction_2.as_markup())

    if call.data == "yes":
        await call.message.answer(text=wish_s.get("positive").get(str(user_data.get("day_counter"))), parse_mode=ParseMode.HTML)
        await call.message.edit_reply_markup(reply_markup=None)
        update_day_counter(call.message.chat.id)
        if user_data.get("day_counter") < 9:
            create_msg_to_send(call.message.chat.id,
                               datetime.datetime.now() + datetime.timedelta(seconds=10),
                               text=wish_s.get('tasks').get(str(user_data['day_counter'] + 1)),
                               msg_type="task"
                               )
        if user_data.get("day_counter") == 9:
            create_msg_to_send(call.message.chat.id,
                               datetime.datetime.now() + datetime.timedelta(seconds=20),
                               text="""Жду от вас фото вашей карты желаний!

То что вы пришлете, не увидит никто кроме вас. Но именно сейчас, настало время вашей ответственности: какую фотографию карты желаний вы вышлите, то и активируется.""",
                               msg_type="last"
                               )

    if call.data == "no":
        await call.message.answer(text=wish_s.get("negative").get(str(user_data.get("day_counter"))), parse_mode=ParseMode.HTML)
        await call.message.edit_reply_markup(reply_markup=None)
        update_day_counter(call.message.chat.id)
        if user_data.get("day_counter") <= 9:
            create_msg_to_send(call.message.chat.id,
                               datetime.datetime.now() + datetime.timedelta(seconds=10),
                               text=wish_s.get('tasks').get(str(user_data['day_counter'] + 1)),
                               msg_type="task"
                               )
            if user_data.get("day_counter") == 9:
                create_msg_to_send(call.message.chat.id,
                                   datetime.datetime.now() + datetime.timedelta(seconds=20),
                                   text="""Жду от вас фото вашей карты желаний!

То что вы пришлете, не увидит никто кроме вас. Но именно сейчас, настало время вашей ответственности: какую фотографию карты желаний вы вышлите, то и активируется.""",
                                   msg_type="last"
                                   )

    if call.data == "moon_calendar":
        await call.message.answer(text="""🎄01.01-13.01
❄️30.01-11.02
🌤01.03- 13.03
☀️30.03-12.04
🍀28.04-11.05
🌿28.05-10.06
🌸26.06-09.07
🍄‍🟫25.07-08.08
💐24.08-06.09
🌻22.09-05.10
🍁22.10-04.11
🌧21.11-04.12
🌲21.12-31.12""", reply_markup=instruction_2.as_markup())

    if call.data == "start_magic":
        user = get_usr_by_tg(call.message.chat.id)
        if user:
            set_user_day(1, user["tg_id"])
            user['day_counter'] = 1
            await send_user_day(call.message, user['day_counter'], user)


async def send_daily_msgs(bot: Bot):
    while True:
        await asyncio.sleep(5)
        msgs = get_send_msgs()

        for msg in msgs:
            if msg['type'] == 'question':
                try:
                    await bot.send_message(chat_id=msg['chat_id'], text=msg['text'], reply_markup=y_or_n.as_markup())
                    set_msgs_sent(msg['id'])
                except Exception as e:
                    logging.info(e)
            elif msg['type'] == 'task':
                user = get_usr_by_tg(msg['chat_id'])
                try:
                    await send_user_day_2(bot, msg['text'], user)
                    set_msgs_sent(msg['id'])
                except Exception as e:
                    logging.info(e)
            else:
                user = get_usr_by_tg(msg['chat_id'])
                try:
                    await send_user_day_3(bot, msg['text'], user)
                    set_msgs_sent(msg['id'])
                except Exception as e:
                    logging.info(e)


@router.message(F.document | F.photo)
async def get_user_map(msg: Message):
    user = get_usr_by_tg(msg.chat.id)
    if user.get("day_counter") == 10:
        await msg.answer("🎉", parse_mode=ParseMode.HTML)
        update_day_counter(user.get("tg_id"))
        create_msg_to_send(
            user['tg_id'],
            datetime.datetime.now() + datetime.timedelta(seconds=15),
            "Настал тот самый день! Сегодня вы получите инструкции, как сделать так, чтобы ваша карта заработала на полную мощность!",
            "last"
        )
        create_msg_to_send(
            user['tg_id'],
            datetime.datetime.now() + datetime.timedelta(seconds=25),
            """Благодарим за то, что прошли этот Марафон до конца. Пусть эта карта будет вашим компасом для достижения целей. Для этого вам может понадобиться обучение. Узнать об образовательных продуктах Norland academy""",
            "last"
        )
