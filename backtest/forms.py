from django import forms
from .models import MyConfigModel

class ConfigForm(forms.Form):
    TRADING_RULE_CHOICES = [
        ('breakout10', 'Breakout 10'),
        ('breakout20', 'Breakout 20'),
        ('breakout40', 'Breakout 40'),
        ('breakout80', 'Breakout 80'),
        ('breakout160', 'Breakout 160'),
        ('breakout320', 'Breakout 320'),
        ('relmomentum10', 'Relative Momentum 10'),
        ('relmomentum20', 'Relative Momentum 20'),
        ('relmomentum40', 'Relative Momentum 40'),
        ('relmomentum80', 'Relative Momentum 80'),
        ('mrinasset1000', 'MR In Asset 1000'),
        ('assettrend2', 'Asset Trend 2'),
        ('assettrend4', 'Asset Trend 4'),
        ('assettrend8', 'Asset Trend 8'),
        ('assettrend16', 'Asset Trend 16'),
        ('assettrend32', 'Asset Trend 32'),
        ('assettrend64', 'Asset Trend 64'),
        ('normmom2', 'Normalized Momentum 2'),
        ('normmom4', 'Normalized Momentum 4'),
        ('normmom8', 'Normalized Momentum 8'),
        ('normmom16', 'Normalized Momentum 16'),
        ('normmom32', 'Normalized Momentum 32'),
        ('normmom64', 'Normalized Momentum 64'),
        ('momentum4', 'Momentum 4'),
        ('momentum8', 'Momentum 8'),
        ('momentum16', 'Momentum 16'),
        ('momentum32', 'Momentum 32'),
        ('momentum64', 'Momentum 64'),
    ]
    
    # Создаем поле выбора правила с помощью MultipleChoiceField
    trading_rules = forms.MultipleChoiceField(choices=TRADING_RULE_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}))
