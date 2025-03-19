from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import os
import yaml
import psutil
import datetime
import logging
import subprocess
import sys
from django.conf import settings
from django.core.management import call_command

logger = logging.getLogger(__name__)

class SystemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def _read_config(self, filename):
        try:
            full_path = os.path.join(settings.BASE_DIR, filename)
            with open(full_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return None

    def _write_config(self, filename, content):
        full_path = os.path.join(settings.BASE_DIR, filename)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(content)

    def _check_system_status(self):
        """Проверяет реальный статус системы"""
        try:
            # Проверяем наличие файла с PID
            pid_file = os.path.join(settings.BASE_DIR, 'private', 'system.pid')
            if not os.path.exists(pid_file):
                logger.info("PID file not found, system is stopped")
                return "stopped", None

            # Читаем PID из файла
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
                logger.debug(f"Read PID {pid} from file")

            # Проверяем, существует ли процесс
            if not psutil.pid_exists(pid):
                logger.info(f"Process with PID {pid} does not exist")
                os.remove(pid_file)  # Удаляем устаревший PID файл
                return "stopped", None

            # Получаем информацию о процессе
            process = psutil.Process(pid)
            start_time = datetime.datetime.fromtimestamp(process.create_time())
            
            # Проверяем статус процесса
            status_str = process.status()
            logger.debug(f"Process status: {status_str}")
            
            if status_str == psutil.STATUS_RUNNING:
                return "running", start_time
            elif status_str == psutil.STATUS_SLEEPING:
                return "idle", start_time
            else:
                return status_str, start_time

        except (FileNotFoundError, ProcessLookupError, psutil.NoSuchProcess) as e:
            logger.warning(f"Error checking system status: {str(e)}")
            if os.path.exists(pid_file):
                os.remove(pid_file)
            return "stopped", None
        except Exception as e:
            logger.error(f"Unexpected error checking system status: {str(e)}")
            return f"error: {str(e)}", None

    def _stop_system(self):
        """Останавливает систему"""
        try:
            pid_file = os.path.join(settings.BASE_DIR, 'private', 'system.pid')
            if not os.path.exists(pid_file):
                return False, "System is not running"

            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())

            if not psutil.pid_exists(pid):
                os.remove(pid_file)
                return False, "Process not found"

            process = psutil.Process(pid)
            process.terminate()  # Отправляем SIGTERM
            
            try:
                process.wait(timeout=10)  # Ждем завершения процесса
            except psutil.TimeoutExpired:
                process.kill()  # Если процесс не завершился, отправляем SIGKILL
            
            os.remove(pid_file)
            return True, "System stopped successfully"
            
        except Exception as e:
            logger.error(f"Error stopping system: {str(e)}")
            return False, str(e)

    @action(detail=False, methods=['get'])
    def config_private(self, request):
        """Получить приватную конфигурацию"""
        content = self._read_config('private/private_config.yaml')
        if content is None:
            return Response({"error": "Файл конфигурации не найден"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"content": content})

    @action(detail=False, methods=['get'])
    def config_control(self, request):
        """Получить конфигурацию управления"""
        content = self._read_config('private/private_control_config.yaml')
        if content is None:
            return Response({"error": "Файл конфигурации не найден"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"content": content})

    @action(detail=False, methods=['post'])
    def config_private_update(self, request):
        """Обновить приватную конфигурацию"""
        content = request.data.get('content')
        if not content:
            return Response({"error": "Содержимое не предоставлено"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Проверяем, что это валидный YAML
            yaml.safe_load(content)
            self._write_config('private/private_config.yaml', content)
            return Response({"message": "Конфигурация успешно обновлена"})
        except yaml.YAMLError as e:
            return Response({"error": f"Невалидный YAML: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def config_control_update(self, request):
        """Обновить конфигурацию управления"""
        content = request.data.get('content')
        if not content:
            return Response({"error": "Содержимое не предоставлено"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Проверяем, что это валидный YAML
            yaml.safe_load(content)
            self._write_config('private/private_control_config.yaml', content)
            return Response({"message": "Конфигурация успешно обновлена"})
        except yaml.YAMLError as e:
            return Response({"error": f"Невалидный YAML: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Получить статус системы"""
        status_str, start_time = self._check_system_status()
        
        response = {
            "status": status_str,
            "last_update": datetime.datetime.now().isoformat()
        }
        
        if start_time:
            response["start_time"] = start_time.isoformat()
            response["uptime"] = str(datetime.datetime.now() - start_time)
        
        return Response(response)

    @action(detail=False, methods=['post'])
    def run(self, request):
        """Запустить систему"""
        current_status, _ = self._check_system_status()
        if current_status == "running":
            return Response({"error": "Система уже запущена"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Получаем путь к Python из виртуального окружения
            python_executable = getattr(settings, 'PYTHON_EXECUTABLE', sys.executable)
            logger.info(f"Using Python executable: {python_executable}")

            # Создаем лог файл
            log_file = os.path.join(settings.BASE_DIR, 'private', 'system.log')
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Запускаем Django команду run_systems в отдельном процессе
            manage_py = os.path.join(settings.BASE_DIR, 'manage.py')
            if not os.path.exists(manage_py):
                logger.error(f"manage.py не найден по пути: {manage_py}")
                raise FileNotFoundError(f"manage.py не найден по пути: {manage_py}")
            logger.info(f"manage.py найден по пути: {manage_py}")
            with open(log_file, 'a') as f:
                logger.info("Запуск команды run_systems через manage.py, используя python_executable: " + python_executable)
                process = subprocess.Popen(
                    [python_executable, manage_py, 'run_systems'],
                    cwd=settings.BASE_DIR,
                    stdout=f,
                    stderr=f,
                    start_new_session=True
                )

            # Сохраняем PID процесса
            pid_file = os.path.join(settings.BASE_DIR, 'private', 'system.pid')
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))

            logger.info(f"System started with PID {process.pid}")
            return Response({
                "message": "Система запущена",
                "pid": process.pid
            })
        except Exception as e:
            logger.error(f"Error starting system: {str(e)}")
            return Response(
                {"error": f"Ошибка запуска системы: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def stop(self, request):
        """Остановить систему"""
        success, message = self._stop_system()
        if success:
            return Response({"message": message})
        else:
            return Response(
                {"error": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 