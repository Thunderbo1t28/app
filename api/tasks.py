# tasks.py
import json
from celery import shared_task
from django.core.management import call_command
from django.core.management.base import CommandError
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

@shared_task
def run_management_command_task(command, **kwargs):
    try:
        '''if 'instrument' in kwargs and isinstance(kwargs['instrument'], list):
            kwargs['instrument'] = ' '.join(kwargs['instrument'])'''  # Преобразование списка в строку с пробелами

        logger.info(f"Running command: {command} with arguments: {kwargs}")

        if command == 'run_backtest':
            # Извлекаем аргументы из kwargs в нужном порядке
            instrument = kwargs.get('instrument', 'AFKS,ALRS')
            currency = kwargs.get('currency', 'RUB')
            capital = kwargs.get('capital', 2000000.0)
            target = kwargs.get('target', 25.0)

            # Передаем аргументы как позиционные
            args = [instrument, currency, capital, target]
            res = call_command(command, *args)
            output_dict = json.loads(res)
            return {'status': 'success', 'output': output_dict}

        elif command == 'load_to_database':
            res = call_command(command)
            output_dict = json.loads(res)
            return {'status': 'success', 'output': output_dict}
    
    except CommandError as e:
        logger.error(f"CommandError: {e}")
        return {'status': 'failure', 'output': str(e)}
    except Exception as e:
        logger.error(f"Exception: {e}")
        return {'status': 'failure', 'output': str(e)}
