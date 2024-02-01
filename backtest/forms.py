from django import forms


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
        ('carry10', 'carry10'),
        ('carry30', 'carry30'),
        ('carry60', 'carry60'),
        ('carry125', 'carry125'),
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
        ('relcarry', 'relcarry'),
        ('skewabs365', 'skewabs365'),
        ('skewabs180', 'skewabs180'),
        ('skewrv365', 'skewrv365'),
        ('skewrv180', 'skewrv180'),
        ('accel16', 'accel16'),
        ('accel32', 'accel32'),
        ('accel64', 'accel64'),
    ]
    
    # Создаем поле выбора правила с помощью MultipleChoiceField
    trading_rules = forms.MultipleChoiceField(choices=TRADING_RULE_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}))

class InstrumentChoiceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        instrument_choices = kwargs.pop('instrument_choices', None)
        super(InstrumentChoiceForm, self).__init__(*args, **kwargs)
        
        # Создаем выбор инструментов на основе QuerySet
        if instrument_choices:
            choices = [(instrument.id, instrument.instrument) for instrument in instrument_choices]
            self.fields['instruments'] = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple)