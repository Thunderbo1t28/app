from django.core.management.base import BaseCommand
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from quotes.models import Instrument, MultiplePriceData, Quote, AdjustedPrice

class Command(BaseCommand):
    help = 'Calculate and save adjusted prices'

    
    def handle(self, *args, **options):
        # Получите уникальные инструменты из PriceData
        instruments = MultiplePriceData.objects.values_list('instrument__instrument', flat=True).distinct()

        for instrument_code in instruments:
            self.stdout.write(f'Processing instrument: {instrument_code}')
            
            # Получите данные из вашей модели PriceData для текущего инструмента
            multiple_prices_data = MultiplePriceData.objects.filter(instrument__instrument=instrument_code)
            # Преобразуйте данные в pandas DataFrame
            multiple_prices_df = pd.DataFrame.from_records(
                multiple_prices_data.values("datetime", "price", "price_contract", "forward", "forward_contract")
            )
            #print(multiple_prices_df)
            multiple_prices_df.set_index("datetime", inplace=True)

            # Примените _panama_stitch для вычисления скорректированных цен
            adjusted_prices = self._panama_stitch(multiple_prices_df, forward_fill=True)
            

            # Сохраните скорректированные цены в базе данных Django
            for timestamp, price in adjusted_prices.items():
                
        
                # Обрабатываем все найденные объекты Quote
                instrument_obj = Instrument.objects.get(instrument=instrument_code)
                AdjustedPrice.objects.create(
                    instrument=instrument_obj, timestamp=timestamp, price=price
                )

            self.stdout.write(self.style.SUCCESS(f'Successfully processed instrument: {instrument_code}'))


    def _panama_stitch(self, multiple_prices_input, forward_fill=False):
        multiple_prices = multiple_prices_input.copy()
        if forward_fill:
            multiple_prices.ffill(inplace=True)

        if multiple_prices.empty:
            raise Exception("Can't stitch an empty multiple prices object")

        adjusted_prices_values = []

        previous_row = multiple_prices.iloc[0, :]
        adjusted_prices_values.append(previous_row.price)

        for _, current_row in multiple_prices.iterrows():
            if current_row.price_contract == previous_row.price_contract:
                adjusted_prices_values.append(current_row.price)
            else:
                adjusted_prices_values = self._roll_in_panama(
                    adjusted_prices_values, previous_row, current_row
                )

            previous_row = current_row

        # Преобразуем adjusted_prices_values в pd.Series с использованием индексов
        adjusted_prices = pd.Series(
            adjusted_prices_values[: len(multiple_prices.index)], index=multiple_prices.index, name="adjusted_price"
        )

        return adjusted_prices



    def _roll_in_panama(self, adjusted_prices_values, previous_row, current_row):
        roll_differential = previous_row.forward - previous_row.price
        if np.isnan(roll_differential):
            raise Exception(
                f"On this day {current_row.timestamp} which should be a roll date "
                f"we don't have prices for both {previous_row.price_contract} and {previous_row.forward_contract} contracts"
            )

        #adjusted_prices_values = [
            #adj_price + roll_differential for adj_price in adjusted_prices_values
        #]
        #adjusted_prices_values.append(current_row.price)
        # Корректируем цены вправо, добавляя разницу к текущей и будущим значениям
        adjusted_prices_values.append(current_row.price + roll_differential)
        return adjusted_prices_values


