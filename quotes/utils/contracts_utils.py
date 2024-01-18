from datetime import datetime, timedelta
import re

def parse_contract_date(contract):
    match = re.match(r'\D+(\d{4})(\d{2})(\d{2})', contract)
    if match:
        year, month, day = map(int, match.groups())
        return datetime(year, month, day)

def find_current_next_contracts_for_instruments(quote_objects, current_date):
    instruments = quote_objects.values_list('instrument', flat=True).distinct()

    current_next_contracts = {}

    for instrument in instruments:
        instrument_quotes = quote_objects.filter(instrument=instrument)

        future_contracts = instrument_quotes.filter(timestamp__gt=current_date).order_by('timestamp').values_list('contract', flat=True).distinct()

        if future_contracts:
            current_contract = min(future_contracts)
            next_contract = instrument_quotes.filter(contract__gt=current_contract, timestamp__gt=current_date).order_by('timestamp').values_list('contract', flat=True).first()
        else:
            past_contracts = instrument_quotes.filter(timestamp__lt=current_date).order_by('-timestamp').values_list('contract', flat=True).distinct()

            current_contract = None
            next_contract = None

            # Итерируемся по датам в прошлое, пока не найдем подходящий контракт
            for past_contract in past_contracts:
                contract_date = parse_contract_date(past_contract)
                if contract_date and contract_date <= current_date:
                    current_contract = past_contract
                    next_contract = instrument_quotes.filter(contract__gt=current_contract).order_by('timestamp').values_list('contract', flat=True).first()
                    break

        current_next_contracts[instrument] = {'current_contract': current_contract, 'next_contract': next_contract}

    return current_next_contracts

# Пример использования
current_date = datetime.now()
quote_objects = Quote.objects.all()

current_next_contracts = find_current_next_contracts_for_instruments(quote_objects, current_date)

for instrument, contracts in current_next_contracts.items():
    print(f"Instrument: {instrument}, Current Contract: {contracts['current_contract']}, Next Contract: {contracts['next_contract']}")
