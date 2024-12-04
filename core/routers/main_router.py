import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from aiogram.enums.parse_mode import ParseMode

from core.routers.register import start_reg

router = Router()


@router.message(CommandStart())
async def start(mes: Message, state: FSMContext):
    await start_reg(mes, state)
    await mes.delete()


# @router.message(Command("test"))
# async def test(mes: Message):
#     # await mes.answer(text=END_REG_MSG_2, reply_markup=instruction_2.as_markup())
#     await mes.answer_video(video="BAACAgIAAxkBAAICQ2dMj5NSDDcG9Tyz6bj7Ofu0FYsPAAKoZgAC-XloSgPtw2y8dmBeNgQ")
#     ...
#
#
# @router.message(F.video)
# def test2(msg: Message):
#     print("test2")
#     logging.info(f"{msg.video.file_id} | {msg.video.file_name}")


# @router.message(Command("call"))
# async def test3(msg: Message):
#     await msg.answer("**Предпоследний сектор готов!** \uD83C\uDFC5\nПредлагаю в качестве благодарности к себе за выполненную работу прямо сейчас __начать свой путь к богатству и процветанию.__ Создайте целевой накопительный счет на свою мечту и переведите туда 5000 ✉\uFE0F")
