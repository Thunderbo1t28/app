# models.py
from django.db import models

class MyConfigModel(models.Model):
    trading_rules_ewmac8_Lfast = models.IntegerField()
    trading_rules_ewmac8_Lslow = models.IntegerField()
    trading_rules_ewmac32_Lfast = models.IntegerField()
    trading_rules_ewmac32_Lslow = models.IntegerField()
    # Добавьте другие поля модели, если необходимо


class BacktestResult(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    metrics = models.JSONField()
    additional_info = models.JSONField()

    def __str__(self):
        return f"Backtest Result {self.timestamp}"

class TradingRuleModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    function = models.CharField(max_length=100)
    data = models.JSONField()
    other_args = models.JSONField()

    def __str__(self):
        return self.name