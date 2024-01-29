from quotes.sysdata.base_data import baseData
from quotes.syscore.exceptions import ContractNotFound
from quotes.sysdata.futures.contracts import futuresContractData
from quotes.sysobjects.contract_dates_and_expiries import listOfContractDateStr
from quotes.sysobjects.contracts import futuresContract, listOfFuturesContracts
from quotes.models import Quote  # Замените "your_app" на имя вашего приложения Django

class djangoFuturesContractData(futuresContractData):
    def get_list_of_contract_dates_for_instrument_code(
        self, instrument_code: str, allow_expired: bool = False
    ) -> listOfContractDateStr:
        dates_queryset = Quote.objects.filter(instrument=instrument_code).values_list('timestamp', flat=True).distinct()
        return listOfContractDateStr(sorted(set(dates_queryset)))

    def get_all_contract_objects_for_instrument_code(
        self, instrument_code: str
    ) -> listOfFuturesContracts:
        contracts = []
        for timestamp in self.get_list_of_contract_dates_for_instrument_code(instrument_code):
            contract = self.get_contract_object(instrument_code, str(timestamp.date()))
            contracts.append(contract)
        return listOfFuturesContracts(contracts)

    def _get_contract_data_without_checking(
        self, instrument_code: str, contract_date: str
    ) -> futuresContract:
        try:
            quote = Quote.objects.get(instrument=instrument_code, timestamp=contract_date)
            return futuresContract(
                instrument_code=quote.instrument,
                date_str=str(quote.timestamp.date()),
                expiry_date_str="",  # Заполните этот атрибут соответствующим значением из модели, если требуется
                roll_cycle="",  # Заполните этот атрибут соответствующим значением из модели, если требуется
                open_price=quote.open_price,
                high_price=quote.high_price,
                low_price=quote.low_price,
                close_price=quote.close_price,
                volume=quote.volume
            )
        except Quote.DoesNotExist:
            raise ContractNotFound(f"Contract {instrument_code}/{contract_date} not found")

    def _delete_contract_data_without_any_warning_be_careful(
        self, instrument_code: str, contract_date: str
    ):
        Quote.objects.filter(instrument=instrument_code, timestamp=contract_date).delete()

    def get_list_of_all_instruments_with_contracts(self) -> list:
        return Quote.objects.values_list('instrument', flat=True).distinct()

    def is_contract_in_data(self, instrument_code: str, contract_date_str: str) -> bool:
        return Quote.objects.filter(instrument=instrument_code, timestamp=contract_date_str).exists()

    def _add_contract_object_without_checking_for_existing_entry(
        self, contract_object: futuresContract
    ):
        timestamp_date = contract_object.date_str
        Quote.objects.create(
            exchange="",  # Заполните этот атрибут соответствующим значением из модели, если требуется
            instrument=contract_object.instrument_code,
            section="",  # Заполните этот атрибут соответствующим значением из модели, если требуется
            contract="",  # Заполните этот атрибут соответствующим значением из модели, если требуется
            sectype="",  # Заполните этот атрибут соответствующим значением из модели, если требуется
            secid="",  # Заполните этот атрибут соответствующим значением из модели, если требуется
            open_price=contract_object.open_price,
            high_price=contract_object.high_price,
            low_price=contract_object.low_price,
            close_price=contract_object.close_price,
            volume=contract_object.volume,
            timestamp=timestamp_date
        )
