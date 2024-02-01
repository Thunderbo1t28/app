# models.py
from django.db import models

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
    
class TradingConfiguration(models.Model):
    config_id = models.AutoField(primary_key=True)  # Простой порядковый номер
# Дополнительные поля, если необходимо

class TradingRuleConfig(models.Model):
    configuration = models.ForeignKey(TradingConfiguration, on_delete=models.CASCADE)
    rule_name = models.CharField(max_length=500)  # Список имен торговых правил, разделенных запятыми

    def get_rule_names_list(self):
        return self.rule_name.split(',') if self.rule_name else []

class InstrumentChoice(models.Model):
    configuration = models.ForeignKey(TradingConfiguration, on_delete=models.CASCADE)
    instrument_name = models.CharField(max_length=100)
    