"""
Обращение к Claude API (Anthropic) для персональной трактовки расклада
под конкретный вопрос пользователя.

Требует переменную окружения ANTHROPIC_API_KEY. Если она не задана —
функция просто возвращает None, и приложение молча работает без ИИ-трактовки
(только карты и их базовые значения).
"""

import os
import httpx

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# claude-haiku-4-5 — быстро и дёшево, хорошо подходит для частых коротких
# трактовок. Для более глубокого текста можно заменить на "claude-sonnet-5".
MODEL = "claude-haiku-4-5-20251001"


def get_interpretation(question: str, deck_name: str, spread_name: str, cards: list) -> str | None:
    if not ANTHROPIC_API_KEY or not question.strip():
        return None

    cards_text = "\n".join(
        f"- {c['position']}: {c['card']}"
        f"{' (перевёрнута)' if c['reversed'] else ''} — {c['meaning']}"
        for c in cards
    )

    system = (
        "Ты — опытный таролог, который даёт тёплую, но честную трактовку. "
        f"Сейчас используется колода «{deck_name}» — выдерживай её тон и атмосферу. "
        "Пиши по-русски, связывай карты друг с другом и с вопросом человека, "
        "избегай общих фраз и воды, давай конкретный, применимый к жизни вывод. "
        "3–5 предложений, без списков и заголовков, обращайся на 'ты'."
    )
    user = (
        f"Вопрос человека: {question}\n"
        f"Расклад: {spread_name}\n"
        f"Карты:\n{cards_text}\n\n"
        "Дай итоговую трактовку, которая отвечает именно на этот вопрос, "
        "используя связку карт, а не пересказывая каждую по отдельности."
    )

    try:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": MODEL,
                "max_tokens": 400,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
            timeout=25,
        )
        resp.raise_for_status()
        data = resp.json()
        parts = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
        text = "\n".join(parts).strip()
        return text or None
    except Exception:
        return None
