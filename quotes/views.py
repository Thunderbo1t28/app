from django.shortcuts import get_list_or_404, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from quotes.models import PriceData, Quote, RollCalendar
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
    roll_calendar_entries = RollCalendar.objects.filter(exchange=exchange, instrument=instrument)

    context = {
        'instrument': instrument,
        'roll_calendar_entries': roll_calendar_entries,
    }
    return render(request, 'quotes/roll_calendar.html', context)

def instrument_price_data(request, instrument):
    price_data = PriceData.objects.filter(instrument=instrument)
    return render(request, 'quotes/instrument_price_data.html', {'price_data': price_data})

def instrument_list(request):
    instruments = set(PriceData.objects.values_list('instrument', flat=True))
    return render(request, 'quotes/instrument_list_multiple.html', {'instruments': instruments})

def multi_price_data(request):
    return render(request, 'quotes/multi_price_data.html')

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
