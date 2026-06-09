from datetime import datetime

def format_date_ru(created_at: datetime) -> str:
    """
    Русская версия форматирования даты.

    Правила:
    - Сегодня: "сегодня"
    - Вчера: "вчера"
    - До недели: "X дней назад" (с правильным склонением)
    - В этом году: "2 июня"
    - В прошлые годы: "3 декабря 2025"
    """
    now = datetime.now()
    diff = now - created_at

    if diff.days == 0:
        return "сегодня"

    if diff.days == 1:
        return "вчера"

    if diff.days < 7:
        days = diff.days
        if days % 10 == 1 and days != 11:
            return f"{days} день назад"
        elif days % 10 in [2, 3, 4] and days not in [12, 13, 14]:
            return f"{days} дня назад"
        else:
            return f"{days} дней назад"

    months_ru = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]

    if created_at.year == now.year:
        return f"{created_at.day} {months_ru[created_at.month - 1]}"

    return f"{created_at.day} {months_ru[created_at.month - 1]} {created_at.year}"