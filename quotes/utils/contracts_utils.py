from datetime import datetime, timedelta
import re

from quotes.models import Quote

def parse_contract_date(contract):
    match = re.match(r'\D+(\d{4})(\d{2})(\d{2})', contract)
    if match:
        year, month, day = map(int, match.groups())
        date = datetime(year, month, day)
        date += timedelta(days=1)
        return date

def find_current_next_contracts_for_instruments(quote_objects, current_date):
    instruments = quote_objects.values_list('instrument', flat=True).distinct()
    current_next_contracts = {}

    for instrument in instruments:
        instrument_quotes = quote_objects.filter(instrument=instrument)
        exchange = instrument_quotes.values('exchange').first()['exchange']
        current_contract = current_date
        next_contract = None
        next_contract_date = None  # Определяем переменную заранее

        future_contracts = instrument_quotes.filter(timestamp__gt=current_date).order_by('timestamp').values_list('contract', flat=True).distinct()

        if future_contracts:
            current_contract = min(future_contracts)
            try:
                next_contract_date = datetime.strptime(current_contract, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Обработка случаев, когда значение не соответствует формату
                print(f"Skipping invalid date: {current_contract}")
                next_contract_date = None
                    # или установите значение, которое вам нужно
            
                if next_contract_date:
                    next_contract_date += timedelta(days=10)
                    
                    #next_contract = next_contract_date.strftime("%Y-%m-%d %H:%M:%S")
        #print(next_contract_date)
        # Используем переменную next_contract_date вне условия
        if next_contract_date is not None:
            next_contracts = instrument_quotes.filter(timestamp__gt=next_contract_date).order_by('timestamp').values_list('contract', flat=True)
            #print(list(next_contracts))
            if next_contracts:
                next_contract = min(next_contracts)
            else:
                next_contracts = instrument_quotes.filter(contract__gt=current_contract, timestamp__gt=current_date).order_by('timestamp').values_list('contract', flat=True)
                
                if next_contracts:
                    next_contract = min(next_contracts)
                else:
                    next_contract = None
        current_next_contracts[instrument] = {'exchange': exchange, 'current_contract': current_contract, 'next_contract': next_contract}

    return current_next_contracts
