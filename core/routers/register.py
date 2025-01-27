import datetime
import logging
from threading import Thread

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram import F

from core.states.registration import Form
from core.validators.phone import validate_phone_number
from core.validators.email import email_validator
from core.db.scripts import create_user, get_user, check_payment, update_user_phone, get_user_by
from core.keyboards.wish_kb import instruction, instruction_2
from texts import REG_MSG, END_REG_MSG, END_REG_MSG_2, REG_MSG_2, HELLO_MSG, HELLO_MSG_2, HELLO_MSG_3

router = Router()


async def show_form(mes: Message, state: FSMContext):
    data = await state.get_data()
    user = get_user_by(mes.from_user.id)[0]
    update_user_phone(data.get('phone'), data.get('tg_id'))
    if user.get("join_date").date() <= datetime.date(2024, 12, 2):
        try:
            await mes.answer_video(
                video="BAACAgIAAxkBAAICQ2dMj5NSDDcG9Tyz6bj7Ofu0FYsPAAKoZgAC-XloSgPtw2y8dmBeNgQ",
                caption=REG_MSG_2,
                reply_markup=instruction_2.as_markup(),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logging.info(e)
            await mes.answer(REG_MSG_2, reply_markup=instruction_2.as_markup(), parse_mode=ParseMode.HTML)
    else:
        try:
            await mes.answer_video(
                video="BAACAgIAAxkBAAICQ2dMj5NSDDcG9Tyz6bj7Ofu0FYsPAAKoZgAC-XloSgPtw2y8dmBeNgQ",
                caption=REG_MSG_2,
                reply_markup=instruction_2.as_markup(),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logging.info(e)
            await mes.answer(REG_MSG_2, reply_markup=instruction_2.as_markup(), parse_mode=ParseMode.HTML)
    await state.clear()


@router.message(Form.phone)
async def get_phone(mes: Message, state: FSMContext):
    data = await state.get_data()
    create_user(data.get('tg_id'), data.get('name'), data.get('email'))

    thr = Thread(target=check_payment, args=[data.get('email')])
    thr.start()

    status, phone = validate_phone_number(mes.text)
    if status:
        await state.update_data(phone=phone)
        await state.set_state(Form.phone)
        await show_form(mes, state)
    else:
        await mes.answer(text="Неверный формат номера. Попробуйте ещё раз. Номер телефона должен содержать 11 цифр и\
 начинаться с 7 или 8. Например, +79999999999",
                         parse_mode=ParseMode.HTML)
        await state.set_state(Form.phone)


@router.message(Form.email)
async def get_email(mes: Message, state: FSMContext):
    if email_validator(mes.text):
        await mes.answer(
            text="Теперь мне нужен ваш телефон",
            parse_mode=ParseMode.HTML
        )
        await state.update_data(email=mes.text)
        await state.set_state(Form.phone)
    else:
        await mes.answer(text="Неверный формат почты. Попробуйте ещё раз. Например, example@example.com", parse_mode=ParseMode.HTML)
        await state.set_state(Form.email)


@router.message(Form.name)
async def get_name(mes: Message, state: FSMContext):
    await mes.answer(text="Какая у вас почта?", parse_mode=ParseMode.HTML)
    await state.update_data(name=mes.text)
    await state.set_state(Form.email)


async def start_reg(mes: Message, state: FSMContext):
    user = get_user(mes.from_user.id)
    if user:
        await mes.answer(text=HELLO_MSG_3, parse_mode=ParseMode.HTML)
        await mes.answer(text=REG_MSG_2, reply_markup=instruction_2.as_markup(), parse_mode=ParseMode.HTML)
        return
    if user and user.get("join_date") <= datetime.date(2024, 12, 2):
        await mes.answer(text=HELLO_MSG, parse_mode=ParseMode.HTML)
    else:
        await mes.answer(text=HELLO_MSG_2, parse_mode=ParseMode.HTML)
    await state.update_data(tg_id=mes.from_user.id)
    await state.set_state(Form.name)
