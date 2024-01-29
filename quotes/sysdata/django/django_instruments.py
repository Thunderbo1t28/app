from quotes.sysdata.futures.instruments import futuresInstrumentData
from quotes.models import Instrument
from quotes.sysobjects.instruments import futuresInstrument, futuresInstrumentWithMetaData, instrumentMetaData

class djangoFuturesInstrumentData(futuresInstrumentData):
    """
    Read and write data class to get instrument data using Django ORM.

    We'd inherit from this class for a specific implementation.
    """

    def __repr__(self):
        return "DjangoFuturesInstrumentData base class - DO NOT USE"

    def _add_instrument_data_without_checking_for_existing_entry(
        self, instrument_object: futuresInstrumentWithMetaData
    ):
        # Создание записи в базе данных на основе переданного объекта инструмента
        Instrument.objects.create(
            instrument=instrument_object.instrument_code,
            description=instrument_object.description,
            point_size=instrument_object.point_size,
            currency=instrument_object.currency,
            asset_class=instrument_object.asset_class,
            slippage=instrument_object.slippage,
            per_block=instrument_object.per_block,
            percentage=instrument_object.percentage,
            per_trade=instrument_object.per_trade
        )

    def get_list_of_instruments(self):
        # Получение списка всех инструментов из базы данных
        return list(Instrument.objects.values_list('instrument', flat=True))

    def _get_instrument_data_without_checking(self, instrument_code: str):
        try:
            instrument = Instrument.objects.get(instrument=instrument_code)
            meta_data = instrumentMetaData(
                Description=instrument.description,
                Currency=instrument.currency,
                Pointsize=instrument.point_size,
                AssetClass=instrument.asset_class,
                PerBlock=instrument.per_block,
                Percentage=instrument.percentage,
                PerTrade=instrument.per_trade,
                Region=""  # You might need to adjust this based on your data
            )
            # Получение объекта Instrument из базы данных по коду инструмента
            #instrument_instance = Instrument.objects.get(instrument=instrument_code)
            # Создание объекта futuresInstrumentWithMetaData на основе полученных данных из базы данных
            instrument_data = futuresInstrumentWithMetaData(futuresInstrument(instrument_code), meta_data)
                #Description=instrument_instance.description,
                #Pointsize=instrument_instance.point_size,
               # Currency=instrument_instance.currency,
                #AssetClass=instrument_instance.asset_class,
                #PerBlock=instrument_instance.per_block,
                #Percentage=instrument_instance.percentage,
                #PerTrade=instrument_instance.per_trade
            #)
        except Instrument.DoesNotExist:
            # Если инструмент не найден в базе данных, создаем пустой объект
            instrument_data = futuresInstrumentWithMetaData.create_empty()

        return instrument_data

    def _delete_instrument_data_without_any_warning_be_careful(
        self, instrument_code: str
    ):
        # Удаление записи из базы данных по коду инструмента
        Instrument.objects.filter(instrument=instrument_code).delete()
