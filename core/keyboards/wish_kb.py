from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

instruction = InlineKeyboardBuilder()
instruction.add(InlineKeyboardButton(text="Инструкция", callback_data="instruction"))

instruction_2 = InlineKeyboardBuilder()
instruction_2.add(InlineKeyboardButton(text="Инструкция", callback_data="instruction"))
instruction_2.add(InlineKeyboardButton(text="Посмотреть лунный календарь", callback_data="moon_calendar"))
instruction_2.add(InlineKeyboardButton(text="Запустить магию", callback_data="start_magic"))
instruction_2.max_width = 1
instruction_2.adjust(1)

instruction_3 = InlineKeyboardBuilder()
instruction_3.add(InlineKeyboardButton(text="Инструкция", callback_data="instruction"))
instruction_3.add(InlineKeyboardButton(text="Посмотреть лунный календарь", callback_data="moon_calendar"))
instruction_3.max_width = 1
instruction_3.adjust(1)

y_or_n = InlineKeyboardBuilder()
y_or_n.add(InlineKeyboardButton(text="Да", callback_data="yes"))
y_or_n.add(InlineKeyboardButton(text="Нет", callback_data="no"))

final_kb = InlineKeyboardBuilder()
final_kb.add(InlineKeyboardButton(text="Предзапись в академию Norland", url="https://norland.academy/anketa"))
