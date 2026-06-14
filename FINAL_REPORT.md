# Финальный технический отчёт
## Проект: Трекер привычек (Habit Tracker)

---

## Содержание

1. [Описание системы](#1-описание-системы)
2. [Выбор технологий](#2-выбор-технологий-и-обоснование)
3. [Архитектура приложения](#3-архитектура-приложения)
4. [Этапы разработки](#4-этапы-разработки)
5. [База данных](#5-база-данных)
6. [Тестирование](#6-тестирование)
7. [Контейнеризация (Docker)](#7-контейнеризация-docker)
8. [CI/CD Pipeline](#8-cicd-pipeline)
9. [Безопасность](#9-безопасность)
10. [Выводы](#10-выводы)

---

## 1. Описание системы

**Трекер привычек** — веб-приложение, которое позволяет пользователю создавать ежедневные привычки, отмечать их выполнение и отслеживать прогресс в виде «растущего цветка».

### Функциональность

| Функция | Описание |
|---|---|
| Просмотр списка | Все привычки на главной, невыполненные — первыми |
| Добавление | Форма с валидацией (не пустой заголовок, max 200 символов) |
| Отметка выполнения | Один раз в день; повторная отметка игнорируется |
| Удаление | С подтверждением через `confirm()` в браузере |
| Streak | Счётчик непрерывных дней выполнения |
| Визуализация | Emoji-цветок, растущий со streak |
| Статистика | Общее число привычек, выполнений, лучший streak |

---

## 2. Выбор технологий

### Python 3.12

Основной язык. Python выбран как самый распространённый язык для backend-разработки начального и среднего уровня. Версия 3.12 — актуальная стабильная, с улучшенными сообщениями об ошибках и ускоренным интерпретатором.

### Flask

Минималистичный веб-фреймворк.

### SQLite

Встраиваемая база данных без отдельного сервера.

### Gunicorn

WSGI-сервер для production.

### Docker

Контейнеризация гарантирует одинаковое поведение на любой машине. Использован многоэтапный build для минимизации размера образа.

### GitHub Actions

CI/CD прямо в репозитории. Три независимых job-а:
1. `check-code` — форматирование, линтер, тесты, аудит уязвимостей
2. `semgrep` — статический анализ безопасности
3. `docker-check` — сборка и smoke-тест образа

### Black + Flake8

- **Black** — автоформаттер. Применяет единый стандарт стиля кода.
- **Flake8** — линтер. Ловит ошибки (неиспользуемые импорты, слишком длинные строки).

### Semgrep + pip-audit

- **Semgrep** — статический анализ с кастомными правилами безопасности.
- **pip-audit** — аудит зависимостей на известные CVE.

---

## 3. Архитектура приложения

### Структура файлов

```
FLS_INTR_TO_SP/
├── app.py                      # Бизнес-логика + Flask-маршруты
├── requirements.txt            # Python-зависимости
├── Dockerfile                  # Multi-stage Docker build
├── .dockerignore
├── .gitignore
├── .flake8                     # Конфигурация линтера
├── sbom.json                   # Software Bill of Materials (CycloneDX)
│
├── database/
│   └── schema.sql              # DDL: создание таблиц
│
├── templates/                  # Jinja2-шаблоны
│   ├── base.html               # Базовый layout (header, footer, nav)
│   ├── index.html              # Главная страница
│   ├── add_habit.html          # Форма добавления
│   └── stats.html              # Страница статистики
│
├── static/
│   ├── css/style.css           # Дизайн
│   └── js/script.js            # Подтверждение удаления
│
├── tests/                      # Тестовый пакет
│   ├── conftest.py             # pytest-фикстура client
│   ├── test_unit.py            # Юнит-тесты (get_flower_stage)
│   ├── test_functional.py      # Функциональные тесты (HTTP)
│   └── test_integration.py     # Интеграционный тест (full flow)
│
└── .github/
    └── workflows/
        └── ci.yml              # GitHub Actions Pipeline
```

### Паттерн MVC (упрощённый)

```
Браузер
   │  HTTP-запрос
   ▼
Flask Router (app.py)       ← Controller
   │
   ├── SQLite (database/)   ← Model
   │
   └── Jinja2 (templates/)  ← View
```

### Маршруты

| Метод | URL | Функция | Описание |
|---|---|---|---|
| GET | `/` | `index()` | Список привычек |
| GET | `/add` | `add_habit()` | Форма добавления |
| POST | `/add` | `add_habit()` | Сохранить привычку |
| POST | `/complete/<id>` | `complete_habit()` | Отметить выполнение |
| POST | `/delete/<id>` | `delete_habit()` | Удалить привычку |
| GET | `/stats` | `stats()` | Страница статистики |

---

## 4. Этапы разработки

Разработка велась итерационно через feature-ветки с merge в `main` через Pull Request.

### Этап 1 — MVP (ветка `dz2`)

Первый рабочий прототип:
- Flask-приложение с базовыми маршрутами
- SQLite с инициализацией через `schema.sql`
- HTML-шаблоны с Jinja2
- Алгоритм подсчёта streak

### Этап 2 — CI/CD (ветка `ci` → `feat/docker-and-ci`)

Настройка автоматических проверок:
- GitHub Actions с job `check-code`: black, flake8, pytest
- Multi-stage Dockerfile с Gunicorn
- Job `docker-check`: сборка образа + `curl` smoke-test

### Этап 3 — Тестирование (ветка `feat/testing`)

Написаны три уровня тестов с использованием `pytest` и `pytest-cov`:
- **Юнит-тесты** — проверка `get_flower_stage()`
- **Функциональные** — HTTP-запросы через `test_client`
- **Интеграционный** — полный сценарий: создать → выполнить → проверить → удалить

Добавлен `conftest.py` с фикстурой, использующей `tmp_path` для изоляции БД.

### Этап 4 — Безопасность (ветки `feat/static-analysis`, `feat/dependency-analysis`)

- Написаны кастомные правила Semgrep (2 правила)
- Добавлен job `semgrep` в CI, зависящий от `check-code`
- `pip-audit` для аудита CVE в зависимостях
- Сгенерирован SBOM (Software Bill of Materials) в формате CycloneDX JSON

---

## 5. База данных

### Схема

```sql
CREATE TABLE IF NOT EXISTS habits (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS completions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id       INTEGER NOT NULL,
    completed_date TEXT NOT NULL,
    FOREIGN KEY (habit_id) REFERENCES habits(id),
    UNIQUE (habit_id, completed_date)
);
```

---

## 6. Тестирование

### Структура тестов

```
tests/
├── conftest.py           # Общая фикстура
├── test_unit.py          # 9 тестов — чистая функция
├── test_functional.py    # 8 тестов — HTTP
└── test_integration.py   # 1 тест — end-to-end
```

### conftest.py — изоляция через tmp_path

```python
@pytest.fixture
def client(monkeypatch, tmp_path):
    db = str(tmp_path / "test.db")
    monkeypatch.setattr(app_module, "DATABASE_PATH", db)
    app_module.init_db()
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c
```

`monkeypatch.setattr` подменяет путь к БД на временную директорию pytest — каждый тест получает чистую БД.

### Юнит-тесты (test_unit.py)

Тестируют `get_flower_stage()` — чистую функцию без зависимостей:

```python
def test_flower_zero():    assert get_flower_stage(0) == "🌰"
def test_flower_one():     assert get_flower_stage(1) == "🌱"
def test_flower_three():   assert get_flower_stage(3) == "🌿"
def test_flower_six():     assert get_flower_stage(6) == "🌸"
def test_flower_eleven():  assert get_flower_stage(11) == "🌻"
```

### Функциональные тесты (test_functional.py)

```python
def test_add_habit(client):
    client.post("/add", data={"title": "Читать книгу"})
    r = client.get("/")
    assert "Читать книгу" in r.data.decode("utf-8")

def test_complete_twice(client):
    client.post("/add", data={"title": "Пить воду"})
    client.post("/complete/1")
    r = client.post("/complete/1")  # повторная отметка
    assert r.status_code == 302     # не должно быть ошибки

def test_delete_habit(client):
    client.post("/add", data={"title": "Медитация"})
    client.post("/delete/1")
    r = client.get("/")
    assert "Медитация" not in r.data.decode("utf-8")
```

### Интеграционный тест (test_integration.py)

Полный жизненный цикл привычки:

```python
def test_full_flow(client):
    client.post("/add", data={"title": "Спорт"})       # создать
    r = client.get("/")
    assert "Спорт" in r.data.decode("utf-8")            # видна на главной

    client.post("/complete/1")                          # выполнить
    r2 = client.get("/stats")
    assert "Спорт" in r2.data.decode("utf-8")           # видна в статистике

    client.post("/delete/1")                            # удалить
    r3 = client.get("/")
    assert "Спорт" not in r3.data.decode("utf-8")       # исчезла
```

### Запуск тестов с покрытием

```bash
pytest --cov=app --cov-report=term-missing -v
```

---

## 8. Контейнеризация (Docker)

### Multi-stage Dockerfile

```dockerfile
# --- Этап 1: сборка зависимостей ---
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install \
    Flask==3.0.3 \
    gunicorn==23.0.0

# --- Этап 2: финальный образ ---
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/app/data/habits.db

WORKDIR /app
COPY --from=builder /install /usr/local
COPY database/schema.sql database/schema.sql
COPY templates/ templates/
COPY static/ static/
COPY app.py .

# Безопасность: непривилегированный пользователь
RUN useradd --no-create-home --shell /bin/false appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app
USER appuser

VOLUME /app/data
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", \
     "--access-logfile", "-", "app:app"]
```

### Запуск

```bash
docker build -t habit-tracker .

docker run -d \
  -p 8080:5000 \
  -v habit-data:/app/data \
  --name habits \
  habit-tracker
# Приложение: http://localhost:8080
```

---

## 9. CI/CD Pipeline

### Схема pipeline

```
push / pull_request
        │
        ▼
  ┌─────────────┐
  │ check-code  │   black · flake8 · pytest --cov · pip-audit
  └──────┬──────┘
         │ needs: check-code
         ▼
  ┌─────────────┐
  │   semgrep   │   custom rules: .semgrep/rules.yml
  └──────┬──────┘
         │ needs: check-code + semgrep
         ▼
  ┌──────────────┐
  │ docker-check │   build → run → curl → logs → stop
  └──────────────┘
```

### ci.yml — ключевые шаги

```yaml
jobs:
  check-code:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements.txt
      - run: black --check .
      - run: flake8 .
      - run: pytest --cov=app --cov-report=term-missing -v
      - run: pip-audit -r requirements.txt

  semgrep:
    needs: check-code
    steps:
      - run: pip install semgrep
      - run: semgrep --config=.semgrep/rules.yml --error app.py

  docker-check:
    needs: [check-code, semgrep]
    steps:
      - run: docker build -t habit-tracker .
      - run: docker run -d -p 8080:5000 --name habits-test habit-tracker
      - run: sleep 5
      - run: curl -f http://localhost:8080
      - run: docker logs habits-test
```

**`needs`** создаёт зависимость между job-ами: `docker-check` запускается только если `check-code` и `semgrep` завершились успешно. Это предотвращает сборку образа из «сломанного» кода.

---

## 10. Безопасность

### Кастомные правила Semgrep (.semgrep/rules.yml)

#### Правило 1: Flask debug mode

```yaml
- id: flask-run-without-debug-false
  patterns:
    - pattern: $APP.run()
  message: >
    app.run() without debug=False exposes the Werkzeug interactive
    debugger in production, allowing arbitrary code execution.
  severity: ERROR
  languages: [python]
  metadata:
    category: security
    cwe: CWE-94
```

**Устранение в коде:**
```python
if __name__ == "__main__":
    app.run(debug=False)  # явно отключён debug
```

#### Правило 2: Hardcoded secret key

```yaml
- id: flask-hardcoded-secret-key
  pattern: $APP.secret_key = "..."
  message: >
    SECRET_KEY is hardcoded. Use os.environ.get() instead.
  severity: ERROR
  metadata:
    cwe: CWE-798
```

**Устранение в коде:**
```python
app.secret_key = os.environ.get("SECRET_KEY", "dev")
# В production SECRET_KEY задаётся через переменную окружения
```

### pip-audit — аудит CVE

```bash
pip-audit -r requirements.txt
```

Проверяет каждую зависимость из `requirements.txt` по базе PyPI Advisory Database. Запускается автоматически в CI.

### SBOM (Software Bill of Materials)

Сгенерирован файл `sbom.json` в формате **CycloneDX 1.4** — стандарт для описания состава программного обеспечения. Содержит 22 компонента с версиями (Flask 3.1.3, Jinja2 3.1.6, Werkzeug 3.1.8 и др.).

### Меры безопасности: сводка

| Угроза | Мера защиты |
|---|---|
| SQL-инъекция | Параметризованные запросы (`?`-плейсхолдеры) |
| XSS | Jinja2 экранирует HTML по умолчанию |
| Дублирование данных | `UNIQUE` constraint + `INSERT OR IGNORE` |
| Небезопасный debug | Правило Semgrep + `debug=False` |
| Утечка secret key | Только через `os.environ.get()` |
| Уязвимые зависимости | pip-audit в CI |
| Root-процесс в контейнере | `USER appuser` в Dockerfile |
| Попадание секретов в образ | `.dockerignore` исключает `.env*` |

---

## 10. Выводы

### Достигнутые результаты

В ходе выполнения проекта был реализован полный цикл разработки веб-приложения: от проектирования архитектуры до внедрения CI/CD пайплайна и практик DevSecOps.

**Ключевые инженерные решения:**
- **Backend-архитектура:** Использование Flask обеспечило минималистичную и прозрачную структуру приложения. Внедрение паттерна MVC позволило отделить бизнес-логику от представления и взаимодействия с базой данных.
- **Работа с данными:** Применение SQLite с принудительным контролем ссылочной целостности (`PRAGMA foreign_keys = ON`) и ограничениями (`UNIQUE`, `NOT NULL`) гарантирует консистентность данных на уровне СУБД, защищая от дублирования и аномалий.
- **Контейнеризация:** Использование multi-stage сборок Docker существенно сократило размер финального образа. Разграничение прав доступа (запуск процесса от непривилегированного пользователя `appuser`) и использование `VOLUME` для персистентности данных обеспечили готовность контейнера к безопасному развертыванию.
- **Автоматизация и CI/CD:** Настроенный пайплайн GitHub Actions полностью автоматизировал процессы проверки качества кода (Black, Flake8), запуска тестирования (pytest с покрытием) и валидации Docker-образа. Использование зависимостей между job-ами (`needs`) исключило возможность деплоя нестабильных сборок.
- **Безопасность (DevSecOps):** Интеграция статического анализа (Semgrep) с кастомными правилами, регулярный аудит зависимостей (pip-audit) и генерация SBOM позволили внедрить процессы выявления уязвимостей (Shift-Left Security) на ранних этапах CI.

### Перспективы развития

Для дальнейшего масштабирования и улучшения приложения целесообразно внедрить следующие архитектурные и функциональные изменения:
- **Многопользовательская архитектура:** Добавление модуля аутентификации (JWT или сессионные cookie) и авторизации, изоляция данных между профилями пользователей.
- **Внедрение ORM:** Переход на SQLAlchemy для повышения безопасности (защита от сложных SQL-инъекций), удобства миграций (с использованием Alembic) и абстрагирования от конкретного SQL-диалекта.
- **Оптимизация производительности:** Внедрение пагинации (offset/limit) на страницу статистики для обеспечения стабильной работы при большом объеме исторических данных.
- **Расширение тестирования:** Внедрение изолированных модульных тестов для алгоритмов расчёта прогресса (streak) с применением mock-объектов.

### Итог

Проект прошел успешную эволюцию от базового MVP до production-ready сервиса:

```text
MVP → CI/CD Pipeline → Docker Containers → Automated Tests → Security & SBOM
```

Разработанная система демонстрирует применение современных индустриальных стандартов промышленной разработки ПО. Настроенный CI/CD пайплайн выполняет роль строгого гейтвей-контроля, не позволяя интегрировать код с проблемами форматирования, архитектурными уязвимостями или сломанными тестами.
