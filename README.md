# Systematic Trading Platform

Платформа для систематической торговли, построенная на Django с использованием современных практик разработки.

## Функциональность

- Автоматизированная торговля на различных рынках
- Бэктестинг торговых стратегий
- API для интеграции с брокерами
- Система управления рисками
- Аналитические инструменты

## Требования

- Python 3.8+
- Redis
- PostgreSQL (опционально)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/systematic-trading.git
cd systematic-trading
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements/dev.txt  # для разработки
pip install -r requirements/base.txt # для продакшена
```

4. Создайте файл .env на основе .env.example:
```bash
cp .env.example .env
```

5. Примените миграции:
```bash
python manage.py migrate
```

6. Запустите сервер разработки:
```bash
python manage.py runserver
```

## Структура проекта

- `api/` - REST API endpoints
- `syscore/` - Базовые классы и утилиты
- `sysbrokers/` - Интеграция с брокерами
- `sysdata/` - Работа с данными
- `systems/` - Торговые системы
- `backtest/` - Бэктестинг
- `requirements/` - Зависимости проекта

## Разработка

### Запуск тестов
```bash
pytest
```

### Линтинг
```bash
flake8
black .
isort .
```

### Документация
```bash
cd docs
make html
```

## API Documentation

API документация доступна по адресу `/api/docs/` после запуска сервера.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 