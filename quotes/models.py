from email.policy import default
from django.db import models

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

class PriceData(models.Model):
    datetime = models.DateTimeField()
    carry = models.FloatField()
    carry_contract = models.CharField(max_length=10)
    price = models.FloatField()
    price_contract = models.CharField(max_length=10)
    forward = models.FloatField()
    forward_contract = models.CharField(max_length=10)

class RollCalendar(models.Model):
    instrument = models.CharField(max_length=50)
    current_contract = models.CharField(max_length=50)
    next_contract = models.CharField(max_length=50)
    start_of_roll_period = models.DateTimeField()
    end_of_roll_period = models.DateTimeField()

    def __str__(self):
        return f"{self.current_contract} ({self.start_of_roll_period} - {self.end_of_roll_period})"
