from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardButton

instruction = InlineKeyboardBuilder()
instruction.add(InlineKeyboardButton(text="Инструкция", callback_data="instruction"))

instruction_2 = InlineKeyboardBuilder()
instruction_2.add(InlineKeyboardButton(text="Инструкция", callback_data="instruction"))
instruction_2.add(InlineKeyboardButton(text="Посмотреть лунный календарь", callback_data="moon_calendar"))
instruction_2.add(InlineKeyboardButton(text="Запустить магию", callback_data="start_magic"))

y_or_n = InlineKeyboardBuilder()
y_or_n.add(InlineKeyboardButton(text="Да", callback_data="yes"))
y_or_n.add(InlineKeyboardButton(text="Нет", callback_data="no"))
