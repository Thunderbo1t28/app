# quotes/management/commands/contracts_to_instrument.py
from django.core.management.base import BaseCommand
from quotes.models import FxPriceData, Quote

class Command(BaseCommand):
    help = 'Load contracts to instrument data into the database'

    def handle(self, *args, **options):
        # Инициализация словаря
        fx_name = []

        # Заполнение словаря на основе данных из базы данных
        quotes = FxPriceData.objects.all()

        for quote in quotes:
            # Проверка наличия значений в полях contract и instrument
            if quote.instrument and quote.instrument in fx_name:
                continue
            fx_name.append(quote.instrument)

        # Вывод словаря (можете удалить эту строку в конечной версии)
        print(fx_name)

        # Ваш дальнейший код...
