# SQL Agent Demo

Интеллектуальный SQL агент для работы с базой данных PostgreSQL, использующий возможности ИИ для генерации и выполнения SQL запросов.

## Возможности

- 🤖 Интеллектуальная генерация SQL запросов с помощью ИИ
- 🗄️ Работа с PostgreSQL базой данных
- 🌐 Веб-интерфейс для взаимодействия с агентом
- 📊 Аналитика и визуализация данных
- 🔧 REST API для интеграции

## Быстрый старт

### Локальная разработка

```bash
# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp env.example .env
# Отредактируйте .env файл, указав ваши настройки AI Gateway

# Запуск приложения
bash dev.sh  # На Windows: python main.py
```

### Развертывание с Docker

#### Простой запуск

1. **Настройка окружения:**
   ```bash
   # Скопируйте файл конфигурации
   cp docker.env .env
   
   # Отредактируйте .env файл, указав ваши настройки:
   # - AI_GATEWAY_URL: URL вашего AI Gateway
   # - AI_GATEWAY_API_KEY: API ключ для доступа к ИИ
   ```

2. **Запуск приложения:**
   ```bash
   docker-compose up --build -d
   ```

3. **Доступ к приложению:**
   - Веб-интерфейс: http://localhost:8000
   - PostgreSQL: localhost:5432

#### Ручной запуск Docker Compose

```bash
# Сборка и запуск всех сервисов
docker-compose up --build -d

# Просмотр логов
docker-compose logs -f app

# Остановка сервисов
docker-compose down
```


## Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `AI_GATEWAY_URL` | URL AI Gateway для ИИ | - |
| `AI_GATEWAY_API_KEY` | API ключ для AI Gateway | - |
| `DB_CONNECTION_STRING` | Строка подключения к PostgreSQL | Настроена для Docker |
| `LLM_MODEL` | Модель ИИ для генерации SQL | `qwen3-coder` |
| `SCHEMA_NAME` | Имя схемы базы данных | `public` |

### Структура проекта

```
sql_agent_demo/
├── agents/              # SQL агенты и инструменты
├── analytics/           # Аналитические сервисы
├── controller/          # API контроллеры
├── database/            # Работа с базой данных
├── llm/                 # Интеграция с ИИ
├── static/              # Статические файлы веб-интерфейса
├── Dockerfile           # Конфигурация Docker
├── docker-compose.yml   # Основная конфигурация Docker Compose
```

## Полезные команды

### Docker

```bash
# Перезапуск приложения
docker-compose restart app

# Просмотр логов конкретного сервиса
docker-compose logs -f postgres

# Подключение к базе данных
docker-compose exec postgres psql -U postgres -d PurchaseService

# Очистка данных (удаление volumes)
docker-compose down -v

# Пересборка без кеша
docker-compose build --no-cache
```

### Разработка

```bash
# Запуск тестов
python test.py

# Просмотр структуры базы данных
python -c "from database.db_schema_service import *; print('Schema loaded')"
```

## Требования

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (для контейнеризации)
- Доступ к AI Gateway (OpenAI, Anthropic или совместимый API)

## Лицензия

Проект распространяется под лицензией, указанной в файле LICENSE.