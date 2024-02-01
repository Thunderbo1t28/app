import json
from django.core.management import call_command
from django.shortcuts import redirect, render
from django.urls import reverse

from backtest.forms import ConfigForm, InstrumentChoiceForm
from backtest.models import BacktestResult, InstrumentChoice, TradingConfiguration, TradingRuleConfig
from quotes.models import Instrument
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

# Представление Django для страницы выбора торговых инструментов
def select_instruments_view(request):
    if request.method == 'GET':
        # Получаем доступные инструменты из базы данных или любого другого источника данных
        instruments = Instrument.objects.all  # Пример доступных инструментов
        instrument_form = InstrumentChoiceForm(instrument_choices=instruments)
        return render(request, 'select_instruments.html', {'instrument_form': instrument_form})
    elif request.method == 'POST':
        selected_instruments = request.POST.getlist('instrument_choices')
        config_id = request.GET.get('config_id')
        # Создаем или обновляем выбранные инструменты для данной конфигурации
        configuration = TradingConfiguration.objects.get(config_id=config_id)
        for instrument_name in selected_instruments:
            InstrumentChoice.objects.create(configuration=configuration, instrument_name=instrument_name)
        # Перенаправляем пользователя на другую страницу или делаем что-то еще
        return redirect('some_view')

# Представление Django для страницы выбора торговых правил
def select_rules_view(request):
    if request.method == 'POST':
        form = ConfigForm(request.POST)
        if form.is_valid():
            # Создаем новую конфигурацию
            new_configuration = TradingConfiguration.objects.create()
            selected_rules = request.POST.getlist('trading_rules')
            # Создаем торговое правило для каждого выбранного правила и связываем его с новой конфигурацией
            for rule_name in selected_rules:
                TradingRuleConfig.objects.create(configuration=new_configuration, rule_name=rule_name)
            # Перенаправляем пользователя на страницу выбора торговых инструментов с параметром конфигурации
            return redirect(reverse('select_instruments') + f'?config_id={new_configuration.config_id}')
    else:
        form = ConfigForm()
    return render(request, 'select_rules.html', {'form': form})



