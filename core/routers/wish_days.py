import asyncio
import datetime
import logging

from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram import F

from core.db.scripts import get_user_data, get_user_by, get_wish_settings, update_day_counter, update_started_status, \
    create_del_msg, del_user_msgs, get_10_days_users, get_11_days_users, check_user_payment, update_users_status, \
    get_usr_by_tg, set_user_day, create_msg_to_send, get_send_msgs, set_msgs_sent
from core.keyboards.wish_kb import y_or_n, instruction_2, instruction_3, final_kb
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
    await msg.answer(text=wish_s.get("tasks").get(str(user['day_counter'])))
    create_msg_to_send(
        user['tg_id'],
        datetime.datetime.now() + datetime.timedelta(seconds=15),
        "Сегодняшний сектор карты уже готов?",
        msg_type="question"
    )


async def send_user_day_2(bot: Bot, text: str, user: dict):
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

    await bot.send_message(chat_id=user['tg_id'], text=text)
    create_msg_to_send(
        user['tg_id'],
        datetime.datetime.now() + datetime.timedelta(seconds=15),
        "Сегодняшний сектор карты уже готов?",
        msg_type="question"
    )


async def send_user_day_3(bot: Bot, text: str, user: dict):
    if "Благодарим за то, что прошли этот Марафон до конца." in text:
        await bot.send_message(user['tg_id'], text, reply_markup=final_kb.as_markup())
    else:
        await bot.send_message(user['tg_id'], text)


@router.callback_query()
async def get_callback(call: CallbackQuery):
    data = call.data
    user_data = get_user_by(call.message.chat.id)[0]
    wish_s = get_wish_settings()
    if data == "instruction":
        await call.message.answer(INSTRUCTION)

    if call.data == "yes":
        await call.message.answer(text=wish_s.get("positive").get(str(user_data.get("day_counter"))))
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
        await call.message.answer(text=wish_s.get("negative").get(str(user_data.get("day_counter"))))
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
            await send_user_day(call.message, user['day_counter'], user)

        # user = get_user_data()[0]
        # if check_user_payment(user.get("email")):
        #     update_started_status(call.message.chat.id)
        #     if user.get("day_counter") <= 9:
        #         user_day = user.get("day_counter", 1)
        #         await call.message.edit_reply_markup(reply_markup=instruction_3.as_markup())
        #         message = await call.message.answer_video(
        #                                        video="BAACAgIAAxkBAAICfGdMk_tAL4ODpJECe5xfHRbsZJG5AAL5ZgAC-XloSsMCUum9c3clNgQ")
        #         create_del_msg("task", message.message_id, message.chat.id)
        #         message = await call.message.answer_video(
        #                                        video="BAACAgIAAxkBAAICfmdMlFH-CgelmudhTIcZFhicFb3lAAL_ZgAC-XloSoQqxyXln0KwNgQ")
        #         create_del_msg("task", message.message_id, message.chat.id)
        #         message = await call.message.answer(
        #                                          text=wish_s.get("tasks").get(str(user_day)))
        #         create_del_msg("task", message.message_id, message.chat.id)
        # else:
        #     await call.message.answer(text="Не удается найти оплату")


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


async def send_users_msg(bot: Bot):
    # update_users_status()
    users = get_user_data()
    wish_s = get_wish_settings()
    await del_user_msgs(bot, "task")
    for user in users:
        if user.get("day_counter") <= 9:
            if user.get("day_counter") == 1:
                user_day = user.get("day_counter", 1)
                # message = await bot.send_message(user.get("tg_id"), text=wish_s.get("tasks").get(str(user_day)))
                message = await bot.send_video(chat_id=user.get("tg_id"),
                                               video="BAACAgIAAxkBAAICfGdMk_tAL4ODpJECe5xfHRbsZJG5AAL5ZgAC-XloSsMCUum9c3clNgQ")
                create_del_msg("task", message.message_id, message.chat.id)
                message = await bot.send_video(chat_id=user.get("tg_id"),
                                               video="BAACAgIAAxkBAAICfmdMlFH-CgelmudhTIcZFhicFb3lAAL_ZgAC-XloSoQqxyXln0KwNgQ")
                create_del_msg("task", message.message_id, message.chat.id)
                message = await bot.send_message(chat_id=user.get("tg_id"),
                                                 text=wish_s.get("tasks").get(str(user_day)))
                create_del_msg("task", message.message_id, message.chat.id)
            elif user.get("day_counter") == 2:
                user_day = user.get("day_counter", 1)
                message = await bot.send_video(chat_id=user.get("tg_id"),
                                               video="BAACAgIAAxkBAAID12dMqXXfObbcJXWHO2BoKxdgclOCAAKVaAAC-XloShRsAh4W8ZJSNgQ")
                create_del_msg("task", message.message_id, message.chat.id)
                message = await bot.send_message(chat_id=user.get("tg_id"),
                                                 text=wish_s.get("tasks").get(str(user_day)))
                create_del_msg("task", message.message_id, message.chat.id)
            elif user.get("day_counter") == 3:
                user_day = user.get("day_counter", 1)
                message = await bot.send_video(chat_id=user.get("tg_id"),
                                               video="BAACAgIAAxkBAAID2GdMqejmWtXPgIFHsyJlKlNGXKt4AAKZaAAC-XloSmEvZg37lHEpNgQ")
                create_del_msg("task", message.message_id, message.chat.id)
                message = await bot.send_message(chat_id=user.get("tg_id"),
                                                 text=wish_s.get("tasks").get(str(user_day)))
                create_del_msg("task", message.message_id, message.chat.id)
            elif user.get("day_counter") == 4:
                user_day = user.get("day_counter", 1)
                message = await bot.send_video(chat_id=user.get("tg_id"),
                                               video="BAACAgIAAxkBAAID2mdMq2Zk3ZfLwB_NVcZ_v2UB_wABuQACtmgAAvl5aEqldFcTAAGi_Rk2BA")
                create_del_msg("task", message.message_id, message.chat.id)
                message = await bot.send_video(chat_id=user.get("tg_id"),
                                               video="BAACAgIAAxkBAAID2WdMqwkdZBEwLinUCvfj5UyKQ8TkAAKmaAAC-XloSqf4LTL66c2YNgQ")
                create_del_msg("task", message.message_id, message.chat.id)
                message = await bot.send_message(chat_id=user.get("tg_id"),
                                                 text=wish_s.get("tasks").get(str(user_day)))
                create_del_msg("task", message.message_id, message.chat.id)
            elif user.get("day_counter") == 5:
                user_day = user.get("day_counter", 1)
                message = await bot.send_video(chat_id=user.get("tg_id"),
                                               video="BAACAgIAAxkBAAID22dMrG5tFcIXQiJ6jBWjvx9n-CdNAALEaAAC-XloShVkFogJ-W0MNgQ")
                create_del_msg("task", message.message_id, message.chat.id)
                message = await bot.send_message(chat_id=user.get("tg_id"),
                                                 text=wish_s.get("tasks").get(str(user_day)))
                create_del_msg("task", message.message_id, message.chat.id)
            elif user.get("day_counter") == 6:
                user_day = user.get("day_counter", 1)
                message = await bot.send_video(chat_id=user.get("tg_id"),
                                               video="BAACAgIAAxkBAAID3GdMrKQpqczdCegZl7HbeAbMHbEaAALHaAAC-XloSltxiHkhuDkTNgQ")
                create_del_msg("task", message.message_id, message.chat.id)
                message = await bot.send_message(chat_id=user.get("tg_id"),
                                                 text=wish_s.get("tasks").get(str(user_day)))
                create_del_msg("task", message.message_id, message.chat.id)
            elif user.get("day_counter") == 7:
                user_day = user.get("day_counter", 1)
                message = await bot.send_video(chat_id=user.get("tg_id"),
                                               video="BAACAgIAAxkBAAID3WdMrbS0Q3f-Pt2cHVvD0KtvHRa7AALUaAAC-XloSiF3b_PjZDntNgQ")
                create_del_msg("task", message.message_id, message.chat.id)
                message = await bot.send_video(chat_id=user.get("tg_id"),
                                               video="BAACAgIAAxkBAAID3mdMrfJMVYSckSH6WKAoStX9z5v1AALdaAAC-XloSmPco-oNR0ybNgQ")
                create_del_msg("task", message.message_id, message.chat.id)
                message = await bot.send_message(chat_id=user.get("tg_id"),
                                                 text=wish_s.get("tasks").get(str(user_day)))
                create_del_msg("task", message.message_id, message.chat.id)
            elif user.get("day_counter") == 8:
                user_day = user.get("day_counter", 1)
                message = await bot.send_video(chat_id=user.get("tg_id"),
                                               video="BAACAgIAAxkBAAID32dMru3KXuipOex5pG6iE9Ioi5TuAALuaAAC-XloSrwJCpOnHKIFNgQ")
                create_del_msg("task", message.message_id, message.chat.id)
                message = await bot.send_message(chat_id=user.get("tg_id"),
                                                 text=wish_s.get("tasks").get(str(user_day)))
                create_del_msg("task", message.message_id, message.chat.id)
            elif user.get("day_counter") == 9:
                user_day = user.get("day_counter", 1)
                message = await bot.send_video(chat_id=user.get("tg_id"),
                                               video="BAACAgIAAxkBAAID8WdMswRDuc5MuR_7WupWyrjvdBTUAAJFaQAC-XloSj3jaJL2ieppNgQ")
                create_del_msg("task", message.message_id, message.chat.id)
                message = await bot.send_video(chat_id=user.get("tg_id"),
                                               video="BAACAgIAAxkBAAID8mdMs0wByyX2UnqYFCxNNT_fN8KOAAJIaQAC-XloSs_JaxrCxL7YNgQ")
                create_del_msg("task", message.message_id, message.chat.id)
                message = await bot.send_message(chat_id=user.get("tg_id"),
                                                 text=wish_s.get("tasks").get(str(user_day)))
                create_del_msg("task", message.message_id, message.chat.id)
            else:
                user_day = user.get("day_counter", 1)
                message = await bot.send_message(user.get("tg_id"), text=wish_s.get("tasks").get(str(user_day)))
                create_del_msg("task", message.message_id, message.chat.id)


@router.message(F.document | F.photo)
async def get_user_map(msg: Message):
    user = get_usr_by_tg(msg.chat.id)
    if user.get("day_counter") == 10:
        await msg.answer("🎉")
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


async def send_10_day_msg(bot: Bot):
    users = get_10_days_users()
    for user in users:
        await bot.send_message(chat_id=user.get("tg_id"), text="""Жду от вас фото вашей карты желаний!

То что вы пришлете, не увидит никто кроме вас. Но именно сейчас, настало время вашей ответственности: какую фотографию карты желаний вы вышлите, то и активируется.""")


async def send_10_day(bot: Bot):
    while True:
        now = datetime.datetime.now()
        target_time = now.replace(hour=21, minute=30, second=0, microsecond=0)

        try:
            await send_10_day_msg(bot)
        except Exception as e:
            logging.error(f"Failed to send message to 334019728: {e}")

        if now >= target_time:
            target_time += datetime.timedelta(days=1)

        await asyncio.sleep((target_time - now).total_seconds())


async def send_11_day_msg(bot: Bot):
    users = get_11_days_users()
    for user in users:
        if user.get("day_counter") == 11 and user.get("payment_status"):
            await bot.send_message(chat_id=user.get("tg_id"),
                                   text="""Настал тот самый день! Сегодня вы получите инструкции, как сделать так, чтобы ваша карта заработала на полную мощность!""")
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
            target_time += datetime.timedelta(days=1)

        await asyncio.sleep((target_time - now).total_seconds())


async def send_db_msgs(bot: Bot):
    while True:
        await asyncio.sleep(2)
