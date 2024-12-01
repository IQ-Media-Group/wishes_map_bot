import re


def validate_phone_number(phone: str) -> tuple[bool, str]:
    # Убираем все символы, кроме цифр
    phone_digits = re.sub(r'\D', '', phone)

    # Проверяем, что номер состоит из 11 цифр и начинается с 7
    if len(phone_digits) == 11 and phone_digits.startswith('7'):
        return True, phone_digits

    # Проверка на возможность исправить код страны (например, если номер начинается с 8)
    if len(phone_digits) == 11 and phone_digits.startswith('8'):
        return True, '7' + phone_digits[1:]

    # Проверка на номер из 10 цифр (начинается с 9)
    if len(phone_digits) == 10 and phone_digits.startswith('9'):
        return True, '7' + phone_digits

    # Если номер не прошёл проверку, возвращаем False и исходный номер
    return False, phone