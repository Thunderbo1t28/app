from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from django.db import transaction
from quotes.models import Instrument, Quote, RollCalendar
from quotes.utils.contracts_utils import find_current_next_contracts_for_instruments

class Command(BaseCommand):
    help = 'Find current and next contracts for instruments and save to RollCalendar model'

    def handle(self, *args, **options):
        current_date = datetime.strptime("2024-01-18", "%Y-%m-%d").date() 
        quote_objects = Quote.objects.all()

        # Установите количество дней, на которое вы хотите вернуться в прошлое
        days_to_go_back = 2000  # Например, 1 год

        created_entries_count = 0  # Добавленная запись в RollCalendar

        #with transaction.atomic():
        for _ in range(days_to_go_back + 1):
            current_next_contracts = find_current_next_contracts_for_instruments(quote_objects, current_date)
            
            roll_calendar_entries = []

            for instrument, contracts in current_next_contracts.items():
                current_contract = contracts['current_contract']
                next_contract = contracts['next_contract']
                exchange = contracts['exchange']
                #print(f"Instrument: {instrument}, Exchange: {exchange}, Current Contract: {current_contract}, Next Contract: {next_contract}")
                existing_entry = RollCalendar.objects.filter(
                    instrument__instrument=instrument,
                    current_contract=current_contract,
                    next_contract=next_contract,
                    carry_contract=next_contract
                ).exists()

                # Если запись не существует, добавляем её во временный список
                if not existing_entry:
                    # Получите объект Instrument для указанного инструмента
                    instrument_obj = Instrument.objects.get(instrument=instrument)

                    # Создайте объект RollCalendar с использованием объекта Instrument
                    roll_calendar_entries.append(RollCalendar(
                        exchange=exchange,
                        instrument=instrument_obj,
                        current_contract=current_contract,
                        next_contract=next_contract,
                        carry_contract=next_contract,
                        timestamp=current_date
                    ))

            # Если есть записи, добавляем их в базу данных
            if roll_calendar_entries:
                RollCalendar.objects.bulk_create(roll_calendar_entries)
                created_entries_count += len(roll_calendar_entries)
            #print("Roll Calendar Entries:", roll_calendar_entries)
            # Уменьшение текущей даты на один день
            current_date -= timedelta(days=1)

        #self.stdout.write(self.style.SUCCESS(f"Saved {created_entries_count} RollCalendar entries."))