from datetime import datetime, timedelta
import re

from quotes.models import Quote

def parse_contract_date(contract):
    match = re.match(r'\D+(\d{4})(\d{2})(\d{2})', contract)
    if match:
        year, month, day = map(int, match.groups())
        date = datetime(year, month, day) + timedelta(days=1)
        return date

def find_current_next_contracts_for_instruments(quote_objects, current_date):
    instruments = quote_objects.values_list('instrument', flat=True).distinct()
    print(current_date)
    current_next_contracts = {}
    
    for instrument in instruments:
        instrument_quotes = quote_objects.filter(instrument=instrument)
        exchange = instrument_quotes.values('exchange').first()  # Simplified the exchange retrieval
        current_contract = ''
        next_contract = ''
        future_contracts = instrument_quotes.filter(timestamp__gt=current_date).order_by('timestamp').values_list('contract', flat=True).distinct()

        if future_contracts:
            current_contract = min(future_contracts)
            next_contract_date = parse_contract_date(current_contract).strftime("%Y-%m-%d") if current_contract and '_' in current_contract else current_date
            next_contracts = instrument_quotes.filter(timestamp__gt=next_contract_date).order_by('timestamp').values_list('contract', flat=True)

            if next_contracts:
                next_contract = min(next_contracts)
            else:
                next_contract = instrument_quotes.filter(contract__gt=current_contract, timestamp__gt=current_date).order_by('timestamp').values_list('contract', flat=True).first() if current_contract else ''

        if next_contract and '_' in next_contract:
            next_contract = next_contract.split('_')[1]
            next_contract = f"{next_contract[:4]}{next_contract[4:6]}{next_contract[6:8]}"

        if current_contract and '_' in current_contract:
            current_contract = current_contract.split('_')[1]
            current_contract = f"{current_contract[:4]}{current_contract[4:6]}{current_contract[6:8]}"

        current_next_contracts[instrument] = {'exchange': exchange, 'current_contract': current_contract, 'next_contract': next_contract}
    
    return current_next_contracts
