from django.core.management.base import BaseCommand
import os
import stat
from django.conf import settings

class Command(BaseCommand):
    help = 'Создает необходимые директории с правильными правами доступа'

    def handle(self, *args, **options):
        # Список директорий для создания
        directories = [
            os.path.join(settings.BASE_DIR, 'data'),
            os.path.join(settings.BASE_DIR, 'data', 'backtests'),
            os.path.join(settings.BASE_DIR, 'data', 'backtests', 'first'),
            os.path.join(settings.BASE_DIR, 'private'),
        ]

        for directory in directories:
            try:
                if not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                    self.stdout.write(self.style.SUCCESS(f'Создана директория: {directory}'))
                
                # Устанавливаем полные права доступа
                os.chmod(directory, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                self.stdout.write(self.style.SUCCESS(f'Установлены права доступа для: {directory}'))
                
                # Проверяем права на запись
                test_file = os.path.join(directory, 'test.txt')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    self.stdout.write(self.style.SUCCESS(f'Проверка прав записи успешна для: {directory}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Ошибка при проверке прав записи для {directory}: {str(e)}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка при настройке директории {directory}: {str(e)}')) 