# Поиск+Модель (локальный прототип)

Минимальный сервис на FastAPI, который принимает текстовый запрос, выполняет поиск в Google Programmable Search Engine, передает результаты в OpenAI Responses API и показывает ответ со сносками в интерфейсе, напоминающем ChatGPT с браузингом.

## Быстрый старт

1. Создайте виртуальное окружение и установите зависимости:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Скопируйте файл `.env.example` в `.env` и заполните значения:
   ```bash
   cp .env.example .env
   ```
   - `GOOGLE_API_KEY` — ключ для Google Custom Search JSON API.
   - `GOOGLE_CSE_ID` — идентификатор Programmable Search Engine.
   - `OPENAI_API_KEY` — ключ OpenAI c доступом к Responses API.
   - При необходимости измените `OPENAI_MODEL` и `OPENAI_BASE_URL`.
3. Запустите сервер разработки:
   ```bash
   uvicorn src.vibechecker.api.main:app --reload
   ```
4. Откройте [http://127.0.0.1:8000/](http://127.0.0.1:8000/) и отправьте вопрос. Ответ и источники появятся в блоках под формой.

## Основные команды

- `uvicorn src.vibechecker.api.main:app --reload` — запуск локального сервера.
- `curl -X POST http://127.0.0.1:8000/api/ask -H "Content-Type: application/json" -d '{"query": "Новости Python"}'` — пример запроса без UI.

## Структура

```
.
├── src/
│   └── vibechecker/
│       ├── api/
│       │   └── main.py
│       ├── models/
│       │   └── ask.py
│       └── services/
│           ├── google.py
│           └── openai_client.py
├── templates/
│   └── index.html
├── docs/
│   ├── roadmap.md
│   ├── specification.md
│   └── technical_assignment.md
├── requirements.txt
├── .env.example
└── README.md
```

## Ограничения MVP

- Нет автоматических тестов, кешей и долговременного хранения истории.
- В случае ошибок внешних API сервис сообщает об этом, но не выполняет повторных попыток.
- Ответ отображается в виде текста без рендеринга полного Markdown.

Дальнейшие улучшения перечислены в `technical_description.txt`.
