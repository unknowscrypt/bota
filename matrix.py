"""
Расчёт Матрицы Судьбы (нумерологический квадрат/октаграмма по дате рождения).
Классический алгоритм: числа дня/месяца/года сводятся к аркану 1–22,
затем комбинируются попарно, образуя 8 ключевых точек схемы.

Это работающая реализация популярного метода. Тексты трактовок — по мотивам
22 арканов Таро; при желании их стоит заменить на собственные авторские
формулировки под матрицу (в этом стартере они переиспользуются из tarot_data
для скорости запуска).
"""

from datetime import date
from tarot_data import MAJOR_ARCANA


def _reduce(n: int) -> int:
    """Сводит число к диапазону 1–22 через сумму цифр."""
    while n > 22:
        n = sum(int(d) for d in str(n))
    return n if n != 0 else 22


def _arcana(n: int) -> dict:
    n = max(1, min(22, n))
    card = MAJOR_ARCANA[n - 1]
    return {"number": n, "name": card["name"], "emoji": card["emoji"], "meaning": card["upright"]}


def calculate_matrix(day: int, month: int, year: int) -> dict:
    a = _reduce(day)
    b = _reduce(month)
    c = _reduce(sum(int(d) for d in str(year)))
    d = _reduce(a + b + c)
    e = _reduce(a + d)
    f = _reduce(b + d)
    g = _reduce(c + d)
    h = _reduce(e + f + g)

    points = [
        {"code": "A", "label": "Таланты и жизненный путь", "source": "день рождения", **_arcana(a)},
        {"code": "B", "label": "Энергия рода, связь с родителями", "source": "месяц рождения", **_arcana(b)},
        {"code": "C", "label": "Материальный мир и финансовый поток", "source": "год рождения", **_arcana(c)},
        {"code": "D", "label": "Предназначение", "source": "A + B + C", **_arcana(d)},
        {"code": "E", "label": "Женская энергия", "source": "A + D", **_arcana(e)},
        {"code": "F", "label": "Мужская энергия", "source": "B + D", **_arcana(f)},
        {"code": "G", "label": "Гармония в отношениях", "source": "C + D", **_arcana(g)},
        {"code": "H", "label": "Родовая задача и баланс", "source": "E + F + G", **_arcana(h)},
    ]

    return {
        "birth_date": f"{day:02d}.{month:02d}.{year}",
        "points": points,
    }


def validate_date(day: int, month: int, year: int) -> bool:
    try:
        date(year, month, day)
        return 1900 <= year <= date.today().year
    except ValueError:
        return False
