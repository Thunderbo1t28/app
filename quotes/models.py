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
        #print(ident)
        #print(model)
        if data is None:
            data = ident
        # Попытаться получить существующий объект по идентификатору
        try:
            arctic_data = model.objects.get(ident=ident)
            # Если объект существует, обновить его данные
            arctic_data.data = data
            arctic_data.save()
        except model.DoesNotExist:
            # Если объект не существует, создать новый объект
            arctic_data = model.objects.create(ident=ident, data=data)

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

class spread_costs(models.Model):
    ident = models.CharField(max_length=255, unique=True)
    data = models.JSONField()
    
    objects = ArcticDataManager()

class spotfx_prices(models.Model):
    ident = models.CharField(max_length=255, unique=True)
    data = models.JSONField()
    
    objects = ArcticDataManager()

class arctic_capital(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField()
    
    objects = ArcticDataManager()

class margin(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField()
    
    objects = ArcticDataManager()

class process_control(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField()
    
    objects = ArcticDataManager()

class limit_status(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField()
    
    objects = ArcticDataManager() 

class futures_contracts(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField()
    
    objects = ArcticDataManager()

class spreads(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager() 

class IBClientTracker(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager() 

class optimal_positions(models.Model):
    ident = models.CharField(max_length=255, unique=True)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager() 

class INSTRUMENT_ORDER_STACK(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager() 

class CONTRACT_ORDER_STACK(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager()

class BROKER_ORDER_STACK(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager()

class CONTRACT_HISTORIC_ORDERS(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager()

class STRATEGY_HISTORIC_ORDERS(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager()

class BROKER_HISTORIC_ORDERS(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager()

class futures_roll_status(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager()

class strategy_positions(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager()

class contract_positions(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager()

    def __str__(self):
        return self.ident

class overide_status(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager()

class position_limit_status(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager()

class temporary_close_collection(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager()

class locks(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager()

class Logs(models.Model):
    ident = models.CharField(max_length=255)
    data = models.JSONField(null=True, blank=True)
    
    objects = ArcticDataManager()

class MongoDataSingleKey(models.Model):
    collection_name = models.CharField(max_length=255)
    key_name = models.CharField(max_length=255)

class MongoDataMultipleKeys(models.Model):
    collection_name = models.CharField(max_length=255)
    index_config = models.JSONField(null=True, blank=True)

class MyData(models.Model):
    key = models.CharField(max_length=100)
    trade = models.JSONField()
    fill = models.JSONField()
    fill_datetime = models.DateTimeField(null=True)
    filled_price = models.FloatField(null=True)
    locked = models.BooleanField(default=False)
    order_id = models.IntegerField()
    parent = models.CharField(max_length=100)
    children = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    order_type = models.CharField(max_length=100)
    limit_contract = models.CharField(max_length=100, null=True)
    limit_price = models.FloatField(null=True)
    reference_contract = models.CharField(max_length=100)
    reference_price = models.FloatField()
    manual_trade = models.BooleanField(default=False)
    roll_order = models.BooleanField(default=False)
    reference_datetime = models.DateTimeField()
    generated_datetime = models.DateTimeField()

    class Meta:
        ordering = ['fill_datetime']