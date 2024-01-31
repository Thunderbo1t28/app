import json
from django.core.management import call_command
from django.shortcuts import render

from backtest.forms import ConfigForm
from backtest.models import BacktestResult
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
            trading_rules_ewmac8_Lfast = form.cleaned_data['trading_rules_ewmac8_Lfast']
            trading_rules_ewmac8_Lslow = form.cleaned_data['trading_rules_ewmac8_Lslow']
            trading_rules_ewmac32_Lfast = form.cleaned_data['trading_rules_ewmac32_Lfast']
            trading_rules_ewmac32_Lslow = form.cleaned_data['trading_rules_ewmac32_Lslow']
            
            #print("trading_rules_ewmac8_Lfast:", trading_rules_ewmac8_Lfast)
            #print("trading_rules_ewmac8_Lslow:", trading_rules_ewmac8_Lslow)
            #print("trading_rules_ewmac32_Lfast:", trading_rules_ewmac32_Lfast)
            #print("trading_rules_ewmac32_Lslow:", trading_rules_ewmac32_Lslow)
            
            # Добавьте этот код для отладки
            #print("arg_options:", request.POST)
            # Получение других значений конфигурации
            # Вызов команды backtest_test с передачей колбэка
            
            args = ['8', '32', '32', '128']
            call_command('backtest_test', *args, '--callback', 'backtest_callback',)

            # Извлечение сохраненных результатов из базы данных
            backtest_results = BacktestResult.objects.all()

            # Представление результатов в удобном формате для шаблона
            formatted_results = []
            for result in backtest_results:
                metrics = json.loads(result.metrics)
                additional_info = json.loads(result.additional_info)
                formatted_result = {
                    'metrics': metrics,
                    'additional_info': additional_info,
                }
                formatted_results.append(formatted_result)
            return render(request, 'backtest/results.html', {'results': formatted_results})
    else:
        form = ConfigForm()
    return render(request, 'backtest/backtest.html', {'form': form})
