from email.policy import default
from django.db import models

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

