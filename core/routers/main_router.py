from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.routers.register import start_reg
from texts import HELLO_MSG

router = Router()


@router.message(CommandStart())
async def start(mes: Message, state: FSMContext):
    await mes.answer(text=HELLO_MSG)
    await start_reg(mes, state)
    await mes.delete()


# @router.message(Command("test"))
# async def test(mes: Message):
#     await mes.answer("Сегодняшний сектор карты уже готов?", reply_markup=y_or_n.as_markup())
