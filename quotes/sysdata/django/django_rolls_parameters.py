
from quotes.sysdata.futures.rolls_parameters import rollParametersData
from quotes.models import Instrument, RollParameters
from quotes.sysobjects.rolls import rollParameters

class djangoRollParametersData(rollParametersData):
    """
    Read and write data class to get roll data for a given instrument using Django ORM.

    We'd inherit from this class for a specific implementation.
    """

    def __repr__(self):
        return "DjangoRollParametersData base class - DO NOT USE"

    def _add_roll_parameters_without_checking_for_existing_entry(
        self, instrument_code: str, roll_parameters: rollParameters
    ):
        # Создание записи в базе данных на основе переданного объекта rollParameters
        instrument_instance = Instrument.objects.get(instrument=instrument_code)
        RollParameters.objects.create(
            exchange=roll_parameters.exchange,
            instrument=instrument_instance,
            hold_rollcycle=roll_parameters.hold_rollcycle,
            priced_rollcycle=roll_parameters.priced_rollcycle,
            roll_offset_day=roll_parameters.roll_offset_day,
            carry_offset=roll_parameters.carry_offset,
            approx_expiry_offset=roll_parameters.approx_expiry_offset
        )

    def _delete_roll_parameters_data_without_any_warning_be_careful(
        self, instrument_code: str
    ):
        # Удаление всех записей из базы данных с указанным кодом инструмента
        RollParameters.objects.filter(instrument__instrument=instrument_code).delete()

    def get_list_of_instruments(self) -> list:
        # Получение списка всех инструментов из базы данных
        return list(Instrument.objects.values_list('instrument', flat=True))

    def _get_roll_parameters_without_checking(
        self, instrument_code: str
    ) -> rollParameters:
        # Получение данных из базы данных для указанного инструмента
        instrument_instance = Instrument.objects.get(instrument=instrument_code)
        roll_parameters_instance = RollParameters.objects.get(instrument=instrument_instance)
        roll_parameters = rollParameters(
            #exchange=roll_parameters_instance.exchange,
            hold_rollcycle=roll_parameters_instance.hold_rollcycle,
            priced_rollcycle=roll_parameters_instance.priced_rollcycle,
            roll_offset_day=roll_parameters_instance.roll_offset_day,
            carry_offset=roll_parameters_instance.carry_offset,
            approx_expiry_offset=roll_parameters_instance.approx_expiry_offset
        )
        return roll_parameters
