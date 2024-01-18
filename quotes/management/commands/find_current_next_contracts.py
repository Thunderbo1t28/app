from django.core.management.base import BaseCommand
from datetime import datetime
from quotes.models import Quote, RollCalendar
from quotes.utils.contracts_utils import find_current_next_contracts_for_instruments

class Command(BaseCommand):
    help = 'Find current and next contracts for instruments and save to RollCalendar model'

    def handle(self, *args, **options):
        current_date = datetime.now()
        quote_objects = Quote.objects.all()

        current_next_contracts = find_current_next_contracts_for_instruments(quote_objects, current_date)

        for instrument, contracts in current_next_contracts.items():
            current_contract = contracts['current_contract']
            next_contract = contracts['next_contract']
            start_of_roll_period = contracts['current_contract_date']
            end_of_roll_period = contracts['next_contract_date']

            # Сохранение данных в модель RollCalendar
            roll_calendar_entry = RollCalendar.objects.create(
                instrument=instrument,
                current_contract=current_contract,
                next_contract=next_contract,
                start_of_roll_period=start_of_roll_period,
                end_of_roll_period=end_of_roll_period
            )

            self.stdout.write(self.style.SUCCESS(f"Saved RollCalendar entry: {roll_calendar_entry}"))
