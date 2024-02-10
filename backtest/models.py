# models.py
from django.db import models


class BacktestResult(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    min = models.FloatField(null=True, blank=True)
    max = models.FloatField(null=True, blank=True)
    median = models.FloatField(null=True, blank=True)
    mean = models.FloatField(null=True, blank=True)
    std = models.FloatField(null=True, blank=True)
    skew = models.FloatField(null=True, blank=True)
    ann_mean = models.FloatField(null=True, blank=True)
    ann_std = models.FloatField(null=True, blank=True)
    sharpe = models.FloatField(null=True, blank=True)
    sortino = models.FloatField(null=True, blank=True)
    avg_drawdown = models.FloatField(null=True, blank=True)
    time_in_drawdown = models.FloatField(null=True, blank=True)
    calmar = models.FloatField(null=True, blank=True)
    avg_return_to_drawdown = models.FloatField(null=True, blank=True)
    avg_loss = models.FloatField(null=True, blank=True)
    avg_gain = models.FloatField(null=True, blank=True)
    gaintolossratio = models.FloatField(null=True, blank=True)
    profitfactor = models.FloatField(null=True, blank=True)
    hitrate = models.FloatField(null=True, blank=True)
    t_stat = models.FloatField(null=True, blank=True)
    p_value = models.FloatField(null=True, blank=True)
    metrics = models.JSONField(null=True, blank=True)
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

class BacktestResult2(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    instruments = models.TextField()
    min = models.FloatField(null=True, blank=True)
    max = models.FloatField(null=True, blank=True)
    median = models.FloatField(null=True, blank=True)
    mean = models.FloatField(null=True, blank=True)
    std = models.FloatField(null=True, blank=True)
    skew = models.FloatField(null=True, blank=True)
    ann_mean = models.FloatField(null=True, blank=True)
    ann_std = models.FloatField(null=True, blank=True)
    sharpe = models.FloatField(null=True, blank=True)
    sortino = models.FloatField(null=True, blank=True)
    avg_drawdown = models.FloatField(null=True, blank=True)
    time_in_drawdown = models.FloatField(null=True, blank=True)
    calmar = models.FloatField(null=True, blank=True)
    avg_return_to_drawdown = models.FloatField(null=True, blank=True)
    avg_loss = models.FloatField(null=True, blank=True)
    avg_gain = models.FloatField(null=True, blank=True)
    gaintolossratio = models.FloatField(null=True, blank=True)
    profitfactor = models.FloatField(null=True, blank=True)
    hitrate = models.FloatField(null=True, blank=True)
    t_stat = models.FloatField(null=True, blank=True)
    p_value = models.FloatField(null=True, blank=True)
      