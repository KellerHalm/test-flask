# Тестирование веб-приложения на Flask

### Клонируем репозиторий
``` bash 
git clone https://github.com/KellerHalm/test-flask
```

### Устанавливаем зависимости
``` bash
pip install pytest httpx asyncio threading flask flask_sqlalchemy
```

### Запускаем тесты
``` bash
pytest test_app.py -v
```

Веб-приложение запускать необязательно. При запуске теста веб-приложение запускается автоматически
