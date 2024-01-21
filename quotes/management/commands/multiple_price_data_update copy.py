# myapp/management/commands/populate_pricedata.py

from django.core.management.base import BaseCommand
from quotes.models import Quote, RollCalendar, PriceData
from datetime import datetime, timedelta

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

                    # Создайте запись в модели PriceData с учетом цен закрытия карри и следующего контракта
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

                # Если есть следующий контракт, получите котировки и создайте записи для него
                if next_contract:
                    quotes_next = Quote.objects.filter(
                        instrument=instrument, contract=next_contract, timestamp__gt=end_date
                    )
                    next_contract_date = None
                    carry_contract = next_contract
                    try:
                        next_contract_date = datetime.strptime(current_contract, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        # Обработка случаев, когда значение не соответствует формату
                        print(f"Skipping invalid date: {current_contract}")
                        next_contract_date = None
                            # или установите значение, которое вам нужно
                    
                        if next_contract_date:
                            next_contract_date += timedelta(days=10)
                    if next_contract_date is not None:
                        carry_contracts = Quote.objects.filter(instrument=instrument,timestamp__gt=next_contract_date).order_by('timestamp').values_list('contract', flat=True)
                        #print(list(next_contracts))
                        if carry_contracts:
                            carry_contract = min(carry_contracts)
                        else:
                            carry_contract = None

                    for quote in quotes_next:

                        carry_quote = Quote.objects.filter(
                            instrument=instrument, contract=carry_contract, timestamp=quote.timestamp
                        ).first()

                        # Создайте запись в модели PriceData с учетом цен закрытия карри и следующего контракта
                        PriceData.objects.create(
                            instrument=instrument,
                            datetime=quote.timestamp,
                            carry=carry_quote.close_price if carry_quote else 0,
                            carry_contract=carry_contract,
                            price=quote.close_price,
                            price_contract=next_contract,
                            forward=carry_quote.close_price if carry_quote else 0,
                            forward_contract=carry_contract,
                            quote=quote
                        )

            self.stdout.write(self.style.SUCCESS(f'Successfully populated PriceData for instrument {instrument}.'))
