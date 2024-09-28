import json
from click import command
import pandas as pd
from rest_framework import viewsets
from rest_framework.response import Response
from api.management.commands import run_backtest
from api.tasks import run_management_command_task
from backtest.models import BacktestResult2
from quotes.models import Instrument, contract_positions, arctic_capital
from .serializers import arctic_capitalSerializer, contract_positionsSerializer, instrumentSerializer
from sysdata.arctic.arctic_connection import arcticData
import numpy as np
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.contrib.auth.models import User  # Добавляем этот импорт
from rest_framework_simplejwt.tokens import AccessToken
import logging
from django.core.management import call_command

from celery.result import AsyncResult

logger = logging.getLogger(__name__)

from time import sleep

@api_view(['GET'])
def check_task_status(request):
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({'error': 'Task ID not provided'}, status=400)

    
    task_result = AsyncResult(task_id)
    
    if task_result.state == 'SUCCESS':
        output = task_result.result['output']
        try:
            # Преобразование строки в словарь
            #output_dict = json.loads(output)
            if output['command'] == 'run_backtest':
                backtest_id = output['stats']
                positions = output['positions']
                backtest_result = BacktestResult2.objects.get(id=backtest_id)
                result_data = {
                    'instruments': backtest_result.instruments,
                    'min': backtest_result.min,
                    'max': backtest_result.max,
                    'median': backtest_result.median,
                    'mean': backtest_result.mean,
                    'std': backtest_result.std,
                    'skew': backtest_result.skew,
                    'ann_mean': backtest_result.ann_mean,
                    'ann_std': backtest_result.ann_std,
                    'sharpe': backtest_result.sharpe,
                    'sortino': backtest_result.sortino,
                    'avg_drawdown': backtest_result.avg_drawdown,
                    'time_in_drawdown': backtest_result.time_in_drawdown,
                    'calmar': backtest_result.calmar,
                    'avg_return_to_drawdown': backtest_result.avg_return_to_drawdown,
                    'avg_loss': backtest_result.avg_loss,
                    'avg_gain': backtest_result.avg_gain,
                    'gaintolossratio': backtest_result.gaintolossratio,
                    'profitfactor': backtest_result.profitfactor,
                    'hitrate': backtest_result.hitrate,
                    't_stat': backtest_result.t_stat,
                    'p_value': backtest_result.p_value,
                    'positions': positions
                }
                return JsonResponse({'status': 'SUCCESS', 'result': result_data})
            elif output['command'] == 'load_to_database':

                return JsonResponse({'status': 'SUCCESS'})
        except BacktestResult2.DoesNotExist:
            return JsonResponse({'status': 'FAILURE', 'error': 'Result not found'}, status=404)
    
    elif task_result.state == 'FAILURE':
        return JsonResponse({'status': 'FAILURE', 'error': str(task_result.result)}, status=500)
    
    elif task_result.state == 'PENDING':
        return JsonResponse({'status': 'PENDING', 'task_id': str(task_id)}, status=202)
    
    else:
        return JsonResponse({'status': task_result.state})



class contract_positionsViewSet(viewsets.ModelViewSet):
    queryset = contract_positions.objects.all()
    serializer_class = contract_positionsSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Собираем все идентификаторы для однократного запроса к arcticData
        idents = [item.ident for item in queryset]
        
        # Читаем данные из arcticData для всех идентификаторов
        parsed_data = {}
        for ident in idents:
            data = arcticData("contract_positions", mongo_db=None).read(ident)
            if isinstance(data, pd.DataFrame):
                # Если data является датафреймом, извлекаем последнюю запись из столбца position
                last_position = data['position'].iloc[-1] if not data.empty else None
                if isinstance(last_position, np.float64):
                    parsed_data[ident] = [float(last_position)]  # Преобразуем в список с одним элементом
                else:
                    parsed_data[ident] = None
            else:
                parsed_data[ident] = None
        
        # Строим ответ с использованием сериализатора
        results = []
        for item in queryset:
            results.append({
                "id": item.id,
                "ident": item.ident,
                "data": {
                    "position": parsed_data[item.ident]
                }
            })
        
        return Response(results)


class arctic_capitalViewSet(viewsets.ModelViewSet):
    queryset = arctic_capital.objects.all()
    serializer_class = arctic_capitalSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Собираем все идентификаторы для однократного запроса к arcticData
        idents = [item.ident for item in queryset]
        
        # Читаем данные из arcticData для всех идентификаторов
        parsed_data = {}
        for ident in idents:
            data = arcticData("arctic_capital", mongo_db=None).read(ident)
            if isinstance(data, pd.DataFrame):
                # Преобразуем индекс в строку и значения в списки
                parsed_data[ident] = {
                    'x': data.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    'y': data.iloc[:, 0].tolist()  # Предполагаем, что значения находятся в первом столбце
                }
            else:
                parsed_data[ident] = None
        
        # Строим ответ с использованием сериализатора
        results = []
        for item in queryset:
            if item.ident == 'example':
                results.append({
                    "id": item.id,
                    "ident": item.ident,
                    "data": parsed_data[item.ident]
                })
        
        return Response(results)
    
class instrumentViewSet(viewsets.ModelViewSet):
    queryset = Instrument.objects.all()
    serializer_class = instrumentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Строим ответ с использованием сериализатора
        results = []
        for item in queryset:
            results.append({
                "instrument": item.instrument,
            })
        
        return Response(results)



@api_view(['POST'])
def run_management_command(request):
    token_key = request.data.get('token')
    if not token_key:
        return JsonResponse({'error': 'Token not specified'}, status=400)

    try:
        # Декодируем JWT токен
        access_token = AccessToken(token_key)
        user_id = access_token['user_id']

        # Получаем пользователя из ID
        user = User.objects.get(id=user_id)
        request.user = user
    except Exception as e:
        logger.error(f"Error decoding token or retrieving user: {e}")
        return JsonResponse({'error': 'Invalid token or user does not exist', 'details': str(e)}, status=401)

    command_name = request.data.get('command')
    if not command_name:
        return JsonResponse({'error': 'Command not specified'}, status=400)

    command_args = request.data.get('args', [])
    command_options = request.data.get('options', {})

    if not command_args:
        command_args = ['default_value']  # замените 'default_value' на актуальные значения
    
    if command_name == 'run_backtest':
        for key in ['instrument', 'currency', 'capital', 'target']:
            if key not in command_options or not command_options[key]:
                return JsonResponse({'error': f'Missing or empty value for required parameter: {key}'}, status=400)

    try:
        # Запускаем Celery задачу
        task = run_management_command_task.delay(command_name, **command_options)
        return JsonResponse({'status': 'success', 'task_id': task.id})
    except Exception as e:
        logger.error(f"Error running management command: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)