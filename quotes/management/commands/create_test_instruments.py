from django.core.management.base import BaseCommand
from quotes.models import Instrument

class Command(BaseCommand):
    help = 'Создает тестовые инструменты в базе данных'

    def handle(self, *args, **options):
        test_instruments = [
            {
                'instrument': 'AAPL',
                'description': 'Apple Inc.',
                'point_size': 0.01,
                'currency': 'USD',
                'asset_class': 'stock',
                'slippage': 0.01,
                'per_block': 1.0,
                'percentage': 0.1,
                'per_trade': 0.5
            },
            {
                'instrument': 'GOOGL',
                'description': 'Alphabet Inc.',
                'point_size': 0.01,
                'currency': 'USD',
                'asset_class': 'stock',
                'slippage': 0.01,
                'per_block': 1.0,
                'percentage': 0.1,
                'per_trade': 0.5
            },
            {
                'instrument': 'MSFT',
                'description': 'Microsoft Corporation',
                'point_size': 0.01,
                'currency': 'USD',
                'asset_class': 'stock',
                'slippage': 0.01,
                'per_block': 1.0,
                'percentage': 0.1,
                'per_trade': 0.5
            }
        ]

        for instrument_data in test_instruments:
            try:
                instrument, created = Instrument.objects.get_or_create(
                    instrument=instrument_data['instrument'],
                    defaults=instrument_data
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Создан инструмент "{instrument.instrument}"'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'Инструмент "{instrument.instrument}" уже существует'
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Ошибка при создании инструмента "{instrument_data["instrument"]}": {str(e)}'
                )) 