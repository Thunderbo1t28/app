from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установка переменной окружения DJANGO_SETTINGS_MODULE для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Создание экземпляра Celery
celery_app = Celery('app')

# Загрузка конфигурации из Django settings.py
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач в приложениях Django
celery_app.autodiscover_tasks()
