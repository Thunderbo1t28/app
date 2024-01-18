from django.shortcuts import get_list_or_404, render, get_object_or_404

from quotes.models import PriceData, Quote
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

def contract_detail_view(request, exchange, instrument, contract):
    contract_data = Quote.objects.filter(exchange=exchange, instrument=instrument, contract=contract)
    return render(request, 'quotes/contract_detail.html', {'contract_data': contract_data})

def price_data_view(request):
    prices = PriceData.objects.all()
    return render(request, 'your_app/price_data.html', {'prices': prices})
