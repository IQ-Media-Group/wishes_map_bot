from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

from core.keyboards.wish_kb import instruction_2
from core.routers.register import start_reg
from texts import HELLO_MSG, END_REG_MSG_2

router = Router()


@router.message(CommandStart())
async def start(mes: Message, state: FSMContext):
    await start_reg(mes, state)
    await mes.delete()


@router.message(Command("test"))
async def test(mes: Message):
    # await mes.answer(text=END_REG_MSG_2, reply_markup=instruction_2.as_markup())
    await mes.answer_video(video="BAACAgIAAxkBAAICQ2dMj5NSDDcG9Tyz6bj7Ofu0FYsPAAKoZgAC-XloSgPtw2y8dmBeNgQ")
    ...


@router.message(F.video)
def test2(msg: Message):
    print("test2")
    print(msg.video.file_id)