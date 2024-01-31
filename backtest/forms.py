# forms.py
from django import forms
from .models import MyConfigModel

class ConfigForm(forms.ModelForm):
    class Meta:
        model = MyConfigModel
        fields = ['trading_rules_ewmac8_Lfast', 'trading_rules_ewmac8_Lslow',
                  'trading_rules_ewmac32_Lfast', 'trading_rules_ewmac32_Lslow']
        # Добавьте другие поля модели, если необходимо
