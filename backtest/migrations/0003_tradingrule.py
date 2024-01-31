# Generated by Django 4.2.9 on 2024-01-31 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backtest', '0002_backtestresult'),
    ]

    operations = [
        migrations.CreateModel(
            name='TradingRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('function', models.CharField(max_length=100)),
                ('data', models.JSONField()),
                ('other_args', models.JSONField()),
            ],
        ),
    ]
