
import pandas as pd
from quotes.sysdata.futures.spread_costs import spreadCostData
from quotes.models import Instrument, SpreadCosts

class djangoSpreadCostData(spreadCostData):
    """
    Read and write data class to get spread cost data for a given instrument using Django ORM.

    We'd inherit from this class for a specific implementation.
    """

    def __repr__(self):
        return "DjangoSpreadCostData base class - DO NOT USE"

    def delete_spread_cost(self, instrument_code: str):
        # Удаление всех записей из базы данных с указанным кодом инструмента
        SpreadCosts.objects.filter(instrument__instrument=instrument_code).delete()

    def update_spread_cost(self, instrument_code: str, spread_cost: float):
        # Обновление или создание записи в базе данных с указанным кодом инструмента
        instrument_instance = Instrument.objects.get(instrument=instrument_code)
        spread_cost_instance, created = SpreadCosts.objects.get_or_create(
            instrument=instrument_instance, defaults={'spreadcost': spread_cost}
        )
        if not created:
            spread_cost_instance.spreadcost = spread_cost
            spread_cost_instance.save()

    def get_list_of_instruments(self) -> list:
        # Получение списка всех инструментов из базы данных
        return list(SpreadCosts.objects.values_list('instrument__instrument', flat=True))

    def get_spread_cost(self, instrument_code: str) -> float:
        # Получение данных из базы данных для указанного инструмента
        instrument_instance = Instrument.objects.get(instrument=instrument_code)
        try:
            spread_cost_instance = SpreadCosts.objects.get(instrument=instrument_instance)
            return spread_cost_instance.spreadcost
        except SpreadCosts.DoesNotExist:
            return 0.0

    def get_spread_costs_as_series(self) -> pd.Series:
        # Получение всех данных из базы данных в виде pd.Series
        spread_costs = SpreadCosts.objects.all().values_list(
            'instrument__instrument', 'spreadcost'
        )
        return pd.Series(dict(spread_costs))
