# Таро · Матрица Судьбы — Telegram-бот с Web App

Состав проекта:
- `backend/app.py` — FastAPI-сервер: отдаёт Web App и API (`/api/tarot/draw`, `/api/matrix/calculate`)
- `backend/bot.py` — сам Telegram-бот (aiogram), открывает Web App кнопкой
- `backend/tarot_data.py` — колода из 78 карт с трактовками
- `backend/matrix.py` — расчёт матрицы судьбы
- `webapp/` — интерфейс (HTML/CSS/JS), открывается внутри Telegram

## 1. Получить токен бота
В Telegram: @BotFather → `/newbot` → задать имя и username. Сохранить токен.

## 2. Задеплоить на Railway (без сервера и консоли)
1. Зарегистрируйся на railway.app через GitHub.
2. Залей эту папку в новый репозиторий на GitHub (можно через веб-интерфейс GitHub — просто перетащить файлы, без git-команд).
3. В Railway: **New Project → Deploy from GitHub repo** → выбери репозиторий.
4. Railway должен предложить запустить `backend/app.py` (FastAPI/uvicorn). Если нет — в настройках сервиса укажи:
   - Root Directory: `backend`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. После деплоя Railway выдаст публичный домен вида `https://твой-проект.up.railway.app` — это и есть `WEBAPP_URL`.
6. Создай **второй сервис** в том же проекте для самого бота:
   - Root Directory: `backend`
   - Start Command: `python bot.py`
   - Переменные окружения: `BOT_TOKEN=<токен от BotFather>`, `WEBAPP_URL=<домен из шага 5>`

## 3. Подключить кнопку Web App в самом Telegram (необязательно, но красиво)
В @BotFather: `/mybots` → выбери бота → **Bot Settings → Menu Button** → укажи тот же `WEBAPP_URL`.
Тогда кнопка открытия приложения будет всегда рядом с полем ввода сообщения.

## 4. Проверка локально (если понадобится)
```
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
# в отдельном терминале, указав BOT_TOKEN и WEBAPP_URL (например, ngrok-адрес):
python bot.py
```
Локально Web App нужно пробросить наружу через https (например, ngrok), Telegram не откроет `http://localhost`.

## Что стоит доработать дальше
- Тексты младших арканов (56 карт) сгенерированы по шаблону масть+ранг — рабочие и осмысленные, но для премиум-ощущения стоит заменить на полностью авторские формулировки.
- Алгоритм матрицы судьбы — рабочая версия классического метода; при желании можно уточнить трактовки конкретно под матричные позиции (сейчас переиспользуются описания арканов Таро).
- Оплата платных раскладов — через Telegram Payments API или Telegram Stars, добавляется отдельным шагом в `bot.py`.
