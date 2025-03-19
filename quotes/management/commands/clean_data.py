from django.core.management.base import BaseCommand
from quotes.models import (
    LastDownloadDate, MultiplePriceData, RollParameters,
    RollCalendar, AdjustedPrice, SpreadCosts, Instrument
)

class Command(BaseCommand):
    help = 'Очищает проблемные записи в базе данных'

    def handle(self, *args, **options):
        # Получаем все существующие ID инструментов
        valid_instrument_ids = set(Instrument.objects.values_list('id', flat=True))

        # Очищаем LastDownloadDate
        deleted_count = LastDownloadDate.objects.exclude(
            instrument_id__in=valid_instrument_ids
        ).delete()[0]
        self.stdout.write(f'Удалено {deleted_count} записей из LastDownloadDate')

        # Очищаем MultiplePriceData
        deleted_count = MultiplePriceData.objects.exclude(
            instrument_id__in=valid_instrument_ids
        ).delete()[0]
        self.stdout.write(f'Удалено {deleted_count} записей из MultiplePriceData')

        # Очищаем RollParameters
        deleted_count = RollParameters.objects.exclude(
            instrument_id__in=valid_instrument_ids
        ).delete()[0]
        self.stdout.write(f'Удалено {deleted_count} записей из RollParameters')

        # Очищаем RollCalendar
        deleted_count = RollCalendar.objects.exclude(
            instrument_id__in=valid_instrument_ids
        ).delete()[0]
        self.stdout.write(f'Удалено {deleted_count} записей из RollCalendar')

        # Очищаем AdjustedPrice
        deleted_count = AdjustedPrice.objects.exclude(
            instrument_id__in=valid_instrument_ids
        ).delete()[0]
        self.stdout.write(f'Удалено {deleted_count} записей из AdjustedPrice')

        # Очищаем SpreadCosts
        deleted_count = SpreadCosts.objects.exclude(
            instrument_id__in=valid_instrument_ids
        ).delete()[0]
        self.stdout.write(f'Удалено {deleted_count} записей из SpreadCosts') 