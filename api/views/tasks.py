from rest_framework import viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from celery.result import AsyncResult
import os
import sys
import subprocess
from django.conf import settings

from api.models import Task, LoadHistory
from quotes.models import LastDownloadDate
from api.serializers.serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    lookup_value_regex = '\d+'

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=False, methods=['post'], url_path='run')
    def run_task(self, request):
        command = request.data.get('command', '')
        if command == 'load_to_database':
            try:
                python_executable = getattr(settings, 'PYTHON_EXECUTABLE', sys.executable)
                manage_py = os.path.join(settings.BASE_DIR, 'manage.py')
                log_file = os.path.join(settings.BASE_DIR, 'private', 'load_to_database.log')
                log_dir = os.path.dirname(log_file)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                with open(log_file, 'w') as f:
                    process = subprocess.Popen(
                        [python_executable, manage_py, 'load_to_database'],
                        cwd=settings.BASE_DIR,
                        stdout=f,
                        stderr=f,
                        start_new_session=True
                    )
                return Response({"task_id": process.pid}, status=202)
            except Exception as e:
                return Response({"error": f"Ошибка при запуске команды: {str(e)}"}, status=500)
        return Response({"error": "Неизвестная команда"}, status=400)

@api_view(['GET'])
def check_task_status(request, task_id):
    task_result = AsyncResult(task_id)
    result = {
        'task_id': task_id,
        'task_status': task_result.status,
        'task_result': task_result.result
    }
    return Response(result)

@api_view(['GET'])
def instruments_status(request):
    log_file = os.path.join(settings.BASE_DIR, 'private', 'instruments_status.log')
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    with open(log_file, 'a', encoding='utf-8') as logf:
        logf.write("BASE_DIR: {}. Лог файл: {}. Вход в функцию instruments_status\n".format(settings.BASE_DIR, log_file))
        logf.flush()

    try:
        instruments = LastDownloadDate.objects.all()
    except Exception as e:
        with open(log_file, 'a', encoding='utf-8') as logf:
            logf.write("Ошибка при доступе к базе данных модели LastDownloadDate: {}\n".format(str(e)))
        return Response({"error": "Ошибка доступа к базе данных"}, status=500)

    instruments_data = []
    with open(log_file, 'a', encoding='utf-8') as logf:
        count = instruments.count()
        logf.write("Запрос статуса инструментов: {} записей найдено\n".format(count))
        for inst in instruments:
            try:
                inst_instrument = str(inst.instrument) if inst.instrument else None
            except Exception as e:
                inst_instrument = "NonSerializable"
                logf.write("Ошибка конвертации поля instrument для ID {}: {}\n".format(inst.id, str(e)))
            try:
                inst_contract = str(inst.contract) if inst.contract else None
            except Exception as e:
                inst_contract = "NonSerializable"
                logf.write("Ошибка конвертации поля contract для ID {}: {}\n".format(inst.id, str(e)))
            try:
                inst_last_download_date = inst.last_download_date.isoformat() if inst.last_download_date else None
            except Exception as e:
                inst_last_download_date = "NonSerializable"
                logf.write("Ошибка конвертации поля last_download_date для ID {}: {}\n".format(inst.id, str(e)))
            logf.write("Инструмент ID {}: instrument: {}, contract: {}\n".format(inst.id, inst_instrument, inst_contract))
            instruments_data.append({
                "id": inst.id,
                "instrument": inst_instrument,
                "last_contract": inst_contract,
                "last_download_date": inst_last_download_date,
            })
    data = {"instruments": instruments_data}
    try:
        import json
        json.dumps(data)
    except Exception as e:
        with open(log_file, 'a', encoding='utf-8') as logf:
            logf.write("Ошибка сериализации JSON: {}\n".format(str(e)))
        return Response({"error": "Ошибка сериализации JSON", "detail": str(e)}, status=500)
    return Response(data)

@api_view(['GET'])
def load_history(request):
    history_qs = LoadHistory.objects.all().order_by('-created_at')
    history_list = [{
        "id": item.id,
        "status": item.status,
        "message": item.message,
        "details": item.details,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "completed_at": item.completed_at.isoformat() if item.completed_at else None,
    } for item in history_qs]
    return Response({"history": history_list})

@api_view(['POST'])
def load_to_database(request):
    try:
        python_executable = getattr(settings, 'PYTHON_EXECUTABLE', sys.executable)
        manage_py = os.path.join(settings.BASE_DIR, 'manage.py')
        log_file = os.path.join(settings.BASE_DIR, 'private', 'load_to_database.log')
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        with open(log_file, 'w') as f:
            process = subprocess.Popen(
                [python_executable, manage_py, 'load_to_database'],
                cwd=settings.BASE_DIR,
                stdout=f,
                stderr=f,
                start_new_session=True
            )
        return Response({"task_id": process.pid}, status=202)
    except Exception as e:
        return Response({"error": f"Ошибка при запуске команды: {str(e)}"}, status=500)

@api_view(['POST'])
def run_systems(request):
    try:
        python_executable = getattr(settings, 'PYTHON_EXECUTABLE', sys.executable)
        manage_py = os.path.join(settings.BASE_DIR, 'manage.py')
        log_file = os.path.join(settings.BASE_DIR, 'private', 'system.log')
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        with open(log_file, 'w') as f:
            process = subprocess.Popen(
                [python_executable, manage_py, 'run_systems'],
                cwd=settings.BASE_DIR,
                stdout=f,
                stderr=f,
                start_new_session=True
            )
        return Response({"task_id": process.pid}, status=202)
    except Exception as e:
        return Response({"error": f"Ошибка при запуске команды: {str(e)}"}, status=500) 