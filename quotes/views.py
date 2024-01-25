from django.shortcuts import get_list_or_404, redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from quotes.dao import DjangoFuturesSimData

from quotes.models import AdjustedPrice, FxPriceData, Instrument, MultiplePriceData, Quote, RollCalendar
from .forms import LoadDataForm
from django.core.management import call_command


def load_data_view(request):
    if request.method == 'POST':
        form = LoadDataForm(request.POST)
        if form.is_valid():
            # Получите данные из формы
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Вызовите вашу команду с нужными параметрами
            call_command('load_history_instrument_moex', start_date=start_date, end_date=end_date)

            # Опционально: добавьте сообщение об успешной загрузке или другую обратную связь
            success_message = "Data loaded successfully"
            return render(request, 'quotes/quote_load.html', {'form': form, 'success_message': success_message})

    else:
        form = LoadDataForm()

    return render(request, 'quotes/quote_load.html', {'form': form})
def data_view(request):
    return render(request, 'quotes/main_data.html')

def exchange_list_view(request):
    exchanges = Quote.objects.values_list('exchange', flat=True).distinct()
    return render(request, 'quotes/exchange_list.html', {'exchanges': exchanges})

def instrument_list_view(request, exchange):
    # Исключаем записи с пустым значением exchange
    instruments = Quote.objects.exclude(exchange__isnull=True).filter(exchange=exchange).values_list('instrument', flat=True).distinct()
    return render(request, 'quotes/instrument_list.html', {'instruments': instruments, 'exchange': exchange})


def contract_list_view(request, exchange, instrument):
    contracts = Quote.objects.exclude(exchange__isnull=True).filter(exchange=exchange, instrument=instrument).values_list('contract', flat=True).distinct()
    

    return render(request, 'quotes/contract_list.html', {'contracts': contracts, 'exchange': exchange, 'instrument': instrument})
    #return render(request, 'quotes/contract_list.html', {'contracts': contracts, 'exchange': exchange, 'instrument': instrument})

def contract_detail_view(request, exchange, instrument, contract):
    contract_data = Quote.objects.filter(exchange=exchange, instrument=instrument, contract=contract)
    return render(request, 'quotes/contract_detail.html', {'contract_data': contract_data})

def roll_calendar(request, exchange, instrument):
    roll_calendar_entries = RollCalendar.objects.filter(exchange=exchange, instrument__instrument=instrument)
    instrument_obj = Instrument.objects.get(instrument=instrument)
    context = {
        'instrument': instrument_obj,
        'roll_calendar_entries': roll_calendar_entries,
    }
    return render(request, 'quotes/roll_calendar.html', context)

def multiple_price_data(request, exchange, instrument):
    price_data = MultiplePriceData.objects.filter( instrument__instrument=instrument)
    return render(request, 'quotes/multiple_price_data.html', {'price_data': price_data})



@csrf_exempt  # Используй csrf_exempt, чтобы избежать проблем с CSRF-токеном для примера
def update_multiple_price_data(request):
    if request.method == 'GET':
        try:
            call_command('multiple_price_data_update')
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(status=500)
    else:
        return HttpResponse(status=405)

def adjusted_prices_view(request, exchange, instrument):
    # Получите данные о корректированных ценах для отображения
    adjusted_prices = AdjustedPrice.objects.filter(instrument__instrument=instrument)
    instrument_obj = Instrument.objects.get(instrument=instrument)

    # Передайте данные в контексте для использования на странице
    context = {
        'instrument': instrument_obj,
        'adjusted_prices': adjusted_prices,
    }

    # Отобразите HTML-страницу с данными
    return render(request, 'quotes/adjusted_prices.html', context)

def select_exchange_view(request):
    # Получите уникальные биржи
    exchanges = FxPriceData.objects.values_list('exchange', flat=True).distinct()
    return render(request, 'quotes/select_exchange_fx.html', {'exchanges': exchanges})

def select_instrument_view(request, exchange):
    # Получите уникальные инструменты для выбранной биржи
    instruments = FxPriceData.objects.filter(exchange=exchange).values('instrument').distinct()
    return render(request, 'quotes/select_instrument_fx.html', {'exchange': exchange, 'instruments': instruments})

def fx_price_data_view(request, exchange, instrument):
    # Получите данные для выбранной биржи и инструмента
    data = FxPriceData.objects.filter(exchange=exchange, instrument=instrument)
    return render(request, 'quotes/fx_price_data.html', {'exchange': exchange, 'instrument': instrument, 'data': data})

from django.shortcuts import render, redirect
from .models import Instrument

def create_instrument(request):
    # Проверяем, был ли отправлен POST-запрос с данными формы
    if request.method == 'POST':
        # Получаем данные из POST-запроса
        instrument_name = request.POST.get('instrument')
        description = request.POST.get('description')
        point_size = float(request.POST.get('point_size'))
        currency = request.POST.get('currency')
        asset_class = request.POST.get('asset_class')
        slippage = float(request.POST.get('slippage'))
        per_block = float(request.POST.get('per_block'))
        percentage = float(request.POST.get('percentage'))
        per_trade = float(request.POST.get('per_trade'))
        
        # Проверяем, существует ли инструмент с таким именем
        if Instrument.objects.filter(instrument=instrument_name).exists():
            # Инструмент с таким именем уже существует, можете обработать это по своему усмотрению
            return render(request, 'quotes/create_instrument.html', {'error': 'Instrument with this symbol already exists'})

        # Создаем и сохраняем новый инструмент
        instrument = Instrument.objects.create(
            instrument=instrument_name,
            description=description,
            point_size=point_size,
            currency=currency,
            asset_class=asset_class,
            slippage=slippage,
            per_block=per_block,
            percentage=percentage,
            per_trade=per_trade
        )

        # Перенаправляем пользователя на страницу с созданным инструментом
        return redirect('instrument_detail', pk=instrument.pk)

    # Если это GET-запрос, просто отображаем форму создания инструмента
    return render(request, 'quotes/create_instrument.html')


def instrument_detail(request, exchange, instrument):
    # Получаем объект инструмента по его первичному ключу (pk)
    data = Instrument.objects.filter(instrument=instrument)
    return render(request, 'quotes/instrument_detail.html', {'exchange': exchange, 'instrument': instrument, 'data': data})

def test(request):
    # Используем ваш DAO-класс для получения данных
    data_access_object = DjangoFuturesSimData()
    instrument_data = data_access_object.get_instrument_raw_carry_data('Si')

    # Далее обработка данных и передача их в контекст для рендеринга представления
    context = {'instrument_data': instrument_data}
    return render(request, 'test.html', context)

