"""
Связный текстовый итог по раскладу без обращения к внешнему ИИ —
собирается из значений выпавших карт и вопроса пользователя.
"""

CONNECTORS = [
    "Начнём с того, что",
    "При этом",
    "Дальше добавляется вот что:",
    "Ещё один слой —",
    "И наконец,",
]


def build_summary(question: str, cards: list) -> str | None:
    if not cards:
        return None

    parts = []
    for i, c in enumerate(cards):
        snippet = c["meaning"].split(".")[0].strip()
        if snippet:
            snippet = snippet[0].lower() + snippet[1:]
        connector = CONNECTORS[i] if i < len(CONNECTORS) else "И ещё:"
        parts.append(
            f"{connector} на позиции «{c['position']}» — {c['card']}"
            f"{' (перевёрнута)' if c['reversed'] else ''}: {snippet}."
        )

    body = " ".join(parts)
    question = question.strip()
    if question:
        return f"По твоему вопросу «{question}»: {body}"
    return body
