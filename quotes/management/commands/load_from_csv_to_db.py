# scripts/load_instruments.py
import pandas as pd
from your_app.models import Quote

# Пример словаря, где ключ - код инструмента, значение - формат строки даты
instrument_to_format = {
    'AE': 'AE_%Y%m%d',
    # Добавьте другие инструменты, если необходимо
}

# Пример словаря, где ключ - контракт, значение - инструмент
contracts_to_instruments = {
    'AE_20240300': 'AED',
    # и так далее
}

# Предположим, что у вас есть DataFrame, считанный из файла CSV
df = pd.read_csv('путь_к_вашему_файлу.csv')

for index, row in df.iterrows():
    # Получаем инструмент из контракта
    instrument = contracts_to_instruments.get(row['INSTRUMENT'], None)

    if instrument:
        # Извлекаем последние два символа контракта
        last_two_chars = row['INSTRUMENT'][-2:]

        # Извлекаем год и месяц из последних двух символов
        year_digit = int(last_two_chars[1])
        month_char = last_two_chars[0]
        month_mapping = {'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6, 'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12}
        month = month_mapping.get(month_char, None)

        if month and year_digit:
            # Создаем объект datetime из года и месяца
            timestamp = pd.to_datetime(f'20{year_digit:02d}-{month:02d}-01')

            Quote.objects.create(
                exchange=row['EXCHANGE'],
                instrument=instrument,
                section=row['SECTION'],
                contract=row['INSTRUMENT'],
                open_price=row['OPEN'],
                high_price=row['HIGH'],
                low_price=row['LOW'],
                close_price=row['CLOSE'],
                volume=row['VOL'],
                timestamp=timestamp
            )

print('Data loaded successfully')
