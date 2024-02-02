# Generated by Django 4.2.9 on 2024-02-02 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backtest', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TradingConfiguration',
            fields=[
                ('config_id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='TradingRuleConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_name', models.CharField(max_length=500)),
                ('configuration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backtest.tradingconfiguration')),
            ],
        ),
        migrations.CreateModel(
            name='InstrumentChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instrument_name', models.CharField(max_length=100)),
                ('configuration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backtest.tradingconfiguration')),
            ],
        ),
    ]
