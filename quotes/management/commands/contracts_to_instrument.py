# quotes/management/commands/contracts_to_instrument.py
from django.core.management.base import BaseCommand
from quotes.models import Quote

class Command(BaseCommand):
    help = 'Load contracts to instrument data into the database'

    def handle(self, *args, **options):
        # Инициализация словаря
        contracts_to_instruments = {}

        # Заполнение словаря на основе данных из базы данных
        quotes = Quote.objects.all()

        for quote in quotes:
            # Проверка наличия значений в полях contract и instrument
            if quote.secid and quote.contract:
                contracts_to_instruments[quote.secid] = quote.contract

        # Вывод словаря (можете удалить эту строку в конечной версии)
        print(contracts_to_instruments)

        # Ваш дальнейший код...
