# Generated by Django 4.2.9 on 2024-01-31 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MyConfigModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trading_rules_ewmac8_Lfast', models.IntegerField()),
                ('trading_rules_ewmac8_Lslow', models.IntegerField()),
                ('trading_rules_ewmac32_Lfast', models.IntegerField()),
                ('trading_rules_ewmac32_Lslow', models.IntegerField()),
            ],
        ),
    ]
