# Generated by Django 4.2.9 on 2024-01-17 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0005_alter_quote_close_price_alter_quote_high_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='close_price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='quote',
            name='high_price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='quote',
            name='low_price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='quote',
            name='open_price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='quote',
            name='volume',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
