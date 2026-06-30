from datetime import datetime
from typing import Optional, List


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Парсит дату из строки с поддержкой разных форматов."""
    if not dt_str:
        return None
    
    try:
        # Убираем Z и +00:00 если есть
        dt_str_clean = dt_str.replace('Z', '+00:00')
        return datetime.fromisoformat(dt_str_clean)
    except ValueError:
        try:
            # Пробуем без миллисекунд
            if '.' in dt_str:
                dt_str_clean = dt_str.split('.')[0] + '+00:00'
            else:
                dt_str_clean = dt_str
            return datetime.fromisoformat(dt_str_clean)
        except ValueError:
            print(f"⚠️ Не удалось распарсить дату: {dt_str}")
            return None


def format_date_ru(created_at: datetime) -> str:
    """
    Русская версия форматирования даты.
    """
    if not created_at:
        return "сегодня"
    
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