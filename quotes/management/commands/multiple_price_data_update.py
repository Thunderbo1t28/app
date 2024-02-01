# myapp/management/commands/populate_pricedata.py

from django.core.management.base import BaseCommand
from quotes.models import Instrument, MultiplePriceData, Quote, RollCalendar
from datetime import datetime

class Command(BaseCommand):
    help = 'Populate PriceData based on Quote and RollCalendar data'

    def handle(self, *args, **options):
        # Пример даты, до которой нужно собрать данные
        end_date = datetime.strptime('2024-01-31 00:00:00', '%Y-%m-%d %H:%M:%S')

        # Получите уникальные инструменты из модели Quote
        instruments = Quote.objects.values_list('instrument', flat=True).distinct()

        for instrument in instruments:
            # Получите релевантные записи из модели RollCalendar для текущего инструмента
            roll_data = RollCalendar.objects.filter(
                instrument__instrument=instrument, timestamp__lte=end_date
            ).order_by('-timestamp')

            # Проход по всем записям в RollCalendar
            for roll_entry in roll_data:
                current_contract = roll_entry.current_contract
                next_contract = roll_entry.next_contract

                # Получите котировки из модели Quote для текущего контракта и даты
                quotes_current = Quote.objects.filter(
                    instrument=instrument, contract=current_contract, timestamp__lte=end_date
                )

                # Создайте записи в модели PriceData на основе текущих котировок
                for quote in quotes_current:
                    carry_quote = Quote.objects.filter(
                        instrument=instrument, contract=roll_entry.carry_contract, timestamp=quote.timestamp
                    ).first()
                    forward_quote = Quote.objects.filter(
                        instrument=instrument, contract=next_contract, timestamp=quote.timestamp
                    ).first()
                    instrument_obj = Instrument.objects.get(instrument=instrument)
                    # Используйте get_or_create для избежания повторных записей
                    entry, created = MultiplePriceData.objects.get_or_create(
                        instrument=instrument_obj,
                        datetime=quote.timestamp,
                        defaults={
                            'carry': carry_quote.close_price if carry_quote else quote.close_price,
                            'carry_contract': roll_entry.carry_contract,
                            'price': quote.close_price,
                            'price_contract': current_contract,
                            'forward': forward_quote.close_price if forward_quote else quote.close_price,
                            'forward_contract': next_contract,
                            'quote': quote
                        }
                    )

                    if not created:
                        # Если запись уже существует, обновите ее значения
                        entry.carry = carry_quote.close_price if carry_quote else quote.close_price
                        entry.carry_contract = roll_entry.carry_contract
                        entry.price = quote.close_price
                        entry.price_contract = current_contract
                        entry.forward = forward_quote.close_price if forward_quote else quote.close_price
                        entry.forward_contract = next_contract
                        entry.quote = quote
                        entry.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully populated PriceData for instrument {instrument}.'))
