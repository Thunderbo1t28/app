# myapp/management/commands/populate_pricedata.py

from django.core.management.base import BaseCommand
from quotes.models import Quote, RollCalendar, PriceData
from datetime import datetime

class Command(BaseCommand):
    help = 'Populate PriceData based on Quote and RollCalendar data'

    def handle(self, *args, **options):
        # Пример даты, до которой нужно собрать данные
        end_date = datetime.strptime('2023-12-20 00:00:00', '%Y-%m-%d %H:%M:%S')

        # Получите уникальные инструменты из модели Quote
        instruments = Quote.objects.values_list('instrument', flat=True).distinct()

        for instrument in instruments:
            # Получите релевантные записи из модели RollCalendar для текущего инструмента
            roll_data = RollCalendar.objects.filter(
                instrument=instrument, timestamp__lte=end_date
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

                    # Проверка, существует ли уже запись для данного timestamp
                    existing_entry = PriceData.objects.filter(
                        instrument=instrument, datetime=quote.timestamp
                    ).first()

                    if existing_entry:
                        # Если запись уже существует, обновите ее значения
                        existing_entry.carry = carry_quote.close_price if carry_quote else 0
                        existing_entry.carry_contract = next_contract
                        existing_entry.price = quote.close_price
                        existing_entry.price_contract = current_contract
                        existing_entry.forward = forward_quote.close_price if forward_quote else 0
                        existing_entry.forward_contract = next_contract
                        existing_entry.quote = quote
                        existing_entry.save()
                    else:
                        # Иначе создайте новую запись
                        PriceData.objects.create(
                            instrument=instrument,
                            datetime=quote.timestamp,
                            carry=carry_quote.close_price if carry_quote else 0,
                            carry_contract=next_contract,
                            price=quote.close_price,
                            price_contract=current_contract,
                            forward=forward_quote.close_price if forward_quote else 0,
                            forward_contract=next_contract,
                            quote=quote
                        )

            self.stdout.write(self.style.SUCCESS(f'Successfully populated PriceData for instrument {instrument}.'))
