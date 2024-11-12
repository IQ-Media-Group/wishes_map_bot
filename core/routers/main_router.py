from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message


router = Router()


@router.message(CommandStart())
async def start(mes: Message):
    await mes.answer(text="Hello world!")
    await mes.delete()
