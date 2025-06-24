# Codex Prompt — **Telegram Event Bot (MVP v0.1-rev2)**
_Скопируй этот документ в `docs/CONTRIBUTING.md`. Он — «каноническое ТЗ» для всех последующих PR._

---

## 0. Цель

Telegram-бот принимает анонсы мероприятий, хранит их, публикует ежедневный дайджест и выдаёт текст для Telegra.ph.
Первая версия работает на **SQLite-файле** (внутренний том Fly.io). Миграция во внешнюю PostgreSQL (Neon/Supabase) запланирована после стабилизации.

---

## 1. Очерёдность и детализация User Stories

| № | Как (роль) | Я хочу | Чтобы | Acceptance / бизнес-правила |
|---|------------|--------|-------|-----------------------------|
| **US-01** | 💼 **Система** | зарегистрировать первого пользователя как **суперадмина** | остальные функции были доступны только ему | `/start` → если таблица `admins` пуста → `user_id` записывается как `is_superadmin=True`. |
| **US-02** | 👤 Суперадмин | переслать пост боту | бот разобрал события и сохранил их | ① Передать текст → 4o.<br>② Получить массив JSON.<br>③ **Дедупликация**: сравнить `date(+time)` + `place` — если совпало с существующей записью, сформировать «объединённую» карточку (повторный запрос в 4o с добавлением старого описания).<br>④ `complete=false` → очередь модерации; `complete=true` → сразу в БД.<br>⑤ Исходное сырое сообщение сохраняем в поле `raw_text` (на будущее для Web UI). |
| **US-03** | 👤 Суперадмин | получить текст для **Telegra.ph** (`/telegraph`) | скопировать готовый Markdown | Шаблон *самостоятельный* (`templates/telegraph.md`).<br>События, созданные позднее 24 ч, автоматически помечаются `🚩` (красный флаг) перед заголовком. |
| **US-04** | 👤 Суперадмин | отредактировать событие | быстро поправить данные | `/events` → бот присылает пагинированный список: «🔹 {id} {title} ✏️».<br>Нажатие ✏️ → бот шлёт текущий JSON карточки **целиком**, админ редактирует, присылает обратно. Бот валидирует и сохраняет. |
| **US-05** | 👤 Суперадмин | добавить событие вручную (`/add`) | когда переслать нечего | Бот предлагает: «Отправить в LLM для сжатия? ✅/❌».<br>Если ✅ → 4o генерирует `short_desc` и теги; если ❌ → вводятся вручную. |
| **US-06** | 👤 Суперадмин | вызвать `/daily` | увидеть анонс в чате | Используется тот же шаблон, что и для автопубликации. |
| **US-07** | 👤 Суперадмин | настроить каналы и время | бот публиковал, куда нужно | `/channels` → бот показывает список каналов (кнопки «➕ добавить», «🗑️ удалить», «⏰ изменить время»). Данные хранятся в таблице `channels(chat_id, post_time)`. |
| **US-08** | ⏰ **Система** | публиковать ежедневный анонс по расписанию | контент выходил автоматически | Планировщик раз в минуту проверяет, «сейчас == post_time». Публикация → до 3 повторных попыток при ошибке HTTP-403/429, затем критичный лог. |

### Унифицированные требования к каждой US
- **Логирование** через `logging` (`INFO` → stdout, `ERROR` → таблица `logs`).
- **Тесты**: минимум unit-тест логики и интеграционный happy-path (pytest-asyncio).
- **Стиль**: `black + isort + ruff`.
- **Документация**: обновление `docs/CHANGELOG.md` + при необходимости схем.

---

## 2. Стек и файловая структура

telegram-event-bot/
├─ bot/
│ ├─ handlers/ # aiogram routers
│ ├─ services/ # parsing, scheduling, templates
│ └─ templates/
├─ db/
│ ├─ models.py # SQLModel (SQLite)
│ └─ seed.py
├─ templates/
│ ├─ event.md
│ ├─ daily.md
│ └─ telegraph.md
├─ docs/
│ ├─ PROMPTS.md # 4o prompt + canonical venues
│ ├─ USER_STORIES.md
│ ├─ ARCHITECTURE.md
│ └─ CHANGELOG.md
├─ tests/
├─ Dockerfile
├─ fly.toml
├─ requirements.txt
└─ README.md

* **Python 3.12  +  aiogram 3.x**  
* **SQLite** file → позже PostgreSQL  
* **jinja2** шаблоны  
* **httpx** для вызова 4o

---

## 3. Шаблоны

### `templates/event.md`
```
#### {{ title }}

{{ short_desc }}
{{ price_block }}

{{ date_time_line }}
```
`templates/daily.md`
см. предыдущую версию (идентично).

`templates/telegraph.md`
тот же формат, но без обёртки «НЕ ПРОПУСТИТЕ…» — только список событий (используется при ручном копировании).

## 4. Инструкция для 4o (файл docs/PROMPTS.md)
```
System: You are an experienced event-parser for Russian Telegram posts.

Task sequence:

1. Split the incoming text into separate events (1-N).
2. For each event return JSON object:
   title, short_desc (≤180 chars), date, end_date,
   time, end_time, place, city,
   price, source_url, tags[≤3],
   complete (true if title, date, place, city exist)
3. Use exact spelling from the canonical venue list (see below).
4. DO NOT hallucinate: absent → null.
5. Return ONLY a JSON array, no comments.

Canonical venues:
• Дом Семьи — Леонова 4
• Исторический парк Уйкул — Правдинск
• …

User: {raw_post}
```
(добавлять новые площадки просто редактируя список).

## 5. Секреты (Fly.io secrets)
```
keyvalue
TG_TOKENTelegram Bot API token
O4_API_KEYключ для 4o
WEBHOOK_URLURL для Telegram webhook (prod)
```

## 6. CI/CD
GitHub Actions:

lint → test → docker build → fly deploy (на main)

Review-поток: ветка feature → PR → ревью → merge.

Начни с US-01.
В каждом PR обязательно: код, тесты, обновлённая дока и строка в CHANGELOG.md.
Вопросы — в Issues репозитория.

