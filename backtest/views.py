import json
from django.core.management import call_command
from django.shortcuts import render

from backtest.forms import ConfigForm
from backtest.models import BacktestResult, MyConfigModel
def backtest_callback(metrics, additional_info):
    # Сохранение результатов в базе данных
    #metrics_json = json.dumps(metrics)
    #additional_info_json = json.dumps(additional_info)
    backtest_result = BacktestResult(metrics=metrics, additional_info=additional_info)
    backtest_result.save()

def backtest_view(request):
    if request.method == 'POST':
        form = ConfigForm(request.POST)
        if form.is_valid():
            selected_rules = request.POST.getlist('trading_rules')
            #print("arg_options:", request.POST)
            # Получение других значений конфигурации
            # Вызов команды backtest_test с передачей колбэка
            print(selected_rules)
            args = selected_rules
            
            call_command('backtest_test', *args) #'--callback', backtest_callback,)

            # Извлечение сохраненных результатов из базы данных
            backtest_results = BacktestResult.objects.last()

            # Представление результатов в удобном формате для шаблона
            formatted_results = []
            #for result in backtest_results:
            metrics = json.loads(backtest_results.metrics)
            additional_info = json.loads(backtest_results.additional_info)
            formatted_result = {
                'timestamp': backtest_results.timestamp,
                'metrics': metrics,
                'additional_info': additional_info,
            }
            formatted_results.append(formatted_result)
            return render(request, 'backtest/results.html', {'results': formatted_results})
    else:
        form = ConfigForm()
    return render(request, 'backtest/backtest.html', {'form': form})
