from email.policy import default
from django.db import models
import pandas as pd

class Instrument(models.Model):
    instrument = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)
    point_size = models.FloatField()
    currency = models.CharField(max_length=3)
    asset_class = models.CharField(max_length=50)
    slippage = models.FloatField()
    per_block = models.FloatField(null=True, blank=True)
    percentage = models.FloatField(null=True, blank=True)
    per_trade = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.instrument    
    
class Quote(models.Model):
    exchange = models.CharField(max_length=50)
    instrument = models.CharField(max_length=50)
    section = models.CharField(max_length=50)
    contract = models.CharField(max_length=50, blank=True, null=True)
    sectype = models.CharField(max_length=50, blank=True, null=True)
    secid = models.CharField(max_length=50, blank=True, null=True)
    open_price = models.FloatField(default=0,null=True, blank=True)
    high_price = models.FloatField(default=0,null=True, blank=True)
    low_price = models.FloatField(default=0,null=True, blank=True)
    close_price = models.FloatField(default=0, null=True, blank=True)
    volume = models.FloatField(default=0, null=True, blank=True)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.instrument} - {self.timestamp}"

class MultiplePriceData(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    carry = models.FloatField()
    carry_contract = models.CharField(max_length=10, null=True, blank=True)
    price = models.FloatField()
    price_contract = models.CharField(max_length=10)
    forward = models.FloatField()
    forward_contract = models.CharField(max_length=10, null=True, blank=True)

    # Внешний ключ для связи с котировкой
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)

    def __str__(self):
        return f"PriceData for {self.quote.instrument} - {self.datetime}"

class RollParameters(models.Model):
    exchange = models.CharField(max_length=50)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    hold_rollcycle = models.CharField(max_length=50)
    priced_rollcycle = models.CharField(max_length=50)
    roll_offset_day = models.IntegerField(default=0)
    carry_offset = models.IntegerField(default=-1)
    approx_expiry_offset = models.IntegerField(default=0)

class RollCalendar(models.Model):
    exchange = models.CharField(max_length=50)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    current_contract = models.CharField(max_length=50, null=True, blank=True)
    next_contract = models.CharField(max_length=50, null=True, blank=True)
    carry_contract = models.CharField(max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.current_contract} ({self.next_contract} - {self.carry_contract})"
class AdjustedPrice(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    price = models.FloatField()

    def __str__(self):
        return f"AdjustedPrice for {self.instrument} - {self.timestamp}"

class FxPriceData(models.Model):
    timestamp = models.DateTimeField()
    exchange = models.CharField(max_length=50)
    section = models.CharField(max_length=50)
    instrument = models.CharField(max_length=50, blank=True, null=True)
    currency = models.CharField(max_length=50, blank=True, null=True)
    price = models.FloatField(default=0, null=True, blank=True)

    def __str__(self):
        return f"{self.instrument} - {self.timestamp}"
    
class SpreadCosts(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    spreadcost = models.FloatField()

class LastDownloadDate(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    contract = models.CharField(max_length=100)  # Имя контракта - дата последнего торгового дня
    last_download_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)  # Статус контракта (торгуется или закрыт)

    class Meta:
        unique_together = ('instrument', 'contract')

    def __str__(self):
        return f'{self.instrument} - {self.contract} ({self.last_download_date})'
    
class ArcticDataManager(models.Manager):
    def create_arctic_data(self, model, ident, data):
        #print(data)
        arctic_data = model.objects.update_or_create(ident=ident, data=data)
        #arctic_data.save()
        
        # Вернуться к предыдущему порядку столбцов, если необходимо
        #data_copy = data_copy[data_present]
        #print(arctic_data)
        return arctic_data
    
class ArcticDataModel(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField()

    objects = ArcticDataManager()

    def __str__(self):
        return self.ident
    
'''class futures_contract_pricesManager(models.Manager):
    def create_arctic_data(self, ident, data):
        arctic_data = ArcticDataManager().create_arctic_data(ident=ident, data=data)
        return arctic_data'''

class futures_contract_prices(models.Model):
    ident = models.CharField(max_length=255, unique=True)
    data = models.JSONField()
    
    objects = ArcticDataManager()

class futures_adjusted_prices(models.Model):
    ident = models.CharField(max_length=255, unique=True)
    data = models.JSONField()
    
    objects = ArcticDataManager()

class futures_multiple_prices(models.Model):
    ident = models.CharField(max_length=255, unique=True)
    data = models.JSONField()
    
    objects = ArcticDataManager()

class spreads(models.Model):
    ident = models.CharField(max_length=255, unique=True)
    data = models.JSONField()
    
    objects = ArcticDataManager()

class MongoDataSingleKey(models.Model):
    collection_name = models.CharField(max_length=255)
    key_name = models.CharField(max_length=255)

class MongoDataMultipleKeys(models.Model):
    collection_name = models.CharField(max_length=255)
    index_config = models.JSONField(null=True, blank=True)