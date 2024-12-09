from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.exceptions import TelegramForbiddenError

from core.db.scripts import get_payments, get_usr_by_tg, get_payment_from_db, update_user_payment
from core.keyboards.wish_kb import payment_kb
from core.routers.wish_days import send_user_day
from texts import PAYMENT_MSG

router = Router()




