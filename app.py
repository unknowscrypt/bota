import random
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from tarot_data import FULL_DECK, SPREADS, build_deck, DECK_NAMES
from matrix import calculate_matrix, validate_date
from classify import classify_question, pick_deck
from ai_interpret import get_interpretation
from summary import build_summary

app = FastAPI(title="Tarot & Matrix API")

APP_DIR = Path(__file__).resolve().parent


class MatrixRequest(BaseModel):
    day: int
    month: int
    year: int


@app.get("/api/spreads")
def get_spreads():
    return SPREADS


@app.get("/api/tarot/draw")
def draw_tarot(spread: str = "one_card", question: str = ""):
    if spread not in SPREADS:
        raise HTTPException(status_code=400, detail="Неизвестный расклад")

    category = classify_question(question)
    deck_style = pick_deck(category)
    deck = build_deck(deck_style)

    count = len(SPREADS[spread]["positions"])
    cards = random.sample(deck, count)
    result = []
    for position, card in zip(SPREADS[spread]["positions"], cards):
        reversed_ = random.random() < 0.35
        result.append({
            "position": position,
            "card": card["name"],
            "emoji": card["emoji"],
            "reversed": reversed_,
            "meaning": card["reversed"] if reversed_ else card["upright"],
        })
    spread_name = SPREADS[spread]["name"]
    interpretation = get_interpretation(question, DECK_NAMES[deck_style], spread_name, result) \
        or build_summary(question, result)

    return {
        "spread": spread_name,
        "deck": DECK_NAMES[deck_style],
        "category": category,
        "question": question,
        "cards": result,
        "interpretation": interpretation,
    }


@app.post("/api/matrix/calculate")
def matrix_calculate(req: MatrixRequest):
    if not validate_date(req.day, req.month, req.year):
        raise HTTPException(status_code=400, detail="Некорректная дата рождения")
    return calculate_matrix(req.day, req.month, req.year)


@app.get("/")
def index():
    return FileResponse(APP_DIR / "index.html")


@app.get("/style.css")
def style():
    return FileResponse(APP_DIR / "style.css", media_type="text/css")


@app.get("/script.js")
def script():
    return FileResponse(APP_DIR / "script.js", media_type="application/javascript")
