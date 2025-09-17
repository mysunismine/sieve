# Sieve (локальный прототип)

Sieve — это умный поиск, который берёт ваш вопрос, быстро ищет подтверждения в интернете и возвращает понятный ответ с источниками.

Приложение делит работу на логичные слои:
- **Интерфейс** — простая веб-страница, похожая на чат, показывает ответ и ссылки.
- **API-роутеры** — эндпоинты FastAPI.
- **Сервисы** — бизнес-логика: запросы в Google, обращение к модели, сохранение истории.
- **Репозитории и валидаторы** — обрабатывают данные и гарантируют корректные параметры.
- **Общие ядра** — файлы с константами, текстами промтов и настройками логирования.

## Быстрый старт

1. Убедитесь, что установлен Python 3.11 или новее. Создайте виртуальное окружение и установите зависимости:
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
   uvicorn src.sieve.api.main:app --reload
   ```
4. Откройте [http://127.0.0.1:8000/](http://127.0.0.1:8000/) и отправьте вопрос. Ответ и источники появятся в блоках под формой.

## Как это работает под капотом

1. Пользователь отправляет вопрос через веб-форму.
2. Валидаторы проверяют текст и выбранную модель, чтобы защитить сервис от некорректных значений.
3. Сервис обращается к Google Custom Search и собирает релевантные ссылки.
4. Затем результаты и исходный запрос передаются в OpenAI Responses API — модель пишет короткий ответ и расставляет ссылки.
5. История обращений хранится в памяти, чтобы показать последние результаты и очищается по команде.

## Основные команды

- `uvicorn src.sieve.api.main:app --reload` — запуск локального сервера.
- `curl -X POST http://127.0.0.1:8000/api/ask -H "Content-Type: application/json" -d '{"query": "Новости Python"}'` — пример запроса без UI.

## Структура

```
.
├── src/
│   └── sieve/
│       ├── api/
│       │   ├── error_handlers.py
│       │   ├── main.py
│       │   └── routers/
│       │       ├── ask.py
│       │       ├── health.py
│       │       ├── history.py
│       │       └── index.py
│       ├── core/
│       │   ├── constants.py
│       │   ├── logging.py
│       │   └── prompts.py
│       ├── models/
│       │   ├── ask.py
│       │   └── history.py
│       ├── repositories/
│       │   └── history_repository.py
│       └── services/
│           ├── ask_service.py
│           ├── exceptions.py
│           ├── google.py
│           ├── history.py
│           ├── openai_client.py
│           ├── openai_payload.py
│           └── validators/
│               └── ask.py
├── templates/
│   └── index.html
├── docs/
│   ├── roadmap.md
│   ├── specification.md
│   ├── technical_assignment.md
│   └── test_cases.md
├── tests/
│   └── services/
│       ├── test_google.py
│       ├── test_history.py
│       └── test_openai_client.py
├── requirements.txt
├── .env.example
└── README.md
```

## Тестирование

- `pytest` — запуск набора тестов сервисного слоя.
- Текстовое описание сценариев приведено в `docs/test_cases.md`.

## Ограничения MVP

- Покрытие тестами ограничивается сервисным слоем; API и UI остаются без автоматических проверок.
- В случае ошибок внешних API сервис сообщает об этом, но не выполняет повторных попыток.
- Ответ отображается в виде текста без рендеринга полного Markdown.

Дальнейшие улучшения перечислены в `technical_description.txt`.
